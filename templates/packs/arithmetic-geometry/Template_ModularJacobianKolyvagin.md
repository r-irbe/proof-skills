# Template_ModularJacobianKolyvagin - Modular Jacobian Kolyvagin Classes & Selmer Bounds

Use this template for **modular Jacobian Kolyvagin classes**, **Heegner Euler system derivatives**,
**Selmer rank bounds**, and **Jacobian circulation invariants**.

In arithmetic geometry and Fermat's Last Theorem:
Kolyvagin established the finiteness of the Shafarevich-Tate group and determined the rank of
modular Jacobians J_0(N) and associated abelian varieties A_f by constructing Euler systems of
Heegner points across ring class fields. The Kolyvagin derivative classes c(m) in H^1(Q, J_0(N)[p])
annihilate dual Selmer groups, bounding Selmer ranks by the order of vanishing of L-functions.

In stochastic consensus and Markov non-equilibrium networks:
* Kolyvagin derivative classes index higher-order circulation invariants on the Jacobian.
* The Kolyvagin rank measures active topological consensus cycles across network strata.
* The Selmer defect bounds the divergence between full network dimension and circulation ranks.
* Capacity bounds ensure that circulating probability currents remain strictly bounded.

## Main results
* `<ModularJacobianKolyvaginDatum>` - parameters (jacobianDim, kolyvaginRank, selmerBound, capacityBound, circulationTolerance)
* `<KolyvaginDefect>` - defect between Jacobian dimension and Kolyvagin rank
* `<NormalizedKolyvaginRatio>` - normalized ratio of Kolyvagin rank to Jacobian dimension
* `<JacobianKolyvaginCapacityBound>` - total circulation capacity scaled by Jacobian dimension
* `<SelmerSlack>` - slack between tolerance-scaled capacity and observed Selmer bound
* `<IsKolyvaginFullRank>` - Kolyvagin system acts with full rank (dimension equal to genus)
* `<IsKolyvaginBounded>` - Kolyvagin rank is bounded by Jacobian dimension
* `<IsSelmerBoundSafe>` - observed Selmer bound is within tolerance-scaled capacity
* `<KolyvaginDefectNonnegOfBounded>` - Kolyvagin defect is non-negative for bounded systems
* `<KolyvaginBoundedIffDefectNonneg>` - boundedness is equivalent to non-negative defect
* `<NormalizedKolyvaginRatioNonneg>` - normalized Kolyvagin ratio is non-negative
* `<NormalizedKolyvaginRatioLeOneOfBounded>` - normalized ratio is at most 1 for bounded systems
* `<JacobianKolyvaginCapacityBoundPos>` - total capacity bound is strictly positive
* `<JacobianKolyvaginCapacityBoundNonneg>` - total capacity bound is non-negative
* `<FullRankImpliesBounded>` - full rank action is bounded
* `<FullRankImpliesDefectZero>` - full rank action yields zero defect
* `<FullRankImpliesRatioOne>` - full rank action yields normalized ratio equal to 1
* `<SelmerSafeIffSlackNonneg>` - Selmer safety is equivalent to non-negative slack
* `<SlackNonnegOfSelmerSafe>` - slack is non-negative for safe Selmer bounds
* `<SelmerBoundOfSafe>` - Selmer bound is bounded by tolerance-scaled capacity
* `<CapacityBoundScale>` - total capacity bound scales non-negatively with positive scaling
* `<JacobianKolyvaginCapacityMonotone>` - total capacity is monotone in dimension
* `<KolyvaginDefectMonotone>` - defect is monotone in lower bounds on Kolyvagin rank
* `<SelmerSlackMonotoneTolerance>` - Selmer slack is monotone in tolerance

## References
* FLT: `StochasticCCV/Core/ModularJacobianKolyvagin.lean`
* Kolyvagin, V. A. (1990), *Euler systems*, The Grothendieck Festschrift, Vol. II, 435-483.
* Gross, B. H. (1991), *Kolyvagin's work on modular elliptic curves*, L-functions and arithmetic, 235-256.
* Rubin, K. (2000), *Euler Systems*, Annals of Mathematics Studies 147, Princeton University Press.

## Tags
template, modular-jacobian, kolyvagin-system, heegner-points, selmer-bound, euler-system

```lean
/-
Copyright (c) 2026 <Project> Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
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

/-- Datum specifying modular Jacobian dimension, Kolyvagin derivative rank, Selmer bound,
    flow capacity bound, and circulation tolerance. -/
structure <ModularJacobianKolyvaginDatum> where
  jacobianDim : Real
  kolyvaginRank : Real
  selmerBound : Real
  capacityBound : Real
  circulationTolerance : Real
  dim_pos : 0 < jacobianDim
  rank_nonneg : 0 <= kolyvaginRank
  selmer_pos : 0 < selmerBound
  capacity_pos : 0 < capacityBound
  tolerance_pos : 0 < circulationTolerance

/-- Defect between Jacobian dimension and Kolyvagin derivative rank. -/
def <KolyvaginDefect> (d : <ModularJacobianKolyvaginDatum>) : Real :=
  d.jacobianDim - d.kolyvaginRank

/-- Normalized ratio of Kolyvagin rank to Jacobian dimension. -/
def <NormalizedKolyvaginRatio> (d : <ModularJacobianKolyvaginDatum>) : Real :=
  d.kolyvaginRank / d.jacobianDim

/-- Total circulation capacity bound scaled by Jacobian dimension. -/
def <JacobianKolyvaginCapacityBound> (d : <ModularJacobianKolyvaginDatum>) : Real :=
  d.jacobianDim * d.capacityBound

/-- Selmer slack between tolerance-scaled capacity and observed Selmer bound. -/
def <SelmerSlack> (d : <ModularJacobianKolyvaginDatum>) : Real :=
  d.capacityBound * d.circulationTolerance - d.selmerBound

/-- Predicate: Kolyvagin system acts with full rank (dimension equal to genus). -/
def <IsKolyvaginFullRank> (d : <ModularJacobianKolyvaginDatum>) : Prop :=
  d.kolyvaginRank = d.jacobianDim

/-- Predicate: Kolyvagin rank is bounded by Jacobian dimension. -/
def <IsKolyvaginBounded> (d : <ModularJacobianKolyvaginDatum>) : Prop :=
  d.kolyvaginRank <= d.jacobianDim

/-- Predicate: observed Selmer bound is within tolerance-scaled capacity. -/
def <IsSelmerBoundSafe> (d : <ModularJacobianKolyvaginDatum>) : Prop :=
  d.selmerBound <= d.capacityBound * d.circulationTolerance

theorem <KolyvaginDefectNonnegOfBounded> (d : <ModularJacobianKolyvaginDatum>)
    (h : <IsKolyvaginBounded> d) : 0 <= <KolyvaginDefect> d := by
  dsimp [<KolyvaginDefect>, <IsKolyvaginBounded>] at *
  linarith

theorem <KolyvaginBoundedIffDefectNonneg> (d : <ModularJacobianKolyvaginDatum>) :
    <IsKolyvaginBounded> d <-> 0 <= <KolyvaginDefect> d := by
  dsimp [<KolyvaginDefect>, <IsKolyvaginBounded>]
  constructor <;> intro h <;> linarith

theorem <NormalizedKolyvaginRatioNonneg> (d : <ModularJacobianKolyvaginDatum>) :
    0 <= <NormalizedKolyvaginRatio> d := by
  dsimp [<NormalizedKolyvaginRatio>]
  exact div_nonneg d.rank_nonneg (le_of_lt d.dim_pos)

theorem <NormalizedKolyvaginRatioLeOneOfBounded> (d : <ModularJacobianKolyvaginDatum>)
    (h : <IsKolyvaginBounded> d) : <NormalizedKolyvaginRatio> d <= 1 := by
  dsimp [<NormalizedKolyvaginRatio>, <IsKolyvaginBounded>] at *
  exact (div_le_one d.dim_pos).mpr h

theorem <JacobianKolyvaginCapacityBoundPos> (d : <ModularJacobianKolyvaginDatum>) :
    0 < <JacobianKolyvaginCapacityBound> d := by
  dsimp [<JacobianKolyvaginCapacityBound>]
  exact mul_pos d.dim_pos d.capacity_pos

theorem <JacobianKolyvaginCapacityBoundNonneg> (d : <ModularJacobianKolyvaginDatum>) :
    0 <= <JacobianKolyvaginCapacityBound> d :=
  le_of_lt (<JacobianKolyvaginCapacityBoundPos> d)

theorem <FullRankImpliesBounded> (d : <ModularJacobianKolyvaginDatum>)
    (h : <IsKolyvaginFullRank> d) : <IsKolyvaginBounded> d := by
  dsimp [<IsKolyvaginFullRank>, <IsKolyvaginBounded>] at *
  linarith

theorem <FullRankImpliesDefectZero> (d : <ModularJacobianKolyvaginDatum>)
    (h : <IsKolyvaginFullRank> d) : <KolyvaginDefect> d = 0 := by
  dsimp [<KolyvaginDefect>, <IsKolyvaginFullRank>] at *
  linarith

theorem <FullRankImpliesRatioOne> (d : <ModularJacobianKolyvaginDatum>)
    (h : <IsKolyvaginFullRank> d) : <NormalizedKolyvaginRatio> d = 1 := by
  dsimp [<NormalizedKolyvaginRatio>, <IsKolyvaginFullRank>] at *
  rw [h]
  exact div_self (ne_of_gt d.dim_pos)

theorem <SelmerSafeIffSlackNonneg> (d : <ModularJacobianKolyvaginDatum>) :
    <IsSelmerBoundSafe> d <-> 0 <= <SelmerSlack> d := by
  dsimp [<IsSelmerBoundSafe>, <SelmerSlack>]
  constructor <;> intro h <;> linarith

theorem <SlackNonnegOfSelmerSafe> (d : <ModularJacobianKolyvaginDatum>)
    (h : <IsSelmerBoundSafe> d) : 0 <= <SelmerSlack> d :=
  (<SelmerSafeIffSlackNonneg> d).mp h

theorem <SelmerBoundOfSafe> (d : <ModularJacobianKolyvaginDatum>)
    (h : <IsSelmerBoundSafe> d) :
    d.selmerBound <= d.capacityBound * d.circulationTolerance := h

theorem <CapacityBoundScale> (d : <ModularJacobianKolyvaginDatum>) (c : Real) (hc : 0 <= c) :
    0 <= c * <JacobianKolyvaginCapacityBound> d := by
  exact mul_nonneg hc (<JacobianKolyvaginCapacityBoundNonneg> d)

theorem <JacobianKolyvaginCapacityMonotone> (d : <ModularJacobianKolyvaginDatum>) (dim' : Real)
    (hdim : d.jacobianDim <= dim') :
    <JacobianKolyvaginCapacityBound> d <= dim' * d.capacityBound := by
  dsimp [<JacobianKolyvaginCapacityBound>]
  nlinarith [d.capacity_pos]

theorem <KolyvaginDefectMonotone> (d : <ModularJacobianKolyvaginDatum>) (rank' : Real)
    (hrank : rank' <= d.kolyvaginRank) :
    d.jacobianDim - d.kolyvaginRank <= d.jacobianDim - rank' := by
  linarith

theorem <SelmerSlackMonotoneTolerance> (d : <ModularJacobianKolyvaginDatum>) (tol' : Real)
    (htol : d.circulationTolerance <= tol') :
    <SelmerSlack> d <= d.capacityBound * tol' - d.selmerBound := by
  dsimp [<SelmerSlack>]
  nlinarith [d.capacity_pos]

end <Namespace>
```
