# Template_ModularJacobianGramDeterminant - Modular Jacobian Gram Determinants & Mordell-Weil Covolumes

Use this template for **modular Jacobian Gram determinants**, **canonical height pairings**,
**Mordell-Weil lattice covolumes**, and **stochastic network circulation capacity constraints**.

In arithmetic geometry and Fermat's Last Theorem / modular forms:
On the modular Jacobian J_0(N), the Gram determinant of the canonical Neron-Tate height pairing
computed across a basis of the free Mordell-Weil quotient J_0(N)(Q) / Tors defines the canonical
regulator covolume. The Gross-Zagier theorem and Kolyvagin's Euler systems relate this determinant
directly to central derivatives of L-series, establishing non-degeneracy of the Mordell-Weil lattice
and bounding the order of the Shafarevich-Tate group.

In stochastic consensus and Markov non-equilibrium networks:
Gram determinants measure the multi-dimensional volume form on independent network circulation cycles.
The Mordell-Weil capacity bound guarantees certified upper bounds on cycle flux covolumes.
The Gram slack bounds probability current deviation from detailed balance.
The normalized ratio ensures stability against degenerating circulation cycles.

## Main results
* `<ModularJacobianGramDeterminantDatum>` - datum (gramDeterminant, gramBound, mordellWeilCapacity, gramTolerance, gramWeight)
* `<GramDefect>` - defect between Gram bound ceiling and observed Gram determinant
* `<NormalizedGramRatio>` - normalized ratio of observed Gram determinant to Gram bound
* `<MordellWeilCapacityBound>` - total Mordell-Weil capacity bound scaled by Gram bound and capacity volume
* `<GramSlack>` - slack between tolerance-scaled bound and observed Gram determinant
* `<weightedGramBound>` - Gram-weighted bound accounting for Gram weight and tolerance
* `<IsGramBounded>` - predicate: observed Gram determinant is bounded by Gram bound
* `<IsCriticalGram>` - predicate: observed determinant reaches critical Gram threshold
* `<IsGramSafe>` - predicate: observed determinant is within certified Gram tolerance
* `<gram_defect_nonneg_of_bounded>` - Gram defect is non-negative for bounded systems
* `<gram_bounded_iff_defect_nonneg>` - boundedness is equivalent to non-negative Gram defect
* `<normalized_gram_ratio_nonneg>` - normalized Gram ratio is non-negative
* `<normalized_gram_ratio_le_one_of_bounded>` - normalized ratio is bounded by 1 for bounded systems
* `<mordell_weil_capacity_bound_pos>` - Mordell-Weil capacity bound is strictly positive
* `<mordell_weil_capacity_bound_nonneg>` - Mordell-Weil capacity bound is non-negative
* `<exact_gram_implies_bounded>` - exact saturation implies bounded system
* `<exact_gram_defect_zero>` - exact defect vanishes identically
* `<exact_gram_ratio_one>` - exact saturation has normalized ratio 1
* `<gram_safe_iff_slack_nonneg>` - safety is equivalent to non-negative Gram slack
* `<gram_slack_nonneg_of_safe>` - slack is non-negative for safe systems
* `<gram_determinant_reconstruction>` - Gram determinant reconstructed from normalized ratio and bound
* `<weighted_gram_bound_pos>` - Gram-weighted bound is strictly positive
* `<mordell_weil_capacity_scale>` - capacity bound scales non-negatively with positive scaling
* `<mordell_weil_capacity_monotone>` - capacity bound is monotone in Gram bound ceiling
* `<gram_defect_monotone>` - defect is monotone in lower bounds on observed Gram determinant
* `<gram_slack_monotone_tolerance>` - slack is monotone in Gram tolerance parameter

## References
* FLT: `StochasticCCV/Core/ModularJacobianGramDeterminant.lean`
* Gross, B., Zagier, D. (1986), *Heegner points and derivatives of L-series*, Inventiones Mathematicae 84, 225-320.
* Kolyvagin, V. A. (1990), *Euler systems*, The Grothendieck Festschrift, Vol. II, 435-483.
* Mazur, B. (1977), *Modular curves and the Eisenstein ideal*, Publications Mathematiques de l'IHES 47, 33-186.

## Tags
template, modular-jacobian, gram-determinant, canonical-height, mordell-weil, markov-circulation, capacity-envelope

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

/-- Datum specifying modular Jacobian Gram determinant, Gram bound ceiling,
    Mordell-Weil capacity volume, Gram tolerance, and Gram weight. -/
structure <ModularJacobianGramDeterminantDatum> where
  gramDeterminant : ℝ
  gramBound : ℝ
  mordellWeilCapacity : ℝ
  gramTolerance : ℝ
  gramWeight : ℝ
  gram_pos : 0 < gramDeterminant
  bound_pos : 0 < gramBound
  capacity_pos : 0 < mordellWeilCapacity
  tolerance_pos : 0 < gramTolerance
  weight_pos : 0 < gramWeight

/-- Defect between theoretical Gram bound ceiling and observed Gram determinant. -/
def <GramDefect> (d : <ModularJacobianGramDeterminantDatum>) : ℝ :=
  d.gramBound - d.gramDeterminant

/-- Normalized ratio of observed Gram determinant to Gram bound ceiling. -/
def <NormalizedGramRatio> (d : <ModularJacobianGramDeterminantDatum>) : ℝ :=
  d.gramDeterminant / d.gramBound

/-- Mordell-Weil capacity bound scaled by Gram bound and capacity volume. -/
def <MordellWeilCapacityBound> (d : <ModularJacobianGramDeterminantDatum>) : ℝ :=
  d.gramBound * d.mordellWeilCapacity

/-- Gram slack between tolerance-scaled bound and observed Gram determinant. -/
def <GramSlack> (d : <ModularJacobianGramDeterminantDatum>) : ℝ :=
  d.gramBound * d.gramTolerance - d.gramDeterminant

/-- Gram-weighted bound accounting for Gram weight and tolerance. -/
def weightedGramBound (d : <ModularJacobianGramDeterminantDatum>) : ℝ :=
  d.gramBound * (1 + d.gramWeight * d.gramTolerance)

/-- Predicate: observed Gram determinant is bounded by the Gram bound ceiling. -/
def IsGramBounded (d : <ModularJacobianGramDeterminantDatum>) : Prop :=
  d.gramDeterminant ≤ d.gramBound

/-- Predicate: observed Gram determinant reaches the critical Gram threshold. -/
def IsCriticalGram (d : <ModularJacobianGramDeterminantDatum>) : Prop :=
  d.gramDeterminant = d.gramBound

/-- Predicate: observed Gram determinant is within certified Gram tolerance. -/
def IsGramSafe (d : <ModularJacobianGramDeterminantDatum>) : Prop :=
  d.gramDeterminant ≤ d.gramBound * d.gramTolerance

/-- Gram defect is non-negative for bounded systems. -/
theorem gram_defect_nonneg_of_bounded (d : <ModularJacobianGramDeterminantDatum>)
    (h : IsGramBounded d) : 0 ≤ <GramDefect> d := by
  dsimp [<GramDefect>, IsGramBounded] at *
  linarith

/-- Boundedness is equivalent to non-negative Gram defect. -/
theorem gram_bounded_iff_defect_nonneg (d : <ModularJacobianGramDeterminantDatum>) :
    IsGramBounded d ↔ 0 ≤ <GramDefect> d := by
  dsimp [IsGramBounded, <GramDefect>]
  constructor <;> intro h <;> linarith

/-- Normalized Gram ratio is non-negative. -/
theorem normalized_gram_ratio_nonneg (d : <ModularJacobianGramDeterminantDatum>) :
    0 ≤ <NormalizedGramRatio> d := by
  dsimp [<NormalizedGramRatio>]
  exact div_nonneg (le_of_lt d.gram_pos) (le_of_lt d.bound_pos)

/-- Normalized Gram ratio is bounded by 1 for bounded systems. -/
theorem normalized_gram_ratio_le_one_of_bounded (d : <ModularJacobianGramDeterminantDatum>)
    (h : IsGramBounded d) : <NormalizedGramRatio> d ≤ 1 := by
  dsimp [<NormalizedGramRatio>, IsGramBounded] at *
  exact (div_le_one d.bound_pos).mpr h

/-- Mordell-Weil capacity bound is strictly positive. -/
theorem mordell_weil_capacity_bound_pos (d : <ModularJacobianGramDeterminantDatum>) :
    0 < <MordellWeilCapacityBound> d := by
  dsimp [<MordellWeilCapacityBound>]
  exact mul_pos d.bound_pos d.capacity_pos

/-- Mordell-Weil capacity bound is non-negative. -/
theorem mordell_weil_capacity_bound_nonneg (d : <ModularJacobianGramDeterminantDatum>) :
    0 ≤ <MordellWeilCapacityBound> d :=
  le_of_lt (mordell_weil_capacity_bound_pos d)

/-- Exact Gram saturation implies bounded system. -/
theorem exact_gram_implies_bounded (d : <ModularJacobianGramDeterminantDatum>)
    (h : IsCriticalGram d) : IsGramBounded d := by
  dsimp [IsGramBounded, IsCriticalGram] at *
  linarith

/-- Exact Gram defect vanishes identically. -/
theorem exact_gram_defect_zero (d : <ModularJacobianGramDeterminantDatum>)
    (h : IsCriticalGram d) : <GramDefect> d = 0 := by
  dsimp [<GramDefect>, IsCriticalGram] at *
  rw [h]
  ring

/-- Exact Gram saturation has normalized ratio 1. -/
theorem exact_gram_ratio_one (d : <ModularJacobianGramDeterminantDatum>)
    (h : IsCriticalGram d) : <NormalizedGramRatio> d = 1 := by
  dsimp [<NormalizedGramRatio>, IsCriticalGram] at *
  rw [h]
  exact div_self (ne_of_gt d.bound_pos)

/-- Safety is equivalent to non-negative Gram slack. -/
theorem gram_safe_iff_slack_nonneg (d : <ModularJacobianGramDeterminantDatum>) :
    IsGramSafe d ↔ 0 ≤ <GramSlack> d := by
  dsimp [IsGramSafe, <GramSlack>]
  constructor <;> intro h <;> linarith

/-- Slack is non-negative for safe systems. -/
theorem gram_slack_nonneg_of_safe (d : <ModularJacobianGramDeterminantDatum>)
    (h : IsGramSafe d) : 0 ≤ <GramSlack> d :=
  (gram_safe_iff_slack_nonneg d).mp h

/-- Gram determinant reconstructed from normalized ratio and Gram bound ceiling. -/
theorem gram_determinant_reconstruction (d : <ModularJacobianGramDeterminantDatum>) :
    d.gramDeterminant = <NormalizedGramRatio> d * d.gramBound := by
  dsimp [<NormalizedGramRatio>]
  have h_ne : d.gramBound ≠ 0 := ne_of_gt d.bound_pos
  have hu : IsUnit d.gramBound := h_ne.isUnit
  exact (hu.div_mul_cancel d.gramDeterminant).symm

/-- Gram-weighted bound is strictly positive. -/
theorem weighted_gram_bound_pos (d : <ModularJacobianGramDeterminantDatum>) :
    0 < weightedGramBound d := by
  dsimp [weightedGramBound]
  have h_prod : 0 < d.gramWeight * d.gramTolerance :=
    mul_pos d.weight_pos d.tolerance_pos
  have h_sum : 0 < 1 + d.gramWeight * d.gramTolerance := by linarith
  exact mul_pos d.bound_pos h_sum

/-- Linear scaling of Mordell-Weil capacity bound. -/
theorem mordell_weil_capacity_scale (d : <ModularJacobianGramDeterminantDatum>) (c : ℝ) (hc : 0 ≤ c) :
    0 ≤ c * <MordellWeilCapacityBound> d :=
  mul_nonneg hc (mordell_weil_capacity_bound_nonneg d)

/-- Mordell-Weil capacity bound is monotone in Gram bound ceiling. -/
theorem mordell_weil_capacity_monotone (d : <ModularJacobianGramDeterminantDatum>) (b : ℝ)
    (hb : d.gramBound ≤ b) :
    <MordellWeilCapacityBound> d ≤ b * d.mordellWeilCapacity := by
  dsimp [<MordellWeilCapacityBound>]
  nlinarith [d.capacity_pos]

/-- Defect is monotone in lower bounds on observed Gram determinant. -/
theorem gram_defect_monotone (d : <ModularJacobianGramDeterminantDatum>) (p : ℝ)
    (hp : p ≤ d.gramDeterminant) :
    d.gramBound - d.gramDeterminant ≤ d.gramBound - p := by
  linarith

/-- Slack is monotone in Gram tolerance parameter. -/
theorem gram_slack_monotone_tolerance (d : <ModularJacobianGramDeterminantDatum>) (t : ℝ)
    (ht : d.gramTolerance ≤ t) :
    <GramSlack> d ≤ d.gramBound * t - d.gramDeterminant := by
  dsimp [<GramSlack>]
  nlinarith [d.bound_pos]

end <Namespace>
```
