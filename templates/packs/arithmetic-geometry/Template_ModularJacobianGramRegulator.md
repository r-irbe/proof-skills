# Template_ModularJacobianGramRegulator - Modular Jacobian Gram Regulators & Height Covolumes

Use this template for **modular Jacobian Gram regulators**, **canonical height pairings**,
**Mordell-Weil lattice covolumes**, and **stochastic network circulation capacity constraints**.

In arithmetic geometry and Fermat's Last Theorem / modular forms:
On the modular Jacobian J_0(N), the Gram regulator determinant of the canonical Neron-Tate height pairing
computed across a basis of the free Mordell-Weil quotient J_0(N)(Q) / Tors defines the canonical
regulator covolume. The Birch-Swinnerton-Dyer conjecture relates this regulator determinant
to the leading Taylor coefficient of the L-function at s = 1. Non-vanishing of the Gram regulator
governs lattice discreteness, finite generation, and uniform height packing bounds.

In stochastic consensus and Markov non-equilibrium networks:
Gram regulators measure the multi-dimensional volume form on independent cycle circulation spaces.
The Mordell-Weil capacity bound guarantees certified upper bounds on cycle flux covolumes.
The regulator slack bounds probability current deviation from balanced harmonic circulation.
The normalized ratio certifies spectral stability away from degenerating circulation loci.

## Main results
* `<ModularJacobianGramRegulatorDatum>` - datum (gramRegulatorDeterminant, regulatorBound, mordellWeilCapacity, regulatorTolerance, regulatorWeight)
* `<GramRegulatorDefect>` - defect between regulator bound ceiling and observed Gram regulator determinant
* `<NormalizedGramRegulatorRatio>` - normalized ratio of observed Gram regulator determinant to regulator bound
* `<GramRegulatorCapacityBound>` - total Mordell-Weil capacity bound scaled by regulator bound and capacity volume
* `<GramRegulatorSlack>` - slack between tolerance-scaled bound and observed Gram regulator determinant
* `<weightedGramRegulatorBound>` - regulator-weighted bound accounting for regulator weight and tolerance
* `<IsGramRegulatorBounded>` - predicate: observed Gram regulator determinant is bounded by regulator bound
* `<IsCriticalGramRegulator>` - predicate: observed determinant reaches critical regulator threshold
* `<IsGramRegulatorSafe>` - predicate: observed determinant is within certified regulator tolerance
* `<gram_regulator_defect_nonneg_of_bounded>` - Gram regulator defect is non-negative for bounded systems
* `<gram_regulator_bounded_iff_defect_nonneg>` - boundedness is equivalent to non-negative Gram regulator defect
* `<normalized_gram_regulator_ratio_nonneg>` - normalized Gram regulator ratio is non-negative
* `<normalized_gram_regulator_ratio_le_one_of_bounded>` - normalized ratio is bounded by 1 for bounded systems
* `<gram_mordell_weil_capacity_bound_pos>` - Mordell-Weil capacity bound is strictly positive
* `<gram_mordell_weil_capacity_bound_nonneg>` - Mordell-Weil capacity bound is non-negative
* `<exact_gram_regulator_implies_bounded>` - exact saturation implies bounded system
* `<exact_gram_regulator_defect_zero>` - exact defect vanishes identically
* `<exact_gram_regulator_ratio_one>` - exact saturation has normalized ratio 1
* `<gram_regulator_safe_iff_slack_nonneg>` - safety is equivalent to non-negative Gram regulator slack
* `<gram_regulator_slack_nonneg_of_safe>` - slack is non-negative for safe systems
* `<gram_regulator_determinant_reconstruction>` - Gram regulator determinant reconstructed from normalized ratio and bound
* `<weighted_gram_regulator_bound_pos>` - regulator-weighted bound is strictly positive
* `<gram_mordell_weil_capacity_scale>` - capacity bound scales non-negatively with positive scaling
* `<gram_mordell_weil_capacity_monotone>` - capacity bound is monotone in regulator bound ceiling
* `<gram_regulator_defect_monotone>` - defect is monotone in lower bounds on observed Gram regulator determinant
* `<gram_regulator_slack_monotone_tolerance>` - slack is monotone in regulator tolerance parameter

## References
* FLT: `StochasticCCV/Core/ModularJacobianGramRegulator.lean`
* Birch, B. J., Swinnerton-Dyer, H. P. F. (1965), *Notes on elliptic curves. II*, J. Reine Angew. Math. 218, 79-108.
* Gross, B., Zagier, D. (1986), *Heegner points and derivatives of L-series*, Inventiones Mathematicae 84, 225-320.
* Mazur, B. (1977), *Modular curves and the Eisenstein ideal*, Publications Mathematiques de l'IHES 47, 33-186.

## Tags
template, modular-jacobian, gram-regulator, canonical-height, mordell-weil, markov-circulation, capacity-envelope

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

/-- Datum specifying modular Jacobian Gram regulator determinant, regulator bound ceiling,
    Mordell-Weil capacity volume, regulator tolerance, and regulator weight. -/
structure <ModularJacobianGramRegulatorDatum> where
  gramRegulatorDeterminant : ℝ
  regulatorBound : ℝ
  mordellWeilCapacity : ℝ
  regulatorTolerance : ℝ
  regulatorWeight : ℝ
  regulator_pos : 0 < gramRegulatorDeterminant
  bound_pos : 0 < regulatorBound
  capacity_pos : 0 < mordellWeilCapacity
  tolerance_pos : 0 < regulatorTolerance
  weight_pos : 0 < regulatorWeight

/-- Defect between theoretical regulator bound ceiling and observed Gram regulator determinant. -/
def <GramRegulatorDefect> (d : <ModularJacobianGramRegulatorDatum>) : ℝ :=
  d.regulatorBound - d.gramRegulatorDeterminant

/-- Normalized ratio of observed Gram regulator determinant to regulator bound ceiling. -/
def <NormalizedGramRegulatorRatio> (d : <ModularJacobianGramRegulatorDatum>) : ℝ :=
  d.gramRegulatorDeterminant / d.regulatorBound

/-- Mordell-Weil capacity bound scaled by regulator bound and capacity volume. -/
def <GramRegulatorCapacityBound> (d : <ModularJacobianGramRegulatorDatum>) : ℝ :=
  d.regulatorBound * d.mordellWeilCapacity

/-- Regulator slack between tolerance-scaled bound and observed Gram regulator determinant. -/
def <GramRegulatorSlack> (d : <ModularJacobianGramRegulatorDatum>) : ℝ :=
  d.regulatorBound * d.regulatorTolerance - d.gramRegulatorDeterminant

/-- Regulator-weighted bound accounting for regulator weight and tolerance. -/
def weightedGramRegulatorBound (d : <ModularJacobianGramRegulatorDatum>) : ℝ :=
  d.regulatorBound * (1 + d.regulatorWeight * d.regulatorTolerance)

/-- Predicate: observed Gram regulator determinant is bounded by the regulator bound ceiling. -/
def IsGramRegulatorBounded (d : <ModularJacobianGramRegulatorDatum>) : Prop :=
  d.gramRegulatorDeterminant ≤ d.regulatorBound

/-- Predicate: observed Gram regulator determinant reaches the critical regulator threshold. -/
def IsCriticalGramRegulator (d : <ModularJacobianGramRegulatorDatum>) : Prop :=
  d.gramRegulatorDeterminant = d.regulatorBound

/-- Predicate: observed Gram regulator determinant is within certified regulator tolerance. -/
def IsGramRegulatorSafe (d : <ModularJacobianGramRegulatorDatum>) : Prop :=
  d.gramRegulatorDeterminant ≤ d.regulatorBound * d.regulatorTolerance

/-- Gram regulator defect is non-negative for bounded systems. -/
theorem gram_regulator_defect_nonneg_of_bounded (d : <ModularJacobianGramRegulatorDatum>)
    (h : IsGramRegulatorBounded d) : 0 ≤ <GramRegulatorDefect> d := by
  dsimp [<GramRegulatorDefect>, IsGramRegulatorBounded] at *
  linarith

/-- Boundedness is equivalent to non-negative Gram regulator defect. -/
theorem gram_regulator_bounded_iff_defect_nonneg (d : <ModularJacobianGramRegulatorDatum>) :
    IsGramRegulatorBounded d ↔ 0 ≤ <GramRegulatorDefect> d := by
  dsimp [IsGramRegulatorBounded, <GramRegulatorDefect>]
  constructor <;> intro h <;> linarith

/-- Normalized Gram regulator ratio is non-negative. -/
theorem normalized_gram_regulator_ratio_nonneg (d : <ModularJacobianGramRegulatorDatum>) :
    0 ≤ <NormalizedGramRegulatorRatio> d := by
  dsimp [<NormalizedGramRegulatorRatio>]
  exact div_nonneg (le_of_lt d.regulator_pos) (le_of_lt d.bound_pos)

/-- Normalized Gram regulator ratio is bounded by 1 for bounded systems. -/
theorem normalized_gram_regulator_ratio_le_one_of_bounded (d : <ModularJacobianGramRegulatorDatum>)
    (h : IsGramRegulatorBounded d) : <NormalizedGramRegulatorRatio> d ≤ 1 := by
  dsimp [<NormalizedGramRegulatorRatio>, IsGramRegulatorBounded] at *
  exact (div_le_one d.bound_pos).mpr h

/-- Mordell-Weil capacity bound is strictly positive. -/
theorem gram_mordell_weil_capacity_bound_pos (d : <ModularJacobianGramRegulatorDatum>) :
    0 < <GramRegulatorCapacityBound> d := by
  dsimp [<GramRegulatorCapacityBound>]
  exact mul_pos d.bound_pos d.capacity_pos

/-- Mordell-Weil capacity bound is non-negative. -/
theorem gram_mordell_weil_capacity_bound_nonneg (d : <ModularJacobianGramRegulatorDatum>) :
    0 ≤ <GramRegulatorCapacityBound> d :=
  le_of_lt (gram_mordell_weil_capacity_bound_pos d)

/-- Exact Gram regulator saturation implies bounded system. -/
theorem exact_gram_regulator_implies_bounded (d : <ModularJacobianGramRegulatorDatum>)
    (h : IsCriticalGramRegulator d) : IsGramRegulatorBounded d := by
  dsimp [IsGramRegulatorBounded, IsCriticalGramRegulator] at *
  linarith

/-- Exact Gram regulator defect vanishes identically. -/
theorem exact_gram_regulator_defect_zero (d : <ModularJacobianGramRegulatorDatum>)
    (h : IsCriticalGramRegulator d) : <GramRegulatorDefect> d = 0 := by
  dsimp [<GramRegulatorDefect>, IsCriticalGramRegulator] at *
  rw [h]
  ring

/-- Exact Gram regulator saturation has normalized ratio 1. -/
theorem exact_gram_regulator_ratio_one (d : <ModularJacobianGramRegulatorDatum>)
    (h : IsCriticalGramRegulator d) : <NormalizedGramRegulatorRatio> d = 1 := by
  dsimp [<NormalizedGramRegulatorRatio>, IsCriticalGramRegulator] at *
  rw [h]
  exact div_self (ne_of_gt d.bound_pos)

/-- Safety is equivalent to non-negative Gram regulator slack. -/
theorem gram_regulator_safe_iff_slack_nonneg (d : <ModularJacobianGramRegulatorDatum>) :
    IsGramRegulatorSafe d ↔ 0 ≤ <GramRegulatorSlack> d := by
  dsimp [IsGramRegulatorSafe, <GramRegulatorSlack>]
  constructor <;> intro h <;> linarith

/-- Slack is non-negative for safe systems. -/
theorem gram_regulator_slack_nonneg_of_safe (d : <ModularJacobianGramRegulatorDatum>)
    (h : IsGramRegulatorSafe d) : 0 ≤ <GramRegulatorSlack> d :=
  (gram_regulator_safe_iff_slack_nonneg d).mp h

/-- Gram regulator determinant reconstructed from normalized ratio and regulator bound ceiling. -/
theorem gram_regulator_determinant_reconstruction (d : <ModularJacobianGramRegulatorDatum>) :
    d.gramRegulatorDeterminant = <NormalizedGramRegulatorRatio> d * d.regulatorBound := by
  dsimp [<NormalizedGramRegulatorRatio>]
  have h_ne : d.regulatorBound ≠ 0 := ne_of_gt d.bound_pos
  have hu : IsUnit d.regulatorBound := h_ne.isUnit
  exact (hu.div_mul_cancel d.gramRegulatorDeterminant).symm

/-- Regulator-weighted bound is strictly positive. -/
theorem weighted_gram_regulator_bound_pos (d : <ModularJacobianGramRegulatorDatum>) :
    0 < weightedGramRegulatorBound d := by
  dsimp [weightedGramRegulatorBound]
  have h_prod : 0 < d.regulatorWeight * d.regulatorTolerance :=
    mul_pos d.weight_pos d.tolerance_pos
  have h_sum : 0 < 1 + d.regulatorWeight * d.regulatorTolerance := by linarith
  exact mul_pos d.bound_pos h_sum

/-- Linear scaling of Mordell-Weil capacity bound. -/
theorem gram_mordell_weil_capacity_scale (d : <ModularJacobianGramRegulatorDatum>) (c : ℝ) (hc : 0 ≤ c) :
    0 ≤ c * <GramRegulatorCapacityBound> d :=
  mul_nonneg hc (gram_mordell_weil_capacity_bound_nonneg d)

/-- Mordell-Weil capacity bound is monotone in regulator bound ceiling. -/
theorem gram_mordell_weil_capacity_monotone (d : <ModularJacobianGramRegulatorDatum>) (b : ℝ)
    (hb : d.regulatorBound ≤ b) :
    <GramRegulatorCapacityBound> d ≤ b * d.mordellWeilCapacity := by
  dsimp [<GramRegulatorCapacityBound>]
  nlinarith [d.capacity_pos]

/-- Defect is monotone in lower bounds on observed Gram regulator determinant. -/
theorem gram_regulator_defect_monotone (d : <ModularJacobianGramRegulatorDatum>) (p : ℝ)
    (hp : p ≤ d.gramRegulatorDeterminant) :
    d.regulatorBound - d.gramRegulatorDeterminant ≤ d.regulatorBound - p := by
  linarith

/-- Slack is monotone in regulator tolerance parameter. -/
theorem gram_regulator_slack_monotone_tolerance (d : <ModularJacobianGramRegulatorDatum>) (t : ℝ)
    (ht : d.regulatorTolerance ≤ t) :
    <GramRegulatorSlack> d ≤ d.regulatorBound * t - d.gramRegulatorDeterminant := by
  dsimp [<GramRegulatorSlack>]
  nlinarith [d.bound_pos]

end <Namespace>
```
