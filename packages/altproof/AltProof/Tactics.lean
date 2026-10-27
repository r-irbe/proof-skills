/-
Copyright (c) 2026 Proof-Skills. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Proof-Skills Contributors
SPDX-License-Identifier: Apache-2.0
-/

import AltProof.Core
import Mathlib.Tactic
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Algebra.BigOperators.Ring.Finset

set_option autoImplicit false

/-!
# AltProof.Tactics -- Speculative Alternative-Proof & Elegance Meta-Tactics

Production Layer-0 implementation of the AltProof tactic suite
(`SPEC-ALT-PROOF-DES`, `ALT_PROOF_SAIR_BRIDGE`):

1. **Goal AST & Local Context Feature Detector (`GoalFeatures`)**:
   Re-exported from `AltProof.Core` (`import Lean` only) and inspects the active
   `MVarId` target `Expr` and local context to detect:
   - `hasFinsetSum`: `Finset.sum` linear / congruence structures
   - `hasAbs`: norm or absolute-value subgoals (`abs`)
   - `hasIteOrDecide`: branched `ite` / `dite` / `decide` boolean-reflection shapes
   - `hasNegOrContra`: negation / contradiction hypotheses
   - `hasNatArith`: discrete `Nat` / `Int` Presburger arithmetic
   - `hasWellFounded`: `WellFounded.fix` unfolding traps
   - `hasBitVec`: `BitVec` fixed-width bitvector terms

2. **Two-Axis Cost Ranker (`computeCostX10`, `TwoAxisScore`)**:
   Combines the B1 `extraction-outranks` reader-elegance metric with the
   SAIR machine-side kernel heartbeat cost (`IO.getNumHeartbeats`).

3. **`sum_congr_ring`, `finset_nonneg`, and `finset_mono` Tactics**:
   - `sum_congr_ring`: Normalizes `Finset.sum` linearity (`sum_add_distrib`, `sum_sub_distrib`,
     `mul_sum`, `sum_mul`) and closes pointwise congruence goals via
     `Finset.sum_congr rfl fun _ _ => by ring`.
   - `finset_nonneg`: Discharges `0 ≤ ∑ i ∈ s, f i` via `Finset.sum_nonneg` and
     pointwise hypothesis instantiation (`specializePointwiseHyps`).
   - `finset_mono`: Discharges `∑ i ∈ s, f i ≤ ∑ i ∈ s, g i` via `Finset.sum_le_sum`,
     pointwise hypothesis instantiation (`specializePointwiseHyps`), and ordered-ring
     monotonicity closers (`linarith`, `nlinarith`, `omega`, `positivity`, `gcongr`,
     `solve_by_elim`, `aesop`).

4. **`alt_proof` Meta-Tactic**:
   Ordered automated reduction cascade (`rfl`, `assumption`, `bv_decide`, `decide`, `omega`,
   `ring`, `sum_congr_ring`, `finset_nonneg`, `finset_mono`, `positivity`,
   `linarith`, `nlinarith`, `norm_num`, `aesop`)
   that discharges standard algebraic, arithmetic, and finite-sum goals.

5. **Speculative `elegance?` Tactic**:
   - Filters `routeTable` (16 canonical routes) by relevance against `GoalFeatures` (Method 2: relevance
     filter + Method 1: capped enumeration per `SPEC-ALT-PROOF-DES` Section 7).
   - Speculatively executes candidate closers inside `withoutModifyingState`,
     measuring exact heartbeat consumption via `IO.getNumHeartbeats`, ranking
     succeeding closers by `computeCostX10`, and emitting clickable
     `TryThis.addSuggestion` code actions.
-/

open Lean Meta Elab Tactic
open scoped BigOperators

namespace AltProof.Tactics

export AltProof.Core (
  Route
  routeTable
  CostWeights
  computeCostX10
  TwoAxisScore
  routesToJson
  GoalFeatures
  exprContainsConst
  extractExprFeatures
  extractGoalFeatures
  filterRelevantRoutes
)

/-- `sum_congr_ring`: normalizes `Finset.sum` linear combinations (`sum_add_distrib`,
    `sum_sub_distrib`, `sum_neg_distrib`, `mul_sum`, `sum_mul`, and multi-sum linear
    combinations `a * ∑ f ± b * ∑ g ± c * ∑ h`) and discharges pointwise ring equalities
    under `Finset.sum` via `Finset.sum_congr rfl fun _ _ => by ring`. Always closes the
    goal or fails cleanly so `first` combinators can backtrack reliably. -/
syntax (name := sumCongrRingTactic) "sum_congr_ring" : tactic

macro_rules
  | `(tactic| sum_congr_ring) => `(tactic|
      first
      | (refine Finset.sum_congr rfl (fun _ _ => ?_); ring)
      | (rw [← Finset.sum_sub_distrib]; refine Finset.sum_congr rfl (fun _ _ => ?_); ring)
      | (rw [← Finset.sum_add_distrib]; refine Finset.sum_congr rfl (fun _ _ => ?_); ring)
      | (rw [Finset.mul_sum]; refine Finset.sum_congr rfl (fun _ _ => ?_); ring)
      | (rw [← Finset.mul_sum]; refine Finset.sum_congr rfl (fun _ _ => ?_); ring)
      | (rw [Finset.sum_mul]; refine Finset.sum_congr rfl (fun _ _ => ?_); ring)
      | (rw [← Finset.sum_mul]; refine Finset.sum_congr rfl (fun _ _ => ?_); ring)
      | (simp only [Finset.mul_sum, Finset.sum_mul, ← Finset.sum_add_distrib, ← Finset.sum_sub_distrib, ← Finset.sum_neg_distrib];
         first
         | done
         | (refine Finset.sum_congr rfl (fun _ _ => ?_); ring)
         | (rw [← Finset.mul_sum]; refine Finset.sum_congr rfl (fun _ _ => ?_); ring)
         | (rw [← Finset.sum_mul]; refine Finset.sum_congr rfl (fun _ _ => ?_); ring)))

/-- Instantiate universally quantified local hypotheses of the form `∀ x : α, ...`,
    `∀ x ∈ s, ...`, or `∀ x : α, ∀ j : κ, ...` at the freshly introduced index `iFVar`
    and membership `hiFVar` (and any secondary local context variables `j : κ`) so
    pointwise arithmetic/positivity closers and nested sum tactics can see them directly.
    Skips non-`Prop` function declarations (e.g., `f : ι → ℝ`) so local context is not
    polluted with value terms. -/
def specializePointwiseHyps (iFVar hiFVar : Expr) : TacticM Unit :=
  withMainContext do
    let iType ← inferType iFVar
    let hiType ← inferType hiFVar
    let lctx ← getLCtx
    let mut ctxFVars : Array (Expr × Expr) := #[]
    for decl in lctx do
      if !decl.isImplementationDetail && !decl.userName.hasMacroScopes then
        let dTy ← instantiateMVars decl.type
        if !(← isProp dTy) && !dTy.isForall then
          ctxFVars := ctxFVars.push (decl.toExpr, dTy)
    for decl in lctx do
      if !decl.isImplementationDetail && decl.fvarId != iFVar.fvarId! && decl.fvarId != hiFVar.fvarId! then
        let ty ← instantiateMVars decl.type
        if (← isProp ty) && ty.isForall then
          let dom := ty.bindingDomain!
          if ← withoutModifyingState (isDefEq dom iType) then
            try
              let app1 ← mkAppM' decl.toExpr #[iFVar]
              let app1Ty ← instantiateMVars (← inferType app1)
              let val ← if app1Ty.isForall then
                if ← withoutModifyingState (isDefEq app1Ty.bindingDomain! hiType) then
                  mkAppM' app1 #[hiFVar]
                else
                  pure app1
              else
                pure app1
              let valTy ← instantiateMVars (← inferType val)
              let goal ← getMainGoal
              let (_, goal') ← goal.note (decl.userName.appendAfter "_pt") val valTy
              replaceMainGoal [goal']
              if valTy.isForall then
                let dom2 := valTy.bindingDomain!
                if !(← isProp dom2) then
                  for (fvarExpr, fvarTy) in ctxFVars do
                    if fvarExpr.fvarId! != iFVar.fvarId! then
                      if ← withoutModifyingState (isDefEq dom2 fvarTy) then
                        let val2 ← mkAppM' val #[fvarExpr]
                        let val2Ty ← instantiateMVars (← inferType val2)
                        let g ← getMainGoal
                        let (_, g') ← g.note (decl.userName.appendAfter "_pt2") val2 val2Ty
                        replaceMainGoal [g']
            catch _ => pure ()

/-- `finset_nonneg`: discharges `0 ≤ ∑ i ∈ s, f i` (and nested double sums
    `0 ≤ ∑ i, ∑ j, f i j`) by applying `Finset.sum_nonneg`, instantiating any
    universally quantified local hypotheses `h : ∀ i, ...` or `h : ∀ i ∈ s, ...`
    at the introduced summation index, and closing the pointwise non-negativity
    obligation via `positivity`, `linarith`, `nlinarith`, `omega`, `solve_by_elim`,
    recursive `finset_nonneg`, or `aesop`. -/
syntax (name := finsetNonnegTactic) "finset_nonneg" : tactic

@[tactic finsetNonnegTactic]
def evalFinsetNonneg : Tactic := fun _ => do
  evalTactic (← `(tactic| apply Finset.sum_nonneg))
  let goal ← getMainGoal
  let (#[iFVar, hiFVar], goal') ← goal.introNP 2
    | throwError "finset_nonneg: expected 2 binders after Finset.sum_nonneg"
  replaceMainGoal [goal']
  specializePointwiseHyps (.fvar iFVar) (.fvar hiFVar)
  evalTactic (← `(tactic|
    first
    | (positivity; done)
    | linarith
    | nlinarith
    | omega
    | (solve_by_elim (maxDepth := 6) [mul_nonneg, add_nonneg, sq_nonneg, pow_nonneg, abs_nonneg, div_nonneg]; done)
    | (finset_nonneg; done)
    | (aesop; done)))

/-- `finset_mono`: discharges `∑ i ∈ s, f i ≤ ∑ i ∈ s, g i` (and nested double sums
    `∑ i, ∑ j, f i j ≤ ∑ i, ∑ j, g i j`) by applying `Finset.sum_le_sum`,
    instantiating any universally quantified local hypotheses `h : ∀ i, ...` or
    `h : ∀ i ∈ s, ...` at the introduced summation index, and closing the pointwise
    inequality obligation `f i ≤ g i` via `rfl`, `assumption`, `linarith`, `nlinarith`,
    `omega`, `positivity`, `gcongr`, `solve_by_elim` (with ordered-ring monotonicity
    lemmas `mul_le_mul_of_nonneg_left`, `mul_le_mul_of_nonneg_right`, `add_le_add`,
    `sub_le_sub_right`, `sub_le_sub_left`), recursive `finset_mono`, or `aesop`. -/
syntax (name := finsetMonoTactic) "finset_mono" : tactic

@[tactic finsetMonoTactic]
def evalFinsetMono : Tactic := fun _ => do
  evalTactic (← `(tactic| apply Finset.sum_le_sum))
  let goal ← getMainGoal
  let (#[iFVar, hiFVar], goal') ← goal.introNP 2
    | throwError "finset_mono: expected 2 binders after Finset.sum_le_sum"
  replaceMainGoal [goal']
  specializePointwiseHyps (.fvar iFVar) (.fvar hiFVar)
  evalTactic (← `(tactic|
    first
    | rfl
    | assumption
    | linarith
    | nlinarith
    | omega
    | (positivity; done)
    | (gcongr <;> (first | assumption | positivity | linarith | nlinarith | omega))
    | (solve_by_elim (maxDepth := 6) [mul_le_mul_of_nonneg_left, mul_le_mul_of_nonneg_right, add_le_add, sub_le_sub_right, sub_le_sub_left, sq_nonneg, abs_nonneg, le_refl]; done)
    | (finset_mono; done)
    | (aesop; done)))

/-- `alt_proof`: ordered automated reduction cascade that attempts fast kernel-friendly
    closers (`rfl`, `assumption`, `decide`, `omega`, `ring`, `sum_congr_ring`,
    `finset_nonneg`, `finset_mono`, `positivity`, `linarith`, `nlinarith`, `norm_num`, `aesop`). -/
syntax (name := altProofTactic) "alt_proof" : tactic

macro_rules
  | `(tactic| alt_proof) => `(tactic|
      first
      | rfl
      | assumption
      | bv_decide
      | decide
      | omega
      | (ring; done)
      | (sum_congr_ring; done)
      | (finset_nonneg; done)
      | (finset_mono; done)
      | (positivity; done)
      | linarith
      | nlinarith
      | (norm_num; done)
      | (aesop; done))

/-- Result of speculatively probing a candidate tactic in `withoutModifyingState`. -/
structure CandidateResult where
  tacticSyntax : String
  heartbeats : Nat
  costX10 : Int
deriving Inhabited, Repr

/-- Speculatively run `tacStx` without modifying proof state; return `some CandidateResult`
    if the tactic closes all goals. Measures exact kernel/elaborator heartbeats via `IO.getNumHeartbeats`.
    `steps` records the tactic sequence depth (1 for single-step, 2..3 for bounded BFS sequences). -/
def tryCandidateCloser (tacName : String) (tacStx : Syntax) (steps : Nat := 1) : TacticM (Option CandidateResult) := do
  withoutModifyingState do
    try
      let hbStart ← IO.getNumHeartbeats
      evalTactic tacStx
      let rem ← getUnsolvedGoals
      if rem.isEmpty then
        let hbEnd ← IO.getNumHeartbeats
        let hbDelta := hbEnd - hbStart
        let kUnits := hbDelta / 1000
        let cost := computeCostX10 steps 0 false kUnits
        return some { tacticSyntax := tacName, heartbeats := hbDelta, costX10 := cost }
      else
        return none
    catch _ =>
      return none

/-- Bounded depth-$D$ ($D \le 3$) in-kernel `withoutModifyingState` Best-First Search
    (`Proposal 9C` / `nanoproof` / `MiniF2F` in-kernel search).
    Explores depth-2 and depth-3 structural decomposition prefixes (`intros`, `constructor`,
    `push_neg`, `ring_nf`) combined with `alt_proof` and specialized closers, scored by
    `GoalFeatures` and `computeCostX10`. -/
def tryBfsCandidateClosers (feats : GoalFeatures) : TacticM (Array (CandidateResult × TSyntax `tactic)) := do
  let mut bfsCandidates : List (Nat × String × TacticM (TSyntax `tactic)) := [
    (2, "intros; alt_proof", `(tactic| (intros; alt_proof))),
    (2, "constructor <;> alt_proof", `(tactic| (constructor <;> alt_proof)))
  ]
  if feats.hasNegOrContra then
    bfsCandidates := bfsCandidates ++ [
      (2, "push_neg; alt_proof", `(tactic| (push_neg; alt_proof))),
      (3, "intros; push_neg; alt_proof", `(tactic| (intros; push_neg; alt_proof)))
    ]
  if feats.hasFinsetSum then
    bfsCandidates := bfsCandidates ++ [
      (2, "intros; sum_congr_ring", `(tactic| (intros; sum_congr_ring))),
      (2, "intros; finset_mono", `(tactic| (intros; finset_mono))),
      (2, "intros; finset_nonneg", `(tactic| (intros; finset_nonneg)))
    ]
  bfsCandidates := bfsCandidates ++ [
    (3, "intros; constructor <;> alt_proof", `(tactic| (intros; constructor <;> alt_proof)))
  ]
  let mut successes : Array (CandidateResult × TSyntax `tactic) := #[]
  for (depth, name, mkStx) in bfsCandidates do
    let tacStx ← mkStx
    if let some res ← tryCandidateCloser name tacStx (steps := depth) then
      successes := successes.push (res, tacStx)
  return successes.qsort (fun (a, _) (b, _) =>
    if a.costX10 != b.costX10 then a.costX10 < b.costX10 else a.heartbeats < b.heartbeats)

/-- `bfs_elegance?`: Bounded depth-$D$ ($D \le 3$) in-kernel `withoutModifyingState` Best-First
    Search explorer (`Proposal 9C`). Probes both depth-1 closers and depth-2..3 decomposition
    sequences (`intros; alt_proof`, `constructor <;> alt_proof`, `push_neg; alt_proof`,
    `intros; constructor <;> alt_proof`) without mutating proof state, ranking all closing
    paths by `computeCostX10` and emitting a `TryThis.addSuggestion` code action. -/
syntax (name := bfsEleganceTactic) "bfs_elegance?" : tactic

/-- `elegance?`: AST-aware speculative route & tactic explorer (`SPEC-ALT-PROOF-DES`).
    1. Extracts `GoalFeatures` from the current main goal and local context.
    2. Filters `routeTable` to the relevant transformation routes.
    3. Speculatively probes candidate closers (`rfl`, `assumption`, `decide`, `omega`,
       `ring`, `sum_congr_ring`, `finset_nonneg`, `finset_mono`, `positivity`, `linarith`,
       `nlinarith`, `norm_num`, `aesop`) in `withoutModifyingState`, recording exact heartbeat
       deltas (`IO.getNumHeartbeats`) and ranking winning closers by `computeCostX10`.
    4. If no single-step closer succeeds, falls back to bounded depth-$D$ ($D \le 3$) in-kernel
       Best-First Search (`tryBfsCandidateClosers`).
    5. Emits a `TryThis.addSuggestion` code action for the lowest-cost closer if found. -/
syntax (name := eleganceTactic) "elegance?" : tactic

@[tactic eleganceTactic, tactic bfsEleganceTactic]
def evalElegance : Tactic := fun stx => do
  let goal ← getMainGoal
  let target ← instantiateMVars (← goal.getType)
  let targetStr := toString (← ppExpr target)
  let feats ← extractGoalFeatures goal
  let relRoutes := filterRelevantRoutes feats
  logInfo m!"[AltProof.elegance?] Active Goal: {targetStr}"
  logInfo m!"[AltProof.elegance?] AST Features: finsetSum={feats.hasFinsetSum}, abs={feats.hasAbs}, iteDecide={feats.hasIteOrDecide}, natInt={feats.hasNatArith}, bitVec={feats.hasBitVec}, neg={feats.hasNegOrContra}"
  logInfo m!"[AltProof.elegance?] Relevant Routes ({relRoutes.length}/{routeTable.length}):"
  for r in relRoutes do
    logInfo m!"  * [{r.family}] {r.id}: {r.rewriteHint} ({r.costHint})"

  -- Speculative candidate closer sweep in saved state
  let bitVecCandidates : List (String × TacticM (TSyntax `tactic)) :=
    if feats.hasBitVec then [("bv_decide", `(tactic| bv_decide))] else []
  let candidates : List (String × TacticM (TSyntax `tactic)) := bitVecCandidates ++ [
    ("rfl", `(tactic| rfl)),
    ("assumption", `(tactic| assumption)),
    ("decide", `(tactic| decide)),
    ("omega", `(tactic| omega)),
    ("ring", `(tactic| ring)),
    ("sum_congr_ring", `(tactic| sum_congr_ring)),
    ("finset_nonneg", `(tactic| finset_nonneg)),
    ("finset_mono", `(tactic| finset_mono)),
    ("positivity", `(tactic| positivity)),
    ("linarith", `(tactic| linarith)),
    ("nlinarith", `(tactic| nlinarith)),
    ("norm_num", `(tactic| norm_num)),
    ("aesop", `(tactic| aesop))
  ]
  let mut successes : Array (CandidateResult × TSyntax `tactic) := #[]
  for (name, mkStx) in candidates do
    let tacStx ← mkStx
    if let some res ← tryCandidateCloser name tacStx (steps := 1) then
      successes := successes.push (res, tacStx)

  let sorted := successes.qsort (fun (a, _) (b, _) =>
    if a.costX10 != b.costX10 then a.costX10 < b.costX10 else a.heartbeats < b.heartbeats)

  if h : 0 < sorted.size then
    let (best, bestStx) := sorted[0]
    logInfo m!"[AltProof.elegance?] Speculative Closers ({sorted.size} succeeded): best = `{best.tacticSyntax}` (costX10={best.costX10}, heartbeats={best.heartbeats})"
    for (c, _) in sorted do
      logInfo m!"  + `{c.tacticSyntax}`: heartbeats={c.heartbeats}, costX10={c.costX10}"
    Tactic.TryThis.addSuggestion stx bestStx (origSpan? := some stx)
  else
    let bfsSorted ← tryBfsCandidateClosers feats
    if hBfs : 0 < bfsSorted.size then
      let (bestBfs, bestBfsStx) := bfsSorted[0]
      logInfo m!"[AltProof.elegance?] Depth<=3 In-Kernel BFS Closers ({bfsSorted.size} succeeded): best = `{bestBfs.tacticSyntax}` (costX10={bestBfs.costX10}, heartbeats={bestBfs.heartbeats})"
      for (c, _) in bfsSorted do
        logInfo m!"  + [BFS] `{c.tacticSyntax}`: heartbeats={c.heartbeats}, costX10={c.costX10}"
      Tactic.TryThis.addSuggestion stx bestBfsStx (origSpan? := some stx)
    else
      logInfo m!"[AltProof.elegance?] Goal requires multi-step decomposition (0 single-step or depth<=3 BFS closers succeeded)."

end AltProof.Tactics

namespace AltProof

export AltProof.Tactics (
  Route
  routeTable
  CostWeights
  computeCostX10
  TwoAxisScore
  routesToJson
  GoalFeatures
  exprContainsConst
  extractExprFeatures
  extractGoalFeatures
  filterRelevantRoutes
  specializePointwiseHyps
  evalFinsetNonneg
  evalFinsetMono
  CandidateResult
  tryCandidateCloser
  tryBfsCandidateClosers
  evalElegance
)

end AltProof
