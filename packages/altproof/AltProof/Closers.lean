/-
Copyright (c) 2026 Proof-Skills. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Proof-Skills Contributors
SPDX-License-Identifier: Apache-2.0
-/

import Lean
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.GCongr
import Mathlib.Tactic.Push
import Mathlib.Tactic.FieldSimp
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Algebra.BigOperators.Field
import Mathlib.Data.Finset.Max
import Mathlib.Data.Int.Interval
import Mathlib.Basic.Real.Basic
import Mathlib.Data.Matrix.Basic
import Aesop

set_option autoImplicit false

/-!
# AltProof.Closers -- Reusable Mathlib Big-Operator, Matrix, Norm, and Quotient Closers

Lightweight, self-contained proof-closer tactics and bridge lemmas safe for production
formalizations and standalone paper supplements (zero interactive advisor or route-table state):

1. **Big-Operator & Ordered-Ring Closers**:
   - `sum_congr_ring`, `calc_ring_sum`, `gcongr_pos`, `finset_nonneg`, `finset_mono`.
2. **Convex, Markov, and Matrix Domain Closers**:
   - `convex_comb`, `markov_row_sum`, `matrix_pos`.
3. **Sup-Norm, Quotient-Derivative, Grid-Cardinality, and Doeblin Contraction Bridges**:
   - `sup'_const_mul_of_nonneg` & `sup_norm_scale`: positive-homogeneous `Finset.sup'` scaling.
   - `deriv_quot_ring`: pre-normalized denominator-clearing quotient identity closer.
   - `fin_card_filter_Ico`: cardinality of `{i : Fin N | a ≤ i.val ∧ i.val < b}`.
   - `natAbs_le_div_of_cast_abs_le`: integer `natAbs` floor-division bound from real `|·|` inequality.
   - `zero_sum_vecMul_l1_le_of_entry_floor`: Doeblin entry-floor $\ell^1$ contraction on zero-sum vectors.
-/

open Lean Meta Elab Tactic
open scoped BigOperators

namespace AltProof.Closers

/-- `sum_congr_ring`: normalizes `Finset.sum` linear combinations (`sum_add_distrib`,
    `sum_sub_distrib`, `sum_neg_distrib`, `mul_sum`, `sum_mul`, `sum_div`, scalar-sum factors,
    and multi-sum linear combinations `a * ∑ f ± b * ∑ g ± c * ∑ h`) and discharges pointwise
    ring equalities under `Finset.sum` via `Finset.sum_congr rfl fun _ _ => by ring`. Always
    closes the goal or fails cleanly so `first` combinators can backtrack reliably. -/
syntax (name := sumCongrRingTactic) "sum_congr_ring" : tactic

macro_rules
  | `(tactic| sum_congr_ring) => `(tactic|
      first
      | (refine Finset.sum_congr rfl (fun _ _ => ?_); ring)
      | (rw [← Finset.sum_sub_distrib]; first | done | (refine Finset.sum_congr rfl (fun _ _ => ?_); ring))
      | (rw [← Finset.sum_add_distrib]; first | done | (refine Finset.sum_congr rfl (fun _ _ => ?_); ring))
      | (rw [Finset.mul_sum]; first | done | (refine Finset.sum_congr rfl (fun _ _ => ?_); ring))
      | (rw [← Finset.mul_sum]; first | done | (refine Finset.sum_congr rfl (fun _ _ => ?_); ring))
      | (rw [Finset.sum_mul]; first | done | (refine Finset.sum_congr rfl (fun _ _ => ?_); ring))
      | (rw [← Finset.sum_mul]; first | done | (refine Finset.sum_congr rfl (fun _ _ => ?_); ring))
      | (rw [Finset.sum_div]; first | done | (refine Finset.sum_congr rfl (fun _ _ => ?_); ring))
      | (rw [← Finset.sum_div]; first | done | (refine Finset.sum_congr rfl (fun _ _ => ?_); ring))
      | (simp only [Finset.mul_sum, Finset.sum_mul, ← Finset.sum_add_distrib, ← Finset.sum_sub_distrib, ← Finset.sum_neg_distrib];
         first
         | done
         | (refine Finset.sum_congr rfl (fun _ _ => ?_); ring)
         | (rw [← Finset.mul_sum]; first | done | (refine Finset.sum_congr rfl (fun _ _ => ?_); ring))
         | (rw [← Finset.sum_mul]; first | done | (refine Finset.sum_congr rfl (fun _ _ => ?_); ring))))

/-- `calc_ring_sum`: multi-step `Finset.sum` commutation (`Finset.sum_comm`), separable double-sum
    factorization (`(∑ a, ∑ b, f a * g b) = (∑ a, f a) * (∑ b, g b)`), scalar distribution,
    and telescoping closer extending `sum_congr_ring` to swapped double sums. -/
syntax (name := calcRingSumTactic) "calc_ring_sum" : tactic

macro_rules
  | `(tactic| calc_ring_sum) => `(tactic|
      first
      | (sum_congr_ring; done)
      | (rw [Finset.sum_comm]; sum_congr_ring; done)
      | (simp_rw [← Finset.mul_sum]; sum_congr_ring; done)
      | (rw [Finset.sum_mul]; simp_rw [Finset.mul_sum];
         first | done | (refine Finset.sum_congr rfl (fun _ _ => ?_); sum_congr_ring; done))
      | (rw [← Finset.sum_mul]; simp_rw [← Finset.mul_sum];
         first | done | (refine Finset.sum_congr rfl (fun _ _ => ?_); sum_congr_ring; done))
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
    `∀ x ∈ s, ...`, `∀ x : α, ∀ j : κ, ...`, and 2-way conjunction predicates
    at the freshly introduced index `iFVar` and membership `hiFVar`. -/
def specializePointwiseHyps (iFVar hiFVar : Expr) : TacticM Unit :=
  withMainContext do
    let iType ← inferType iFVar
    let hiType ← inferType hiFVar
    let lctx ← getLCtx
    let mut ctxFVars : Array (Expr × Expr) := #[]
    let mut propHyps : Array (Name × Expr × Expr) := #[]
    for decl in lctx do
      if !decl.isImplementationDetail && !decl.userName.hasMacroScopes then
        let dTy ← instantiateMVars decl.type
        if !(← isProp dTy) && !dTy.isForall then
          ctxFVars := ctxFVars.push (decl.toExpr, dTy)
      if !decl.isImplementationDetail && decl.fvarId != iFVar.fvarId! && decl.fvarId != hiFVar.fvarId! then
        let ty ← instantiateMVars decl.type
        if ← isProp ty then
          propHyps := propHyps.push (decl.userName, decl.toExpr, ty)
          if !ty.isForall && !ty.isAppOfArity ``Eq 3 && !ty.isAppOfArity ``LE.le 4
              && !ty.isAppOfArity ``LT.lt 4 && !ty.isAppOfArity ``Not 1 then
            let tyWhnf ← whnf ty
            if tyWhnf.isAppOfArity ``And 2 then
              try
                let p1 := tyWhnf.getArg! 0
                let p2 := tyWhnf.getArg! 1
                let e1 ← mkAppM ``And.left #[decl.toExpr]
                let e2 ← mkAppM ``And.right #[decl.toExpr]
                let g1 ← getMainGoal
                let (_, g2) ← g1.note (decl.userName.appendAfter "_fst") e1 p1
                let (_, g3) ← g2.note (decl.userName.appendAfter "_snd") e2 p2
                replaceMainGoal [g3]
                propHyps := propHyps.push (decl.userName.appendAfter "_fst", e1, p1)
                propHyps := propHyps.push (decl.userName.appendAfter "_snd", e2, p2)
              catch _ => pure ()
    for (baseName, hypExpr, ty) in propHyps do
      if ty.isForall then
        let dom := ty.bindingDomain!
        if ← withoutModifyingState (isDefEq dom iType) then
          try
            let app1 ← mkAppM' hypExpr #[iFVar]
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
            let (_, goal') ← goal.note (baseName.appendAfter "_pt") val valTy
            replaceMainGoal [goal']
            if !valTy.isForall && !valTy.isAppOfArity ``Eq 3 && !valTy.isAppOfArity ``LE.le 4
                && !valTy.isAppOfArity ``LT.lt 4 && !valTy.isAppOfArity ``Not 1 then
              let valWhnf ← whnf valTy
              if valWhnf.isAppOfArity ``And 2 then
                try
                  let vp1 := valWhnf.getArg! 0
                  let vp2 := valWhnf.getArg! 1
                  let ve1 ← mkAppM ``And.left #[val]
                  let ve2 ← mkAppM ``And.right #[val]
                  let ga ← getMainGoal
                  let (_, gb) ← ga.note (baseName.appendAfter "_pt_fst") ve1 vp1
                  let (_, gc) ← gb.note (baseName.appendAfter "_pt_snd") ve2 vp2
                  replaceMainGoal [gc]
                catch _ => pure ()
            if valTy.isForall then
              let dom2 := valTy.bindingDomain!
              if !(← isProp dom2) then
                for (fvarExpr, fvarTy) in ctxFVars do
                  if fvarExpr.fvarId! != iFVar.fvarId! then
                    if ← withoutModifyingState (isDefEq dom2 fvarTy) then
                      let val2 ← mkAppM' val #[fvarExpr]
                      let val2Ty ← instantiateMVars (← inferType val2)
                      let g ← getMainGoal
                      let (_, g') ← g.note (baseName.appendAfter "_pt2") val2 val2Ty
                      replaceMainGoal [g']
          catch _ => pure ()

/-- `finset_nonneg`: discharges `0 ≤ ∑ i ∈ s, f i` (and nested double sums) by applying
    `Finset.sum_nonneg`, instantiating local universally quantified hypotheses, and closing
    pointwise obligations. -/
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
    | (solve_by_elim (maxDepth := 6) [mul_nonneg, mul_self_nonneg, add_nonneg, sq_nonneg, pow_nonneg, abs_nonneg, div_nonneg]; done)
    | (simp only [mul_assoc]; solve_by_elim (maxDepth := 6) [mul_nonneg, mul_self_nonneg, add_nonneg, sq_nonneg, pow_nonneg, abs_nonneg, div_nonneg]; done)
    | (finset_nonneg; done)
    | (aesop; done)))

/-- `finset_mono`: discharges `∑ i ∈ s, f i ≤ ∑ i ∈ s, g i` (and nested double sums) by applying
    `Finset.sum_le_sum`, instantiating local universally quantified hypotheses, and closing
    pointwise obligations. -/
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

/-- Unpack any WHNF-reducible 2-way conjunction hypotheses and `Matrix.rowStochastic`
    membership hypotheses in the main goal's local context. -/
def unpackContextAndHyps : TacticM Unit :=
  withMainContext do
    let env ← getEnv
    let hasSumRow := env.contains `Matrix.sum_row_of_mem_rowStochastic
    let hasNonnegRow := env.contains `Matrix.nonneg_of_mem_rowStochastic
    let lctx ← getLCtx
    for decl in lctx do
      if !decl.isImplementationDetail && !decl.userName.hasMacroScopes then
        let ty ← instantiateMVars decl.type
        if ← isProp ty then
          if hasSumRow then
            try
              let hSum ← mkAppM `Matrix.sum_row_of_mem_rowStochastic #[decl.toExpr]
              let hSumTy ← instantiateMVars (← inferType hSum)
              let g ← getMainGoal
              let (_, g') ← g.note (decl.userName.appendAfter "_rowsum") hSum hSumTy
              replaceMainGoal [g']
            catch _ => pure ()
          if hasNonnegRow then
            try
              let hNn ← mkAppM `Matrix.nonneg_of_mem_rowStochastic #[decl.toExpr]
              let hNnTy ← instantiateMVars (← inferType hNn)
              let g ← getMainGoal
              let (_, g') ← g.note (decl.userName.appendAfter "_nonneg") hNn hNnTy
              replaceMainGoal [g']
            catch _ => pure ()
          if !ty.isForall && !ty.isAppOfArity ``Eq 3 && !ty.isAppOfArity ``LE.le 4
              && !ty.isAppOfArity ``LT.lt 4 && !ty.isAppOfArity ``Not 1 then
            let tyWhnf ← whnf ty
            if tyWhnf.isAppOfArity ``And 2 then
              try
                let p1 := tyWhnf.getArg! 0
                let p2 := tyWhnf.getArg! 1
                let e1 ← mkAppM ``And.left #[decl.toExpr]
                let e2 ← mkAppM ``And.right #[decl.toExpr]
                let g1 ← getMainGoal
                let (_, g2) ← g1.note (decl.userName.appendAfter "_fst") e1 p1
                let (_, g3) ← g2.note (decl.userName.appendAfter "_snd") e2 p2
                replaceMainGoal [g3]
              catch _ => pure ()

/-- Instantiate universally quantified local hypotheses at matching local value variables. -/
def instantiateLocalForallEqsAndBounds : TacticM Unit :=
  withMainContext do
    let lctx ← getLCtx
    let mut valVars : Array (Expr × Expr) := #[]
    let mut forallHyps : Array (Name × Expr × Expr) := #[]
    for decl in lctx do
      if !decl.isImplementationDetail && !decl.userName.hasMacroScopes then
        let ty ← instantiateMVars decl.type
        if !(← isProp ty) && !ty.isForall then
          valVars := valVars.push (decl.toExpr, ty)
        else if (← isProp ty) && ty.isForall then
          forallHyps := forallHyps.push (decl.userName, decl.toExpr, ty)
    for (baseName, hypExpr, ty) in forallHyps do
      let dom1 := ty.bindingDomain!
      for (v1, v1Ty) in valVars do
        if ← withoutModifyingState (isDefEq dom1 v1Ty) then
          try
            let app1 ← mkAppM' hypExpr #[v1]
            let app1Ty ← instantiateMVars (← inferType app1)
            if !app1Ty.isForall then
              let g ← getMainGoal
              let (_, g') ← g.note (baseName.appendAfter "_inst") app1 app1Ty
              replaceMainGoal [g']
            if app1Ty.isForall then
              let dom2 := app1Ty.bindingDomain!
              for (v2, v2Ty) in valVars do
                if ← withoutModifyingState (isDefEq dom2 v2Ty) then
                  let app2 ← mkAppM' app1 #[v2]
                  let app2Ty ← instantiateMVars (← inferType app2)
                  if !app2Ty.isForall then
                    let g ← getMainGoal
                    let (_, g') ← g.note (baseName.appendAfter "_inst2") app2 app2Ty
                    replaceMainGoal [g']
          catch _ => pure ()

/-- `convex_comb`: discharges convex-combination, affine-interpolation, and simplex-bound obligations. -/
syntax (name := convexCombTactic) "convex_comb" : tactic

@[tactic convexCombTactic]
def evalConvexComb : Tactic := fun _ => do
  try evalTactic (← `(tactic| intros)) catch _ => pure ()
  unpackContextAndHyps
  unpackContextAndHyps
  instantiateLocalForallEqsAndBounds
  let linTerms : Array (TSyntax `term) ← withMainContext do
    let mut acc : Array (TSyntax `term) := #[]
    let lctx ← getLCtx
    for decl in lctx do
      if !decl.isImplementationDetail then
        let ty ← instantiateMVars decl.type
        if ty.isAppOfArity ``LE.le 4 then
          let lhs := ty.getArg! 2
          let rhs := ty.getArg! 3
          try
            let diff ← mkAppM ``HSub.hSub #[rhs, lhs]
            let stx ← PrettyPrinter.delab diff
            if acc.size < 8 then
              acc := acc.push stx
          catch _ => pure ()
    pure acc
  let mut prodTerms : Array (TSyntax `term) := #[]
  for i in [:linTerms.size] do
    for j in [i:linTerms.size] do
      if prodTerms.size < 20 then
        let ti := linTerms[i]!
        let tj := linTerms[j]!
        prodTerms := prodTerms.push (← `(mul_nonneg (by linarith : 0 ≤ $ti) (by linarith : 0 ≤ $tj)))
  evalTactic (← `(tactic|
    first
    | (ring; done)
    | linarith
    | (positivity; done)
    | nlinarith [$prodTerms,*]
    | (simp only [Finset.sum_add_distrib, Finset.sum_sub_distrib] at *
       simp only [← Finset.mul_sum, ← Finset.sum_mul] at *
       simp_all only [mul_one, one_mul, add_zero, zero_add]
       first
       | done
       | (ring; done)
       | linarith
       | nlinarith [$prodTerms,*])
    | (constructor <;> convex_comb; done)))

/-- `markov_row_sum`: discharges row-stochastic mass-preservation, Markov kernel normalization,
    convex mixtures of stochastic matrices, and Laplacian zero-row-sum obligations. -/
syntax (name := markovRowSumTactic) "markov_row_sum" : tactic

@[tactic markovRowSumTactic]
def evalMarkovRowSum : Tactic := fun _ => do
  try evalTactic (← `(tactic| intros)) catch _ => pure ()
  unpackContextAndHyps
  unpackContextAndHyps
  instantiateLocalForallEqsAndBounds
  let rowSumLemmas : Array (TSyntax `Lean.Parser.Tactic.simpLemma) ← withMainContext do
    let mut acc : Array (TSyntax `Lean.Parser.Tactic.simpLemma) := #[]
    let lctx ← getLCtx
    for decl in lctx do
      if !decl.isImplementationDetail then
        let ty ← instantiateMVars decl.type
        if (← isProp ty) && (ty.isForall || ty.isAppOfArity ``Eq 3) then
          if acc.size < 16 then
            let idStx := mkIdent decl.userName
            acc := acc.push (← `(Lean.Parser.Tactic.simpLemma| $idStx:ident))
    pure acc
  evalTactic (← `(tactic|
    first
    | (simp only [Finset.sum_add_distrib, Finset.sum_sub_distrib, ← Finset.mul_sum, ← Finset.sum_mul] at *
       simp_all only [mul_one, one_mul, add_zero, zero_add, sub_self]
       first | done | (ring; done) | linarith)
    | (dsimp only [Matrix.vecMul, Matrix.mulVec, Matrix.mul_apply, dotProduct]
       first
       | (rw [Finset.sum_comm]
          simp only [← Finset.mul_sum, ← Finset.sum_mul, mul_one, one_mul, $rowSumLemmas,*]
          first | done | (sum_congr_ring; done) | (ring; done))
       | (simp only [Finset.sum_add_distrib, Finset.sum_sub_distrib, ← Finset.mul_sum, ← Finset.sum_mul]
          try rw [Finset.sum_comm]
          simp only [← Finset.mul_sum, ← Finset.sum_mul, mul_one, one_mul, $rowSumLemmas,*]
          first | done | (sum_congr_ring; done) | (ring; done)))
    | (simp only [Matrix.vecMul_eq_sum, Matrix.mulVec_eq_sum, Pi.smul_apply, smul_eq_mul, Finset.sum_apply]
       rw [Finset.sum_comm]
       simp only [← Finset.mul_sum, ← Finset.sum_mul, mul_one, one_mul, $rowSumLemmas,*]
       first | done | (sum_congr_ring; done) | (ring; done))
    | (calc_ring_sum; done)))

/-- `matrix_pos`: discharges entrywise non-negativity and strict positivity of matrices,
    transition kernels, matrix products, and finite concrete `Fin n` matrices. -/
syntax (name := matrixPosTactic) "matrix_pos" : tactic

@[tactic matrixPosTactic]
def evalMatrixPos : Tactic := fun _ => do
  try evalTactic (← `(tactic| intros)) catch _ => pure ()
  unpackContextAndHyps
  unpackContextAndHyps
  instantiateLocalForallEqsAndBounds
  evalTactic (← `(tactic|
    first
    | assumption
    | (positivity; done)
    | linarith
    | omega
    | (finset_nonneg; done)
    | (dsimp only [Matrix.mul_apply, Matrix.vecMul, Matrix.mulVec, dotProduct, Matrix.add_apply, Matrix.smul_apply, smul_eq_mul, Matrix.of_apply]
       first
       | (positivity; done)
       | (finset_nonneg; done)
       | linarith
       | nlinarith
       | (fin_cases ‹_› <;> first | (norm_num; done) | (decide; done) | (simp; done) | (fin_cases ‹_› <;> first | (norm_num; done) | (decide; done) | (simp; done))))
    | (fin_cases ‹_› <;> first | (norm_num; done) | (decide; done) | (simp; done) | (fin_cases ‹_› <;> first | (norm_num; done) | (decide; done) | (simp; done)))))

-- ============================================================================
-- Sup-Norm Scaling, Quotient Normalization, Grid Cardinality & Doeblin Lemmas
-- ============================================================================

/-- Positive homogeneity of `Finset.sup'` over `ℝ`: scaling every entry by `c ≥ 0`
    scales the finite supremum by `c`. -/
theorem sup'_const_mul_of_nonneg {ι : Type*} (s : Finset ι) (hs : s.Nonempty)
    (c : ℝ) (hc : 0 ≤ c) (f : ι → ℝ) :
    s.sup' hs (fun i => c * f i) = c * s.sup' hs f := by
  apply le_antisymm
  · exact Finset.sup'_le hs _ fun i hi =>
      mul_le_mul_of_nonneg_left (Finset.le_sup' f hi) hc
  · rcases eq_or_lt_of_le hc with rfl | hc_pos
    · simp [Finset.sup'_const hs]
    · rw [← le_div_iff₀' hc_pos]
      refine Finset.sup'_le hs _ fun i hi => ?_
      have hle : c * f i ≤ s.sup' hs (fun j => c * f j) :=
        Finset.le_sup' (fun j => c * f j) hi
      exact (le_div_iff₀' hc_pos).mpr hle

/-- `sup_norm_scale`: pulls non-negative scalar multipliers out of `Finset.sup'` via
    `sup'_const_mul_of_nonneg` and closes sup-norm contraction/equality obligations. -/
syntax (name := supNormScaleTactic) "sup_norm_scale" : tactic

macro_rules
  | `(tactic| sup_norm_scale) => `(tactic|
      (simp only [sup'_const_mul_of_nonneg _ _ _ (by first | assumption | positivity | linarith)];
       first | done | rfl | (ring; done) | linarith | gcongr_pos))

/-- `deriv_quot_ring`: clears nonzero denominators after pre-folding `1 - a / Z` and
    common-denominator sums/differences so quotient derivative and simplex-ratio
    identities close without expanding polynomial denominators inside `( ... )⁻¹`. -/
syntax (name := derivQuotRingTactic) "deriv_quot_ring" : tactic

macro_rules
  | `(tactic| deriv_quot_ring) => `(tactic|
      (try simp only [div_add_div_same, div_sub_div_same]
       field_simp
       ring; done))

/-- Cardinality of the half-open index slice `{i : Fin N | a ≤ i.val ∧ i.val < b}`
    equals `min b N - a`. -/
theorem fin_card_filter_Ico (N a b : ℕ) :
    (Finset.univ.filter (fun i : Fin N => a ≤ i.val ∧ i.val < b)).card = min b N - a := by
  rw [← Nat.card_Ico a (min b N)]
  apply Finset.card_bij (fun (i : Fin N) _ => i.val)
  · intro i hi
    simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hi
    simp only [Finset.mem_Ico]
    exact ⟨hi.1, lt_min hi.2 i.isLt⟩
  · intro i₁ _ i₂ _ hval
    exact Fin.ext hval
  · intro m hm
    simp only [Finset.mem_Ico] at hm
    refine ⟨⟨m, lt_of_lt_of_le hm.2 (min_le_right b N)⟩, ?_, rfl⟩
    simp only [Finset.mem_filter, Finset.mem_univ, true_and]
    exact ⟨hm.1, lt_of_lt_of_le hm.2 (min_le_left b N)⟩

/-- Floor-division bound on `S.natAbs` from a real absolute-value bound `|(S : ℝ)| ≤ n / k`. -/
theorem natAbs_le_div_of_cast_abs_le (S : ℤ) (n k : ℕ) (hk : 0 < k)
    (h : |(S : ℝ)| ≤ (n : ℝ) / (k : ℝ)) :
    S.natAbs ≤ n / k := by
  have hk_r : (0 : ℝ) < (k : ℝ) := Nat.cast_pos.mpr hk
  have habs_cast : ((S.natAbs : ℕ) : ℝ) = |(S : ℝ)| := by
    rw [← Int.cast_natCast]
    push_cast
    rfl
  have hmul_r : ((S.natAbs * k : ℕ) : ℝ) ≤ (n : ℝ) := by
    push_cast
    rw [habs_cast]
    exact (le_div_iff₀ hk_r).mp h
  have hmul_n : S.natAbs * k ≤ n := Nat.cast_le.mp hmul_r
  exact (Nat.le_div_iff_mul_le hk).mpr hmul_n

/-- Quantitative Doeblin $\ell^1$ contraction on zero-sum vectors: if every entry of row-stochastic
    `M : Matrix ι κ ℝ` satisfies `δ ≤ M i j`, then `∑ j, |∑ i, d i * M i j| ≤ (1 - |κ| * δ) * ∑ i, |d i|`
    whenever `∑ i, d i = 0`. -/
theorem zero_sum_vecMul_l1_le_of_entry_floor {ι κ : Type*} [Fintype ι] [Fintype κ]
    (M : Matrix ι κ ℝ) (hrow : ∀ i, ∑ j, M i j = 1)
    (δ : ℝ) (hM : ∀ i j, δ ≤ M i j)
    (d : ι → ℝ) (hd0 : ∑ i, d i = 0) :
    ∑ j, |∑ i, d i * M i j| ≤ (1 - (Fintype.card κ : ℝ) * δ) * ∑ i, |d i| := by
  have hshift : ∀ j : κ, ∑ i, d i * M i j = ∑ i, d i * (M i j - δ) := fun j => by
    have h1 : ∑ i, d i * (M i j - δ) = (∑ i, d i * M i j) - (∑ i, d i) * δ := by
      have step : ∑ i, d i * (M i j - δ) = ∑ i, (d i * M i j - d i * δ) := by sum_congr_ring
      rw [step, Finset.sum_sub_distrib, ← Finset.sum_mul]
    rw [h1, hd0, zero_mul, sub_zero]
  calc ∑ j, |∑ i, d i * M i j|
      = ∑ j, |∑ i, d i * (M i j - δ)| :=
        Finset.sum_congr rfl fun j _ => by rw [hshift j]
    _ ≤ ∑ j, ∑ i, |d i| * (M i j - δ) := by
        refine Finset.sum_le_sum fun j _ =>
          (Finset.abs_sum_le_sum_abs _ _).trans (Finset.sum_le_sum fun i _ => ?_)
        rw [abs_mul, abs_of_nonneg (sub_nonneg.mpr (hM i j))]
    _ = ∑ i, |d i| * (∑ j, (M i j - δ)) := by
        rw [Finset.sum_comm]
        exact Finset.sum_congr rfl fun i _ => (Finset.mul_sum _ _ _).symm
    _ = (1 - (Fintype.card κ : ℝ) * δ) * ∑ i, |d i| := by
        have hcol : ∀ i : ι, ∑ j : κ, (M i j - δ) = 1 - (Fintype.card κ : ℝ) * δ := fun i => by
          rw [Finset.sum_sub_distrib, hrow i, Finset.sum_const, Finset.card_univ, nsmul_eq_mul]
        simp only [hcol]
        rw [← Finset.sum_mul, mul_comm]

end AltProof.Closers
