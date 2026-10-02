# Template_ModularJacobianRegulatorPairing - Modular Jacobian Regulator Pairings & Bilinear Forms

Use this template for **modular Jacobian regulator pairings**, **canonical height bilinear forms**,
**Mordell-Weil lattice geometry**, and **stochastic network circulation capacity constraints**.

In arithmetic geometry and Fermat's Last Theorem / modular forms:
On the modular Jacobian J_0(N), the regulator pairing represents the positive-definite bilinear
form induced by the canonical Neron-Tate height on the Mordell-Weil lattice. Bilinear pairings
govern the arithmetic intersection numbers of Heegner points and Gross-Zagier derivatives,
bounding the covolume of independent cycle classes and precluding degenerate height subspaces.

In stochastic consensus and Markov non-equilibrium networks:
* Regulator pairings evaluate multi-cycle flux overlap and energy dissipation forms.
* The circulation capacity bound provides certified upper limits on steady-state cycle volume.
* The regulator pairing slack bounds probability current deviation from balanced harmonic state.
* The normalized ratio guarantees numerical stability away from collinear circulation channels.

## Main results
* `<ModularJacobianRegulatorPairingDatum>` - datum (regulatorPairing, pairingBound, circulationCapacity, pairingTolerance, pairingWeight)
* `<RegulatorPairingDefect>` - defect between pairing bound ceiling and observed regulator pairing
* `<NormalizedRegulatorPairingRatio>` - normalized ratio of observed regulator pairing to pairing bound
* `<CirculationCapacityBound>` - total circulation capacity bound scaled by pairing bound and capacity volume
* `<RegulatorPairingSlack>` - slack between tolerance-scaled bound and observed regulator pairing
* `<weightedRegulatorPairingBound>` - pairing-weighted bound accounting for pairing weight and tolerance
* `<IsRegulatorPairingBounded>` - predicate: observed regulator pairing is bounded by pairing bound
* `<IsCriticalRegulatorPairing>` - predicate: observed pairing reaches critical pairing threshold
* `<IsRegulatorPairingSafe>` - predicate: observed pairing is within certified pairing tolerance
* `<regulator_pairing_defect_nonneg_of_bounded>` - pairing defect is non-negative for bounded systems
* `<regulator_pairing_bounded_iff_defect_nonneg>` - boundedness is equivalent to non-negative pairing defect
* `<normalized_regulator_pairing_ratio_nonneg>` - normalized pairing ratio is non-negative
* `<normalized_regulator_pairing_ratio_le_one_of_bounded>` - normalized ratio is bounded by 1 for bounded systems
* `<circulation_capacity_bound_pos>` - circulation capacity bound is strictly positive
* `<circulation_capacity_bound_nonneg>` - circulation capacity bound is non-negative
* `<exact_regulator_pairing_implies_bounded>` - exact saturation implies bounded system
* `<exact_regulator_pairing_defect_zero>` - exact defect vanishes identically
* `<exact_regulator_pairing_ratio_one>` - exact saturation has normalized ratio 1
* `<regulator_pairing_safe_iff_slack_nonneg>` - safety is equivalent to non-negative pairing slack
* `<regulator_pairing_slack_nonneg_of_safe>` - slack is non-negative for safe systems
* `<regulator_pairing_reconstruction>` - regulator pairing reconstructed from normalized ratio and bound
* `<weighted_regulator_pairing_bound_pos>` - pairing-weighted bound is strictly positive
* `<circulation_capacity_scale>` - capacity bound scales non-negatively with positive scaling
* `<circulation_capacity_monotone>` - capacity bound is monotone in pairing bound ceiling
* `<regulator_pairing_defect_monotone>` - defect is monotone in lower bounds on observed regulator pairing
* `<regulator_pairing_slack_monotone_tolerance>` - slack is monotone in pairing tolerance parameter

## References
* FLT: `StochasticCCV/Core/ModularJacobianRegulatorPairing.lean`
* Gross, B., Zagier, D. (1986), *Heegner points and derivatives of L-series*, Inventiones Mathematicae 84, 225-320.
* Mazur, B., Tate, J. (1983), *Canonical height pairings via flat cohomology*, Arithmetic and Geometry, Vol. I, 195-237.
* Birch, B. J., Swinnerton-Dyer, H. P. F. (1965), *Notes on elliptic curves. II*, J. Reine Angew. Math. 218, 79-108.

## Tags
template, modular-jacobian, regulator-pairing, canonical-height, bilinear-form, markov-circulation, capacity-envelope

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

/-- Datum specifying modular Jacobian regulator pairing, pairing bound ceiling,
    circulation capacity volume, pairing tolerance, and pairing weight. -/
structure <ModularJacobianRegulatorPairingDatum> where
  regulatorPairing : ℝ
  pairingBound : ℝ
  circulationCapacity : ℝ
  pairingTolerance : ℝ
  pairingWeight : ℝ
  pairing_pos : 0 < regulatorPairing
  bound_pos : 0 < pairingBound
  capacity_pos : 0 < circulationCapacity
  tolerance_pos : 0 < pairingTolerance
  weight_pos : 0 < pairingWeight

/-- Defect between theoretical pairing bound ceiling and observed regulator pairing. -/
def <RegulatorPairingDefect> (d : <ModularJacobianRegulatorPairingDatum>) : ℝ :=
  d.pairingBound - d.regulatorPairing

/-- Normalized ratio of observed regulator pairing to pairing bound ceiling. -/
def <NormalizedRegulatorPairingRatio> (d : <ModularJacobianRegulatorPairingDatum>) : ℝ :=
  d.regulatorPairing / d.pairingBound

/-- Circulation capacity bound scaled by pairing bound and capacity volume. -/
def <CirculationCapacityBound> (d : <ModularJacobianRegulatorPairingDatum>) : ℝ :=
  d.pairingBound * d.circulationCapacity

/-- Regulator pairing slack between tolerance-scaled bound and observed regulator pairing. -/
def <RegulatorPairingSlack> (d : <ModularJacobianRegulatorPairingDatum>) : ℝ :=
  d.pairingBound * d.pairingTolerance - d.regulatorPairing

/-- Pairing-weighted bound accounting for pairing weight and tolerance. -/
def weightedRegulatorPairingBound (d : <ModularJacobianRegulatorPairingDatum>) : ℝ :=
  d.pairingBound * (1 + d.pairingWeight * d.pairingTolerance)

/-- Predicate: observed regulator pairing is bounded by the pairing bound ceiling. -/
def IsRegulatorPairingBounded (d : <ModularJacobianRegulatorPairingDatum>) : Prop :=
  d.regulatorPairing ≤ d.pairingBound

/-- Predicate: observed regulator pairing reaches the critical pairing threshold. -/
def IsCriticalRegulatorPairing (d : <ModularJacobianRegulatorPairingDatum>) : Prop :=
  d.regulatorPairing = d.pairingBound

/-- Predicate: observed regulator pairing is within certified pairing tolerance. -/
def IsRegulatorPairingSafe (d : <ModularJacobianRegulatorPairingDatum>) : Prop :=
  d.regulatorPairing ≤ d.pairingBound * d.pairingTolerance

/-- Pairing defect is non-negative for bounded systems. -/
theorem regulator_pairing_defect_nonneg_of_bounded (d : <ModularJacobianRegulatorPairingDatum>)
    (h : IsRegulatorPairingBounded d) : 0 ≤ <RegulatorPairingDefect> d := by
  dsimp [<RegulatorPairingDefect>, IsRegulatorPairingBounded] at *
  linarith

/-- Boundedness is equivalent to non-negative pairing defect. -/
theorem regulator_pairing_bounded_iff_defect_nonneg (d : <ModularJacobianRegulatorPairingDatum>) :
    IsRegulatorPairingBounded d ↔ 0 ≤ <RegulatorPairingDefect> d := by
  dsimp [IsRegulatorPairingBounded, <RegulatorPairingDefect>]
  constructor <;> intro h <;> linarith

/-- Normalized pairing ratio is non-negative. -/
theorem normalized_regulator_pairing_ratio_nonneg (d : <ModularJacobianRegulatorPairingDatum>) :
    0 ≤ <NormalizedRegulatorPairingRatio> d := by
  dsimp [<NormalizedRegulatorPairingRatio>]
  exact div_nonneg (le_of_lt d.pairing_pos) (le_of_lt d.bound_pos)

/-- Normalized pairing ratio is bounded by 1 for bounded systems. -/
theorem normalized_regulator_pairing_ratio_le_one_of_bounded (d : <ModularJacobianRegulatorPairingDatum>)
    (h : IsRegulatorPairingBounded d) : <NormalizedRegulatorPairingRatio> d ≤ 1 := by
  dsimp [<NormalizedRegulatorPairingRatio>, IsRegulatorPairingBounded] at *
  exact (div_le_one d.bound_pos).mpr h

/-- Circulation capacity bound is strictly positive. -/
theorem circulation_capacity_bound_pos (d : <ModularJacobianRegulatorPairingDatum>) :
    0 < <CirculationCapacityBound> d := by
  dsimp [<CirculationCapacityBound>]
  exact mul_pos d.bound_pos d.capacity_pos

/-- Circulation capacity bound is non-negative. -/
theorem circulation_capacity_bound_nonneg (d : <ModularJacobianRegulatorPairingDatum>) :
    0 ≤ <CirculationCapacityBound> d :=
  le_of_lt (circulation_capacity_bound_pos d)

/-- Exact pairing saturation implies bounded system. -/
theorem exact_regulator_pairing_implies_bounded (d : <ModularJacobianRegulatorPairingDatum>)
    (h : IsCriticalRegulatorPairing d) : IsRegulatorPairingBounded d := by
  dsimp [IsRegulatorPairingBounded, IsCriticalRegulatorPairing] at *
  linarith

/-- Exact pairing defect vanishes identically. -/
theorem exact_regulator_pairing_defect_zero (d : <ModularJacobianRegulatorPairingDatum>)
    (h : IsCriticalRegulatorPairing d) : <RegulatorPairingDefect> d = 0 := by
  dsimp [<RegulatorPairingDefect>, IsCriticalRegulatorPairing] at *
  rw [h]
  ring

/-- Exact pairing saturation has normalized ratio 1. -/
theorem exact_regulator_pairing_ratio_one (d : <ModularJacobianRegulatorPairingDatum>)
    (h : IsCriticalRegulatorPairing d) : <NormalizedRegulatorPairingRatio> d = 1 := by
  dsimp [<NormalizedRegulatorPairingRatio>, IsCriticalRegulatorPairing] at *
  rw [h]
  exact div_self (ne_of_gt d.bound_pos)

/-- Safety is equivalent to non-negative pairing slack. -/
theorem regulator_pairing_safe_iff_slack_nonneg (d : <ModularJacobianRegulatorPairingDatum>) :
    IsRegulatorPairingSafe d ↔ 0 ≤ <RegulatorPairingSlack> d := by
  dsimp [IsRegulatorPairingSafe, <RegulatorPairingSlack>]
  constructor <;> intro h <;> linarith

/-- Slack is non-negative for safe systems. -/
theorem regulator_pairing_slack_nonneg_of_safe (d : <ModularJacobianRegulatorPairingDatum>)
    (h : IsRegulatorPairingSafe d) : 0 ≤ <RegulatorPairingSlack> d :=
  (regulator_pairing_safe_iff_slack_nonneg d).mp h

/-- Regulator pairing reconstructed from normalized ratio and pairing bound ceiling. -/
theorem regulator_pairing_reconstruction (d : <ModularJacobianRegulatorPairingDatum>) :
    d.regulatorPairing = <NormalizedRegulatorPairingRatio> d * d.pairingBound := by
  dsimp [<NormalizedRegulatorPairingRatio>]
  have h_ne : d.pairingBound ≠ 0 := ne_of_gt d.bound_pos
  have hu : IsUnit d.pairingBound := h_ne.isUnit
  exact (hu.div_mul_cancel d.regulatorPairing).symm

/-- Pairing-weighted bound is strictly positive. -/
theorem weighted_regulator_pairing_bound_pos (d : <ModularJacobianRegulatorPairingDatum>) :
    0 < weightedRegulatorPairingBound d := by
  dsimp [weightedRegulatorPairingBound]
  have h_prod : 0 < d.pairingWeight * d.pairingTolerance :=
    mul_pos d.weight_pos d.tolerance_pos
  have h_sum : 0 < 1 + d.pairingWeight * d.pairingTolerance := by linarith
  exact mul_pos d.bound_pos h_sum

/-- Linear scaling of circulation capacity bound. -/
theorem circulation_capacity_scale (d : <ModularJacobianRegulatorPairingDatum>) (c : ℝ) (hc : 0 ≤ c) :
    0 ≤ c * <CirculationCapacityBound> d :=
  mul_nonneg hc (circulation_capacity_bound_nonneg d)

/-- Circulation capacity bound is monotone in pairing bound ceiling. -/
theorem circulation_capacity_monotone (d : <ModularJacobianRegulatorPairingDatum>) (b : ℝ)
    (hb : d.pairingBound ≤ b) :
    <CirculationCapacityBound> d ≤ b * d.circulationCapacity := by
  dsimp [<CirculationCapacityBound>]
  nlinarith [d.capacity_pos]

/-- Defect is monotone in lower bounds on observed regulator pairing. -/
theorem regulator_pairing_defect_monotone (d : <ModularJacobianRegulatorPairingDatum>) (p : ℝ)
    (hp : p ≤ d.regulatorPairing) :
    d.pairingBound - d.regulatorPairing ≤ d.pairingBound - p := by
  linarith

/-- Slack is monotone in pairing tolerance parameter. -/
theorem regulator_pairing_slack_monotone_tolerance (d : <ModularJacobianRegulatorPairingDatum>) (t : ℝ)
    (ht : d.pairingTolerance ≤ t) :
    <RegulatorPairingSlack> d ≤ d.pairingBound * t - d.regulatorPairing := by
  dsimp [<RegulatorPairingSlack>]
  nlinarith [d.bound_pos]

end <Namespace>
```
