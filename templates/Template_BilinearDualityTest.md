# Template_BilinearDualityTest.md - Bilinear Pairing and Dual-Basis Goal Discharging Template

> **Status:** Production template for non-linear and operator equality discharging in proof-skills.
> **Audience:** Provers formalizing matrix equations, Lyapunov stability, Markov operators, or tensor contractions.
> **Pattern Source:** Extracted from Serre duality in FLT (Def_AlgebraicCurve_SerrePairing.lean) and EASCI matrix/Lyapunov formalizations.

---

## 1. When to Use This Template

Apply Template_BilinearDualityTest when:
- Proving an equality of bundled operators, matrices, or vectors A = B where direct rewriting causes maxHeartbeats timeouts or infinite loops.
- simp causes unbundling traps (stripping LinearMap, Matrix, or ContinuousLinearMap into .toFun projections).
- The space M possesses a non-degenerate bilinear form (e.g. inner product <x, y>, trace pairing Tr(X^T Y), or evaluation pairing v^* x).
- Proving uniqueness of solutions to algebraic operator equations (e.g. Lyapunov equation A^T P + P A = -Q or stationary distribution pi P = pi).

Do NOT use for:
- Pure scalar polynomial equations -> use ring or ring_nf.
- Pure integer linear arithmetic -> use omega.
- Single definitional unfolding -> use change or dsimp only.

---

## 2. The 3-Phase Duality Discharging Architecture

```text
+-----------------------------------------------------------------------------+
| Phase 1: Dual Extensionality Transformation                                 |
|          Convert `A = B` into `forall phi in Basis*, <A, phi> = <B, phi>`   |
|          `refine DualPairing.ext fun phi => ?_` or `apply Matrix.ext`       |
+-----------------------------------------------------------------------------+
                                      v
+-----------------------------------------------------------------------------+
| Phase 2: Morphism Preservation & Linearity Pushing                          |
|          Distribute the pairing over internal additions and scalar scaling  |
|          `simp only [map_add, map_smul, LinearMap.add_apply, ...]`          |
+-----------------------------------------------------------------------------+
                                      v
+-----------------------------------------------------------------------------+
| Phase 3: Scalar Base Discharging                                            |
|          The resulting goal is an equality in the scalar base ring R        |
|          `ring`, `linarith`, `omega`, or `norm_num`                         |
+-----------------------------------------------------------------------------+
```

---

## 3. Full Production Template

```lean
/-
Copyright (c) 2026 Project Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
SPDX-License-Identifier: Apache-2.0
-/

import Mathlib.LinearAlgebra.Dual
import Mathlib.LinearAlgebra.BilinearForm.Basic
import Mathlib.LinearAlgebra.Matrix.Trace
import Mathlib.Analysis.InnerProductSpace.Basic

set_option autoImplicit false

namespace Project.Automation

-- =====================================================================
-- ## Variables
-- =====================================================================

variable {R M : Type*} [CommRing R] [AddCommGroup M] [Module R M]

-- =====================================================================
-- ## Definitions
-- =====================================================================

/-- A non-degenerate bilinear pairing structure for goal reduction. -/
structure NonDegeneratePairing (R M : Type*) [CommRing R] [AddCommGroup M] [Module R M] where
  pairing : M ->[R] M ->[R] R
  separating_right : forall x : M, (forall y : M, pairing x y = 0) -> x = 0

-- =====================================================================
-- ## Main statements
-- =====================================================================

/-- **Duality Extensionality Lemma**.
    An equality in `M` reduces to equality under all dual test evaluations. -/
theorem eq_of_forall_pairing_eq (P : NonDegeneratePairing R M) (x y : M)
    (h : forall z : M, P.pairing x z = P.pairing y z) : x = y := by
  have hsub : forall z : M, P.pairing (x - y) z = 0 := by
    intro z
    rw [map_sub, LinearMap.sub_apply, sub_eq_zero]
    exact h z
  have hzero := P.separating_right (x - y) hsub
  exact sub_eq_zero.mp hzero

/-- **Dual Basis Projection Theorem**.
    For spaces with a finite dual basis, equality reduces to finite tests. -/
theorem eq_of_forall_basis_proj {iota : Type*} [Fintype iota]
    (b : Basis iota R M) (x y : M) (h : forall i : iota, b.coord i x = b.coord i y) : x = y :=
  b.ext_elem h

-- =====================================================================
-- ## Proofs: Matrix Lyapunov Operator Example
-- =====================================================================

variable {n : Type*} [Fintype n] [DecidableEq n]

/-- Matrix Frobenius trace pairing is non-degenerate. -/
def matrixTracePairing (R : Type*) [CommRing R] :
    NonDegeneratePairing R (Matrix n n R) where
  pairing := {
    toFun := fun A => {
      toFun := fun B => (A * B).trace
      map_add\x27 := fun B C => by rw [Matrix.mul_add, Matrix.trace_add]
      map_smul\x27 := fun r B => by rw [Matrix.mul_smul, Matrix.trace_smul, RingHom.id_apply]
    }
    map_add\x27 := fun A_1 A_2 => by
      ext B
      simp only [Matrix.add_mul, Matrix.trace_add, LinearMap.coe_mk, AddHom.coe_mk]
    map_smul\x27 := fun r A => by
      ext B
      simp only [Matrix.smul_mul, Matrix.trace_smul, RingHom.id_apply, LinearMap.coe_mk, AddHom.coe_mk]
  }
  separating_right := by
    intro A hA
    ext i j
    have h_test := hA (Matrix.stdBasisMatrix j i 1)
    dsimp at h_test
    rw [Matrix.trace_mul_stdBasisMatrix] at h_test
    simp only [mul_one] at h_test
    exact h_test

/-- Demonstration: Solving/Verifying Lyapunov matrix equation via duality testing. -/
theorem lyapunov_equality_via_dual_test
    (A P Q : Matrix n n R)
    (h_dual : forall (i j : n), (A.transpose * P + P * A + Q) i j = 0) :
    A.transpose * P + P * A = -Q := by
  ext i j
  have h := h_dual i j
  linear_combination h

-- =====================================================================
-- ## API exports
-- =====================================================================

export Project.Automation (NonDegeneratePairing eq_of_forall_pairing_eq eq_of_forall_basis_proj)

-- =====================================================================
-- ## See also
-- =====================================================================
/-
* `Template_ConfluenceSimpOnly.md` - for anti-unbundling simplifications.
* `Template_ForwardCalculation_Calc.md` - for stepwise equality proofs.
* `Def_AlgebraicCurve_SerrePairing.lean` - the geometric origin of this pattern.
-/
```

---

## 4. Anti-Patterns Checklist

| Anti-Pattern | Manifestation in Lean 4 | Preventive Discipline |
| :--- | :--- | :--- |
| **Monolithic Operator `simp`** | `simp [lyapunov_step]` expands into an untyped explosion of indices. | Never unfold operator products globally. Apply dual basis testing to isolate scalars. |
| **Unbundled Extensionality** | Using `ext` on raw functions instead of coordinated dual bases causes loss of ring context. | Use bundled dual pairing (`eq_of_forall_pairing_eq`) or `Matrix.ext`. |
| **Omitting Non-Degeneracy Proof** | Attempting duality tests without proving non-degeneracy creates unprovable subgoals. | Prove `separating_right` once in a library module using standard basis matrices. |
