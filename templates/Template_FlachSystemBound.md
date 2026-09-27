# Template_FlachSystemBound - Flach Euler Systems, Symmetric Square Bounds & Multi-Scale Value Stability

Use this template for **Flach Euler systems**, **symmetric square Galois representation bounds**,
**policy curvature deformation bounds**, and **multi-scale value stability**.

In arithmetic geometry and Fermat's Last Theorem (FLT):
Let f in S_2(Gamma_0(N)) be a normalized Hecke eigenform and rho_f its p-adic Galois representation.
The symmetric square representation Sym^2(rho_f) = Ad^0(rho_f) + Q_p governs the deformation theory
of rho_f and the adjoint Selmer group. Matthias Flach constructed an Euler system of cohomology classes
in H^1(Q, Sym^2(rho_f)) derived from modular units on modular curves. The non-vanishing of Flach's classes
annihilates the Selmer group of the symmetric square and bounds its order in terms of the special
L-value L(Sym^2(f), 2), which relates directly to the Petersson inner product <f, f> and the modular
degree of the elliptic curve parametrization.

In reinforcement learning and multi-scale policy evaluation:
* Sym^2 represents quadratic value curvature and second-order policy variance matrices.
* The Flach symmetric power bound guarantees that policy advantage variance and value curvature
  remain strictly bounded under multi-horizon trajectory exploration.
* The Flach Euler system bound constrains the symmetric power Selmer dimension, ensuring that policy
  evaluations remain stable within certified temporal discount envelopes.
* Multi-horizon exploration scaling guarantees monotone preservation of curvature bounds.

## Main results
* `FlachSymmetricPowerDatum` - datum (symPowerSelmerDim, symPowerBound, policyCurvatureTolerance, symDiscountFactor, symHorizonSteps)
* `symPowerDefect` - defect between Flach symmetric power bound and observed Selmer dimension
* `normalizedSymPowerRatio` - normalized ratio of Selmer dimension to Flach bound
* `discountedSymPowerBound` - discounted bound scaled by temporal discount factor
* `symPowerSlack` - slack between tolerance-scaled bound and Selmer dimension
* `multiHorizonSymPowerBound` - multi-horizon bound accounting for exploration steps
* `IsSymPowerBounded` - condition that Selmer dimension is bounded by Flach bound
* `IsZeroSymPowerSelmer` - condition of completely rigid unramified state (dimension 0)
* `IsSymPowerCurvatureConvergent` - curvature variation is within policy tolerance
* `sym_power_defect_nonneg_of_bounded` - defect is non-negative for Flach-bounded systems
* `sym_power_bounded_iff_defect_nonneg` - boundedness is equivalent to non-negative defect
* `normalized_sym_power_ratio_nonneg` - normalized ratio is non-negative
* `normalized_sym_power_ratio_le_one_of_bounded` - normalized ratio is at most 1 for bounded systems
* `zero_sym_power_implies_bounded` - zero Selmer dimension implies Flach-bounded system
* `zero_sym_power_implies_defect_eq_bound` - zero Selmer dimension has defect equal to bound
* `zero_sym_power_implies_ratio_zero` - zero Selmer dimension has normalized ratio equal to 0
* `discounted_sym_power_bound_pos` - discounted bound is strictly positive
* `discounted_sym_power_bound_le_bound` - discounted bound is bounded by full Flach bound
* `sym_power_curvature_convergent_iff_slack_nonneg` - curvature convergence equivalent to non-negative slack
* `sym_power_slack_nonneg_of_convergent` - slack is non-negative for convergent systems
* `sym_power_dim_reconstruction` - Selmer dimension reconstructed from ratio and bound
* `multi_horizon_sym_power_bound_pos` - multi-horizon bound is strictly positive
* `discounted_sym_power_bound_monotone` - discounted bound is monotone in discount factor
* `sym_power_slack_monotone_tolerance` - slack is monotone in curvature tolerance
* `sym_power_defect_monotone_bound` - defect is monotone in Flach bound
* `multi_horizon_sym_power_monotone_steps` - multi-horizon bound is monotone in horizon steps

## References
* FLT: `Definitions/Def_GalRep_FlachEulerSystem.lean`, `Definitions/Def_GalRep_AdjointSelmerGroup.lean`
* Flach, M. (1992), *A finiteness theorem for the symmetric square of an elliptic curve*, Invent. Math. 109, 307-327
* Wiles, A. (1995), *Modular elliptic curves and Fermat's Last Theorem*, Ann. of Math. 141(3), 443-551

## Tags
template, flach-system, euler-system, symmetric-square, adjoint-selmer, curvature-bound, value-stability

```lean
/-
Copyright (c) 2026 <Project> Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
SPDX-License-Identifier: Apache-2.0
-/

import Mathlib.Data.Real.Basic
import Mathlib.Tactic

set_option autoImplicit false
set_option linter.unusedVariables false
set_option linter.unusedSectionVars false
set_option linter.unusedSimpArgs false

noncomputable section

namespace <Project>.ProofSkills.FlachSystemBound

/-- Datum specifying symmetric square Selmer dimension, Flach bound, policy curvature tolerance,
    discount factor, and horizon exploration steps. -/
structure FlachSymmetricPowerDatum where
  symPowerSelmerDim : Real
  symPowerBound : Real
  policyCurvatureTolerance : Real
  symDiscountFactor : Real
  symHorizonSteps : Real
  dim_nonneg : 0 <= symPowerSelmerDim
  bound_pos : 0 < symPowerBound
  tolerance_pos : 0 < policyCurvatureTolerance
  discount_pos : 0 < symDiscountFactor
  discount_le_one : symDiscountFactor <= 1
  horizon_pos : 0 < symHorizonSteps

/-- Defect between Flach symmetric power bound and observed Selmer dimension. -/
def symPowerDefect (d : FlachSymmetricPowerDatum) : Real :=
  d.symPowerBound - d.symPowerSelmerDim

/-- Normalized ratio of symmetric square Selmer dimension to Flach bound. -/
def normalizedSymPowerRatio (d : FlachSymmetricPowerDatum) : Real :=
  d.symPowerSelmerDim / d.symPowerBound

/-- Discounted symmetric power bound scaled by temporal discount factor. -/
def discountedSymPowerBound (d : FlachSymmetricPowerDatum) : Real :=
  d.symPowerBound * d.symDiscountFactor

/-- Symmetric power slack between tolerance-scaled bound and Selmer dimension. -/
def symPowerSlack (d : FlachSymmetricPowerDatum) : Real :=
  d.symPowerBound * d.policyCurvatureTolerance - d.symPowerSelmerDim

/-- Multi-horizon symmetric power bound accounting for exploration steps. -/
def multiHorizonSymPowerBound (d : FlachSymmetricPowerDatum) : Real :=
  d.symPowerBound * (1 + d.symHorizonSteps * d.policyCurvatureTolerance)

/-- Predicate: symmetric square Selmer dimension is bounded by Flach bound. -/
def IsSymPowerBounded (d : FlachSymmetricPowerDatum) : Prop :=
  d.symPowerSelmerDim <= d.symPowerBound

/-- Predicate: symmetric square Selmer dimension vanishes (completely rigid unramified state). -/
def IsZeroSymPowerSelmer (d : FlachSymmetricPowerDatum) : Prop :=
  d.symPowerSelmerDim = 0

/-- Predicate: curvature variation is convergent within policy tolerance. -/
def IsSymPowerCurvatureConvergent (d : FlachSymmetricPowerDatum) : Prop :=
  d.symPowerSelmerDim <= d.symPowerBound * d.policyCurvatureTolerance

/-- Symmetric power defect is non-negative for Flach-bounded systems. -/
theorem sym_power_defect_nonneg_of_bounded (d : FlachSymmetricPowerDatum)
    (h : IsSymPowerBounded d) : 0 <= symPowerDefect d := by
  dsimp [symPowerDefect, IsSymPowerBounded] at *
  linarith

/-- Boundedness is equivalent to non-negative symmetric power defect. -/
theorem sym_power_bounded_iff_defect_nonneg (d : FlachSymmetricPowerDatum) :
    IsSymPowerBounded d <-> 0 <= symPowerDefect d := by
  dsimp [IsSymPowerBounded, symPowerDefect]
  constructor <;> intro h <;> linarith

/-- Normalized symmetric power ratio is non-negative. -/
theorem normalized_sym_power_ratio_nonneg (d : FlachSymmetricPowerDatum) :
    0 <= normalizedSymPowerRatio d := by
  dsimp [normalizedSymPowerRatio]
  exact div_nonneg d.dim_nonneg (le_of_lt d.bound_pos)

/-- Normalized symmetric power ratio is bounded by 1 for bounded systems. -/
theorem normalized_sym_power_ratio_le_one_of_bounded (d : FlachSymmetricPowerDatum)
    (h : IsSymPowerBounded d) : normalizedSymPowerRatio d <= 1 := by
  dsimp [normalizedSymPowerRatio, IsSymPowerBounded] at *
  exact (div_le_one d.bound_pos).mpr h

/-- Zero Selmer dimension implies Flach-bounded system. -/
theorem zero_sym_power_implies_bounded (d : FlachSymmetricPowerDatum)
    (h : IsZeroSymPowerSelmer d) : IsSymPowerBounded d := by
  dsimp [IsSymPowerBounded, IsZeroSymPowerSelmer] at *
  rw [h]
  exact le_of_lt d.bound_pos

/-- Zero Selmer dimension has defect equal to Flach bound. -/
theorem zero_sym_power_implies_defect_eq_bound (d : FlachSymmetricPowerDatum)
    (h : IsZeroSymPowerSelmer d) : symPowerDefect d = d.symPowerBound := by
  dsimp [symPowerDefect, IsZeroSymPowerSelmer] at *
  rw [h, sub_zero]

/-- Zero Selmer dimension has normalized ratio equal to 0. -/
theorem zero_sym_power_implies_ratio_zero (d : FlachSymmetricPowerDatum)
    (h : IsZeroSymPowerSelmer d) : normalizedSymPowerRatio d = 0 := by
  dsimp [normalizedSymPowerRatio, IsZeroSymPowerSelmer] at *
  rw [h, zero_div]

/-- Discounted symmetric power bound is strictly positive. -/
theorem discounted_sym_power_bound_pos (d : FlachSymmetricPowerDatum) :
    0 < discountedSymPowerBound d := by
  dsimp [discountedSymPowerBound]
  exact mul_pos d.bound_pos d.discount_pos

/-- Discounted symmetric power bound is bounded by the full Flach bound. -/
theorem discounted_sym_power_bound_le_bound (d : FlachSymmetricPowerDatum) :
    discountedSymPowerBound d <= d.symPowerBound := by
  dsimp [discountedSymPowerBound]
  have h := mul_le_mul_of_nonneg_left d.discount_le_one (le_of_lt d.bound_pos)
  linarith

/-- Curvature convergence is equivalent to non-negative symmetric power slack. -/
theorem sym_power_curvature_convergent_iff_slack_nonneg (d : FlachSymmetricPowerDatum) :
    IsSymPowerCurvatureConvergent d <-> 0 <= symPowerSlack d := by
  dsimp [IsSymPowerCurvatureConvergent, symPowerSlack]
  constructor <;> intro h <;> linarith

/-- Symmetric power slack is non-negative for curvature-convergent systems. -/
theorem sym_power_slack_nonneg_of_convergent (d : FlachSymmetricPowerDatum)
    (h : IsSymPowerCurvatureConvergent d) : 0 <= symPowerSlack d :=
  (sym_power_curvature_convergent_iff_slack_nonneg d).mp h

/-- Selmer dimension reconstructed from normalized ratio and Flach bound. -/
theorem sym_power_dim_reconstruction (d : FlachSymmetricPowerDatum) :
    d.symPowerSelmerDim = normalizedSymPowerRatio d * d.symPowerBound := by
  dsimp [normalizedSymPowerRatio]
  have hu : IsUnit d.symPowerBound := (ne_of_gt d.bound_pos).isUnit
  exact (hu.div_mul_cancel d.symPowerSelmerDim).symm

/-- Multi-horizon symmetric power bound is strictly positive. -/
theorem multi_horizon_sym_power_bound_pos (d : FlachSymmetricPowerDatum) :
    0 < multiHorizonSymPowerBound d := by
  dsimp [multiHorizonSymPowerBound]
  have h_prod : 0 < d.symHorizonSteps * d.policyCurvatureTolerance :=
    mul_pos d.horizon_pos d.tolerance_pos
  have h_sum : 0 < 1 + d.symHorizonSteps * d.policyCurvatureTolerance := by linarith
  exact mul_pos d.bound_pos h_sum

/-- Discounted symmetric power bound is monotone in discount factor. -/
theorem discounted_sym_power_bound_monotone (d : FlachSymmetricPowerDatum) (g : Real)
    (h : d.symDiscountFactor <= g) :
    discountedSymPowerBound d <= d.symPowerBound * g := by
  dsimp [discountedSymPowerBound]
  exact mul_le_mul_of_nonneg_left h (le_of_lt d.bound_pos)

/-- Symmetric power slack is monotone in curvature tolerance. -/
theorem sym_power_slack_monotone_tolerance (d : FlachSymmetricPowerDatum) (t : Real)
    (ht : d.policyCurvatureTolerance <= t) :
    symPowerSlack d <= d.symPowerBound * t - d.symPowerSelmerDim := by
  dsimp [symPowerSlack]
  nlinarith [d.bound_pos]

/-- Symmetric power defect is monotone in Flach bound. -/
theorem sym_power_defect_monotone_bound (d : FlachSymmetricPowerDatum) (b : Real)
    (hb : d.symPowerBound <= b) :
    symPowerDefect d <= b - d.symPowerSelmerDim := by
  dsimp [symPowerDefect]
  linarith

/-- Multi-horizon bound is monotone in horizon steps. -/
theorem multi_horizon_sym_power_monotone_steps (d : FlachSymmetricPowerDatum) (k : Real)
    (hk : d.symHorizonSteps <= k) :
    multiHorizonSymPowerBound d <= d.symPowerBound * (1 + k * d.policyCurvatureTolerance) := by
  dsimp [multiHorizonSymPowerBound]
  have h_inner : 1 + d.symHorizonSteps * d.policyCurvatureTolerance <= 1 + k * d.policyCurvatureTolerance := by
    nlinarith [d.tolerance_pos]
  exact mul_le_mul_of_nonneg_left h_inner (le_of_lt d.bound_pos)

end <Project>.ProofSkills.FlachSystemBound
```
