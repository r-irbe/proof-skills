# Template_ModularJacobianHeightRegulator - Modular Jacobian Height Regulators & Gross-Zagier Capacities

Use this template for **modular Jacobian height regulators**, **Gross-Zagier capacity bounds**,
**Mordell-Weil lattice covolumes**, and **stochastic network circulation capacity constraints**.

In arithmetic geometry and Fermat's Last Theorem / modular forms:
On the modular Jacobian J_0(N), the height regulator is the discriminant (Gram determinant)
of the canonical Neron-Tate height pairing on the Mordell-Weil group modulo torsion.
The Gross-Zagier formula relates the central derivative of the Rankin-Selberg L-series
L'(E, 1) directly to the canonical height of Heegner points on modular curves,
establishing that non-vanishing of the height regulator governs the analytic rank
and yields rigorous upper and lower bounds on the Mordell-Weil lattice covolume.

In stochastic consensus and Markov non-equilibrium networks:
Height regulators define multi-cycle volume forms on network circulation spaces.
The Gross-Zagier capacity bound enforces certified bounds on total cycle flux covolumes.
The canonical regulator slack guarantees divergence-free probability currents across complex topologies.
The normalized ratio bounds information geometric drift away from non-equilibrium steady states.

## Main results
* `<ModularJacobianHeightRegulatorDatum>` - datum (regulatorDeterminant, regulatorBound, regulatorCapacity, regulatorTolerance, regulatorWeight)
* `<HeightRegulatorDefect>` - defect between regulator bound ceiling and observed height regulator determinant
* `<NormalizedHeightRegulatorRatio>` - normalized ratio of observed height regulator determinant to regulator bound
* `<GrossZagierCapacityBound>` - total Gross-Zagier capacity bound scaled by regulator bound and capacity volume
* `<HeightRegulatorSlack>` - slack between tolerance-scaled bound and observed height regulator determinant
* `<weightedHeightRegulatorBound>` - regulator-weighted bound accounting for regulator weight and tolerance
* `<IsHeightRegulatorBounded>` - predicate: observed height regulator determinant is bounded by regulator bound
* `<IsCriticalHeightRegulator>` - predicate: observed determinant reaches critical regulator threshold
* `<IsHeightRegulatorSafe>` - predicate: observed determinant is within certified regulator tolerance
* `<height_regulator_defect_nonneg_of_bounded>` - height regulator defect is non-negative for bounded systems
* `<height_regulator_bounded_iff_defect_nonneg>` - boundedness is equivalent to non-negative height regulator defect
* `<normalized_height_regulator_ratio_nonneg>` - normalized height regulator ratio is non-negative
* `<normalized_height_regulator_ratio_le_one_of_bounded>` - normalized ratio is bounded by 1 for bounded systems
* `<gross_zagier_capacity_bound_pos>` - Gross-Zagier capacity bound is strictly positive
* `<gross_zagier_capacity_bound_nonneg>` - Gross-Zagier capacity bound is non-negative
* `<exact_height_regulator_implies_bounded>` - exact saturation implies bounded system
* `<exact_height_regulator_defect_zero>` - exact defect vanishes identically
* `<exact_height_regulator_ratio_one>` - exact saturation has normalized ratio 1
* `<height_regulator_safe_iff_slack_nonneg>` - safety is equivalent to non-negative height regulator slack
* `<height_regulator_slack_nonneg_of_safe>` - slack is non-negative for safe systems
* `<height_regulator_determinant_reconstruction>` - height regulator determinant reconstructed from normalized ratio and bound
* `<weighted_height_regulator_bound_pos>` - regulator-weighted bound is strictly positive
* `<gross_zagier_capacity_scale>` - capacity bound scales non-negatively with positive scaling
* `<gross_zagier_capacity_monotone>` - capacity bound is monotone in regulator bound ceiling
* `<height_regulator_defect_monotone>` - defect is monotone in lower bounds on observed regulator determinant
* `<height_regulator_slack_monotone_tolerance>` - slack is monotone in regulator tolerance parameter

## References
* FLT: `StochasticCCV/Core/ModularJacobianHeightRegulator.lean`
* Gross, B., Zagier, D. (1986), *Heegner points and derivatives of L-series*, Inventiones Mathematicae 84, 225-320.
* Mazur, B. (1977), *Modular curves and the Eisenstein ideal*, Publications Mathematiques de l'IHES 47, 33-186.
* Merel, L. (1996), *Bornes pour la torsion des courbes elliptiques sur les corps de nombres*, Inventiones Mathematicae 124, 437-449.

## Tags
template, modular-jacobian, height-regulator, gross-zagier, markov-circulation, capacity-envelope

```lean
/-
Copyright (c) 2026 <Project> Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: <Authors>
SPDX-License-Identifier: Apache-2.0
-/

import Mathlib.Data.Real.Basic
import Mathlib.Tactic

set_option autoImplicit false
set_option linter.unusedVariables false
set_option linter.unusedSectionVars false
set_option linter.unusedSimpArgs false

noncomputable section

namespace <Namespace>

/-- Datum specifying modular Jacobian height regulator determinant, regulator bound ceiling,
    Gross-Zagier capacity volume, regulator tolerance, and regulator weight. -/
structure <ModularJacobianHeightRegulatorDatum> where
  regulatorDeterminant : ℝ
  regulatorBound : ℝ
  regulatorCapacity : ℝ
  regulatorTolerance : ℝ
  regulatorWeight : ℝ
  regulator_pos : 0 < regulatorDeterminant
  bound_pos : 0 < regulatorBound
  capacity_pos : 0 < regulatorCapacity
  tolerance_pos : 0 < regulatorTolerance
  weight_pos : 0 < regulatorWeight

/-- Defect between theoretical regulator bound ceiling and observed height regulator determinant. -/
def <HeightRegulatorDefect> (d : <ModularJacobianHeightRegulatorDatum>) : ℝ :=
  d.regulatorBound - d.regulatorDeterminant

/-- Normalized ratio of observed height regulator determinant to regulator bound ceiling. -/
def <NormalizedHeightRegulatorRatio> (d : <ModularJacobianHeightRegulatorDatum>) : ℝ :=
  d.regulatorDeterminant / d.regulatorBound

/-- Gross-Zagier capacity bound scaled by regulator bound and capacity volume. -/
def <GrossZagierCapacityBound> (d : <ModularJacobianHeightRegulatorDatum>) : ℝ :=
  d.regulatorBound * d.regulatorCapacity

/-- Regulator slack between tolerance-scaled bound and observed height regulator determinant. -/
def <HeightRegulatorSlack> (d : <ModularJacobianHeightRegulatorDatum>) : ℝ :=
  d.regulatorBound * d.regulatorTolerance - d.regulatorDeterminant

/-- Regulator-weighted bound accounting for regulator weight and tolerance. -/
def weightedHeightRegulatorBound (d : <ModularJacobianHeightRegulatorDatum>) : ℝ :=
  d.regulatorBound * (1 + d.regulatorWeight * d.regulatorTolerance)

/-- Predicate: observed height regulator determinant is bounded by the regulator bound ceiling. -/
def IsHeightRegulatorBounded (d : <ModularJacobianHeightRegulatorDatum>) : Prop :=
  d.regulatorDeterminant ≤ d.regulatorBound

/-- Predicate: observed height regulator determinant reaches the critical regulator threshold. -/
def IsCriticalHeightRegulator (d : <ModularJacobianHeightRegulatorDatum>) : Prop :=
  d.regulatorDeterminant = d.regulatorBound

/-- Predicate: observed height regulator determinant is within certified regulator tolerance. -/
def IsHeightRegulatorSafe (d : <ModularJacobianHeightRegulatorDatum>) : Prop :=
  d.regulatorDeterminant ≤ d.regulatorBound * d.regulatorTolerance

/-- Height regulator defect is non-negative for bounded systems. -/
theorem height_regulator_defect_nonneg_of_bounded (d : <ModularJacobianHeightRegulatorDatum>)
    (h : IsHeightRegulatorBounded d) : 0 ≤ <HeightRegulatorDefect> d := by
  dsimp [<HeightRegulatorDefect>, IsHeightRegulatorBounded] at *
  linarith

/-- Boundedness is equivalent to non-negative height regulator defect. -/
theorem height_regulator_bounded_iff_defect_nonneg (d : <ModularJacobianHeightRegulatorDatum>) :
    IsHeightRegulatorBounded d ↔ 0 ≤ <HeightRegulatorDefect> d := by
  dsimp [IsHeightRegulatorBounded, <HeightRegulatorDefect>]
  constructor <;> intro h <;> linarith

/-- Normalized height regulator ratio is non-negative. -/
theorem normalized_height_regulator_ratio_nonneg (d : <ModularJacobianHeightRegulatorDatum>) :
    0 ≤ <NormalizedHeightRegulatorRatio> d := by
  dsimp [<NormalizedHeightRegulatorRatio>]
  exact div_nonneg (le_of_lt d.regulator_pos) (le_of_lt d.bound_pos)

/-- Normalized height regulator ratio is bounded by 1 for bounded systems. -/
theorem normalized_height_regulator_ratio_le_one_of_bounded (d : <ModularJacobianHeightRegulatorDatum>)
    (h : IsHeightRegulatorBounded d) : <NormalizedHeightRegulatorRatio> d ≤ 1 := by
  dsimp [<NormalizedHeightRegulatorRatio>, IsHeightRegulatorBounded] at *
  exact (div_le_one d.bound_pos).mpr h

/-- Gross-Zagier capacity bound is strictly positive. -/
theorem gross_zagier_capacity_bound_pos (d : <ModularJacobianHeightRegulatorDatum>) :
    0 < <GrossZagierCapacityBound> d := by
  dsimp [<GrossZagierCapacityBound>]
  exact mul_pos d.bound_pos d.capacity_pos

/-- Gross-Zagier capacity bound is non-negative. -/
theorem gross_zagier_capacity_bound_nonneg (d : <ModularJacobianHeightRegulatorDatum>) :
    0 ≤ <GrossZagierCapacityBound> d :=
  le_of_lt (gross_zagier_capacity_bound_pos d)

/-- Exact height regulator saturation implies bounded system. -/
theorem exact_height_regulator_implies_bounded (d : <ModularJacobianHeightRegulatorDatum>)
    (h : IsCriticalHeightRegulator d) : IsHeightRegulatorBounded d := by
  dsimp [IsHeightRegulatorBounded, IsCriticalHeightRegulator] at *
  linarith

/-- Exact height regulator defect vanishes identically. -/
theorem exact_height_regulator_defect_zero (d : <ModularJacobianHeightRegulatorDatum>)
    (h : IsCriticalHeightRegulator d) : <HeightRegulatorDefect> d = 0 := by
  dsimp [<HeightRegulatorDefect>, IsCriticalHeightRegulator] at *
  rw [h]
  ring

/-- Exact height regulator saturation has normalized ratio 1. -/
theorem exact_height_regulator_ratio_one (d : <ModularJacobianHeightRegulatorDatum>)
    (h : IsCriticalHeightRegulator d) : <NormalizedHeightRegulatorRatio> d = 1 := by
  dsimp [<NormalizedHeightRegulatorRatio>, IsCriticalHeightRegulator] at *
  rw [h]
  exact div_self (ne_of_gt d.bound_pos)

/-- Safety is equivalent to non-negative height regulator slack. -/
theorem height_regulator_safe_iff_slack_nonneg (d : <ModularJacobianHeightRegulatorDatum>) :
    IsHeightRegulatorSafe d ↔ 0 ≤ <HeightRegulatorSlack> d := by
  dsimp [IsHeightRegulatorSafe, <HeightRegulatorSlack>]
  constructor <;> intro h <;> linarith

/-- Slack is non-negative for safe systems. -/
theorem height_regulator_slack_nonneg_of_safe (d : <ModularJacobianHeightRegulatorDatum>)
    (h : IsHeightRegulatorSafe d) : 0 ≤ <HeightRegulatorSlack> d :=
  (height_regulator_safe_iff_slack_nonneg d).mp h

/-- Height regulator determinant reconstructed from normalized ratio and regulator bound ceiling. -/
theorem height_regulator_determinant_reconstruction (d : <ModularJacobianHeightRegulatorDatum>) :
    d.regulatorDeterminant = <NormalizedHeightRegulatorRatio> d * d.regulatorBound := by
  dsimp [<NormalizedHeightRegulatorRatio>]
  have h_ne : d.regulatorBound ≠ 0 := ne_of_gt d.bound_pos
  have hu : IsUnit d.regulatorBound := h_ne.isUnit
  exact (hu.div_mul_cancel d.regulatorDeterminant).symm

/-- Regulator-weighted bound is strictly positive. -/
theorem weighted_height_regulator_bound_pos (d : <ModularJacobianHeightRegulatorDatum>) :
    0 < weightedHeightRegulatorBound d := by
  dsimp [weightedHeightRegulatorBound]
  have h_prod : 0 < d.regulatorWeight * d.regulatorTolerance :=
    mul_pos d.weight_pos d.tolerance_pos
  have h_sum : 0 < 1 + d.regulatorWeight * d.regulatorTolerance := by linarith
  exact mul_pos d.bound_pos h_sum

/-- Linear scaling of Gross-Zagier capacity bound. -/
theorem gross_zagier_capacity_scale (d : <ModularJacobianHeightRegulatorDatum>) (c : ℝ) (hc : 0 ≤ c) :
    0 ≤ c * <GrossZagierCapacityBound> d :=
  mul_nonneg hc (gross_zagier_capacity_bound_nonneg d)

/-- Gross-Zagier capacity bound is monotone in regulator bound ceiling. -/
theorem gross_zagier_capacity_monotone (d : <ModularJacobianHeightRegulatorDatum>) (b : ℝ)
    (hb : d.regulatorBound ≤ b) :
    <GrossZagierCapacityBound> d ≤ b * d.regulatorCapacity := by
  dsimp [<GrossZagierCapacityBound>]
  nlinarith [d.capacity_pos]

/-- Defect is monotone in lower bounds on observed regulator determinant. -/
theorem height_regulator_defect_monotone (d : <ModularJacobianHeightRegulatorDatum>) (p : ℝ)
    (hp : p ≤ d.regulatorDeterminant) :
    d.regulatorBound - d.regulatorDeterminant ≤ d.regulatorBound - p := by
  linarith

/-- Slack is monotone in regulator tolerance parameter. -/
theorem height_regulator_slack_monotone_tolerance (d : <ModularJacobianHeightRegulatorDatum>) (t : ℝ)
    (ht : d.regulatorTolerance ≤ t) :
    <HeightRegulatorSlack> d ≤ d.regulatorBound * t - d.regulatorDeterminant := by
  dsimp [<HeightRegulatorSlack>]
  nlinarith [d.bound_pos]

end <Namespace>
```
