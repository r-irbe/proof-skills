/-
Copyright (c) 2026 Proof-Skills. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Proof-Skills Contributors
SPDX-License-Identifier: Apache-2.0
-/

import Lean

set_option autoImplicit false

/-!
# AltProof.Core -- Core-Only Route Table, Cost Ranker, and Goal Feature Detector

Core-only (`import Lean`) definitions for the AltProof 16-route advisor,
two-axis cost ranker (`computeCostX10`, `TwoAxisScore`), and `Expr`/`LocalContext`
AST feature detector (`GoalFeatures`, `extractGoalFeatures`, `filterRelevantRoutes`).
Usable in zero-Mathlib projects without requiring Mathlib in `lakefile.lean`.
-/

open Lean Meta

namespace AltProof.Core

/-- An alternative proof route definition from the route table (`SPEC-ALT-PROOF-DES` Section 5b). -/
structure Route where
  id : String
  family : String
  matchShape : String
  rewriteHint : String
  costHint : String
  provenance : String
deriving Inhabited, Repr, DecidableEq

/-- The canonical 16-route table corresponding to `SPEC-ALT-PROOF-DES` Section 5b / `route-table.json`. -/
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
    provenance := "SAIR Lean Kernel Challenge lanes (primecount L1 structural trial division S5)" },
  { id := "constructive-decidable-reduction",
    family := "kernel-friendly-term-design",
    matchShape := "Classical.choice leakage in first-order Nat/Int/Bool/BitVec theorems caused by split on &&/And or classical by_cases",
    rewriteHint := "replace split/by_cases with Bool.and_eq_true, decide_eq_true_eq, omega, or bv_decide to keep axiom closure Classical.choice-free",
    costHint := "high kernel & trust yield: eliminates Classical.choice from decidable first-order theorems",
    provenance := "lean_rules constructive-gate audit & AltProof bidirectional cross-pollination" },
  { id := "closed-def-whnf-caching",
    family := "kernel-friendly-term-design",
    matchShape := "giant decimal nat_lit constants (>64 bits) or repeated closed shift-add/mask expressions inside Nat.rec/List.rec step lambdas",
    rewriteHint := "evaluate closed constant expressions to raw nat_lit at elaboration time via an elab 'eval_nat%' macro (import Lean has 0 exported Lean.* refs), or hoist into a closed top-level def C : Nat := <formula> with a := rfl spec bridge (cached in m_st->m_whnf after 1 evaluation per kernel invocation)",
    costHint := "eval_nat% gives 0 runtime instruction overhead (vs +160K/invocation for closed def C) and eliminates multi-hundred-digit magic literals",
    provenance := "SAIR Lean Kernel Challenge C++ type_checker.cpp whnf/m_whnf audit (partition DerivedConstants eval_nat% vs partCplusSpec, sha256 shaPaddingSuffix)" },
  { id := "gmp-swar-word-packing",
    family := "algorithm-class-substitution",
    matchShape := "inner loops over fixed-width integer/boolean arrays or linear recurrences with bounded slot bit-width, or manually unrolled block trees",
    rewriteHint := "pack k lanes into a single b-bit GMP Nat word (Kronecker substitution / bitboard ANF) and use elaboration-time pre-unfolding (elab 'preunfold%' / 'unroll_top%') over binary-doubling combinators (t0..t6) to eliminate multi-thousand-line source inlining with 0 runtime unfold overhead",
    costHint := "15-30x kernel instruction reduction on convolution/bitboard loops; preunfold% matches manual inlining (12.72M vs 18.49M for runtime combinators) at 4.2x smaller source",
    provenance := "SAIR Lean Kernel Challenge (partition Kronecker SWAR convolution, ca-rule110 4-gate ANF + preunfold% t0..t6 block tree, fib unroll_top%, sha256 512-bit schedule window)" },
  { id := "bv_decide",
    family := "bitvector-decision",
    matchShape := "BitVec or fixed-width UInt8/UInt16/UInt32/UInt64 bitwise identity/inequality (&&&, |||, ^^^, <<<, >>>)",
    rewriteHint := "discharge directly via by bv_decide (QF_BV bit-blasting decision procedure)",
    costHint := "single-step kernel-certified bitvector closure",
    provenance := "Lean 4 Std.Tactic.BVDecide + lean-analyzer QF_BV pre-screen" },
  { id := "sum_congr_ring",
    family := "big-operators",
    matchShape := "Finset.sum linear combination or pointwise algebraic ring identity under summation",
    rewriteHint := "normalize Finset.sum linearity and close pointwise via Finset.sum_congr rfl (fun _ _ => by ring)",
    costHint := "collapses 4-12 line Finset.sum rewrite chains to 1 line",
    provenance := "AltProof.sum_congr_ring" },
  { id := "finset_nonneg",
    family := "big-operators",
    matchShape := "0 <= Finset.sum s (fun i => f i) non-negativity obligation",
    rewriteHint := "apply Finset.sum_nonneg, instantiate pointwise hypotheses, and close via positivity/linarith/omega",
    costHint := "collapses Finset.sum_nonneg + intro + specialize boilerplate to 1 line",
    provenance := "AltProof.finset_nonneg" },
  { id := "finset_mono",
    family := "big-operators",
    matchShape := "Finset.sum s f <= Finset.sum s g pointwise monotonicity inequality",
    rewriteHint := "apply Finset.sum_le_sum, instantiate pointwise hypotheses, and close via linarith/gcongr/omega",
    costHint := "collapses Finset.sum_le_sum + pointwise instantiation to 1 line",
    provenance := "AltProof.finset_mono" },
  { id := "induction-rescaling",
    family := "structural-induction",
    matchShape := "fixed-arity numbered scalar parameters (a0 a1 a2 a3) or recursive loop with decreasing Nat measure n - i",
    rewriteHint := "generalize fixed-arity parameters to Fin n / List or attach certified termination_by n - i decreasing_by omega",
    costHint := "eliminates fixed-arity duplication and WellFounded fuel boilerplate",
    provenance := "lean-analyzer SOUND-04 NatZoneDomain::check_nat_sub_decreasing + FIDELITY-08" }
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
  hasBitVec : Bool := false
deriving Inhabited, Repr, DecidableEq

/-- Check if an `Expr` mentions any constant name satisfying `pred`. -/
def exprContainsConst (e : Expr) (pred : Name → Bool) : Bool :=
  Option.isSome <| e.find? fun sub =>
    match sub with
    | .const n _ => pred n
    | _ => false

/-- Extract `GoalFeatures` from a target `Expr` and optional local context expressions. -/
def extractExprFeatures (target : Expr) : GoalFeatures :=
  { hasFinsetSum := exprContainsConst target fun n => n == `Finset.sum
    hasAbs := exprContainsConst target fun n => n == `abs || n == `Norm.norm || n == `Dist.dist
    hasIteOrDecide := exprContainsConst target fun n =>
      n == ``ite || n == ``dite || n == ``Decidable.decide
    hasNegOrContra := exprContainsConst target fun n => n == ``Not || n == ``False
    hasNatArith := exprContainsConst target fun n => n == ``Nat || n == ``Int
    hasWellFounded := exprContainsConst target fun n => n == ``WellFounded.fix
    hasBitVec := exprContainsConst target fun n =>
      n == `BitVec || (n.getRoot == `BitVec) }

/-- Combine two `GoalFeatures` records by logical OR. -/
def GoalFeatures.merge (a b : GoalFeatures) : GoalFeatures :=
  { hasFinsetSum := a.hasFinsetSum || b.hasFinsetSum
    hasAbs := a.hasAbs || b.hasAbs
    hasIteOrDecide := a.hasIteOrDecide || b.hasIteOrDecide
    hasNegOrContra := a.hasNegOrContra || b.hasNegOrContra
    hasNatArith := a.hasNatArith || b.hasNatArith
    hasWellFounded := a.hasWellFounded || b.hasWellFounded
    hasBitVec := a.hasBitVec || b.hasBitVec }

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
    | "algorithm-class-substitution" => f.hasFinsetSum || f.hasWellFounded || f.hasBitVec
    | "kernel-friendly-term-design" => f.hasWellFounded || f.hasNatArith || f.hasBitVec
    | "constructive-decidable-reduction" => f.hasIteOrDecide || f.hasNatArith || f.hasBitVec
    | "closed-def-whnf-caching" => f.hasNatArith || f.hasBitVec
    | "gmp-swar-word-packing" => f.hasBitVec || f.hasWellFounded
    | "bv_decide" => f.hasBitVec
    | "sum_congr_ring" => f.hasFinsetSum
    | "finset_nonneg" => f.hasFinsetSum
    | "finset_mono" => f.hasFinsetSum
    | "induction-rescaling" => f.hasNatArith || f.hasWellFounded
    | _ => false
  if picked.isEmpty then routeTable.take 3 else picked

end AltProof.Core
