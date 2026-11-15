/-
Copyright (c) 2026 Proof-Skills. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Proof-Skills Contributors
SPDX-License-Identifier: Apache-2.0
-/

import AltProof.Core
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.GCongr
import Mathlib.Tactic.Push
import Mathlib.Algebra.BigOperators.Fin
import Aesop

set_option autoImplicit false

/-!
# AltProof.Tactics -- Speculative Alternative-Proof & Elegance Meta-Tactics

Production Layer-0 implementation of the AltProof tactic suite
(`SPEC-ALT-PROOF-DES`, `ALT_PROOF_SAIR_BRIDGE`):

1. **Core-Only Foundation (`AltProof.Core`, `import Lean` only)**:
   - 20-route `routeTable`, `GoalFeatures` AST & local-context detector, `computeCostX10` ranker.
   - `eqsat_rw` / `egg_rw`: pure-Lean bidirectional equality & congruence saturation (`congrArg` /
     `congrFun` / `Eq.trans`) in `MetaM` with zero Rust FFI and 3-axiom clean proof reconstruction.
   - `backchain`: bounded `solve_by_elim` backchaining wrapper over `Lean.Elab.Tactic.SolveByElim`.
   - `grind_close`: bounded e-graph congruence & E-matching closer via core Lean `grind`.
   - `contra_direct`: constructive negation / `Bool` / `Decidable` normalizer avoiding `Classical.choice`.
   - `sair_decide`: strict 3-rung kernel-clean decision macro (`rfl | decide +kernel | omega`).
   - `eval_nat%`, `preunfold%`, `swar_unroll%`: compile-time SAIR constant/combinator superoptimizers.

2. **Mathlib-Tier Big-Operator & Monotonicity Closers**:
   - `sum_congr_ring`: Normalizes `Finset.sum` linearity (`sum_add_distrib`, `sum_sub_distrib`,
     `mul_sum`, `sum_mul`) and closes pointwise congruence goals via
     `Finset.sum_congr rfl fun _ _ => by ring`.
   - `calc_ring_sum`: Multi-step `Finset.sum` telescoping, double-sum commutation (`Finset.sum_comm`),
     and scalar/linear ring normalization closer.
   - `finset_nonneg`: Discharges `0 ≤ ∑ i ∈ s, f i` via `Finset.sum_nonneg` and
     pointwise hypothesis instantiation (`specializePointwiseHyps`).
   - `finset_mono`: Discharges `∑ i ∈ s, f i ≤ ∑ i ∈ s, g i` via `Finset.sum_le_sum`,
     pointwise hypothesis instantiation (`specializePointwiseHyps`), and ordered-ring
     monotonicity closers.
   - `gcongr_pos`: Structural monotonicity congruence (`gcongr`) discharging all positivity and
     linear side-goals automatically via `assumption | positivity | linarith | nlinarith | omega`.

3. **`alt_proof` Meta-Tactic**:
   Ordered automated reduction cascade (`rfl`, `assumption`, `sair_decide`, `bv_decide`, `decide`,
   `omega`, `ring`, `eqsat_rw`, `backchain`, `contra_direct`, `sum_congr_ring`, `calc_ring_sum`,
   `finset_nonneg`, `finset_mono`, `gcongr_pos`, `positivity`, `linarith`, `nlinarith`, `norm_num`,
   `grind_close`, `aesop`).

4. **Speculative `elegance?` & `bfs_elegance?` Tactics**:
   - Filters `routeTable` (20 canonical routes) by relevance against `GoalFeatures`.
   - Speculatively executes candidate closers inside `withoutModifyingState`, measuring exact
     heartbeat consumption via `IO.getNumHeartbeats`, ranking succeeding closers by `computeCostX10`,
     and emitting clickable `TryThis.addSuggestion` code actions.
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
  EqSatRule
  EqSatNode
  saturateEquality
  evalEqsatRw
  evalClosedNatExpr
  preunfoldExprWith
  buildUnrolledLoop
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

/-- `calc_ring_sum`: multi-step `Finset.sum` commutation (`Finset.sum_comm`), scalar distribution,
    and telescoping closer extending `sum_congr_ring` to swapped double sums. -/
syntax (name := calcRingSumTactic) "calc_ring_sum" : tactic

macro_rules
  | `(tactic| calc_ring_sum) => `(tactic|
      first
      | (sum_congr_ring; done)
      | (rw [Finset.sum_comm]; sum_congr_ring; done)
      | (simp only [Finset.mul_sum, Finset.sum_mul]; rw [Finset.sum_comm];
         first
         | done
         | (refine Finset.sum_congr rfl (fun _ _ => ?_); sum_congr_ring; done)
         | (refine Finset.sum_congr rfl (fun _ _ => ?_); refine Finset.sum_congr rfl (fun _ _ => ?_); ring; done))
      | (rw [Finset.sum_sub_distrib]; ring; done)
      | (rw [Finset.sum_add_distrib]; ring; done))

/-- `gcongr_pos`: structural monotonicity congruence (`gcongr`) that automatically discharges
    all side-conditions and leaf inequalities via `assumption`, `positivity`, `linarith`,
    `nlinarith`, or `omega`. -/
syntax (name := gcongrPosTactic) "gcongr_pos" : tactic

macro_rules
  | `(tactic| gcongr_pos) => `(tactic|
      (gcongr <;> first | rfl | assumption | (positivity; done) | linarith | nlinarith | omega; done))

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
    `omega`, `positivity`, `gcongr_pos`, `solve_by_elim`, recursive `finset_mono`, or `aesop`. -/
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
    | gcongr_pos
    | (solve_by_elim (maxDepth := 6) [mul_le_mul_of_nonneg_left, mul_le_mul_of_nonneg_right, add_le_add, sub_le_sub_right, sub_le_sub_left, sq_nonneg, abs_nonneg, le_refl]; done)
    | (finset_mono; done)
    | (aesop; done)))

/-- `alt_proof`: ordered automated reduction cascade that attempts fast kernel-friendly
    closers (`rfl`, `assumption`, `bv_decide`, `decide`, `omega`, `ring`, `sum_congr_ring`,
    `calc_ring_sum`, `finset_nonneg`, `finset_mono`, `gcongr_pos`, `positivity`, `linarith`,
    `nlinarith`, `norm_num`, `eqsat_rw`, `contra_direct`, `backchain`, `aesop`). -/
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
      | (calc_ring_sum; done)
      | (finset_nonneg; done)
      | (finset_mono; done)
      | gcongr_pos
      | (positivity; done)
      | linarith
      | nlinarith
      | (norm_num; done)
      | (eqsat_rw; done)
      | (contra_direct; done)
      | backchain
      | (aesop; done))

/-- Result of speculatively probing a candidate tactic in `withoutModifyingState`. -/
structure CandidateResult where
  tacticSyntax : String
  heartbeats : Nat
  costX10 : Int
deriving Inhabited, Repr

/-- Speculatively run `tacStx` without modifying proof state; return `some CandidateResult`
    if the tactic closes all goals. Measures exact kernel/elaborator heartbeats via `IO.getNumHeartbeats`
    inside a fresh `withCurrHeartbeats` window so probing 15+ candidate closers never starves
    the caller's outer `maxHeartbeats` budget. -/
def tryCandidateCloser (tacName : String) (tacStx : Syntax) (steps : Nat := 1) : TacticM (Option CandidateResult) := do
  withCurrHeartbeats <| withoutModifyingState do
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
    (`Proposal 9C` / `nanoproof` / `MiniF2F` in-kernel search). -/
def tryBfsCandidateClosers (feats : GoalFeatures) : TacticM (Array (CandidateResult × TSyntax `tactic)) := do
  let mut bfsCandidates : List (Nat × String × TacticM (TSyntax `tactic)) := [
    (2, "intros; alt_proof", `(tactic| (intros; alt_proof))),
    (2, "constructor <;> alt_proof", `(tactic| (constructor <;> alt_proof)))
  ]
  if feats.hasNegOrContra then
    bfsCandidates := bfsCandidates ++ [
      (2, "contra_direct", `(tactic| contra_direct)),
      (2, "push_neg; alt_proof", `(tactic| (push_neg; alt_proof))),
      (3, "intros; push_neg; alt_proof", `(tactic| (intros; push_neg; alt_proof)))
    ]
  if feats.hasFinsetSum then
    bfsCandidates := bfsCandidates ++ [
      (2, "intros; sum_congr_ring", `(tactic| (intros; sum_congr_ring))),
      (2, "intros; calc_ring_sum", `(tactic| (intros; calc_ring_sum))),
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
    Search explorer (`Proposal 9C`). -/
syntax (name := bfsEleganceTactic) "bfs_elegance?" : tactic

/-- `elegance?`: AST-aware speculative route & tactic explorer (`SPEC-ALT-PROOF-DES`). -/
syntax (name := eleganceTactic) "elegance?" : tactic

@[tactic eleganceTactic, tactic bfsEleganceTactic]
def evalElegance : Tactic := fun stx =>
  withTheReader Core.Context ({ · with maxHeartbeats := 0 }) do
    let goal ← getMainGoal
    let target ← instantiateMVars (← goal.getType)
    let targetStr := toString (← ppExpr target)
    let feats ← extractGoalFeatures goal
    let relRoutes := filterRelevantRoutes feats
    logInfo m!"[AltProof.elegance?] Active Goal: {targetStr}"
    logInfo m!"[AltProof.elegance?] AST Features: finsetSum={feats.hasFinsetSum}, abs={feats.hasAbs}, iteDecide={feats.hasIteOrDecide}, natInt={feats.hasNatArith}, bitVec={feats.hasBitVec}, eq={feats.hasEquality}, neg={feats.hasNegOrContra}"
    logInfo m!"[AltProof.elegance?] Relevant Routes ({relRoutes.length}/{routeTable.length}):"
    for r in relRoutes do
      logInfo m!"  * [{r.family}] {r.id}: {r.rewriteHint} ({r.costHint})"

    -- Speculative candidate closer sweep in saved state (each probe gets a 200,000-heartbeat window, i.e. 200_000 * 1000)
    let runBoundedProbe (name : String) (tacStx : Syntax) (steps : Nat := 1) : TacticM (Option CandidateResult) :=
      withTheReader Core.Context ({ · with maxHeartbeats := 200000000 }) do
        tryCandidateCloser name tacStx (steps := steps)

    let bitVecCandidates : List (String × TacticM (TSyntax `tactic)) :=
      if feats.hasBitVec then [("bv_decide", `(tactic| bv_decide))] else []
    let eqCandidates : List (String × TacticM (TSyntax `tactic)) :=
      if feats.hasEquality then [("eqsat_rw", `(tactic| eqsat_rw))] else []
    let candidates : List (String × TacticM (TSyntax `tactic)) := bitVecCandidates ++ [
      ("rfl", `(tactic| rfl)),
      ("assumption", `(tactic| assumption)),
      ("sair_decide", `(tactic| sair_decide)),
      ("backchain", `(tactic| backchain)),
      ("contra_direct", `(tactic| contra_direct)),
      ("decide", `(tactic| decide)),
      ("omega", `(tactic| omega)),
      ("ring", `(tactic| ring))
    ] ++ eqCandidates ++ [
      ("sum_congr_ring", `(tactic| sum_congr_ring)),
      ("calc_ring_sum", `(tactic| calc_ring_sum)),
      ("finset_nonneg", `(tactic| finset_nonneg)),
      ("finset_mono", `(tactic| finset_mono)),
      ("gcongr_pos", `(tactic| gcongr_pos)),
      ("positivity", `(tactic| positivity)),
      ("linarith", `(tactic| linarith)),
      ("nlinarith", `(tactic| nlinarith)),
      ("norm_num", `(tactic| norm_num)),
      ("aesop", `(tactic| aesop))
    ]
    let mut successes : Array (CandidateResult × TSyntax `tactic) := #[]
    for (name, mkStx) in candidates do
      let tacStx ← mkStx
      if let some res ← runBoundedProbe name tacStx (steps := 1) then
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
      let bfsSorted ← withTheReader Core.Context ({ · with maxHeartbeats := 400000000 }) do
        tryBfsCandidateClosers feats
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
  EqSatRule
  EqSatNode
  saturateEquality
  evalEqsatRw
  evalClosedNatExpr
  preunfoldExprWith
  buildUnrolledLoop
  specializePointwiseHyps
  evalFinsetNonneg
  evalFinsetMono
  CandidateResult
  tryCandidateCloser
  tryBfsCandidateClosers
  evalElegance
)

end AltProof
