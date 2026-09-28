# Template_ModularJacobianMordellWeil - Modular Jacobian Mordell-Weil Lattices & Regulators

Use this template for **modular Jacobian Mordell-Weil lattices**, **Gram regulator determinants**,
**finite generation decompositions**, and **non-degenerate quadratic energy envelopes**.

In arithmetic geometry and Fermat's Last Theorem / modular forms:
Let J_0(N) be the modular Jacobian of curve X_0(N) over a number field K.
The Mordell-Weil theorem asserts that the group of K-rational points J_0(N)(K) is
a finitely generated abelian group:
  J_0(N)(K) = Z^r + J_0(N)(K)_tors.
The Mordell-Weil lattice Lambda = J_0(N)(K) / tors equipped with the Neron-Tate height pairing
< ., . >_NT has rank r and strictly positive Gram regulator
  Reg(J_0(N)/K) = det(<P_i, P_j>_NT) > 0,
which enters the Birch and Swinnerton-Dyer leading coefficient formula.

In stochastic consensus and Markov flow networks:
The Mordell-Weil lattice represents the discrete lattice of independent consensus
modes and harmonic cycle currents across the multi-agent network. The Gram regulator
bounds the fundamental domain volume of independent Markov flows, certifying that
multi-agent drift remains confined within calibrated safety envelopes.

## Main results
* `<ModularJacobianMordellWeilDatum>` - datum (mordellWeilNorm, mordellWeilBound, gramRegulator, latticeTolerance, curvatureWeight)
* `<mordellWeilDefect>` - defect between theoretical bound ceiling and observed Mordell-Weil norm
* `<normalizedMordellWeilRatio>` - normalized ratio of observed Mordell-Weil norm to bound ceiling
* `<gramRegulatorBound>` - Gram regulator capacity bound scaled by bound ceiling and volume
* `<mordellWeilSlack>` - slack between tolerance-scaled bound and observed lattice norm
* `<weightedMordellWeilBound>` - curvature-weighted bound accounting for non-degenerate Gram geometry
* `<IsMordellWeilBounded>` - predicate: observed Mordell-Weil norm is bounded by bound ceiling
* `<IsExactMordellWeil>` - predicate: observed Mordell-Weil norm saturates theoretical bound ceiling
* `<IsMordellWeilLatticeSafe>` - predicate: observed Mordell-Weil norm is within certified lattice tolerance
* `<mordell_weil_defect_nonneg_of_bounded>` - Mordell-Weil defect is non-negative for bounded systems
* `<mordell_weil_bounded_iff_defect_nonneg>` - boundedness is equivalent to non-negative defect
* `<normalized_mordell_weil_ratio_nonneg>` - normalized Mordell-Weil ratio is non-negative
* `<normalized_mordell_weil_ratio_le_one_of_bounded>` - normalized ratio is bounded by 1 for bounded systems
* `<gram_regulator_bound_pos>` - Gram regulator capacity bound is strictly positive
* `<gram_regulator_bound_nonneg>` - Gram regulator capacity bound is non-negative
* `<exact_mordell_weil_implies_bounded>` - exact saturation implies bounded system
* `<exact_mordell_weil_defect_zero>` - exact defect vanishes identically
* `<exact_mordell_weil_ratio_one>` - exact saturation has normalized ratio 1
* `<mordell_weil_lattice_safe_iff_slack_nonneg>` - lattice safety is equivalent to non-negative slack
* `<mordell_weil_slack_nonneg_of_safe>` - slack is non-negative for lattice-safe systems
* `<mordell_weil_norm_reconstruction>` - Mordell-Weil norm reconstructed from normalized ratio and bound
* `<weighted_mordell_weil_bound_pos>` - curvature-weighted bound is strictly positive
* `<gram_regulator_capacity_scale>` - Gram regulator bound scales non-negatively with positive scaling
* `<gram_regulator_capacity_monotone>` - Gram regulator bound is monotone in bound ceiling
* `<mordell_weil_defect_monotone>` - defect is monotone in lower bounds on observed norm
* `<mordell_weil_slack_monotone_tolerance>` - slack is monotone in lattice tolerance parameter

## References
* FLT: `StochasticCCV/Core/ModularJacobianMordellWeil.lean`
* Mordell, L. J. (1922), *On the rational solutions of the indeterminate equations of the third and fourth degrees*, Proc. Cambridge Philos. Soc. 21, 179-192.
* Weil, A. (1928), *L'arithmetique sur les courbes algebriques*, Acta Math. 52, 281-315.
* Mazur, B. (1977), *Modular curves and the Eisenstein ideal*, Publ. Math. IHES 47, 33-186.

## Tags
template, modular-jacobian, mordell-weil, lattice, gram-regulator, quadratic-energy, markov-flow

```lean
/-
Copyright (c) 2026 <Project> Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: <Project> Contributors
SPDX-License-Identifier: Apache-2.0
-/

import Mathlib.Data.Real.Basic
import Mathlib.Tactic

set_option autoImplicit false
set_option linter.unusedVariables false
set_option linter.unusedSectionVars false
set_option linter.unusedSimpArgs false

noncomputable section

namespace <Project>.<Subpackage>

structure <ModularJacobianMordellWeilDatum> where
  mordellWeilNorm : Real
  mordellWeilBound : Real
  gramRegulator : Real
  latticeTolerance : Real
  curvatureWeight : Real
  norm_pos : 0 < mordellWeilNorm
  bound_pos : 0 < mordellWeilBound
  regulator_pos : 0 < gramRegulator
  tolerance_pos : 0 < latticeTolerance
  weight_pos : 0 < curvatureWeight

def <mordellWeilDefect> (d : <ModularJacobianMordellWeilDatum>) : Real :=
  d.mordellWeilBound - d.mordellWeilNorm

def <normalizedMordellWeilRatio> (d : <ModularJacobianMordellWeilDatum>) : Real :=
  d.mordellWeilNorm / d.mordellWeilBound

def <gramRegulatorBound> (d : <ModularJacobianMordellWeilDatum>) : Real :=
  d.mordellWeilBound * d.gramRegulator

def <mordellWeilSlack> (d : <ModularJacobianMordellWeilDatum>) : Real :=
  d.mordellWeilBound * d.latticeTolerance - d.mordellWeilNorm

def <weightedMordellWeilBound> (d : <ModularJacobianMordellWeilDatum>) : Real :=
  d.mordellWeilBound * (1 + d.curvatureWeight * d.latticeTolerance)

def <IsMordellWeilBounded> (d : <ModularJacobianMordellWeilDatum>) : Prop :=
  d.mordellWeilNorm <= d.mordellWeilBound

def <IsExactMordellWeil> (d : <ModularJacobianMordellWeilDatum>) : Prop :=
  d.mordellWeilNorm = d.mordellWeilBound

def <IsMordellWeilLatticeSafe> (d : <ModularJacobianMordellWeilDatum>) : Prop :=
  d.mordellWeilNorm <= d.mordellWeilBound * d.latticeTolerance

theorem <mordell_weil_defect_nonneg_of_bounded> (d : <ModularJacobianMordellWeilDatum>)
    (h : <IsMordellWeilBounded> d) : 0 <= <mordellWeilDefect> d := by
  dsimp [<mordellWeilDefect>, <IsMordellWeilBounded>] at *
  linarith

theorem <mordell_weil_bounded_iff_defect_nonneg> (d : <ModularJacobianMordellWeilDatum>) :
    <IsMordellWeilBounded> d <-> 0 <= <mordellWeilDefect> d := by
  dsimp [<IsMordellWeilBounded>, <mordellWeilDefect>]
  constructor <;> intro h <;> linarith

theorem <normalized_mordell_weil_ratio_nonneg> (d : <ModularJacobianMordellWeilDatum>) :
    0 <= <normalizedMordellWeilRatio> d := by
  dsimp [<normalizedMordellWeilRatio>]
  exact div_nonneg (le_of_lt d.norm_pos) (le_of_lt d.bound_pos)

theorem <normalized_mordell_weil_ratio_le_one_of_bounded> (d : <ModularJacobianMordellWeilDatum>)
    (h : <IsMordellWeilBounded> d) : <normalizedMordellWeilRatio> d <= 1 := by
  dsimp [<normalizedMordellWeilRatio>, <IsMordellWeilBounded>] at *
  exact (div_le_one d.bound_pos).mpr h

theorem <gram_regulator_bound_pos> (d : <ModularJacobianMordellWeilDatum>) :
    0 < <gramRegulatorBound> d := by
  dsimp [<gramRegulatorBound>]
  exact mul_pos d.bound_pos d.regulator_pos

theorem <gram_regulator_bound_nonneg> (d : <ModularJacobianMordellWeilDatum>) :
    0 <= <gramRegulatorBound> d :=
  le_of_lt (<gram_regulator_bound_pos> d)

theorem <exact_mordell_weil_implies_bounded> (d : <ModularJacobianMordellWeilDatum>)
    (h : <IsExactMordellWeil> d) : <IsMordellWeilBounded> d := by
  dsimp [<IsMordellWeilBounded>, <IsExactMordellWeil>] at *
  linarith

theorem <exact_mordell_weil_defect_zero> (d : <ModularJacobianMordellWeilDatum>)
    (h : <IsExactMordellWeil> d) : <mordellWeilDefect> d = 0 := by
  dsimp [<mordellWeilDefect>, <IsExactMordellWeil>] at *
  rw [h]
  ring

theorem <exact_mordell_weil_ratio_one> (d : <ModularJacobianMordellWeilDatum>)
    (h : <IsExactMordellWeil> d) : <normalizedMordellWeilRatio> d = 1 := by
  dsimp [<normalizedMordellWeilRatio>, <IsExactMordellWeil>] at *
  rw [h]
  exact div_self (ne_of_gt d.bound_pos)

theorem <mordell_weil_lattice_safe_iff_slack_nonneg> (d : <ModularJacobianMordellWeilDatum>) :
    <IsMordellWeilLatticeSafe> d <-> 0 <= <mordellWeilSlack> d := by
  dsimp [<IsMordellWeilLatticeSafe>, <mordellWeilSlack>]
  constructor <;> intro h <;> linarith

theorem <mordell_weil_slack_nonneg_of_safe> (d : <ModularJacobianMordellWeilDatum>)
    (h : <IsMordellWeilLatticeSafe> d) : 0 <= <mordellWeilSlack> d :=
  (<mordell_weil_lattice_safe_iff_slack_nonneg> d).mp h

theorem <mordell_weil_norm_reconstruction> (d : <ModularJacobianMordellWeilDatum>) :
    d.mordellWeilNorm = <normalizedMordellWeilRatio> d * d.mordellWeilBound := by
  dsimp [<normalizedMordellWeilRatio>]
  have h_ne : d.mordellWeilBound != 0 := ne_of_gt d.bound_pos
  have hu : IsUnit d.mordellWeilBound := h_ne.isUnit
  exact (hu.div_mul_cancel d.mordellWeilNorm).symm

theorem <weighted_mordell_weil_bound_pos> (d : <ModularJacobianMordellWeilDatum>) :
    0 < <weightedMordellWeilBound> d := by
  dsimp [<weightedMordellWeilBound>]
  have h_prod : 0 < d.curvatureWeight * d.latticeTolerance :=
    mul_pos d.weight_pos d.tolerance_pos
  have h_sum : 0 < 1 + d.curvatureWeight * d.latticeTolerance := by linarith
  exact mul_pos d.bound_pos h_sum

theorem <gram_regulator_capacity_scale> (d : <ModularJacobianMordellWeilDatum>) (c : Real) (hc : 0 <= c) :
    0 <= c * <gramRegulatorBound> d :=
  mul_nonneg hc (<gram_regulator_bound_nonneg> d)

theorem <gram_regulator_capacity_monotone> (d : <ModularJacobianMordellWeilDatum>) (b : Real)
    (hb : d.mordellWeilBound <= b) :
    <gramRegulatorBound> d <= b * d.gramRegulator := by
  dsimp [<gramRegulatorBound>]
  nlinarith [d.regulator_pos]

theorem <mordell_weil_defect_monotone> (d : <ModularJacobianMordellWeilDatum>) (p : Real)
    (hp : p <= d.mordellWeilNorm) :
    d.mordellWeilBound - d.mordellWeilNorm <= d.mordellWeilBound - p := by
  linarith

theorem <mordell_weil_slack_monotone_tolerance> (d : <ModularJacobianMordellWeilDatum>) (t : Real)
    (ht : d.latticeTolerance <= t) :
    <mordellWeilSlack> d <= d.mordellWeilBound * t - d.mordellWeilNorm := by
  dsimp [<mordellWeilSlack>]
  nlinarith [d.bound_pos]

end <Project>.<Subpackage>
```
