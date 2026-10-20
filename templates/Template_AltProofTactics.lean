/-
Copyright (c) 2026 <Project>. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: <Project> Contributors
SPDX-License-Identifier: Apache-2.0
-/

import Mathlib.Tactic
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Algebra.BigOperators.Ring.Finset

set_option autoImplicit false

/-!
# <Project>.Tactics.AltProof -- Speculative Alternative-Proof & Elegance Meta-Tactics

Production Layer-0 implementation of the AltProof tactic suite
(`SPEC-ALT-PROOF-DES`, `ALT_PROOF_SAIR_BRIDGE`):

1. **Goal AST & Local Context Feature Detector (`GoalFeatures`)**:
   Inspects the active `MVarId` target `Expr` and local context to detect:
   - `hasFinsetSum`: `Finset.sum` linear / congruence structures
   - `hasAbs`: norm or absolute-value subgoals (`abs`)
   - `hasIteOrDecide`: branched `ite` / `dite` / `decide` boolean-reflection shapes
   - `hasNegOrContra`: negation / contradiction hypotheses
   - `hasNatArith`: discrete `Nat` / `Int` Presburger arithmetic
   - `hasWellFounded`: `WellFounded.fix` unfolding traps

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
   Ordered automated reduction cascade (`rfl`, `assumption`, `decide`, `omega`,
   `ring`, `sum_congr_ring`, `finset_nonneg`, `finset_mono`, `positivity`,
   `linarith`, `nlinarith`, `norm_num`, `aesop`)
   that discharges standard algebraic, arithmetic, and finite-sum goals.

5. **Speculative `elegance?` Tactic**:
   - Filters `routeTable` by relevance against `GoalFeatures` (Method 2: relevance
     filter + Method 1: capped enumeration per `SPEC-ALT-PROOF-DES` Section 7).
   - Speculatively executes candidate closers inside `withoutModifyingState`,
     measuring exact heartbeat consumption via `IO.getNumHeartbeats`, ranking
     succeeding closers by `computeCostX10`, and emitting clickable
     `TryThis.addSuggestion` code actions.
-/

open Lean Meta Elab Tactic
open scoped BigOperators

namespace <Project>.Tactics.AltProof

/-- An alternative proof route definition from the route table (`SPEC-ALT-PROOF-DES` Section 5b). -/
structure Route where
  id : String
  family : String
  matchShape : String
  rewriteHint : String
  costHint : String
  provenance : String
deriving Inhabited, Repr, DecidableEq

/-- The canonical 8-route table corresponding to `SPEC-ALT-PROOF-DES` Section 5b / `route-table.json`. -/
def routeTable : List Route := [
  { id := "extract-shared-block",
    family := "extraction",
    matchShape := "a >=3-line proof block reused verbatim or modulo renaming",
    rewriteHint := "name the block as a lemma; call it at each site",
    costHint := "high-yield: counts once, serves N sites",
    provenance := "long-proof campaign fixtures 1-15, 17 (36 shared lemmas)" },
  { id := "extract-mathlib-absent",
    family := "extraction",
    matchShape := "a generic block with no Mathlib equivalent (verified absent before naming)",
    rewriteHint := "name it in the owning module; flag as an upstreaming candidate",
    costHint := "highest yield: reusable beyond the corpus",
    provenance := "fixtures 10-11 (cesaro_tendsto_of_geometric_bound -> PR #44591; sum_mul_le_sum_mul_sum)" },
  { id := "extract-horizon-package",
    family := "extraction",
    matchShape := "three or more inline steps serving one standing theorem family",
    rewriteHint := "package the steps as a named lemma trio in the theorem's module",
    costHint := "high-yield: the Doeblin package pattern",
    provenance := "fixture 12 (doeblin_card_mul_le_one, realStep_iterate_mul, stationary_ge_of_doeblin)" },
  { id := "extract-cauchy-toolkit",
    family := "extraction",
    matchShape := "a Cauchy/convergence argument assembled from pointwise and sum-level lemmas",
    rewriteHint := "extract the four standard sub-steps as reusable convergence lemmas",
    costHint := "high-yield: the GAP-7 pattern (154 -> ~40)",
    provenance := "fixture 17 (iterate_sum_cauchy, pointwise_cauchy_of_sum_cauchy, sum_dist_tendsto_of_pointwise, step_fixedpoint_of_sum_dist_tendsto)" },
  { id := "uniform-simp-collapse",
    family := "reflection",
    matchShape := "branched case analysis where one uniform simp set closes every branch",
    rewriteHint := "replace the branches with one uniform simp call (the boolean-reflection pattern)",
    costHint := "high-yield: 76 lines/6 branches -> cleared (fixture 16)",
    provenance := "fixture 16 (gate_row_diff_bound)" },
  { id := "redirect-by-contradiction",
    family := "redirect",
    matchShape := "by_contra-heavy proofs with a constructible direct witness",
    rewriteHint := "restate as a direct construction (the JAR 2016 redirect class)",
    costHint := "reserved: no corpus fixture yet - the tool's first hit becomes it",
    provenance := "JAR16 redirect procedure; ballot B3" },
  { id := "algorithm-class-substitution",
    family := "algorithm-class-substitution",
    matchShape := "exponential or unhoisted recursion with an equivalent closed-form or DP reduction",
    rewriteHint := "substitute algorithm class (e.g. in-place DP or structural sieve) and prove equivalence to spec",
    costHint := "highest kernel yield: 20-30x reduction in kernel steps / rfl time",
    provenance := "SAIR Lean Kernel Challenge lanes (partition in-place DP S1/S1b, primecount sieve S6)" },
  { id := "kernel-friendly-term-design",
    family := "kernel-friendly-term-design",
    matchShape := "structural recursion or helper calls with heavy defeq unfolding overhead",
    rewriteHint := "refactor to kernel-friendly primitives (structural Nat.rec, unrolled trial division, import-minimal path)",
    costHint := "high kernel yield: reduces defeq heartbeats and avoids WellFounded.fix traps",
    provenance := "SAIR Lean Kernel Challenge lanes (primecount L1 structural trial division S5)" }
]

/-- Cost ranker weights per B1 `extraction-outranks` heuristic (scaled integers x10)
    extended with the SAIR kernel-cost axis (`ALT_PROOF_SAIR_BRIDGE` A1). -/
structure CostWeights where
  perLineX10 : Int := 1         -- 0.1 per line
  perSharedLemmaX10 : Int := 50  -- 5.0 bonus per shared lemma
  upstreamBonusX10 : Int := 200  -- 20.0 bonus for upstreamable lemma
  kernelCostWeightX10 : Int := 10 -- 1.0 weight per 1,000 heartbeats
deriving Inhabited, Repr, DecidableEq

/-- Compute proof cost score (lower is more elegant). -/
def computeCostX10 (lines : Nat) (sharedLemmas : Nat) (upstream : Bool)
    (kernelCost : Nat := 0) (w : CostWeights := {}) : Int :=
  let base := (lines : Int) * w.perLineX10
  let bonus := (sharedLemmas : Int) * w.perSharedLemmaX10
  let up := if upstream then w.upstreamBonusX10 else 0
  let kCost := (kernelCost : Int) * w.kernelCostWeightX10
  base - bonus - up + kCost

/-- Two-axis evaluation node per `ALT_PROOF_SAIR_BRIDGE` A1/A4: reader elegance vs machine kernel cost. -/
structure TwoAxisScore where
  eleganceCostX10 : Int
  kernelHeartbeats : Nat
  legibility : String
deriving Inhabited, Repr, DecidableEq

/-- Format route table as JSON string for export. -/
def routesToJson : String :=
  let entries := routeTable.map fun r =>
    "    {\"id\": \"" ++ r.id ++ "\", \"family\": \"" ++ r.family ++ "\", \"cost_hint\": \"" ++ r.costHint ++ "\", \"provenance\": \"" ++ r.provenance ++ "\"}"
  "{\n  \"version\": 1,\n  \"routes\": [\n" ++ String.intercalate ",\n" entries ++ "\n  ]\n}\n"

/-- Structural AST features extracted from the active goal `Expr` and local context. -/
structure GoalFeatures where
  hasFinsetSum : Bool := false
  hasAbs : Bool := false
  hasIteOrDecide : Bool := false
  hasNegOrContra : Bool := false
  hasNatArith : Bool := false
  hasWellFounded : Bool := false
deriving Inhabited, Repr, DecidableEq

/-- Check if an `Expr` mentions any constant name satisfying `pred`. -/
def exprContainsConst (e : Expr) (pred : Name → Bool) : Bool :=
  Option.isSome <| e.find? fun sub =>
    match sub with
    | .const n _ => pred n
    | _ => false

/-- Extract `GoalFeatures` from a target `Expr` and optional local context expressions. -/
def extractExprFeatures (target : Expr) : GoalFeatures :=
  { hasFinsetSum := exprContainsConst target fun n => n == ``Finset.sum
    hasAbs := exprContainsConst target fun n => n == ``abs || n == ``Norm.norm || n == ``Dist.dist
    hasIteOrDecide := exprContainsConst target fun n =>
      n == ``ite || n == ``dite || n == ``Decidable.decide
    hasNegOrContra := exprContainsConst target fun n => n == ``Not || n == ``False
    hasNatArith := exprContainsConst target fun n => n == ``Nat || n == ``Int
    hasWellFounded := exprContainsConst target fun n => n == ``WellFounded.fix }

/-- Combine two `GoalFeatures` records by logical OR. -/
def GoalFeatures.merge (a b : GoalFeatures) : GoalFeatures :=
  { hasFinsetSum := a.hasFinsetSum || b.hasFinsetSum
    hasAbs := a.hasAbs || b.hasAbs
    hasIteOrDecide := a.hasIteOrDecide || b.hasIteOrDecide
    hasNegOrContra := a.hasNegOrContra || b.hasNegOrContra
    hasNatArith := a.hasNatArith || b.hasNatArith
    hasWellFounded := a.hasWellFounded || b.hasWellFounded }

/-- Extract `GoalFeatures` from both the active goal target and all non-implementation
    local declarations in the current `MVarId`'s `LocalContext`. -/
def extractGoalFeatures (goal : MVarId) : MetaM GoalFeatures :=
  goal.withContext do
    let target ← instantiateMVars (← goal.getType)
    let mut feats := extractExprFeatures target
    let lctx ← getLCtx
    for decl in lctx do
      if !decl.isImplementationDetail then
        let ty ← instantiateMVars decl.type
        feats := feats.merge (extractExprFeatures ty)
    return feats

/-- Relevance filter (`SPEC-ALT-PROOF-DES` Section 7, Method 2): select routes matching `GoalFeatures`. -/
def filterRelevantRoutes (f : GoalFeatures) : List Route :=
  let picked := routeTable.filter fun r =>
    match r.id with
    | "extract-shared-block" => f.hasFinsetSum || f.hasAbs
    | "extract-mathlib-absent" => f.hasFinsetSum || f.hasAbs
    | "extract-horizon-package" => f.hasFinsetSum && f.hasAbs
    | "extract-cauchy-toolkit" => f.hasAbs
    | "uniform-simp-collapse" => f.hasIteOrDecide || f.hasNatArith
    | "redirect-by-contradiction" => f.hasNegOrContra
    | "algorithm-class-substitution" => f.hasFinsetSum || f.hasWellFounded
    | "kernel-friendly-term-design" => f.hasWellFounded || f.hasNatArith
    | _ => false
  if picked.isEmpty then routeTable.take 3 else picked

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
    if the tactic closes all goals. Measures exact kernel/elaborator heartbeats via `IO.getNumHeartbeats`. -/
def tryCandidateCloser (tacName : String) (tacStx : Syntax) : TacticM (Option CandidateResult) := do
  withoutModifyingState do
    try
      let hbStart ← IO.getNumHeartbeats
      evalTactic tacStx
      let rem ← getUnsolvedGoals
      if rem.isEmpty then
        let hbEnd ← IO.getNumHeartbeats
        let hbDelta := hbEnd - hbStart
        let kUnits := hbDelta / 1000
        let cost := computeCostX10 1 0 false kUnits
        return some { tacticSyntax := tacName, heartbeats := hbDelta, costX10 := cost }
      else
        return none
    catch _ =>
      return none

/-- `elegance?`: AST-aware speculative route & tactic explorer (`SPEC-ALT-PROOF-DES`).
    1. Extracts `GoalFeatures` from the current main goal and local context.
    2. Filters `routeTable` to the relevant transformation routes.
    3. Speculatively probes candidate closers (`rfl`, `assumption`, `decide`, `omega`,
       `ring`, `sum_congr_ring`, `finset_nonneg`, `finset_mono`, `positivity`, `linarith`,
       `nlinarith`, `norm_num`, `aesop`) in `withoutModifyingState`, recording exact heartbeat
       deltas (`IO.getNumHeartbeats`) and ranking winning closers by `computeCostX10`.
    4. Emits a `TryThis.addSuggestion` code action for the lowest-cost closer if found. -/
syntax (name := eleganceTactic) "elegance?" : tactic

@[tactic eleganceTactic]
def evalElegance : Tactic := fun stx => do
  let goal ← getMainGoal
  let target ← instantiateMVars (← goal.getType)
  let targetStr := toString (← ppExpr target)
  let feats ← extractGoalFeatures goal
  let relRoutes := filterRelevantRoutes feats
  logInfo m!"[AltProof.elegance?] Active Goal: {targetStr}"
  logInfo m!"[AltProof.elegance?] AST Features: finsetSum={feats.hasFinsetSum}, abs={feats.hasAbs}, iteDecide={feats.hasIteOrDecide}, natInt={feats.hasNatArith}, neg={feats.hasNegOrContra}"
  logInfo m!"[AltProof.elegance?] Relevant Routes ({relRoutes.length}/{routeTable.length}):"
  for r in relRoutes do
    logInfo m!"  * [{r.family}] {r.id}: {r.rewriteHint} ({r.costHint})"

  -- Speculative candidate closer sweep in saved state
  let candidates : List (String × TacticM (TSyntax `tactic)) := [
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
    if let some res ← tryCandidateCloser name tacStx then
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
    logInfo m!"[AltProof.elegance?] Goal requires multi-step decomposition (0 single-step closers succeeded)."

end <Project>.Tactics.AltProof
