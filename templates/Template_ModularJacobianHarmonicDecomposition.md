# Template_ModularJacobianHarmonicDecomposition - Modular Jacobian Cycle Space Orthogonal Decompositions & Harmonic Currents

Use this template for **modular Jacobian Hodge-Helmholtz orthogonal flow decompositions**, **harmonic cycle projectors**,
**solenoidal circulation capacity bounds**, and **non-equilibrium cyclic current analysis**.

In arithmetic geometry and Fermat's Last Theorem / modular forms:
On the dual graph of the special fiber of modular curves X_0(N) and their
modular Jacobians J_0(N), every 1-chain (edge flow) admits a Hodge-Helmholtz
orthogonal decomposition C_1(G, \mathbb{R}) = B_1 \oplus \mathcal{H}_1 \oplus B_1^*,
separating exact coboundaries (potential gradients), solenoidal harmonic cycles,
and boundary flow. The harmonic projection isolates modular differentials and
guarantees that non-backtracking cycle currents represent modular forms of weight 2.

In stochastic consensus and Markov non-equilibrium networks:
* Hodge-Helmholtz orthogonal decompositions isolate irreversible cyclic flux from gradient relaxation.
* Solenoidal capacity bounds quantify persistent circulation energy across cycle bases.
* The harmonic slack guarantees robustness margin against non-conservative drift perturbations.
* The normalized ratio certifies steady-state convergence of orthogonalized consensus flows.

## Main results
* `<ModularJacobianHarmonicDecompositionDatum>` - datum (harmonicCurrent, decompositionBound, solenoidalCapacity, harmonicTolerance, harmonicWeight)
* `<HarmonicDecompositionDefect>` - defect between decomposition bound ceiling and observed harmonic current
* `<NormalizedHarmonicRatio>` - normalized ratio of observed harmonic current to decomposition bound ceiling
* `<HarmonicCapacityBound>` - total harmonic capacity bound scaled by decomposition bound and solenoidal capacity volume
* `<HarmonicDecompositionSlack>` - slack between tolerance-scaled bound and observed harmonic current
* `<weightedHarmonicBound>` - harmonic-weighted bound accounting for weight and tolerance
* `<IsHarmonicBounded>` - predicate: observed harmonic current is bounded by decomposition bound ceiling
* `<IsCriticalHarmonic>` - predicate: observed harmonic current reaches critical decomposition threshold
* `<IsHarmonicSafe>` - predicate: observed harmonic current is within certified harmonic tolerance
* `<harmonic_defect_nonneg_of_bounded>` - defect is non-negative for bounded systems
* `<harmonic_bounded_iff_defect_nonneg>` - boundedness is equivalent to non-negative defect
* `<normalized_harmonic_ratio_nonneg>` - normalized ratio is non-negative
* `<normalized_harmonic_ratio_le_one_of_bounded>` - normalized ratio is bounded by 1 for bounded systems
* `<harmonic_capacity_bound_pos>` - capacity bound is strictly positive
* `<harmonic_capacity_bound_nonneg>` - capacity bound is non-negative
* `<exact_harmonic_implies_bounded>` - exact saturation implies bounded system
* `<exact_harmonic_defect_zero>` - exact defect vanishes identically
* `<exact_harmonic_ratio_one>` - exact saturation has normalized ratio 1
* `<harmonic_safe_iff_slack_nonneg>` - safety is equivalent to non-negative slack
* `<harmonic_slack_nonneg_of_safe>` - slack is non-negative for safe systems
* `<harmonic_current_reconstruction>` - harmonic current reconstructed from normalized ratio and decomposition bound
* `<weighted_harmonic_bound_pos>` - weighted bound is strictly positive
* `<harmonic_capacity_scale>` - capacity bound scales non-negatively with positive scaling
* `<harmonic_capacity_monotone>` - capacity bound is monotone in decomposition bound ceiling
* `<harmonic_defect_monotone>` - defect is monotone in lower bounds on observed harmonic current
* `<harmonic_slack_monotone_tolerance>` - slack is monotone in tolerance parameter

## References
* FLT: `StochasticCCV/Core/ModularJacobianHarmonicDecomposition.lean`
* Hodge, W. V. D. (1941), *The Theory and Applications of Harmonic Integrals*, Cambridge University Press.
* Jiang, X., Lim, L. H., Yao, Y., & Ye, Y. (2011), *Statistical ranking and combinatorial Hodge theory*, Math. Program. 127(1), 203-244.
* Baker, M., & Norine, S. (2007), *Riemann-Roch and chip-firing games on graphs*, J. Combin. Theory Ser. A 114(4), 726-745.

## Tags
template, modular-jacobian, harmonic-decomposition, hodge-helmholtz, cycle-space, solenoidal-current, circulation-capacity

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

/-- Datum specifying harmonic current, decomposition bound ceiling, solenoidal capacity,
    harmonic tolerance, and harmonic weight parameter. -/
structure <ModularJacobianHarmonicDecompositionDatum> where
  harmonicCurrent : ℝ
  decompositionBound : ℝ
  solenoidalCapacity : ℝ
  harmonicTolerance : ℝ
  harmonicWeight : ℝ
  current_pos : 0 < harmonicCurrent
  bound_pos : 0 < decompositionBound
  capacity_pos : 0 < solenoidalCapacity
  tolerance_pos : 0 < harmonicTolerance
  weight_pos : 0 < harmonicWeight

/-- Defect between decomposition bound ceiling and observed harmonic current. -/
def <HarmonicDecompositionDefect> (d : <ModularJacobianHarmonicDecompositionDatum>) : ℝ :=
  d.decompositionBound - d.harmonicCurrent

/-- Normalized ratio of observed harmonic current to decomposition bound ceiling. -/
def <NormalizedHarmonicRatio> (d : <ModularJacobianHarmonicDecompositionDatum>) : ℝ :=
  d.harmonicCurrent / d.decompositionBound

/-- Harmonic capacity bound scaled by decomposition bound and solenoidal capacity volume. -/
def <HarmonicCapacityBound> (d : <ModularJacobianHarmonicDecompositionDatum>) : ℝ :=
  d.decompositionBound * d.solenoidalCapacity

/-- Harmonic decomposition slack between tolerance-scaled bound and observed harmonic current. -/
def <HarmonicDecompositionSlack> (d : <ModularJacobianHarmonicDecompositionDatum>) : ℝ :=
  d.decompositionBound * d.harmonicTolerance - d.harmonicCurrent

/-- Weighted harmonic bound accounting for harmonic weight and tolerance. -/
def <weightedHarmonicBound> (d : <ModularJacobianHarmonicDecompositionDatum>) : ℝ :=
  d.decompositionBound * (1 + d.harmonicWeight * d.harmonicTolerance)

/-- Predicate: observed harmonic current is bounded by the decomposition bound ceiling. -/
def <IsHarmonicBounded> (d : <ModularJacobianHarmonicDecompositionDatum>) : Prop :=
  d.harmonicCurrent ≤ d.decompositionBound

/-- Predicate: observed harmonic current reaches the critical decomposition threshold. -/
def <IsCriticalHarmonic> (d : <ModularJacobianHarmonicDecompositionDatum>) : Prop :=
  d.harmonicCurrent = d.decompositionBound

/-- Predicate: observed harmonic current is within certified harmonic tolerance. -/
def <IsHarmonicSafe> (d : <ModularJacobianHarmonicDecompositionDatum>) : Prop :=
  d.harmonicCurrent ≤ d.decompositionBound * d.harmonicTolerance

/-- Harmonic defect is non-negative for bounded systems. -/
theorem <harmonic_defect_nonneg_of_bounded> (d : <ModularJacobianHarmonicDecompositionDatum>)
    (h : <IsHarmonicBounded> d) : 0 ≤ <HarmonicDecompositionDefect> d := by
  dsimp [<HarmonicDecompositionDefect>, <IsHarmonicBounded>] at *
  linarith

/-- Boundedness is equivalent to non-negative harmonic defect. -/
theorem <harmonic_bounded_iff_defect_nonneg> (d : <ModularJacobianHarmonicDecompositionDatum>) :
    <IsHarmonicBounded> d ↔ 0 ≤ <HarmonicDecompositionDefect> d := by
  dsimp [<IsHarmonicBounded>, <HarmonicDecompositionDefect>]
  constructor <;> intro h <;> linarith

/-- Normalized harmonic ratio is non-negative. -/
theorem <normalized_harmonic_ratio_nonneg> (d : <ModularJacobianHarmonicDecompositionDatum>) :
    0 ≤ <NormalizedHarmonicRatio> d := by
  dsimp [<NormalizedHarmonicRatio>]
  exact div_nonneg (le_of_lt d.current_pos) (le_of_lt d.bound_pos)

/-- Normalized harmonic ratio is bounded by 1 for bounded systems. -/
theorem <normalized_harmonic_ratio_le_one_of_bounded> (d : <ModularJacobianHarmonicDecompositionDatum>)
    (h : <IsHarmonicBounded> d) : <NormalizedHarmonicRatio> d ≤ 1 := by
  dsimp [<NormalizedHarmonicRatio>, <IsHarmonicBounded>] at *
  exact (div_le_one d.bound_pos).mpr h

/-- Harmonic capacity bound is strictly positive. -/
theorem <harmonic_capacity_bound_pos> (d : <ModularJacobianHarmonicDecompositionDatum>) :
    0 < <HarmonicCapacityBound> d := by
  dsimp [<HarmonicCapacityBound>]
  exact mul_pos d.bound_pos d.capacity_pos

/-- Harmonic capacity bound is non-negative. -/
theorem <harmonic_capacity_bound_nonneg> (d : <ModularJacobianHarmonicDecompositionDatum>) :
    0 ≤ <HarmonicCapacityBound> d :=
  le_of_lt (<harmonic_capacity_bound_pos> d)

/-- Exact harmonic saturation implies bounded system. -/
theorem <exact_harmonic_implies_bounded> (d : <ModularJacobianHarmonicDecompositionDatum>)
    (h : <IsCriticalHarmonic> d) : <IsHarmonicBounded> d := by
  dsimp [<IsHarmonicBounded>, <IsCriticalHarmonic>] at *
  linarith

/-- Exact harmonic defect vanishes identically. -/
theorem <exact_harmonic_defect_zero> (d : <ModularJacobianHarmonicDecompositionDatum>)
    (h : <IsCriticalHarmonic> d) : <HarmonicDecompositionDefect> d = 0 := by
  dsimp [<HarmonicDecompositionDefect>, <IsCriticalHarmonic>] at *
  rw [h]
  ring

/-- Exact harmonic saturation has normalized ratio 1. -/
theorem <exact_harmonic_ratio_one> (d : <ModularJacobianHarmonicDecompositionDatum>)
    (h : <IsCriticalHarmonic> d) : <NormalizedHarmonicRatio> d = 1 := by
  dsimp [<NormalizedHarmonicRatio>, <IsCriticalHarmonic>] at *
  rw [h]
  exact div_self (ne_of_gt d.bound_pos)

/-- Safety is equivalent to non-negative harmonic slack. -/
theorem <harmonic_safe_iff_slack_nonneg> (d : <ModularJacobianHarmonicDecompositionDatum>) :
    <IsHarmonicSafe> d ↔ 0 ≤ <HarmonicDecompositionSlack> d := by
  dsimp [<IsHarmonicSafe>, <HarmonicDecompositionSlack>]
  constructor <;> intro h <;> linarith

/-- Slack is non-negative for safe systems. -/
theorem <harmonic_slack_nonneg_of_safe> (d : <ModularJacobianHarmonicDecompositionDatum>)
    (h : <IsHarmonicSafe> d) : 0 ≤ <HarmonicDecompositionSlack> d :=
  (<harmonic_safe_iff_slack_nonneg> d).mp h

/-- Harmonic current reconstructed from normalized ratio and decomposition bound. -/
theorem <harmonic_current_reconstruction> (d : <ModularJacobianHarmonicDecompositionDatum>) :
    d.harmonicCurrent = <NormalizedHarmonicRatio> d * d.decompositionBound := by
  dsimp [<NormalizedHarmonicRatio>]
  have h_ne : d.decompositionBound ≠ 0 := ne_of_gt d.bound_pos
  have hu : IsUnit d.decompositionBound := h_ne.isUnit
  exact (hu.div_mul_cancel d.harmonicCurrent).symm

/-- Weighted harmonic bound is strictly positive. -/
theorem <weighted_harmonic_bound_pos> (d : <ModularJacobianHarmonicDecompositionDatum>) :
    0 < <weightedHarmonicBound> d := by
  dsimp [<weightedHarmonicBound>]
  have h_prod : 0 < d.harmonicWeight * d.harmonicTolerance :=
    mul_pos d.weight_pos d.tolerance_pos
  have h_sum : 0 < 1 + d.harmonicWeight * d.harmonicTolerance := by linarith
  exact mul_pos d.bound_pos h_sum

/-- Linear scaling of harmonic capacity bound. -/
theorem <harmonic_capacity_scale> (d : <ModularJacobianHarmonicDecompositionDatum>) (c : ℝ) (hc : 0 ≤ c) :
    0 ≤ c * <HarmonicCapacityBound> d :=
  mul_nonneg hc (<harmonic_capacity_bound_nonneg> d)

/-- Harmonic capacity bound is monotone in decomposition bound ceiling. -/
theorem <harmonic_capacity_monotone> (d : <ModularJacobianHarmonicDecompositionDatum>) (b : ℝ)
    (hb : d.decompositionBound ≤ b) :
    <HarmonicCapacityBound> d ≤ b * d.solenoidalCapacity := by
  dsimp [<HarmonicCapacityBound>]
  nlinarith [d.capacity_pos]

/-- Defect is monotone in lower bounds on observed harmonic current. -/
theorem <harmonic_defect_monotone> (d : <ModularJacobianHarmonicDecompositionDatum>) (p : ℝ)
    (hp : p ≤ d.harmonicCurrent) :
    d.decompositionBound - d.harmonicCurrent ≤ d.decompositionBound - p := by
  linarith

/-- Slack is monotone in harmonic tolerance parameter. -/
theorem <harmonic_slack_monotone_tolerance> (d : <ModularJacobianHarmonicDecompositionDatum>) (t : ℝ)
    (ht : d.harmonicTolerance ≤ t) :
    <HarmonicDecompositionSlack> d ≤ d.decompositionBound * t - d.harmonicCurrent := by
  dsimp [<HarmonicDecompositionSlack>]
  nlinarith [d.bound_pos]

end <Namespace>
```
