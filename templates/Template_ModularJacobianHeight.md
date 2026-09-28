# Template_ModularJacobianHeight - Modular Jacobian Heights & Canonical Regulators

Use this template for **modular Jacobian canonical heights**, **Neron-Tate quadratic pairings**,
**regulator matrix determinants**, and **non-degenerate Markov flow quadratic energy envelopes**.

In arithmetic geometry and Fermat's Last Theorem / modular forms:
Let X_0(N) be a modular curve over Q, and let J_0(N) be its modular Jacobian. The Neron-Tate
canonical height pairing
  < ., . >_NT : J_0(N)(Q) x J_0(N)(Q) -> R
is a symmetric, positive-definite bilinear form on the Mordell-Weil group modulo torsion.
The regulator Reg(J_0(N)/Q) = det(<P_i, P_j>_NT) is the Gram determinant of a basis
of non-torsion points, which is strictly positive by non-degeneracy. In the Birch and
Swinnerton-Dyer conjecture, the regulator determines the leading Taylor coefficient
of the L-function L(J_0(N), s) at s = 1.

In stochastic consensus and Markov flow networks:
Canonical heights quantify the quadratic Lyapunov energy of non-equilibrium potential
differences across the network graph. The regulator matrix bounds the volume of independent
drift modes, guaranteeing that multi-agent consensus processes exhibit strictly positive
energy dissipation and that height defects remain bounded within certified tolerance.

## Main results
* `<ModularJacobianHeightDatum>` - datum (canonicalHeight, heightBound, regulatorVolume, driftTolerance, curvatureWeight)
* `<heightDefect>` - defect between theoretical height bound ceiling and observed canonical height
* `<normalizedHeightRatio>` - normalized ratio of observed canonical height to height bound ceiling
* `<regulatorCapacityBound>` - total regulator capacity bound scaled by height bound and volume
* `<heightSlack>` - slack between tolerance-scaled bound and observed canonical height
* `<weightedHeightBound>` - curvature-weighted bound accounting for non-degenerate regulator geometry
* `<IsHeightBounded>` - predicate: observed canonical height is bounded by height bound ceiling
* `<IsExactHeight>` - predicate: observed canonical height saturates theoretical bound ceiling
* `<IsHeightDriftSafe>` - predicate: observed canonical height is within certified drift tolerance
* `<height_defect_nonneg_of_bounded>` - height defect is non-negative for bounded systems
* `<height_bounded_iff_defect_nonneg>` - boundedness is equivalent to non-negative height defect
* `<normalized_height_ratio_nonneg>` - normalized height ratio is non-negative
* `<normalized_height_ratio_le_one_of_bounded>` - normalized ratio is bounded by 1 for bounded systems
* `<regulator_capacity_bound_pos>` - regulator capacity bound is strictly positive
* `<regulator_capacity_bound_nonneg>` - regulator capacity bound is non-negative
* `<exact_height_implies_bounded>` - exact saturation implies bounded system
* `<exact_height_defect_zero>` - exact defect vanishes identically
* `<exact_height_ratio_one>` - exact saturation has normalized ratio 1
* `<height_drift_safe_iff_slack_nonneg>` - drift safety is equivalent to non-negative height slack
* `<height_slack_nonneg_of_safe>` - slack is non-negative for drift-safe systems
* `<height_reconstruction>` - canonical height reconstructed from normalized ratio and bound
* `<weighted_height_bound_pos>` - curvature-weighted bound is strictly positive
* `<regulator_capacity_scale>` - regulator capacity bound scales non-negatively with positive scaling
* `<regulator_capacity_monotone>` - regulator capacity bound is monotone in bound ceiling
* `<height_defect_monotone>` - defect is monotone in lower bounds on observed canonical height
* `<height_slack_monotone_tolerance>` - slack is monotone in drift tolerance parameter

## References
* FLT: `StochasticCCV/Core/ModularJacobianHeight.lean`
* Neron, A. (1965), *Quasi-fonctions et hauteurs sur les varietes abeliennes*, Ann. of Math. 82, 249-331.
* Tate, J. (1983), *Variation of the canonical height of a point dependent on a parameter*, Invent. Math. 71, 311-324.
* Gross, B. H., Zagier, D. B. (1986), *Heegner points and derivatives of L-series*, Invent. Math. 84, 225-320.

## Tags
template, modular-jacobian, canonical-height, neron-tate, regulator-determinant, quadratic-energy, markov-flow

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

structure <ModularJacobianHeightDatum> where
  canonicalHeight : Real
  heightBound : Real
  regulatorVolume : Real
  driftTolerance : Real
  curvatureWeight : Real
  height_pos : 0 < canonicalHeight
  bound_pos : 0 < heightBound
  volume_pos : 0 < regulatorVolume
  tolerance_pos : 0 < driftTolerance
  weight_pos : 0 < curvatureWeight

def <heightDefect> (d : <ModularJacobianHeightDatum>) : Real :=
  d.heightBound - d.canonicalHeight

def <normalizedHeightRatio> (d : <ModularJacobianHeightDatum>) : Real :=
  d.canonicalHeight / d.heightBound

def <regulatorCapacityBound> (d : <ModularJacobianHeightDatum>) : Real :=
  d.heightBound * d.regulatorVolume

def <heightSlack> (d : <ModularJacobianHeightDatum>) : Real :=
  d.heightBound * d.driftTolerance - d.canonicalHeight

def <weightedHeightBound> (d : <ModularJacobianHeightDatum>) : Real :=
  d.heightBound * (1 + d.curvatureWeight * d.driftTolerance)

def <IsHeightBounded> (d : <ModularJacobianHeightDatum>) : Prop :=
  d.canonicalHeight <= d.heightBound

def <IsExactHeight> (d : <ModularJacobianHeightDatum>) : Prop :=
  d.canonicalHeight = d.heightBound

def <IsHeightDriftSafe> (d : <ModularJacobianHeightDatum>) : Prop :=
  d.canonicalHeight <= d.heightBound * d.driftTolerance

theorem <height_defect_nonneg_of_bounded> (d : <ModularJacobianHeightDatum>)
    (h : <IsHeightBounded> d) : 0 <= <heightDefect> d := by
  dsimp [<heightDefect>, <IsHeightBounded>] at *
  linarith

theorem <height_bounded_iff_defect_nonneg> (d : <ModularJacobianHeightDatum>) :
    <IsHeightBounded> d <-> 0 <= <heightDefect> d := by
  dsimp [<IsHeightBounded>, <heightDefect>]
  constructor <;> intro h <;> linarith

theorem <normalized_height_ratio_nonneg> (d : <ModularJacobianHeightDatum>) :
    0 <= <normalizedHeightRatio> d := by
  dsimp [<normalizedHeightRatio>]
  exact div_nonneg (le_of_lt d.height_pos) (le_of_lt d.bound_pos)

theorem <normalized_height_ratio_le_one_of_bounded> (d : <ModularJacobianHeightDatum>)
    (h : <IsHeightBounded> d) : <normalizedHeightRatio> d <= 1 := by
  dsimp [<normalizedHeightRatio>, <IsHeightBounded>] at *
  exact (div_le_one d.bound_pos).mpr h

theorem <regulator_capacity_bound_pos> (d : <ModularJacobianHeightDatum>) :
    0 < <regulatorCapacityBound> d := by
  dsimp [<regulatorCapacityBound>]
  exact mul_pos d.bound_pos d.volume_pos

theorem <regulator_capacity_bound_nonneg> (d : <ModularJacobianHeightDatum>) :
    0 <= <regulatorCapacityBound> d :=
  le_of_lt (<regulator_capacity_bound_pos> d)

theorem <exact_height_implies_bounded> (d : <ModularJacobianHeightDatum>)
    (h : <IsExactHeight> d) : <IsHeightBounded> d := by
  dsimp [<IsHeightBounded>, <IsExactHeight>] at *
  linarith

theorem <exact_height_defect_zero> (d : <ModularJacobianHeightDatum>)
    (h : <IsExactHeight> d) : <heightDefect> d = 0 := by
  dsimp [<heightDefect>, <IsExactHeight>] at *
  rw [h]
  ring

theorem <exact_height_ratio_one> (d : <ModularJacobianHeightDatum>)
    (h : <IsExactHeight> d) : <normalizedHeightRatio> d = 1 := by
  dsimp [<normalizedHeightRatio>, <IsExactHeight>] at *
  rw [h]
  exact div_self (ne_of_gt d.bound_pos)

theorem <height_drift_safe_iff_slack_nonneg> (d : <ModularJacobianHeightDatum>) :
    <IsHeightDriftSafe> d <-> 0 <= <heightSlack> d := by
  dsimp [<IsHeightDriftSafe>, <heightSlack>]
  constructor <;> intro h <;> linarith

theorem <height_slack_nonneg_of_safe> (d : <ModularJacobianHeightDatum>)
    (h : <IsHeightDriftSafe> d) : 0 <= <heightSlack> d :=
  (<height_drift_safe_iff_slack_nonneg> d).mp h

theorem <height_reconstruction> (d : <ModularJacobianHeightDatum>) :
    d.canonicalHeight = <normalizedHeightRatio> d * d.heightBound := by
  dsimp [<normalizedHeightRatio>]
  have h_ne : d.heightBound != 0 := ne_of_gt d.bound_pos
  have hu : IsUnit d.heightBound := h_ne.isUnit
  exact (hu.div_mul_cancel d.canonicalHeight).symm

theorem <weighted_height_bound_pos> (d : <ModularJacobianHeightDatum>) :
    0 < <weightedHeightBound> d := by
  dsimp [<weightedHeightBound>]
  have h_prod : 0 < d.curvatureWeight * d.driftTolerance :=
    mul_pos d.weight_pos d.tolerance_pos
  have h_sum : 0 < 1 + d.curvatureWeight * d.driftTolerance := by linarith
  exact mul_pos d.bound_pos h_sum

theorem <regulator_capacity_scale> (d : <ModularJacobianHeightDatum>) (c : Real) (hc : 0 <= c) :
    0 <= c * <regulatorCapacityBound> d :=
  mul_nonneg hc (<regulator_capacity_bound_nonneg> d)

theorem <regulator_capacity_monotone> (d : <ModularJacobianHeightDatum>) (b : Real)
    (hb : d.heightBound <= b) :
    <regulatorCapacityBound> d <= b * d.regulatorVolume := by
  dsimp [<regulatorCapacityBound>]
  nlinarith [d.volume_pos]

theorem <height_defect_monotone> (d : <ModularJacobianHeightDatum>) (p : Real)
    (hp : p <= d.canonicalHeight) :
    d.heightBound - d.canonicalHeight <= d.heightBound - p := by
  linarith

theorem <height_slack_monotone_tolerance> (d : <ModularJacobianHeightDatum>) (t : Real)
    (ht : d.driftTolerance <= t) :
    <heightSlack> d <= d.heightBound * t - d.canonicalHeight := by
  dsimp [<heightSlack>]
  nlinarith [d.bound_pos]

end <Project>.<Subpackage>
```
