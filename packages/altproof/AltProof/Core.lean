/-
Copyright (c) 2026 Proof-Skills. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Proof-Skills Contributors
SPDX-License-Identifier: Apache-2.0
-/

import Lean

set_option autoImplicit false

/-!
# AltProof.Core -- Core-Only Route Table, Equality Saturation, SolveByElim, and Kernel Superoptimizers

Core-only (`import Lean`) definitions and tactics for the AltProof 20-route advisor,
usable in zero-Mathlib projects without requiring Mathlib or external Rust FFI binaries:

1. **20-Route Advisor & Two-Axis Cost Ranker (`routeTable`, `computeCostX10`, `GoalFeatures`)**:
   Reader-elegance vs kernel-heartbeat cost model (`SPEC-ALT-PROOF-DES`, `ALT_PROOF_KERNEL_BRIDGE`).
2. **Pure-Lean Kernel-Checked Equality Saturation (`eqsat_rw`, `egg_rw`)**:
   Bounded e-graph / BFS equational rewrite saturation in `MetaM` with kernel-checked
   `Eq.trans` / `congrArg` / `congrFun` proof-term reconstruction (zero external FFI, 3-axiom clean).
3. **Core Structural & Search Tactics (`backchain`, `grind_close`, `contra_direct`, `kernel_decide`)**:
   - `backchain`: curated wrapper over core Lean's `Lean.Elab.Tactic.SolveByElim` (`solve_by_elim`).
   - `grind_close`: bounded e-graph congruence & E-matching closer via core Lean's `grind`.
   - `contra_direct`: constructive negation / `Bool` / `Decidable` normalizer avoiding `Classical.choice`.
   - `kernel_decide`: strict 3-rung kernel-clean decision macro (`rfl | decide +kernel | omega`).
4. **Kernel Compile-Time Superoptimizers (`eval_nat%`, `preunfold%`, `swar_unroll%`)**:
   - `eval_nat% t`: evaluates closed `Nat` arithmetic/bitwise formulas at elaboration time to raw
     `Expr.lit (.natVal v)` (`nat_lit`), leaving zero `Lean.*` constants in exported declarations.
   - `preunfold% [d1, ...] t`: unfolds selected definitions, beta/zeta/proj-reduces, folds closed
     `Nat` and `Bool.rec` subterms inside open expressions, and hash-conses via `ShareCommon.shareCommon`.
   - `swar_unroll% k base step` (alias `unroll_nat_rec%`): unrolls static trip-count `k` loops at
     elaboration time with per-step constant folding and DAG sharing.
-/

open Lean Meta Elab Term Tactic

namespace AltProof.Core

-- ============================================================================
-- 1. Canonical 20-Route Table, Cost Model, and AST Feature Detector
-- ============================================================================

/-- An alternative proof route definition from the route table (`SPEC-ALT-PROOF-DES` Section 5b). -/
structure Route where
  id : String
  family : String
  matchShape : String
  rewriteHint : String
  costHint : String
  provenance : String
deriving Inhabited, Repr, DecidableEq

/-- The canonical 20-route table corresponding to `SPEC-ALT-PROOF-DES` Section 5b / `route-table.json`. -/
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
    rewriteHint := "restate as a direct construction or normalize via contra_direct (the JAR 2016 redirect class)",
    costHint := "eliminates non-constructive Classical.choice double-negation overhead",
    provenance := "JAR16 redirect procedure; ballot B3 + AltProof.Core.contra_direct" },
  { id := "algorithm-class-substitution",
    family := "algorithm-class-substitution",
    matchShape := "exponential or unhoisted recursion with an equivalent closed-form or DP reduction",
    rewriteHint := "substitute algorithm class (e.g. in-place DP or structural sieve) and prove equivalence to spec",
    costHint := "highest kernel yield: 20-30x reduction in kernel steps / rfl time",
    provenance := "Lean kernel reduction lanes (partition in-place DP S1/S1b, primecount sieve S6)" },
  { id := "kernel-friendly-term-design",
    family := "kernel-friendly-term-design",
    matchShape := "structural recursion or helper calls with heavy defeq unfolding overhead",
    rewriteHint := "refactor to kernel-friendly primitives (structural Nat.rec, unrolled trial division, import-minimal path)",
    costHint := "high kernel yield: reduces defeq heartbeats and avoids WellFounded.fix traps",
    provenance := "Lean kernel reduction lanes (primecount L1 structural trial division S5)" },
  { id := "constructive-decidable-reduction",
    family := "kernel-friendly-term-design",
    matchShape := "Classical.choice leakage in first-order Nat/Int/Bool/BitVec theorems caused by split on &&/And or classical by_cases",
    rewriteHint := "replace split/by_cases with contra_direct, Bool.and_eq_true, decide_eq_true_eq, omega, or bv_decide to keep axiom closure Classical.choice-free",
    costHint := "high kernel & trust yield: eliminates Classical.choice from decidable first-order theorems",
    provenance := "lean_rules constructive-gate audit & AltProof bidirectional cross-pollination" },
  { id := "closed-def-whnf-caching",
    family := "kernel-friendly-term-design",
    matchShape := "giant decimal nat_lit constants (>64 bits) or repeated closed shift-add/mask expressions inside Nat.rec/List.rec step lambdas",
    rewriteHint := "evaluate closed constant expressions to raw nat_lit at elaboration time via eval_nat% (import Lean has 0 exported Lean.* refs), or hoist into a closed top-level def C : Nat := <formula> with a := rfl spec bridge",
    costHint := "eval_nat% gives 0 runtime instruction overhead (vs +160K/invocation for closed def C) and eliminates multi-hundred-digit magic literals",
    provenance := "Lean C++ type_checker.cpp whnf/m_whnf audit + AltProof.Core.eval_nat%" },
  { id := "gmp-swar-word-packing",
    family := "algorithm-class-substitution",
    matchShape := "inner loops over fixed-width integer/boolean arrays or linear recurrences with bounded slot bit-width, or manually unrolled block trees",
    rewriteHint := "pack k lanes into a single b-bit GMP Nat word (Kronecker substitution / bitboard ANF) and use preunfold% / swar_unroll% over binary-doubling combinators",
    costHint := "15-30x kernel instruction reduction on convolution/bitboard loops; preunfold% matches manual inlining at 4.2x smaller source",
    provenance := "Lean kernel WHNF + AltProof.Core.preunfold% / swar_unroll%" },
  { id := "bv_decide",
    family := "bitvector-decision",
    matchShape := "BitVec or fixed-width UInt8/UInt16/UInt32/UInt64 bitwise identity/inequality (&&&, |||, ^^^, <<<, >>>)",
    rewriteHint := "discharge directly via by bv_decide (QF_BV bit-blasting decision procedure)",
    costHint := "single-step kernel-certified bitvector closure",
    provenance := "Lean 4 Std.Tactic.BVDecide + lean-analyzer QF_BV pre-screen" },
  { id := "sum_congr_ring",
    family := "big-operators",
    matchShape := "Finset.sum linear combination or pointwise algebraic ring identity under summation",
    rewriteHint := "normalize Finset.sum linearity and close pointwise via sum_congr_ring or calc_ring_sum",
    costHint := "collapses 4-12 line Finset.sum rewrite chains to 1 line",
    provenance := "AltProof.sum_congr_ring + AltProof.calc_ring_sum" },
  { id := "finset_nonneg",
    family := "big-operators",
    matchShape := "0 <= Finset.sum s (fun i => f i) non-negativity obligation",
    rewriteHint := "apply Finset.sum_nonneg, instantiate pointwise hypotheses, and close via positivity/linarith/omega",
    costHint := "collapses Finset.sum_nonneg + intro + specialize boilerplate to 1 line",
    provenance := "AltProof.finset_nonneg" },
  { id := "finset_mono",
    family := "big-operators",
    matchShape := "Finset.sum s f <= Finset.sum s g pointwise monotonicity inequality",
    rewriteHint := "apply Finset.sum_le_sum or gcongr_pos, instantiate pointwise hypotheses, and close via linarith/gcongr/omega",
    costHint := "collapses Finset.sum_le_sum + pointwise instantiation to 1 line",
    provenance := "AltProof.finset_mono + AltProof.gcongr_pos" },
  { id := "induction-rescaling",
    family := "structural-induction",
    matchShape := "fixed-arity numbered scalar parameters (a0 a1 a2 a3) or recursive loop with decreasing Nat measure n - i",
    rewriteHint := "generalize fixed-arity parameters to Fin n / List or attach certified termination_by n - i decreasing_by omega",
    costHint := "eliminates fixed-arity duplication and WellFounded fuel boilerplate",
    provenance := "lean-analyzer SOUND-04 NatZoneDomain::check_nat_sub_decreasing + FIDELITY-08" },
  { id := "kernel_decide",
    family := "kernel-friendly-term-design",
    matchShape := "decidable Nat/Bool/Int equality or inequality on a strict 3-axiom kernel lane where Lean.ofReduceBool is forbidden",
    rewriteHint := "close via kernel_decide (first | rfl | decide +kernel | omega) without invoking native_decide or bv_decide",
    costHint := "0 Lean.ofReduceBool axioms; direct WHNF or verified Presburger closure",
    provenance := "Template_KernelDecide.lean + strict 3-axiom kernel gate" },
  { id := "proof-carrying-codegen",
    family := "abstraction-concrete-duality",
    matchShape := "verified BitVec/SWAR bitwise or width-guarded arithmetic kernel lowered to MLIR, CUDA sm_89 PTX, AVX2, or C++20",
    rewriteHint := "prove equivalence to clean spec in Lean (PolyBitOp / CheckedWord.needsWide) and verify native N01..N12 conformance",
    costHint := "zero-UB native execution with bit-exact Lean #eval conformance",
    provenance := "Template_ProofCarryingCodegen.lean + WAVE-13 G1 duality" },
  { id := "eqsat-congruence-closure",
    family := "equality-saturation",
    matchShape := "bidirectional equational chains (commutativity/associativity/congruence) where directional simp loops or stalls",
    rewriteHint := "close via eqsat_rw [h1, h2, ...] (pure-Lean kernel Eq.trans/congrArg saturation) or grind_close",
    costHint := "0 external FFI binaries; reconstructs compact kernel Eq.trans / congrArg proof terms",
    provenance := "AltProof.Core.eqsat_rw + core Lean grind congruence closure" },
  { id := "backchain-solve-by-elim",
    family := "backchaining-search",
    matchShape := "shallow Horn-clause / implication / monotonicity / membership obligations solvable from local context + curated lemmas",
    rewriteHint := "close via backchain or backchain [lem1, lem2] (core Lean SolveByElim bounded depth-first search)",
    costHint := "core-only (0 Mathlib required); deterministic bounded backchaining without aesop import weight",
    provenance := "Lean.Elab.Tactic.SolveByElim + AltProof.Core.backchain" }
]

/-- Cost ranker weights per B1 `extraction-outranks` heuristic (scaled integers x10)
    extended with the kernel-cost axis (`ALT_PROOF_KERNEL_BRIDGE` A1). -/
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

/-- Two-axis evaluation node per `ALT_PROOF_KERNEL_BRIDGE` A1/A4: reader elegance vs machine kernel cost. -/
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
  hasEquality : Bool := false
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
      n == `BitVec || (n.getRoot == `BitVec)
    hasEquality := exprContainsConst target fun n => n == ``Eq || n == ``Iff }

/-- Combine two `GoalFeatures` records by logical OR. -/
def GoalFeatures.merge (a b : GoalFeatures) : GoalFeatures :=
  { hasFinsetSum := a.hasFinsetSum || b.hasFinsetSum
    hasAbs := a.hasAbs || b.hasAbs
    hasIteOrDecide := a.hasIteOrDecide || b.hasIteOrDecide
    hasNegOrContra := a.hasNegOrContra || b.hasNegOrContra
    hasNatArith := a.hasNatArith || b.hasNatArith
    hasWellFounded := a.hasWellFounded || b.hasWellFounded
    hasBitVec := a.hasBitVec || b.hasBitVec
    hasEquality := a.hasEquality || b.hasEquality }

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
    | "kernel_decide" => f.hasIteOrDecide || f.hasNatArith
    | "proof-carrying-codegen" => f.hasBitVec
    | "eqsat-congruence-closure" => f.hasEquality
    | "backchain-solve-by-elim" => !f.hasFinsetSum && !f.hasAbs && (f.hasNegOrContra || f.hasEquality)
    | _ => false
  if picked.isEmpty then routeTable.take 3 else picked

-- ============================================================================
-- 2. Core Structural & Decision Tactics (`kernel_decide`, `backchain`, `grind_close`, `contra_direct`)
-- ============================================================================

/-- `kernel_decide`: strict 3-rung kernel-clean decision macro (`rfl | decide +kernel | omega`)
    preserving `[propext, Classical.choice, Quot.sound]` with zero `Lean.ofReduceBool`. -/
syntax (name := kernelDecideTactic) "kernel_decide" : tactic

macro_rules
  | `(tactic| kernel_decide) => `(tactic|
      first
      | rfl
      | decide +kernel
      | omega)

/-- `backchain` / `backchain [lem1, lem2, ...]`: core-only bounded backchaining wrapper over
    `Lean.Elab.Tactic.SolveByElim` (`solve_by_elim`) with `maxDepth := 6`. Works in zero-Mathlib
    projects (`import Lean` only), handling conjunction introduction as well as local/supplied
    implication chains. -/
syntax (name := backchainTactic) "backchain" (" [" Lean.Parser.Tactic.SolveByElim.arg,* "]")? : tactic

macro_rules
  | `(tactic| backchain) =>
    `(tactic|
      first
      | (solve_by_elim (maxDepth := 6); done)
      | (constructor <;> solve_by_elim (maxDepth := 6); done)
      | (intros; solve_by_elim (maxDepth := 6); done))
  | `(tactic| backchain [$[$lems],*]) =>
    `(tactic|
      first
      | (solve_by_elim (maxDepth := 6) [$[$lems],*]; done)
      | (constructor <;> solve_by_elim (maxDepth := 6) [$[$lems],*]; done)
      | (intros; solve_by_elim (maxDepth := 6) [$[$lems],*]; done))

/-- `grind_close` / `grind_close [lem1, ...]`: core-only bounded e-graph congruence closure and
    E-matching closer backed by core Lean's `grind` engine. -/
syntax (name := grindCloseTactic) "grind_close" (" [" Parser.Tactic.grindParam,* "]")? : tactic

macro_rules
  | `(tactic| grind_close) => `(tactic| (grind; done))
  | `(tactic| grind_close [$[$params:grindParam],*]) => `(tactic| (grind [$[$params],*]; done))

/-- `contra_direct`: constructive negation, `Bool`, and `Decidable` normalizer that simplifies
    `Bool.and_eq_true`, `Bool.or_eq_true`, `Bool.not_eq_true`, `decide_eq_true_eq`, and negated
    implications/conjunctions without introducing `Classical.choice` via classical `split`/`by_cases`. -/
syntax (name := contraDirectTactic) "contra_direct" : tactic

macro_rules
  | `(tactic| contra_direct) => `(tactic|
      first
      | (intro h; exact absurd h (by assumption))
      | (simp only [Bool.and_eq_true, Bool.or_eq_true, Bool.not_eq_true', Bool.not_eq_false',
                    decide_eq_true_eq, decide_eq_false_iff_not, not_and, Classical.not_not] at * <;>
         first
         | done
         | assumption
         | rfl
         | (solve_by_elim (maxDepth := 4) [And.left, And.right, And.intro]; done)
         | decide +kernel
         | omega)
      | (intros; simp only [Bool.and_eq_true, Bool.or_eq_true, Bool.not_eq_true',
                            decide_eq_true_eq, decide_eq_false_iff_not] at *;
         first
         | done
         | assumption
         | rfl
         | (solve_by_elim (maxDepth := 4) [And.left, And.right, And.intro]; done)
         | decide +kernel
         | omega))

-- ============================================================================
-- 3. Pure-Lean Kernel-Checked Equality Saturation (`eqsat_rw`, `egg_rw`)
-- ============================================================================

/-- Oriented rewrite rule extracted from a user-supplied lemma or local hypothesis. -/
structure EqSatRule where
  proofFn : Expr
  numBinders : Nat
  symm : Bool
deriving Inhabited

/-- Equivalence-class node inside the bounded `MetaM` equality saturator:
    stores a reachable `Expr` together with the exact kernel proof `lhs = expr`! -/
structure EqSatNode where
  expr : Expr
  proofFromRoot : Expr
  depth : Nat
deriving Inhabited

/-- Attempt to apply `rule` at the root of `target`, returning `some (rhs, eqProof)` where
    `eqProof : target = rhs` is a kernel-valid equality term. -/
def tryApplyRuleAtRoot (rule : EqSatRule) (target : Expr) : MetaM (Option (Expr × Expr)) :=
  withoutModifyingState do
    try
      let ruleTy ← inferType rule.proofFn
      let (mvars, _, bodyTy) ← forallMetaTelescopeReducing ruleTy (some rule.numBinders)
      let appProof := mkAppN rule.proofFn mvars
      let bodyTy ← whnf bodyTy
      if let some (_, lhs, rhs) := bodyTy.eq? then
        if !rule.symm then
          if ← isDefEq lhs target then
            let rhsInst ← instantiateMVars rhs
            let prfInst ← instantiateMVars appProof
            if !rhsInst.hasMVar && !prfInst.hasMVar then
              return some (rhsInst, prfInst)
        else
          if ← isDefEq rhs target then
            let lhsInst ← instantiateMVars lhs
            let prfInst ← instantiateMVars appProof
            if !lhsInst.hasMVar && !prfInst.hasMVar then
              let symmPrf ← mkEqSymm prfInst
              return some (lhsInst, symmPrf)
      return none
    catch _ =>
      return none

/-- Enumerate all single-step rewrites of `e` (at root and recursively inside `.app` arguments
    via `mkCongrArg` / `mkCongrFun`, bounded to subterm depth 4), returning `(e', proof : e = e')`. -/
partial def rewriteSubtermsOnce (rules : Array EqSatRule) (e : Expr) (subDepth : Nat := 0) :
    MetaM (Array (Expr × Expr)) := do
  let mut out : Array (Expr × Expr) := #[]
  -- 1. Root rewrites
  for rule in rules do
    if let some (rhs, prf) ← tryApplyRuleAtRoot rule e then
      if rhs != e then
        out := out.push (rhs, prf)
  -- 2. Subterm congruence rewrites (`congrArg`, `congrFun`)
  if subDepth < 4 then
    if let .app f a := e then
      let argSteps ← rewriteSubtermsOnce rules a (subDepth + 1)
      for (a', pa) in argSteps do
        if let some cPrf ← (try some <$> mkCongrArg f pa catch _ => pure none) then
          out := out.push (.app f a', cPrf)
      let fnSteps ← rewriteSubtermsOnce rules f (subDepth + 1)
      for (f', pf) in fnSteps do
        if let some cPrf ← (try some <$> mkCongrFun pf a catch _ => pure none) then
          out := out.push (.app f' a, cPrf)
  return out

/-- Bidirectional BFS equality saturation from both `lhs` and `rhs` up to `maxNodes` states:
    whenever forward saturation (`lhs = mid`) and backward saturation (`rhs = mid'`) meet up to
    definitional equality (`isDefEq mid mid'`), reconstructs the exact kernel proof
    `Eq.trans prfL (Eq.symm prfR) : lhs = rhs`! Zero external FFI, 3-axiom clean. -/
def saturateEquality (rules : Array EqSatRule) (lhs rhs : Expr)
    (maxNodes : Nat := 48) (maxDepth : Nat := 4) : MetaM (Option Expr) := do
  if ← withoutModifyingState (isDefEq lhs rhs) then
    return some (← mkEqRefl lhs)
  let lhsRefl ← mkEqRefl lhs
  let rhsRefl ← mkEqRefl rhs
  let mut fwd : Array EqSatNode := #[{ expr := lhs, proofFromRoot := lhsRefl, depth := 0 }]
  let mut bwd : Array EqSatNode := #[{ expr := rhs, proofFromRoot := rhsRefl, depth := 0 }]
  let mut fwdCursor : Nat := 0
  let mut bwdCursor : Nat := 0

  while (fwdCursor < fwd.size || bwdCursor < bwd.size) && (fwd.size + bwd.size < maxNodes) do
    -- Expand one forward node
    if fwdCursor < fwd.size then
      let cur := fwd[fwdCursor]!
      fwdCursor := fwdCursor + 1
      if cur.depth < maxDepth then
        let steps ← rewriteSubtermsOnce rules cur.expr
        for (nextE, stepPrf) in steps do
          if fwd.size + bwd.size < maxNodes then
            let already := fwd.any fun n => n.expr == nextE
            if !already then
              let chainPrf ← mkEqTrans cur.proofFromRoot stepPrf
              -- Meet-in-the-middle check against all backward nodes
              for bNode in bwd do
                if ← withoutModifyingState (isDefEq nextE bNode.expr) then
                  let bSymm ← mkEqSymm bNode.proofFromRoot
                  return some (← mkEqTrans chainPrf bSymm)
              fwd := fwd.push { expr := nextE, proofFromRoot := chainPrf, depth := cur.depth + 1 }

    -- Expand one backward node
    if bwdCursor < bwd.size && (fwd.size + bwd.size < maxNodes) then
      let cur := bwd[bwdCursor]!
      bwdCursor := bwdCursor + 1
      if cur.depth < maxDepth then
        let steps ← rewriteSubtermsOnce rules cur.expr
        for (nextE, stepPrf) in steps do
          if fwd.size + bwd.size < maxNodes then
            let already := bwd.any fun n => n.expr == nextE
            if !already then
              let chainPrf ← mkEqTrans cur.proofFromRoot stepPrf
              for fNode in fwd do
                if ← withoutModifyingState (isDefEq fNode.expr nextE) then
                  let bSymm ← mkEqSymm chainPrf
                  return some (← mkEqTrans fNode.proofFromRoot bSymm)
              bwd := bwd.push { expr := nextE, proofFromRoot := chainPrf, depth := cur.depth + 1 }
  return none

/-- Extract bidirectional `EqSatRule`s from an elaborated proof term `prf` (handling both
    universally quantified equality lemmas and conjunctions/iff hypotheses). -/
def rulesFromExpr (prf : Expr) : MetaM (Array EqSatRule) := do
  let ty ← inferType prf
  let (_, _, bodyTy) ← forallMetaTelescopeReducing ty
  let numB := ty.getForallBinderNames.length
  let bodyWhnf ← whnf bodyTy
  if bodyWhnf.eq?.isSome then
    return #[
      { proofFn := prf, numBinders := numB, symm := false },
      { proofFn := prf, numBinders := numB, symm := true }
    ]
  else if let some (p, q) := bodyWhnf.iff? then
    if numB == 0 then
      let propEq ← mkAppOptM ``propext #[some p, some q, some prf]
      return #[
        { proofFn := propEq, numBinders := 0, symm := false },
        { proofFn := propEq, numBinders := 0, symm := true }
      ]
    else
      return #[]
  else
    return #[]

/-- `eqsat_rw` / `eqsat_rw [r1, r2, ...]` (alias `egg_rw`):
    Pure-Lean bidirectional equality saturation tactic in `MetaM` (`import Lean` only, 0 Rust FFI).
    Harvests equational hypotheses from the local context plus `[r1, r2, ...]`, performs bounded
    meet-in-the-middle congruence saturation (`congrArg`, `congrFun`), and reconstructs a
    kernel-checked `Eq.trans` / `Eq.symm` proof term (3-axiom clean). For heavy SMT/arithmetic
    e-graph closure, invoke `grind_close` explicitly. -/
syntax (name := eqsatRwTactic) ("eqsat_rw" <|> "egg_rw") (" [" term,* "]")? : tactic

@[tactic eqsatRwTactic]
def evalEqsatRw : Tactic := fun stx =>
  withMainContext do
    let goal ← getMainGoal
    let target ← instantiateMVars (← goal.getType)
    let targetWhnf ← whnf target
    let mut rules : Array EqSatRule := #[]
    -- Collect local equational hypotheses automatically
    let lctx ← getLCtx
    for decl in lctx do
      if !decl.isImplementationDetail then
        let rs ← rulesFromExpr decl.toExpr
        rules := rules ++ rs
    -- Collect user-supplied rewrite lemmas `[r1, r2, ...]`
    let extraTerms : Array Syntax :=
      match stx with
      | `(tactic| eqsat_rw [$[$ts:term],*]) => ts.map (·.raw)
      | `(tactic| egg_rw [$[$ts:term],*]) => ts.map (·.raw)
      | _ => #[]
    for tStx in extraTerms do
      let prf ← Tactic.elabTerm tStx none
      let prf ← instantiateMVars prf
      let rs ← rulesFromExpr prf
      rules := rules ++ rs

    if rules.isEmpty then
      throwError "eqsat_rw: no equational hypotheses or rewrite lemmas in scope"

    if let some (_, lhs, rhs) := targetWhnf.eq? then
      if let some eqPrf ← saturateEquality rules lhs rhs then
        goal.assign eqPrf
        replaceMainGoal []
        return
    else if let some (lhs, rhs) := targetWhnf.iff? then
      if let some eqPrf ← saturateEquality rules lhs rhs then
        let iffPrf ← mkAppOptM ``iff_of_eq #[some lhs, some rhs, some eqPrf]
        goal.assign iffPrf
        replaceMainGoal []
        return

    throwError "eqsat_rw: bounded equality saturation did not connect LHS and RHS within node budget"

-- ============================================================================
-- 4. Kernel Elaboration-Time Superoptimizers (`eval_nat%`, `preunfold%`, `swar_unroll%`)
-- ============================================================================

/-- Pure kernel-primitive evaluator for closed `Nat` expressions (`Expr`). Evaluates `Nat.add`,
    `Nat.sub`, `Nat.mul`, `Nat.div`, `Nat.mod`, `Nat.pow`, `Nat.gcd`, `Nat.land`, `Nat.lor`,
    `Nat.xor`, `Nat.shiftLeft`, `Nat.shiftRight`, `Nat.pred`, `Nat.succ`, `Nat.log2`, and closed
    environment definitions without `unsafe evalExpr`. -/
partial def evalClosedNatExpr (e : Expr) : MetaM Nat := do
  let env ← getEnv
  let rec eval (t : Expr) : MetaM Nat := do
    match t with
    | .lit (.natVal v) => return v
    | .mdata _ b => eval b
    | .const c us =>
      if c == ``Nat.zero then return 0
      else
        match env.find? c with
        | some (.defnInfo dval) =>
          eval (dval.value.instantiateLevelParams dval.levelParams us)
        | _ =>
          let w ← whnf t
          match w with
          | .lit (.natVal v) => return v
          | _ => throwError "eval_nat%: cannot reduce constant `{c}` to a Nat literal"
    | .letE _ _ val body _ =>
      let v ← eval val
      eval (body.instantiate1 (mkRawNatLit v))
    | _ =>
      let fn := t.getAppFn
      let args := t.getAppArgs
      if fn.isConstOf ``OfNat.ofNat && args.size ≥ 2 then
        eval args[1]!
      else if fn.isConstOf ``Nat.succ && args.size == 1 then
        return (← eval args[0]!) + 1
      else if fn.isConstOf ``Nat.pred && args.size == 1 then
        return (← eval args[0]!) - 1
      else if fn.isConstOf ``Nat.log2 && args.size == 1 then
        return (← eval args[0]!).log2
      else if (fn.isConstOf ``Nat.add && args.size == 2) || (fn.isConstOf ``HAdd.hAdd && args.size == 6) then
        return (← eval args[args.size - 2]!) + (← eval args[args.size - 1]!)
      else if (fn.isConstOf ``Nat.sub && args.size == 2) || (fn.isConstOf ``HSub.hSub && args.size == 6) then
        return (← eval args[args.size - 2]!) - (← eval args[args.size - 1]!)
      else if (fn.isConstOf ``Nat.mul && args.size == 2) || (fn.isConstOf ``HMul.hMul && args.size == 6) then
        return (← eval args[args.size - 2]!) * (← eval args[args.size - 1]!)
      else if (fn.isConstOf ``Nat.div && args.size == 2) || (fn.isConstOf ``HDiv.hDiv && args.size == 6) then
        return (← eval args[args.size - 2]!) / (← eval args[args.size - 1]!)
      else if (fn.isConstOf ``Nat.mod && args.size == 2) || (fn.isConstOf ``HMod.hMod && args.size == 6) then
        return (← eval args[args.size - 2]!) % (← eval args[args.size - 1]!)
      else if (fn.isConstOf ``Nat.pow && args.size == 2) || (fn.isConstOf ``HPow.hPow && args.size == 6) then
        return (← eval args[args.size - 2]!) ^ (← eval args[args.size - 1]!)
      else if fn.isConstOf ``Nat.gcd && args.size == 2 then
        return Nat.gcd (← eval args[0]!) (← eval args[1]!)
      else if (fn.isConstOf ``Nat.land && args.size == 2) || (fn.isConstOf ``HAnd.hAnd && args.size == 6) then
        return (← eval args[args.size - 2]!) &&& (← eval args[args.size - 1]!)
      else if (fn.isConstOf ``Nat.lor && args.size == 2) || (fn.isConstOf ``HOr.hOr && args.size == 6) then
        return (← eval args[args.size - 2]!) ||| (← eval args[args.size - 1]!)
      else if (fn.isConstOf ``Nat.xor && args.size == 2) || (fn.isConstOf ``HXor.hXor && args.size == 6) then
        return (← eval args[args.size - 2]!) ^^^ (← eval args[args.size - 1]!)
      else if (fn.isConstOf ``Nat.shiftLeft && args.size == 2) || (fn.isConstOf ``HShiftLeft.hShiftLeft && args.size == 6) then
        return (← eval args[args.size - 2]!) <<< (← eval args[args.size - 1]!)
      else if (fn.isConstOf ``Nat.shiftRight && args.size == 2) || (fn.isConstOf ``HShiftRight.hShiftRight && args.size == 6) then
        return (← eval args[args.size - 2]!) >>> (← eval args[args.size - 1]!)
      else if let .const c us := fn then
        if let some (.defnInfo dval) := env.find? c then
          let v := dval.value.instantiateLevelParams dval.levelParams us
          eval (v.beta args)
        else
          let w ← whnf t
          match w with
          | .lit (.natVal v) => return v
          | _ => throwError "eval_nat%: unsupported application `{t}`"
      else if fn.isLambda then
        eval (fn.beta args)
      else
        let w ← whnf t
        match w with
        | .lit (.natVal v) => return v
        | _ => throwError "eval_nat%: term `{t}` did not reduce to a closed Nat literal"
  eval e

/-- `eval_nat% t` elaborates `t : Nat` and evaluates it at elaboration time to a raw `nat_lit`
    (`Expr.lit (.natVal v)`), leaving zero `Lean.*` constants or runtime arithmetic in exported
    declarations (`KERNEL-LAW-11` / `MetaPreUnfold.lean`). -/
elab "eval_nat% " t:term : term => do
  let e ← elabTermAndSynthesize t (some (mkConst ``Nat))
  let e ← instantiateMVars e
  let v ← evalClosedNatExpr e
  return mkRawNatLit v

/-- Evaluate a closed `Bool` expression at elaboration time when possible. -/
partial def evalClosedBoolExpr? (e : Expr) : MetaM (Option Bool) := do
  if e.hasLooseBVars || e.hasFVar || e.hasMVar then
    return none
  let rec evalB (t : Expr) : MetaM (Option Bool) := do
    match t with
    | .mdata _ b => evalB b
    | .const c _ =>
      if c == ``Bool.true then return some true
      else if c == ``Bool.false then return some false
      else
        let w ← whnf t
        if w.isConstOf ``Bool.true then return some true
        else if w.isConstOf ``Bool.false then return some false
        else return none
    | _ =>
      let fn := t.getAppFn
      let args := t.getAppArgs
      if fn.isConstOf ``Nat.beq && args.size == 2 then
        try return some (Nat.beq (← evalClosedNatExpr args[0]!) (← evalClosedNatExpr args[1]!))
        catch _ => return none
      else if fn.isConstOf ``Nat.ble && args.size == 2 then
        try return some (Nat.ble (← evalClosedNatExpr args[0]!) (← evalClosedNatExpr args[1]!))
        catch _ => return none
      else if fn.isConstOf ``Bool.and && args.size == 2 then
        if let (some a, some b) := (← evalB args[0]!, ← evalB args[1]!) then return some (a && b)
      else if fn.isConstOf ``Bool.or && args.size == 2 then
        if let (some a, some b) := (← evalB args[0]!, ← evalB args[1]!) then return some (a || b)
      else if fn.isConstOf ``Bool.not && args.size == 1 then
        if let some a ← evalB args[0]! then return some (!a)
      let w ← whnf t
      if w.isConstOf ``Bool.true then return some true
      else if w.isConstOf ``Bool.false then return some false
      else return none
  evalB e

/-- Check whether `fn` applied to `args` is a full-arity primitive `Nat`-valued application. -/
def isClosedNatPrimitiveApp (fn : Expr) (args : Array Expr) : Bool :=
  (fn.isConstOf ``OfNat.ofNat && args.size ≥ 2) ||
  (fn.isConstOf ``Nat.succ && args.size == 1) ||
  (fn.isConstOf ``Nat.pred && args.size == 1) ||
  (fn.isConstOf ``Nat.log2 && args.size == 1) ||
  ((fn.isConstOf ``Nat.add || fn.isConstOf ``Nat.sub || fn.isConstOf ``Nat.mul ||
    fn.isConstOf ``Nat.div || fn.isConstOf ``Nat.mod || fn.isConstOf ``Nat.pow ||
    fn.isConstOf ``Nat.gcd || fn.isConstOf ``Nat.land || fn.isConstOf ``Nat.lor ||
    fn.isConstOf ``Nat.xor || fn.isConstOf ``Nat.shiftLeft || fn.isConstOf ``Nat.shiftRight) &&
   args.size == 2) ||
  ((fn.isConstOf ``HAdd.hAdd || fn.isConstOf ``HSub.hSub || fn.isConstOf ``HMul.hMul ||
    fn.isConstOf ``HDiv.hDiv || fn.isConstOf ``HMod.hMod || fn.isConstOf ``HPow.hPow ||
    fn.isConstOf ``HAnd.hAnd || fn.isConstOf ``HOr.hOr || fn.isConstOf ``HXor.hXor ||
    fn.isConstOf ``HShiftLeft.hShiftLeft || fn.isConstOf ``HShiftRight.hShiftRight) &&
   args.size == 6 && args[0]!.isConstOf ``Nat)

/-- Recursively unfold every constant satisfying `shouldUnfold` inside `e`, beta/zeta/proj-reduce,
    fold closed `Nat` and `Bool.rec` subterms, and apply `Lean.ShareCommon.shareCommon`. -/
partial def preunfoldExprWith (shouldUnfold : Name → Bool) (e : Expr) : MetaM Expr := do
  let env ← getEnv
  let rec go (t : Expr) : MetaM Expr := do
    match t with
    | .mdata _ b => go b
    | .letE _ _ val body _ =>
      let v ← go val
      go (body.instantiate1 v)
    | .lam n ty body bi =>
      withLocalDecl n bi (← go ty) fun fvar => do
        let b ← go (body.instantiate1 fvar)
        mkLambdaFVars #[fvar] b
    | .forallE n ty body bi =>
      withLocalDecl n bi (← go ty) fun fvar => do
        let b ← go (body.instantiate1 fvar)
        mkForallFVars #[fvar] b
    | .proj s i structExpr =>
      let st ← go structExpr
      if let .const ctorName _ := st.getAppFn then
        if let some (.ctorInfo cval) := env.find? ctorName then
          let stArgs := st.getAppArgs
          if cval.numParams + i < stArgs.size then
            return stArgs[cval.numParams + i]!
      return .proj s i st
    | _ =>
      let fn := t.getAppFn
      let rawArgs := t.getAppArgs
      if let .const c _ := fn then
        if c == ``Bool.rec && rawArgs.size >= 4 then
          let major ← go rawArgs[3]!
          if let some b ← evalClosedBoolExpr? major then
            let branch := if b then rawArgs[2]! else rawArgs[1]!
            let extra ← rawArgs[4:].toArray.mapM go
            return ← go (mkAppN branch extra)
        if c == ``Bool.casesOn && rawArgs.size >= 4 then
          let major ← go rawArgs[1]!
          if let some b ← evalClosedBoolExpr? major then
            let branch := if b then rawArgs[3]! else rawArgs[2]!
            let extra ← rawArgs[4:].toArray.mapM go
            return ← go (mkAppN branch extra)
      let args ← rawArgs.mapM go
      let tReduced := mkAppN fn args
      if !tReduced.hasLooseBVars && !tReduced.hasFVar && !tReduced.hasMVar then
        if isClosedNatPrimitiveApp fn args then
          if let some v ← (try some <$> evalClosedNatExpr tReduced catch _ => pure none) then
            return mkRawNatLit v
      match fn with
      | .const c us =>
        if shouldUnfold c || c.toString.endsWith ".match_1" then
          if let some (.defnInfo dval) := env.find? c then
            let v := dval.value.instantiateLevelParams dval.levelParams us
            let next := v.beta args
            if next == tReduced then return tReduced
            return ← go next
          else return tReduced
        else return tReduced
      | .lam _ _ _ _ =>
        if args.isEmpty then return fn else go (fn.beta args)
      | _ =>
        if args.isEmpty then return fn else return mkAppN (← go fn) args
  let res ← go e
  return Lean.ShareCommon.shareCommon res

/-- `preunfold% [d1, d2, ...] t` unfolds `d1, d2, ...` inside `t` at elaboration time, beta/zeta-reduces,
    folds closed `Nat` and `Bool.rec` subterms, and applies `ShareCommon.shareCommon`. -/
elab "preunfold% " "[" ids:ident,* "]" t:term : term <= expectedType? => do
  let e ← elabTermAndSynthesize t expectedType?
  let e ← instantiateMVars e
  let mut targetNames : NameSet := {}
  for idStx in ids.getElems do
    let resolved ← resolveGlobalConstNoOverload idStx
    targetNames := targetNames.insert resolved
  preunfoldExprWith (fun c => targetNames.contains c) e

/-- Unrolls `k` iterations of `step : Nat → α → α` starting from `base : α`, beta/zeta-reducing and
    folding closed `Nat`/`Bool` subterms at each step, and hash-consing via `ShareCommon.shareCommon`. -/
def buildUnrolledLoop (k : Nat) (base step : Expr) : MetaM Expr := do
  let mut acc := base
  for i in [:k] do
    let idx := mkRawNatLit i
    let next := mkApp2 step idx acc
    acc ← preunfoldExprWith (fun _ => false) next
  return Lean.ShareCommon.shareCommon acc

/-- `swar_unroll% k base step` (alias `unroll_nat_rec%`): unrolls `k` steps of `step (nat_lit i) acc`
    at elaboration time with constant folding and `ShareCommon` DAG hash-consing. -/
elab ("swar_unroll% " <|> "unroll_nat_rec% ") k:num base:term:arg step:term:arg : term <= expectedType? => do
  let baseExpr ← Term.elabTerm base expectedType?
  let baseTy ← inferType baseExpr
  let stepTy ← mkArrow (mkConst ``Nat) (← mkArrow baseTy baseTy)
  let stepExpr ← Term.elabTerm step (some stepTy)
  let baseExpr ← instantiateMVars baseExpr
  let stepExpr ← instantiateMVars stepExpr
  buildUnrolledLoop k.getNat baseExpr stepExpr

end AltProof.Core
