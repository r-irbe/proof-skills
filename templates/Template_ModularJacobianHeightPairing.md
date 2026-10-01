# Template_ModularJacobianHeightPairing - Modular Jacobian Height Pairings & Canonical Regulators

Use this template for **modular Jacobian height pairings**, **canonical regulator determinants**,
**Mordell-Weil lattice covolumes**, and **stochastic network circulation capacity constraints**.

In arithmetic geometry and Fermat's Last Theorem / modular forms:
Let X_0(N) be a modular curve over Q, and let J_0(N) be its modular Jacobian. The Neron-Tate canonical
height pairing is a symmetric, positive-definite bilinear form on the Mordell-Weil group modulo torsion
J_0(N)(Q) \otimes R. The canonical regulator is the Gram determinant of this pairing across a free basis.
Mazur, Gross-Zagier, and Merel established uniform lower bounds on non-zero canonical heights and
non-degeneracy of the regulator, which controls the leading coefficient in the Birch-Swinnerton-Dyer
conjecture and governs the distribution of Heegner points.

In stochastic consensus and Markov flow networks:
Modular Jacobian height pairings define canonical Dirichlet metrics on network circulation spaces.
The regulator bound enforces certified upper bounds on cycle current divergence.
The canonical regulator capacity measures total available circulation volume.
The pairing slack bounds probability current deviation from optimal detailed balance.

## Main results
* `<ModularJacobianHeightPairingDatum>` - datum (heightNorm, regulatorBound, regulatorCapacity, pairingTolerance, heightWeight)
* `<HeightPairingDefect>` - defect between regulator bound ceiling and observed height pairing norm
* `<NormalizedHeightPairingRatio>` - normalized ratio of observed height pairing norm to regulator bound
* `<CanonicalRegulatorCapacityBound>` - total capacity bound scaled by regulator bound and capacity volume
* `<HeightPairingSlack>` - slack between tolerance-scaled bound and observed height pairing norm
* `<weightedHeightPairingBound>` - height-weighted bound accounting for height weight and pairing tolerance
* `<IsHeightPairingBounded>` - predicate: observed height pairing norm is bounded by regulator bound
* `<IsCriticalHeightPairing>` - predicate: observed norm reaches critical regulator threshold
* `<IsHeightPairingSafe>` - predicate: observed norm is within certified pairing tolerance
* `<height_pairing_defect_nonneg_of_bounded>` - height pairing defect is non-negative for bounded systems
* `<height_pairing_bounded_iff_defect_nonneg>` - boundedness is equivalent to non-negative height pairing defect
* `<normalized_height_pairing_ratio_nonneg>` - normalized height pairing ratio is non-negative
* `<normalized_height_pairing_ratio_le_one_of_bounded>` - normalized ratio is bounded by 1 for bounded systems
* `<canonical_regulator_capacity_bound_pos>` - canonical regulator capacity bound is strictly positive
* `<canonical_regulator_capacity_bound_nonneg>` - canonical regulator capacity bound is non-negative
* `<exact_height_pairing_implies_bounded>` - exact saturation implies bounded system
* `<exact_height_pairing_defect_zero>` - exact defect vanishes identically
* `<exact_height_pairing_ratio_one>` - exact saturation has normalized ratio 1
* `<height_pairing_safe_iff_slack_nonneg>` - safety is equivalent to non-negative height pairing slack
* `<height_pairing_slack_nonneg_of_safe>` - slack is non-negative for safe systems
* `<height_pairing_norm_reconstruction>` - height pairing norm reconstructed from normalized ratio and bound
* `<weighted_height_pairing_bound_pos>` - height-weighted bound is strictly positive
* `<canonical_regulator_capacity_scale>` - capacity bound scales non-negatively with positive scaling
* `<canonical_regulator_capacity_monotone>` - capacity bound is monotone in regulator bound ceiling
* `<height_pairing_defect_monotone>` - defect is monotone in lower bounds on observed height pairing norm
* `<height_pairing_slack_monotone_tolerance>` - slack is monotone in pairing tolerance parameter

## References
* FLT: `StochasticCCV/Core/ModularJacobianHeightPairing.lean`
* Gross, B., Zagier, D. (1986), *Heegner points and derivatives of L-series*, Inventiones Mathematicae 84, 225-320.
* Mazur, B. (1977), *Modular curves and the Eisenstein ideal*, Publications Mathematiques de l'IHES 47, 33-186.
* Merel, L. (1996), *Bornes pour la torsion des courbes elliptiques sur les corps de nombres*, Inventiones Mathematicae 124, 437-449.

## Tags
template, modular-jacobian, height-pairing, canonical-regulator, gross-zagier, markov-circulation, capacity-envelope

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

/-- Datum specifying modular Jacobian height pairing norm, regulator bound ceiling,
    canonical regulator capacity volume, pairing tolerance, and height weight. -/
structure <ModularJacobianHeightPairingDatum> where
  heightNorm : ℝ
  regulatorBound : ℝ
  regulatorCapacity : ℝ
  pairingTolerance : ℝ
  heightWeight : ℝ
  norm_pos : 0 < heightNorm
  bound_pos : 0 < regulatorBound
  capacity_pos : 0 < regulatorCapacity
  tolerance_pos : 0 < pairingTolerance
  weight_pos : 0 < heightWeight

/-- Defect between theoretical regulator bound ceiling and observed height pairing norm. -/
def <HeightPairingDefect> (d : <ModularJacobianHeightPairingDatum>) : ℝ :=
  d.regulatorBound - d.heightNorm

/-- Normalized ratio of observed height pairing norm to regulator bound ceiling. -/
def <NormalizedHeightPairingRatio> (d : <ModularJacobianHeightPairingDatum>) : ℝ :=
  d.heightNorm / d.regulatorBound

/-- Total canonical regulator capacity bound scaled by regulator bound and capacity volume. -/
def <CanonicalRegulatorCapacityBound> (d : <ModularJacobianHeightPairingDatum>) : ℝ :=
  d.regulatorBound * d.regulatorCapacity

/-- Pairing slack between tolerance-scaled bound and observed height pairing norm. -/
def <HeightPairingSlack> (d : <ModularJacobianHeightPairingDatum>) : ℝ :=
  d.regulatorBound * d.pairingTolerance - d.heightNorm

/-- Height-weighted bound accounting for height weight and pairing tolerance. -/
def weightedHeightPairingBound (d : <ModularJacobianHeightPairingDatum>) : ℝ :=
  d.regulatorBound * (1 + d.heightWeight * d.pairingTolerance)

/-- Predicate: observed height pairing norm is bounded by regulator bound ceiling. -/
def IsHeightPairingBounded (d : <ModularJacobianHeightPairingDatum>) : Prop :=
  d.heightNorm ≤ d.regulatorBound

/-- Predicate: observed height pairing norm reaches critical regulator threshold. -/
def IsCriticalHeightPairing (d : <ModularJacobianHeightPairingDatum>) : Prop :=
  d.heightNorm = d.regulatorBound

/-- Predicate: observed height pairing norm is within certified pairing tolerance. -/
def IsHeightPairingSafe (d : <ModularJacobianHeightPairingDatum>) : Prop :=
  d.heightNorm ≤ d.regulatorBound * d.pairingTolerance

/-- Height pairing defect is non-negative for bounded systems. -/
theorem height_pairing_defect_nonneg_of_bounded (d : <ModularJacobianHeightPairingDatum>)
    (h : IsHeightPairingBounded d) : 0 ≤ <HeightPairingDefect> d := by
  dsimp [<HeightPairingDefect>, IsHeightPairingBounded] at *
  linarith

/-- Boundedness is equivalent to non-negative height pairing defect. -/
theorem height_pairing_bounded_iff_defect_nonneg (d : <ModularJacobianHeightPairingDatum>) :
    IsHeightPairingBounded d ↔ 0 ≤ <HeightPairingDefect> d := by
  dsimp [IsHeightPairingBounded, <HeightPairingDefect>]
  constructor <;> intro h <;> linarith

/-- Normalized height pairing ratio is non-negative. -/
theorem normalized_height_pairing_ratio_nonneg (d : <ModularJacobianHeightPairingDatum>) :
    0 ≤ <NormalizedHeightPairingRatio> d := by
  dsimp [<NormalizedHeightPairingRatio>]
  exact div_nonneg (le_of_lt d.norm_pos) (le_of_lt d.bound_pos)

/-- Normalized height pairing ratio is bounded by 1 for bounded systems. -/
theorem normalized_height_pairing_ratio_le_one_of_bounded (d : <ModularJacobianHeightPairingDatum>)
    (h : IsHeightPairingBounded d) : <NormalizedHeightPairingRatio> d ≤ 1 := by
  dsimp [<NormalizedHeightPairingRatio>, IsHeightPairingBounded] at *
  exact (div_le_one d.bound_pos).mpr h

/-- Canonical regulator capacity bound is strictly positive. -/
theorem canonical_regulator_capacity_bound_pos (d : <ModularJacobianHeightPairingDatum>) :
    0 < <CanonicalRegulatorCapacityBound> d := by
  dsimp [<CanonicalRegulatorCapacityBound>]
  exact mul_pos d.bound_pos d.capacity_pos

/-- Canonical regulator capacity bound is non-negative. -/
theorem canonical_regulator_capacity_bound_nonneg (d : <ModularJacobianHeightPairingDatum>) :
    0 ≤ <CanonicalRegulatorCapacityBound> d :=
  le_of_lt (canonical_regulator_capacity_bound_pos d)

/-- Exact height pairing saturation implies bounded system. -/
theorem exact_height_pairing_implies_bounded (d : <ModularJacobianHeightPairingDatum>)
    (h : IsCriticalHeightPairing d) : IsHeightPairingBounded d := by
  dsimp [IsHeightPairingBounded, IsCriticalHeightPairing] at *
  linarith

/-- Exact height pairing defect vanishes identically. -/
theorem exact_height_pairing_defect_zero (d : <ModularJacobianHeightPairingDatum>)
    (h : IsCriticalHeightPairing d) : <HeightPairingDefect> d = 0 := by
  dsimp [<HeightPairingDefect>, IsCriticalHeightPairing] at *
  rw [h]
  ring

/-- Exact height pairing saturation has normalized ratio 1. -/
theorem exact_height_pairing_ratio_one (d : <ModularJacobianHeightPairingDatum>)
    (h : IsCriticalHeightPairing d) : <NormalizedHeightPairingRatio> d = 1 := by
  dsimp [<NormalizedHeightPairingRatio>, IsCriticalHeightPairing] at *
  rw [h]
  exact div_self (ne_of_gt d.bound_pos)

/-- Safety is equivalent to non-negative height pairing slack. -/
theorem height_pairing_safe_iff_slack_nonneg (d : <ModularJacobianHeightPairingDatum>) :
    IsHeightPairingSafe d ↔ 0 ≤ <HeightPairingSlack> d := by
  dsimp [IsHeightPairingSafe, <HeightPairingSlack>]
  constructor <;> intro h <;> linarith

/-- Slack is non-negative for safe systems. -/
theorem height_pairing_slack_nonneg_of_safe (d : <ModularJacobianHeightPairingDatum>)
    (h : IsHeightPairingSafe d) : 0 ≤ <HeightPairingSlack> d :=
  (height_pairing_safe_iff_slack_nonneg d).mp h

/-- Height pairing norm reconstructed from normalized ratio and regulator bound ceiling. -/
theorem height_pairing_norm_reconstruction (d : <ModularJacobianHeightPairingDatum>) :
    d.heightNorm = <NormalizedHeightPairingRatio> d * d.regulatorBound := by
  dsimp [<NormalizedHeightPairingRatio>]
  have h_ne : d.regulatorBound ≠ 0 := ne_of_gt d.bound_pos
  have hu : IsUnit d.regulatorBound := h_ne.isUnit
  exact (hu.div_mul_cancel d.heightNorm).symm

/-- Height-weighted bound is strictly positive. -/
theorem weighted_height_pairing_bound_pos (d : <ModularJacobianHeightPairingDatum>) :
    0 < weightedHeightPairingBound d := by
  dsimp [weightedHeightPairingBound]
  have h_prod : 0 < d.heightWeight * d.pairingTolerance :=
    mul_pos d.weight_pos d.tolerance_pos
  have h_sum : 0 < 1 + d.heightWeight * d.pairingTolerance := by linarith
  exact mul_pos d.bound_pos h_sum

/-- Linear scaling of canonical regulator capacity bound. -/
theorem canonical_regulator_capacity_scale (d : <ModularJacobianHeightPairingDatum>) (c : ℝ) (hc : 0 ≤ c) :
    0 ≤ c * <CanonicalRegulatorCapacityBound> d :=
  mul_nonneg hc (canonical_regulator_capacity_bound_nonneg d)

/-- Canonical regulator capacity bound is monotone in regulator bound ceiling. -/
theorem canonical_regulator_capacity_monotone (d : <ModularJacobianHeightPairingDatum>) (b : ℝ)
    (hb : d.regulatorBound ≤ b) :
    <CanonicalRegulatorCapacityBound> d ≤ b * d.regulatorCapacity := by
  dsimp [<CanonicalRegulatorCapacityBound>]
  nlinarith [d.capacity_pos]

/-- Defect is monotone in lower bounds on observed height pairing norm. -/
theorem height_pairing_defect_monotone (d : <ModularJacobianHeightPairingDatum>) (p : ℝ)
    (hp : p ≤ d.heightNorm) :
    d.regulatorBound - d.heightNorm ≤ d.regulatorBound - p := by
  linarith

/-- Slack is monotone in pairing tolerance parameter. -/
theorem height_pairing_slack_monotone_tolerance (d : <ModularJacobianHeightPairingDatum>) (t : ℝ)
    (ht : d.pairingTolerance ≤ t) :
    <HeightPairingSlack> d ≤ d.regulatorBound * t - d.heightNorm := by
  dsimp [<HeightPairingSlack>]
  nlinarith [d.bound_pos]

end <Namespace>
```
