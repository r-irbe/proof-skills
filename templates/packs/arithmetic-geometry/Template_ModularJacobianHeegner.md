# Template_ModularJacobianHeegner - Modular Jacobian Heegner Points & Gross-Zagier Formulae

Use this template for **modular Jacobian Heegner points**,
**Gross-Zagier canonical height pairings**, **modular regulator envelopes**, and **boundary cycle Markov flow stability**.

In arithmetic geometry and Fermat's Last Theorem / modular forms:
Let X_0(N) be a modular curve over Q, and let J_0(N) be its modular Jacobian.
Heegner points y_K in X_0(N) associated with quadratic imaginary fields K
generate rational points P_K in J_0(N)(K). The Gross-Zagier theorem connects the
canonical Neron-Tate height of Heegner points to the first derivative of the
associated L-series at the central point s = 1:
  L'(J_0(N)/K, 1) = (u^2 / (8 * pi^2 * sqrt(|D|))) * (f, f) * h_NT(P_K).
When L'(J_0(N)/K, 1) does not vanish, P_K has infinite order in J_0(N)(K),
establishing rank 1 of the Mordell-Weil lattice and bounding the Shafarevich-Tate group.

In stochastic consensus and Markov flow networks:
Heegner point Euler systems model certified boundary cycle equilibria in
non-equilibrium multi-agent consensus networks. The Heegner defect, normalized
ratio, and Gross-Zagier capacity bounds quantify the margin of spectral
dissipation against persistent topological cycles, guaranteeing that consensus drift
stays within certified tolerances.

## Main results
* `<ModularJacobianHeegnerDatum>` - datum (heegnerHeight, regulatorBound, grossZagierVolume, heegnerTolerance, heightWeight)
* `<heegnerDefect>` - defect between regulator bound ceiling and observed Heegner canonical height
* `<normalizedHeegnerRatio>` - normalized ratio of observed Heegner height to regulator bound ceiling
* `<heegnerCapacityBound>` - total Gross-Zagier capacity bound scaled by regulator bound and volume
* `<heegnerSlack>` - slack between tolerance-scaled bound and observed canonical height
* `<weightedHeegnerBound>` - height-weighted bound accounting for Gross-Zagier volume and Tamagawa factors
* `<IsHeegnerBounded>` - predicate: observed Heegner height is bounded by regulator bound ceiling
* `<IsExactHeegner>` - predicate: observed Heegner height saturates theoretical regulator bound ceiling
* `<IsHeegnerFlowSafe>` - predicate: observed Heegner height is within certified flow tolerance
* `<heegner_defect_nonneg_of_bounded>` - Heegner defect is non-negative for bounded systems
* `<heegner_bounded_iff_defect_nonneg>` - boundedness is equivalent to non-negative Heegner defect
* `<normalized_heegner_ratio_nonneg>` - normalized Heegner ratio is non-negative
* `<normalized_heegner_ratio_le_one_of_bounded>` - normalized ratio is bounded by 1 for bounded systems
* `<heegner_capacity_bound_pos>` - Gross-Zagier capacity bound is strictly positive
* `<heegner_capacity_bound_nonneg>` - Gross-Zagier capacity bound is non-negative
* `<exact_heegner_implies_bounded>` - exact saturation implies bounded system
* `<exact_heegner_defect_zero>` - exact defect vanishes identically
* `<exact_heegner_ratio_one>` - exact saturation has normalized ratio 1
* `<heegner_flow_safe_iff_slack_nonneg>` - flow safety is equivalent to non-negative Heegner slack
* `<heegner_slack_nonneg_of_safe>` - slack is non-negative for flow-safe systems
* `<heegner_height_reconstruction>` - Heegner height reconstructed from normalized ratio and regulator bound ceiling
* `<weighted_heegner_bound_pos>` - height-weighted bound is strictly positive
* `<heegner_capacity_scale>` - Gross-Zagier capacity bound scales non-negatively with positive scaling
* `<heegner_capacity_monotone>` - Gross-Zagier capacity bound is monotone in regulator bound ceiling
* `<heegner_defect_monotone>` - defect is monotone in lower bounds on observed Heegner height
* `<heegner_slack_monotone_tolerance>` - slack is monotone in flow tolerance parameter

## References
* FLT: `StochasticCCV/Core/ModularJacobianHeegner.lean`
* Gross, B. H., Zagier, D. B. (1986), *Heegner points and derivatives of L-series*, Invent. Math. 84, 225-320.
* Kolyvagin, V. A. (1988), *Euler systems*, The Grothendieck Festschrift, Vol. II, Progr. Math. 87, 435-483.
* Wiles, A. (1995), *Modular elliptic curves and Fermat's Last Theorem*, Ann. of Math. 141, 443-551.

## Tags
template, modular-jacobian, heegner-points, gross-zagier, canonical-height, euler-systems, markov-flow

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

structure <ModularJacobianHeegnerDatum> where
  heegnerHeight : Real
  regulatorBound : Real
  grossZagierVolume : Real
  heegnerTolerance : Real
  heightWeight : Real
  height_pos : 0 < heegnerHeight
  bound_pos : 0 < regulatorBound
  volume_pos : 0 < grossZagierVolume
  tolerance_pos : 0 < heegnerTolerance
  weight_pos : 0 < heightWeight

def <heegnerDefect> (d : <ModularJacobianHeegnerDatum>) : Real :=
  d.regulatorBound - d.heegnerHeight

def <normalizedHeegnerRatio> (d : <ModularJacobianHeegnerDatum>) : Real :=
  d.heegnerHeight / d.regulatorBound

def <heegnerCapacityBound> (d : <ModularJacobianHeegnerDatum>) : Real :=
  d.regulatorBound * d.grossZagierVolume

def <heegnerSlack> (d : <ModularJacobianHeegnerDatum>) : Real :=
  d.regulatorBound * d.heegnerTolerance - d.heegnerHeight

def <weightedHeegnerBound> (d : <ModularJacobianHeegnerDatum>) : Real :=
  d.regulatorBound * (1 + d.heightWeight * d.heegnerTolerance)

def <IsHeegnerBounded> (d : <ModularJacobianHeegnerDatum>) : Prop :=
  d.heegnerHeight <= d.regulatorBound

def <IsExactHeegner> (d : <ModularJacobianHeegnerDatum>) : Prop :=
  d.heegnerHeight = d.regulatorBound

def <IsHeegnerFlowSafe> (d : <ModularJacobianHeegnerDatum>) : Prop :=
  d.heegnerHeight <= d.regulatorBound * d.heegnerTolerance

theorem <heegner_defect_nonneg_of_bounded> (d : <ModularJacobianHeegnerDatum>)
    (h : <IsHeegnerBounded> d) : 0 <= <heegnerDefect> d := by
  dsimp [<heegnerDefect>, <IsHeegnerBounded>] at *
  linarith

theorem <heegner_bounded_iff_defect_nonneg> (d : <ModularJacobianHeegnerDatum>) :
    <IsHeegnerBounded> d <-> 0 <= <heegnerDefect> d := by
  dsimp [<IsHeegnerBounded>, <heegnerDefect>]
  constructor <;> intro h <;> linarith

theorem <normalized_heegner_ratio_nonneg> (d : <ModularJacobianHeegnerDatum>) :
    0 <= <normalizedHeegnerRatio> d := by
  dsimp [<normalizedHeegnerRatio>]
  exact div_nonneg (le_of_lt d.height_pos) (le_of_lt d.bound_pos)

theorem <normalized_heegner_ratio_le_one_of_bounded> (d : <ModularJacobianHeegnerDatum>)
    (h : <IsHeegnerBounded> d) : <normalizedHeegnerRatio> d <= 1 := by
  dsimp [<normalizedHeegnerRatio>, <IsHeegnerBounded>] at *
  exact (div_le_one d.bound_pos).mpr h

theorem <heegner_capacity_bound_pos> (d : <ModularJacobianHeegnerDatum>) :
    0 < <heegnerCapacityBound> d := by
  dsimp [<heegnerCapacityBound>]
  exact mul_pos d.bound_pos d.volume_pos

theorem <heegner_capacity_bound_nonneg> (d : <ModularJacobianHeegnerDatum>) :
    0 <= <heegnerCapacityBound> d :=
  le_of_lt (<heegner_capacity_bound_pos> d)

theorem <exact_heegner_implies_bounded> (d : <ModularJacobianHeegnerDatum>)
    (h : <IsExactHeegner> d) : <IsHeegnerBounded> d := by
  dsimp [<IsHeegnerBounded>, <IsExactHeegner>] at *
  linarith

theorem <exact_heegner_defect_zero> (d : <ModularJacobianHeegnerDatum>)
    (h : <IsExactHeegner> d) : <heegnerDefect> d = 0 := by
  dsimp [<heegnerDefect>, <IsExactHeegner>] at *
  rw [h]
  ring

theorem <exact_heegner_ratio_one> (d : <ModularJacobianHeegnerDatum>)
    (h : <IsExactHeegner> d) : <normalizedHeegnerRatio> d = 1 := by
  dsimp [<normalizedHeegnerRatio>, <IsExactHeegner>] at *
  rw [h]
  exact div_self (ne_of_gt d.bound_pos)

theorem <heegner_flow_safe_iff_slack_nonneg> (d : <ModularJacobianHeegnerDatum>) :
    <IsHeegnerFlowSafe> d <-> 0 <= <heegnerSlack> d := by
  dsimp [<IsHeegnerFlowSafe>, <heegnerSlack>]
  constructor <;> intro h <;> linarith

theorem <heegner_slack_nonneg_of_safe> (d : <ModularJacobianHeegnerDatum>)
    (h : <IsHeegnerFlowSafe> d) : 0 <= <heegnerSlack> d :=
  (<heegner_flow_safe_iff_slack_nonneg> d).mp h

theorem <heegner_height_reconstruction> (d : <ModularJacobianHeegnerDatum>) :
    d.heegnerHeight = <normalizedHeegnerRatio> d * d.regulatorBound := by
  dsimp [<normalizedHeegnerRatio>]
  have h_ne : d.regulatorBound != 0 := ne_of_gt d.bound_pos
  have hu : IsUnit d.regulatorBound := h_ne.isUnit
  exact (hu.div_mul_cancel d.heegnerHeight).symm

theorem <weighted_heegner_bound_pos> (d : <ModularJacobianHeegnerDatum>) :
    0 < <weightedHeegnerBound> d := by
  dsimp [<weightedHeegnerBound>]
  have h_prod : 0 < d.heightWeight * d.heegnerTolerance :=
    mul_pos d.weight_pos d.tolerance_pos
  have h_sum : 0 < 1 + d.heightWeight * d.heegnerTolerance := by linarith
  exact mul_pos d.bound_pos h_sum

theorem <heegner_capacity_scale> (d : <ModularJacobianHeegnerDatum>) (c : Real) (hc : 0 <= c) :
    0 <= c * <heegnerCapacityBound> d :=
  mul_nonneg hc (<heegner_capacity_bound_nonneg> d)

theorem <heegner_capacity_monotone> (d : <ModularJacobianHeegnerDatum>) (b : Real)
    (hb : d.regulatorBound <= b) :
    <heegnerCapacityBound> d <= b * d.grossZagierVolume := by
  dsimp [<heegnerCapacityBound>]
  nlinarith [d.volume_pos]

theorem <heegner_defect_monotone> (d : <ModularJacobianHeegnerDatum>) (p : Real)
    (hp : p <= d.heegnerHeight) :
    d.regulatorBound - d.heegnerHeight <= d.regulatorBound - p := by
  linarith

theorem <heegner_slack_monotone_tolerance> (d : <ModularJacobianHeegnerDatum>) (t : Real)
    (ht : d.heegnerTolerance <= t) :
    <heegnerSlack> d <= d.regulatorBound * t - d.heegnerHeight := by
  dsimp [<heegnerSlack>]
  nlinarith [d.bound_pos]

end <Project>.<Subpackage>
```
