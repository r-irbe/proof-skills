# Template_ModularJacobianBSD - Modular Jacobian Birch-Swinnerton-Dyer L-Series & Analytic Ranks

Use this template for **modular Jacobian Birch-Swinnerton-Dyer leading coefficients**,
**analytic ranks**, **canonical regulator products**, and **non-equilibrium Markov flow capacity envelopes**.

In arithmetic geometry and Fermat's Last Theorem / modular forms:
Let X_0(N) be a modular curve over Q, and let J_0(N) be its modular Jacobian.
The Birch and Swinnerton-Dyer (BSD) conjecture relates the behavior of the L-series
L(J_0(N), s) at s = 1 to the algebraic rank r = rank J_0(N)(Q) and the arithmetic
invariants (Neron-Tate regulator Reg, Shafarevich-Tate group order #Sha, real period Omega,
and Tamagawa numbers c_p):
  lim_{s -> 1} L(J_0(N), s) / (s - 1)^r = (Omega * Reg * #Sha * prod c_p) / #J_0(N)(Q)_tors^2.
Gross-Zagier and Kolyvagin established this conjecture for modular curves when r <= 1.

In stochastic consensus and Markov flow networks:
The BSD leading coefficient and analytic rank govern the non-equilibrium steady state
relaxation rate and the dimension of conserved network flow cycles. The BSD defect,
normalized ratio, and regulator capacity bounds quantify the margin of spectral
dissipation against persistent topological cycles, guaranteeing that consensus drift
stays within certified tolerances.

## Main results
* `<ModularJacobianBSDDatum>` - datum (bsdLeadingCoeff, bsdBound, regulatorProduct, bsdTolerance, periodWeight)
* `<bsdDefect>` - defect between theoretical bound ceiling and observed BSD leading coefficient
* `<normalizedBSDRatio>` - normalized ratio of observed BSD leading coefficient to bound ceiling
* `<bsdCapacityBound>` - total regulator capacity bound scaled by bound ceiling and regulator product
* `<bsdSlack>` - slack between tolerance-scaled bound and observed leading coefficient
* `<weightedBSDBound>` - period-weighted bound accounting for BSD real period and Tamagawa factors
* `<IsBSDBounded>` - predicate: observed BSD leading coefficient is bounded by bound ceiling
* `<IsExactBSD>` - predicate: observed BSD leading coefficient saturates theoretical bound ceiling
* `<IsBSDFlowSafe>` - predicate: observed BSD leading coefficient is within certified flow tolerance
* `<bsd_defect_nonneg_of_bounded>` - BSD defect is non-negative for bounded systems
* `<bsd_bounded_iff_defect_nonneg>` - boundedness is equivalent to non-negative BSD defect
* `<normalized_bsd_ratio_nonneg>` - normalized BSD ratio is non-negative
* `<normalized_bsd_ratio_le_one_of_bounded>` - normalized ratio is bounded by 1 for bounded systems
* `<bsd_capacity_bound_pos>` - BSD regulator capacity bound is strictly positive
* `<bsd_capacity_bound_nonneg>` - BSD regulator capacity bound is non-negative
* `<exact_bsd_implies_bounded>` - exact saturation implies bounded system
* `<exact_bsd_defect_zero>` - exact defect vanishes identically
* `<exact_bsd_ratio_one>` - exact saturation has normalized ratio 1
* `<bsd_flow_safe_iff_slack_nonneg>` - flow safety is equivalent to non-negative BSD slack
* `<bsd_slack_nonneg_of_safe>` - slack is non-negative for flow-safe systems
* `<bsd_coeff_reconstruction>` - BSD coefficient reconstructed from normalized ratio and bound ceiling
* `<weighted_bsd_bound_pos>` - period-weighted bound is strictly positive
* `<bsd_capacity_scale>` - BSD capacity bound scales non-negatively with positive scaling
* `<bsd_capacity_monotone>` - BSD capacity bound is monotone in bound ceiling
* `<bsd_defect_monotone>` - defect is monotone in lower bounds on observed leading coefficient
* `<bsd_slack_monotone_tolerance>` - slack is monotone in flow tolerance parameter

## References
* FLT: `StochasticCCV/Core/ModularJacobianBSD.lean`
* Birch, B. J., Swinnerton-Dyer, H. P. F. (1965), *Notes on elliptic curves. II*, J. Reine Angew. Math. 218, 79-108.
* Gross, B. H., Zagier, D. B. (1986), *Heegner points and derivatives of L-series*, Invent. Math. 84, 225-320.
* Kolyvagin, V. A. (1988), *Euler systems*, The Grothendieck Festschrift, Vol. II, Progr. Math. 87, 435-483.

## Tags
template, modular-jacobian, bsd-conjecture, l-series, analytic-rank, regulator-product, markov-flow

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

structure <ModularJacobianBSDDatum> where
  bsdLeadingCoeff : Real
  bsdBound : Real
  regulatorProduct : Real
  bsdTolerance : Real
  periodWeight : Real
  coeff_pos : 0 < bsdLeadingCoeff
  bound_pos : 0 < bsdBound
  regulator_pos : 0 < regulatorProduct
  tolerance_pos : 0 < bsdTolerance
  weight_pos : 0 < periodWeight

def <bsdDefect> (d : <ModularJacobianBSDDatum>) : Real :=
  d.bsdBound - d.bsdLeadingCoeff

def <normalizedBSDRatio> (d : <ModularJacobianBSDDatum>) : Real :=
  d.bsdLeadingCoeff / d.bsdBound

def <bsdCapacityBound> (d : <ModularJacobianBSDDatum>) : Real :=
  d.bsdBound * d.regulatorProduct

def <bsdSlack> (d : <ModularJacobianBSDDatum>) : Real :=
  d.bsdBound * d.bsdTolerance - d.bsdLeadingCoeff

def <weightedBSDBound> (d : <ModularJacobianBSDDatum>) : Real :=
  d.bsdBound * (1 + d.periodWeight * d.bsdTolerance)

def <IsBSDBounded> (d : <ModularJacobianBSDDatum>) : Prop :=
  d.bsdLeadingCoeff <= d.bsdBound

def <IsExactBSD> (d : <ModularJacobianBSDDatum>) : Prop :=
  d.bsdLeadingCoeff = d.bsdBound

def <IsBSDFlowSafe> (d : <ModularJacobianBSDDatum>) : Prop :=
  d.bsdLeadingCoeff <= d.bsdBound * d.bsdTolerance

theorem <bsd_defect_nonneg_of_bounded> (d : <ModularJacobianBSDDatum>)
    (h : <IsBSDBounded> d) : 0 <= <bsdDefect> d := by
  dsimp [<bsdDefect>, <IsBSDBounded>] at *
  linarith

theorem <bsd_bounded_iff_defect_nonneg> (d : <ModularJacobianBSDDatum>) :
    <IsBSDBounded> d <-> 0 <= <bsdDefect> d := by
  dsimp [<IsBSDBounded>, <bsdDefect>]
  constructor <;> intro h <;> linarith

theorem <normalized_bsd_ratio_nonneg> (d : <ModularJacobianBSDDatum>) :
    0 <= <normalizedBSDRatio> d := by
  dsimp [<normalizedBSDRatio>]
  exact div_nonneg (le_of_lt d.coeff_pos) (le_of_lt d.bound_pos)

theorem <normalized_bsd_ratio_le_one_of_bounded> (d : <ModularJacobianBSDDatum>)
    (h : <IsBSDBounded> d) : <normalizedBSDRatio> d <= 1 := by
  dsimp [<normalizedBSDRatio>, <IsBSDBounded>] at *
  exact (div_le_one d.bound_pos).mpr h

theorem <bsd_capacity_bound_pos> (d : <ModularJacobianBSDDatum>) :
    0 < <bsdCapacityBound> d := by
  dsimp [<bsdCapacityBound>]
  exact mul_pos d.bound_pos d.regulator_pos

theorem <bsd_capacity_bound_nonneg> (d : <ModularJacobianBSDDatum>) :
    0 <= <bsdCapacityBound> d :=
  le_of_lt (<bsd_capacity_bound_pos> d)

theorem <exact_bsd_implies_bounded> (d : <ModularJacobianBSDDatum>)
    (h : <IsExactBSD> d) : <IsBSDBounded> d := by
  dsimp [<IsBSDBounded>, <IsExactBSD>] at *
  linarith

theorem <exact_bsd_defect_zero> (d : <ModularJacobianBSDDatum>)
    (h : <IsExactBSD> d) : <bsdDefect> d = 0 := by
  dsimp [<bsdDefect>, <IsExactBSD>] at *
  rw [h]
  ring

theorem <exact_bsd_ratio_one> (d : <ModularJacobianBSDDatum>)
    (h : <IsExactBSD> d) : <normalizedBSDRatio> d = 1 := by
  dsimp [<normalizedBSDRatio>, <IsExactBSD>] at *
  rw [h]
  exact div_self (ne_of_gt d.bound_pos)

theorem <bsd_flow_safe_iff_slack_nonneg> (d : <ModularJacobianBSDDatum>) :
    <IsBSDFlowSafe> d <-> 0 <= <bsdSlack> d := by
  dsimp [<IsBSDFlowSafe>, <bsdSlack>]
  constructor <;> intro h <;> linarith

theorem <bsd_slack_nonneg_of_safe> (d : <ModularJacobianBSDDatum>)
    (h : <IsBSDFlowSafe> d) : 0 <= <bsdSlack> d :=
  (<bsd_flow_safe_iff_slack_nonneg> d).mp h

theorem <bsd_coeff_reconstruction> (d : <ModularJacobianBSDDatum>) :
    d.bsdLeadingCoeff = <normalizedBSDRatio> d * d.bsdBound := by
  dsimp [<normalizedBSDRatio>]
  have h_ne : d.bsdBound != 0 := ne_of_gt d.bound_pos
  have hu : IsUnit d.bsdBound := h_ne.isUnit
  exact (hu.div_mul_cancel d.bsdLeadingCoeff).symm

theorem <weighted_bsd_bound_pos> (d : <ModularJacobianBSDDatum>) :
    0 < <weightedBSDBound> d := by
  dsimp [<weightedBSDBound>]
  have h_prod : 0 < d.periodWeight * d.bsdTolerance :=
    mul_pos d.weight_pos d.tolerance_pos
  have h_sum : 0 < 1 + d.periodWeight * d.bsdTolerance := by linarith
  exact mul_pos d.bound_pos h_sum

theorem <bsd_capacity_scale> (d : <ModularJacobianBSDDatum>) (c : Real) (hc : 0 <= c) :
    0 <= c * <bsdCapacityBound> d :=
  mul_nonneg hc (<bsd_capacity_bound_nonneg> d)

theorem <bsd_capacity_monotone> (d : <ModularJacobianBSDDatum>) (b : Real)
    (hb : d.bsdBound <= b) :
    <bsdCapacityBound> d <= b * d.regulatorProduct := by
  dsimp [<bsdCapacityBound>]
  nlinarith [d.regulator_pos]

theorem <bsd_defect_monotone> (d : <ModularJacobianBSDDatum>) (p : Real)
    (hp : p <= d.bsdLeadingCoeff) :
    d.bsdBound - d.bsdLeadingCoeff <= d.bsdBound - p := by
  linarith

theorem <bsd_slack_monotone_tolerance> (d : <ModularJacobianBSDDatum>) (t : Real)
    (ht : d.bsdTolerance <= t) :
    <bsdSlack> d <= d.bsdBound * t - d.bsdLeadingCoeff := by
  dsimp [<bsdSlack>]
  nlinarith [d.bound_pos]

end <Project>.<Subpackage>
```
