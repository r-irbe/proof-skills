# Template_RegulatorDeterminant - P-adic Regulators, Volume Determinants & Non-Singular Lattices

Use this template for **p-adic regulator determinants**, **lattice volume invariance**,
**non-singular Markov equilibrium phase space**, and **Hadamard multilinear volume bounds**.

In arithmetic geometry and Iwasawa theory (FLT), the p-adic regulator R_p(E/K) of an elliptic
curve or number field unit group is the determinant of the p-adic height pairing matrix.
Non-vanishing of the regulator (R_p != 0) certifies that the lattice of global rational points
or units is non-degenerate and spans full rank, establishing non-degeneracy in p-adic BSD conjectures.

In stochastic consensus and multi-agent dynamics, this structure transfers directly to:
* 2D generator vectors u = (u1, u2) and v = (v1, v2) spanning Markov flow lattices.
* Oriented volume determinants R(u, v) = u1 * v2 - u2 * v1 measuring ergodic mixing volume.
* Alternating skew-symmetry R(v, u) = -R(u, v) and vanishing on identical vectors R(u, u) = 0.
* Multilinear scaling and unimodular shear invariance R(u + c * v, v) = R(u, v).
* Certified non-singularity |R(u, v)| >= Vmin > 0 preventing dimensional collapse.
* Hadamard volume bounds |R(u, v)| <= 2 * B^2 under bounded generator norms.

## Main results
* `RegulatorLattice2` - 2D generator vectors (u1, u2) and (v1, v2)
* `regulatorDet` - oriented volume determinant R(u, v) = u1 * v2 - u2 * v1
* `regulator_det_self` - vanishing on identical generators R(u, u) = 0
* `regulator_det_skew` - alternating skew-symmetry R(v, u) = -R(u, v)
* `regulator_det_scale_left` - left multilinear scalar scaling
* `regulator_det_scale_right` - right multilinear scalar scaling
* `regulator_shear_invariance` - unimodular shear invariance
* `IsNonSingularRegulator` - certified volume lower bound |R| >= Vmin > 0
* `nonsingular_regulator_ne_zero` - non-singularity implies R != 0
* `hadamard_volume_bound` - Hadamard product bound |R| <= 2 * B^2

## References
* FLT: `Regulators/PadicRegulator.lean`, `Lattices/VolumeDeterminant.lean`
* Schneider, P. (1982), *p-adic height pairings II*, Inventiones Mathematicae 79, 329-374
* Mazur, B., Tate, J., Teitelbaum, J. (1986), *On p-adic analogues of the conjectures of Birch and Swinnerton-Dyer*, Invent. Math. 84, 1-48

## Tags
template, p-adic-regulator, volume-determinant, unimodular-shear, hadamard-bound, non-singular-lattice, markov-flow

```lean
/-
Copyright (c) 2026 <Project> Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
SPDX-License-Identifier: Apache-2.0
-/

import Mathlib.Data.Real.Basic
import Mathlib.Tactic

set_option autoImplicit false

namespace <Project>.ProofSkills.RegulatorDeterminant

/-- 2D generator vectors spanning a Markov equilibrium flow lattice. -/
structure RegulatorLattice2 where
  u1 : Real
  u2 : Real
  v1 : Real
  v2 : Real

/-- Oriented volume determinant of the regulator lattice: R(u, v) = u1 * v2 - u2 * v1. -/
def regulatorDet (L : RegulatorLattice2) : Real :=
  L.u1 * L.v2 - L.u2 * L.v1

/-- Vanishing of the regulator determinant for identical generator vectors. -/
theorem regulator_det_self (u1 u2 : Real) :
    regulatorDet { u1 := u1, u2 := u2, v1 := u1, v2 := u2 } = 0 := by
  unfold regulatorDet
  ring

/-- Alternating skew-symmetry: interchanging generators negates the volume determinant. -/
theorem regulator_det_skew (u1 u2 v1 v2 : Real) :
    regulatorDet { u1 := v1, u2 := v2, v1 := u1, v2 := u2 } =
      - regulatorDet { u1 := u1, u2 := u2, v1 := v1, v2 := v2 } := by
  unfold regulatorDet
  ring

/-- Left scalar linearity: scaling u scales the volume determinant. -/
theorem regulator_det_scale_left (c u1 u2 v1 v2 : Real) :
    regulatorDet { u1 := c * u1, u2 := c * u2, v1 := v1, v2 := v2 } =
      c * regulatorDet { u1 := u1, u2 := u2, v1 := v1, v2 := v2 } := by
  unfold regulatorDet
  ring

/-- Right scalar linearity: scaling v scales the volume determinant. -/
theorem regulator_det_scale_right (c u1 u2 v1 v2 : Real) :
    regulatorDet { u1 := u1, u2 := u2, v1 := c * v1, v2 := c * v2 } =
      c * regulatorDet { u1 := u1, u2 := u2, v1 := v1, v2 := v2 } := by
  unfold regulatorDet
  ring

/-- Unimodular shear invariance: adding a multiple of v to u preserves volume. -/
theorem regulator_shear_invariance (u1 u2 v1 v2 c : Real) :
    regulatorDet { u1 := u1 + c * v1, u2 := u2 + c * v2, v1 := v1, v2 := v2 } =
      regulatorDet { u1 := u1, u2 := u2, v1 := v1, v2 := v2 } := by
  unfold regulatorDet
  ring

/-- Non-singular regulator condition: volume bounded away from zero by certified margin. -/
def IsNonSingularRegulator (L : RegulatorLattice2) (Vmin : Real) : Prop :=
  0 < Vmin /\ Vmin <= |regulatorDet L|

/-- Non-singularity implies non-vanishing of the regulator determinant. -/
theorem nonsingular_regulator_ne_zero (L : RegulatorLattice2) (Vmin : Real)
    (h : IsNonSingularRegulator L Vmin) :
    regulatorDet L != 0 := by
  intro h_zero
  unfold IsNonSingularRegulator at h
  have h_abs : |regulatorDet L| = 0 := by rw [h_zero, abs_zero]
  have h_contr : 0 < (0 : Real) := by
    calc 0 < Vmin := h.1
    _ <= |regulatorDet L| := h.2
    _ = 0 := h_abs
  exact lt_irrefl 0 h_contr

/-- Hadamard volume bound: if generators are bounded by B, volume is bounded by 2 B^2. -/
theorem hadamard_volume_bound (L : RegulatorLattice2) (B : Real)
    (hu1 : |L.u1| <= B) (hu2 : |L.u2| <= B)
    (hv1 : |L.v1| <= B) (hv2 : |L.v2| <= B)
    (hB : 0 <= B) :
    |regulatorDet L| <= 2 * B^2 := by
  unfold regulatorDet
  have h_tri : |L.u1 * L.v2 - L.u2 * L.v1| <= |L.u1 * L.v2| + |L.u2 * L.v1| := abs_sub _ _
  have h_m1 : |L.u1 * L.v2| = |L.u1| * |L.v2| := abs_mul _ _
  have h_m2 : |L.u2 * L.v1| = |L.u2| * |L.v1| := abs_mul _ _
  have h_term1 : |L.u1| * |L.v2| <= B * B := mul_le_mul hu1 hv2 (abs_nonneg _) hB
  have h_term2 : |L.u2| * |L.v1| <= B * B := mul_le_mul hu2 hv1 (abs_nonneg _) hB
  calc |L.u1 * L.v2 - L.u2 * L.v1|
    _ <= |L.u1 * L.v2| + |L.u2 * L.v1| := h_tri
    _ = |L.u1| * |L.v2| + |L.u2| * |L.v1| := by rw [h_m1, h_m2]
    _ <= B * B + B * B := add_le_add h_term1 h_term2
    _ = 2 * B^2 := by ring

end <Project>.ProofSkills.RegulatorDeterminant
```
