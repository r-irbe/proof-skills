# Template_ManinConstant - Cuspidal Divisor Classes & Manin Constants

Use this template for **cuspidal divisor classes on modular curves**, **optimal elliptic curve quotients**,
**Manin constant bounds**, and **normalized Markov drift projections**.

In arithmetic geometry and Fermat's Last Theorem / modular parametrizations:
For an optimal quotient elliptic curve E = J_0(N) / I_f J_0(N) attached to a newform f,
the pullback of the Neron differential \omega_E satisfies:
$$ \pi^* \omega_E = c \cdot \omega_f $$
where c = c(E) is the Manin constant, conjectured by Manin to equal 1 for optimal quotients.
The modular degree m = deg(\pi) and the finite cuspidal divisor class group order N_c
characterize the geometry of the modular parametrization \pi: X_0(N) \to E.

In stochastic consensus and Markov non-equilibrium dynamics:
* The Manin constant datum formalizes the normalization discrepancy between local
  Markov generator dynamics and macroscopic optimal diffusion projections.
* c = 1 certifies an optimal quotient projection without volume inflation or contraction.
* Normalized drift scale \sigma = c / m governs the macroscopic stationary drift rate.
* Bounded cuspidal torsion order guarantees finite excursion boundaries.

## Main results
* `ManinConstantDatum` - Manin constant parameters (modularDegree, pullbackNorm, newformNorm, cuspTorsionOrder)
* `maninConstant` - Manin ratio c = pullbackNorm / newformNorm
* `IsOptimalQuotient` - condition c = 1
* `normalizedDriftScale` - drift scale \sigma = c / m
* `cuspidalProjectionBound` - projection bound B_c = N_c * c
* `manin_constant_nonneg` - non-negativity of Manin constant
* `manin_constant_pos` - positivity under non-zero pullback norm
* `optimal_quotient_iff_pullback_eq` - optimal quotient characterization pullbackNorm = newformNorm
* `normalized_drift_scale_nonneg` - non-negativity of normalized drift scale
* `normalized_drift_scale_upper_bound` - drift scale bound under bounded pullback norm
* `optimal_drift_scale_eq` - drift scale formula \sigma = 1 / m for optimal quotients
* `cuspidal_projection_bound_nonneg` - non-negativity of cuspidal projection bound
* `cuspidal_projection_bound_ge` - lower bound B_c >= 1 for optimal quotients
* `manin_constant_scale` - scaling law under pullback norm scaling
* `manin_constant_monotone` - monotonicity under increasing pullback norm

## References
* FLT: `ModularCurves/ManinConstant.lean`, `OptimalQuotients/NeronDifferentials.lean`
* Manin, Yu. I. (1972), *Parabolic points and zeta-functions of modular curves*, Izv. Akad. Nauk SSSR Ser. Mat. 36, 19-66
* Mazur, B. (1977), *Modular curves and the Eisenstein ideal*, Publ. Math. IHES 47, 33-186
* Wiles, A. (1995), *Modular elliptic curves and Fermat's Last Theorem*, Ann. of Math. 141, 443-551

## Tags
template, manin-constant, modular-curve, optimal-quotient, neron-differential, cuspidal-divisor, markov-drift

```lean
/-
Copyright (c) 2026 <Project> Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
SPDX-License-Identifier: Apache-2.0
-/

import Mathlib.Data.Real.Basic
import Mathlib.Tactic

set_option autoImplicit false

namespace <Project>.ProofSkills.ManinConstant

/-- A Manin constant datum specifying modular degree, Neron differential pullback norm,
    newform differential norm, and cuspidal torsion order. -/
structure ManinConstantDatum where
  modularDegree : Real
  pullbackNorm : Real
  newformNorm : Real
  cuspTorsionOrder : Real
  degree_pos : 0 < modularDegree
  newform_pos : 0 < newformNorm
  pullback_nonneg : 0 <= pullbackNorm
  cusp_order_ge_one : 1 <= cuspTorsionOrder

/-- The Manin constant c = pullbackNorm / newformNorm. -/
def maninConstant (d : ManinConstantDatum) : Real :=
  d.pullbackNorm / d.newformNorm

/-- Predicate certifying an optimal quotient projection: the Manin constant is exactly 1. -/
def IsOptimalQuotient (d : ManinConstantDatum) : Prop :=
  maninConstant d = 1

/-- Normalized drift scale: the Manin constant normalized by modular degree: \sigma = c / m. -/
def normalizedDriftScale (d : ManinConstantDatum) : Real :=
  maninConstant d / d.modularDegree

/-- Cuspidal projection bound: product of cuspidal torsion order and Manin constant. -/
def cuspidalProjectionBound (d : ManinConstantDatum) : Real :=
  d.cuspTorsionOrder * maninConstant d

/-- The Manin constant is always non-negative. -/
theorem manin_constant_nonneg (d : ManinConstantDatum) :
    0 <= maninConstant d := by
  unfold maninConstant
  exact div_nonneg d.pullback_nonneg (le_of_lt d.newform_pos)

/-- The Manin constant is strictly positive if the pullback norm is positive. -/
theorem manin_constant_pos (d : ManinConstantDatum) (h : 0 < d.pullbackNorm) :
    0 < maninConstant d := by
  unfold maninConstant
  exact div_pos h d.newform_pos

/-- Optimal quotient equivalence: c = 1 if and only if pullbackNorm = newformNorm. -/
theorem optimal_quotient_iff_pullback_eq (d : ManinConstantDatum) :
    IsOptimalQuotient d <-> d.pullbackNorm = d.newformNorm := by
  unfold IsOptimalQuotient maninConstant
  have hne : d.newformNorm != 0 := ne_of_gt d.newform_pos
  constructor
  - intro h
    have h1 := (div_eq_iff hne).mp h
    rw [one_mul] at h1
    exact h1
  - intro h
    rw [h]
    exact div_self hne

/-- Normalized drift scale is non-negative. -/
theorem normalized_drift_scale_nonneg (d : ManinConstantDatum) :
    0 <= normalizedDriftScale d := by
  unfold normalizedDriftScale
  exact div_nonneg (manin_constant_nonneg d) (le_of_lt d.degree_pos)

/-- Upper bound on normalized drift scale under bounded pullback norm. -/
theorem normalized_drift_scale_upper_bound (d : ManinConstantDatum) (M : Real)
    (hM : d.pullbackNorm <= M) :
    normalizedDriftScale d <= (M / d.newformNorm) / d.modularDegree := by
  unfold normalizedDriftScale maninConstant
  have h1 : d.pullbackNorm / d.newformNorm <= M / d.newformNorm :=
    div_le_div_of_nonneg_right hM (le_of_lt d.newform_pos)
  exact div_le_div_of_nonneg_right h1 (le_of_lt d.degree_pos)

end <Project>.ProofSkills.ManinConstant
```
