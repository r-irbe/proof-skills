# Template_ModularJacobianNeronTateHeight - Modular Jacobian Neron-Tate Heights & Global Regulators

Use this template for **modular Jacobian Neron-Tate heights**, **canonical height pairings**,
**global regulator volumes**, and **circulation dissipation energy bounds**.

In arithmetic geometry and Fermat's Last Theorem / modular forms:
On a modular curve X_0(N) and its modular Jacobian variety J_0(N), the canonical Neron-Tate
height pairing <., .>_NT : J_0(N)(Q) x J_0(N)(Q) -> R is a symmetric, positive-definite bilinear
form on the free quotient of the Mordell-Weil group. The determinant of the height pairing
matrix across a basis of J_0(N)(Q) defines the regulator Reg(J_0(N)). In the Birch and
Swinnerton-Dyer conjecture and the Gross-Zagier formula, non-vanishing of the regulator certifies
non-degeneracy of rational points, bounding the rank of modular abelian varieties and controlling
Selmer group growth in modularity proofs.

In stochastic consensus and Markov non-equilibrium networks:
* Neron-Tate heights quantify the global quadratic dissipation energy of network state profiles.
* Regulator volume bounds certify that harmonic circulation cycles preserve non-degenerate energy.
* The Neron-Tate height slack defines certified safety headroom against energy dissipation collapse.
* The normalized height ratio bounds quadratic deviation relative to total network capacity.

## Main results
* `<ModularJacobianNeronTateHeightDatum>` - datum (neronTateHeight, heightCapacity, regulatorVolumeBound, heightTolerance, heightWeight)
* `<neronTateHeightDefect>` - defect between height capacity ceiling and observed Neron-Tate height norm
* `<normalizedNeronTateHeightRatio>` - normalized ratio of observed Neron-Tate height norm to capacity ceiling
* `<neronTateHeightCapacityBound>` - total capacity bound scaled by capacity ceiling and regulator volume bound
* `<neronTateHeightSlack>` - height slack between tolerance-scaled capacity and observed norm
* `<neronTateHeightWeightedMargin>` - weighted margin combining height weight and height tolerance
* `<neronTateHeightCombinedIndex>` - combined index of normalized height ratio and height slack
* `<IsNeronTateHeightBounded>` - predicate: Neron-Tate height norm does not exceed capacity ceiling
* `<IsCriticalNeronTateHeight>` - predicate: Neron-Tate height norm matches capacity ceiling exactly
* `<IsStrictNeronTateHeightBounded>` - predicate: Neron-Tate height norm is strictly below capacity ceiling
* `<IsNeronTateHeightCapacitySafe>` - predicate: Neron-Tate height norm does not exceed capacity bound
* `<IsNeronTateHeightSafe>` - safety envelope certifying both ceiling boundedness and capacity boundedness
* `<neron_tate_height_defect_pos_of_strict>` - defect is strictly positive for strict bounded systems
* `<neron_tate_height_defect_nonneg_of_bounded>` - defect is non-negative for bounded systems
* `<bounded_of_neron_tate_height_defect_nonneg>` - non-negative defect implies bounded system
* `<neron_tate_height_bounded_iff_defect_nonneg>` - boundedness is equivalent to non-negative defect
* `<normalized_neron_tate_height_ratio_pos>` - normalized ratio is strictly positive
* `<normalized_neron_tate_height_ratio_le_one_of_bounded>` - normalized ratio is at most 1 for bounded systems
* `<bounded_of_normalized_neron_tate_height_ratio_le_one>` - ratio at most 1 implies bounded system
* `<neron_tate_height_bounded_iff_normalized_le_one>` - boundedness is equivalent to normalized ratio at most 1

## References
* FLT: `StochasticCCV/Core/ModularJacobianNeronTateHeight.lean`
* Neron, A. (1965), *Quasi-fonctions et hauteurs sur les varietes abeliennes*, Ann. of Math. 82, 249-331.
* Tate, J. (1965), *On the conjectures of Birch and Swinnerton-Dyer and a geometric analog*, Seminaire Bourbaki 306.
* Gross, B., Zagier, D. (1986), *Heegner points and derivatives of L-series*, Invent. Math. 84, 225-320.

## Tags
template, modular-jacobian, neron-tate-height, canonical-height, regulator-volume, mordell-weil, gross-zagier

```lean
/-
Copyright (c) 2026 <Project> Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: <Project> Formalization Team
SPDX-License-Identifier: Apache-2.0
-/

import Mathlib.Data.Real.Basic
import Mathlib.Tactic

set_option autoImplicit false
set_option linter.unusedVariables false
set_option linter.unusedSectionVars false
set_option linter.unusedSimpArgs false

noncomputable section

namespace <Project>

structure <ModularJacobianNeronTateHeightDatum> where
  neronTateHeight : ℝ
  heightCapacity : ℝ
  regulatorVolumeBound : ℝ
  heightTolerance : ℝ
  heightWeight : ℝ
  height_pos : 0 < neronTateHeight
  capacity_pos : 0 < heightCapacity
  bound_pos : 0 < regulatorVolumeBound
  tolerance_pos : 0 < heightTolerance
  weight_pos : 0 < heightWeight

def <neronTateHeightDefect> (d : <ModularJacobianNeronTateHeightDatum>) : ℝ :=
  d.heightCapacity - d.neronTateHeight

def <normalizedNeronTateHeightRatio> (d : <ModularJacobianNeronTateHeightDatum>) : ℝ :=
  d.neronTateHeight / d.heightCapacity

def <neronTateHeightCapacityBound> (d : <ModularJacobianNeronTateHeightDatum>) : ℝ :=
  d.heightCapacity * d.regulatorVolumeBound

def <neronTateHeightSlack> (d : <ModularJacobianNeronTateHeightDatum>) : ℝ :=
  d.heightCapacity * d.heightTolerance - d.neronTateHeight

def <neronTateHeightWeightedMargin> (d : <ModularJacobianNeronTateHeightDatum>) : ℝ :=
  d.heightWeight * <neronTateHeightDefect> d + d.heightTolerance

def <neronTateHeightCombinedIndex> (d : <ModularJacobianNeronTateHeightDatum>) : ℝ :=
  <normalizedNeronTateHeightRatio> d + <neronTateHeightSlack> d

def <IsNeronTateHeightBounded> (d : <ModularJacobianNeronTateHeightDatum>) : Prop :=
  d.neronTateHeight ≤ d.heightCapacity

def <IsCriticalNeronTateHeight> (d : <ModularJacobianNeronTateHeightDatum>) : Prop :=
  d.neronTateHeight = d.heightCapacity

def <IsStrictNeronTateHeightBounded> (d : <ModularJacobianNeronTateHeightDatum>) : Prop :=
  d.neronTateHeight < d.heightCapacity

def <IsNeronTateHeightCapacitySafe> (d : <ModularJacobianNeronTateHeightDatum>) : Prop :=
  d.neronTateHeight < <neronTateHeightCapacityBound> d

def <IsNeronTateHeightSafe> (d : <ModularJacobianNeronTateHeightDatum>) : Prop :=
  <IsNeronTateHeightBounded> d ∧ <IsNeronTateHeightCapacitySafe> d

theorem <neron_tate_height_defect_pos_of_strict> (d : <ModularJacobianNeronTateHeightDatum>)
    (h : <IsStrictNeronTateHeightBounded> d) : 0 < <neronTateHeightDefect> d := by
  dsimp [<IsStrictNeronTateHeightBounded>] at h
  dsimp [<neronTateHeightDefect>]
  linarith

theorem <neron_tate_height_defect_nonneg_of_bounded> (d : <ModularJacobianNeronTateHeightDatum>)
    (h : <IsNeronTateHeightBounded> d) : 0 ≤ <neronTateHeightDefect> d := by
  dsimp [<IsNeronTateHeightBounded>] at h
  dsimp [<neronTateHeightDefect>]
  linarith

theorem <bounded_of_neron_tate_height_defect_nonneg> (d : <ModularJacobianNeronTateHeightDatum>)
    (h : 0 ≤ <neronTateHeightDefect> d) : <IsNeronTateHeightBounded> d := by
  dsimp [<neronTateHeightDefect>] at h
  dsimp [<IsNeronTateHeightBounded>]
  linarith

theorem <neron_tate_height_bounded_iff_defect_nonneg> (d : <ModularJacobianNeronTateHeightDatum>) :
    <IsNeronTateHeightBounded> d ↔ 0 ≤ <neronTateHeightDefect> d :=
  ⟨<neron_tate_height_defect_nonneg_of_bounded> d, <bounded_of_neron_tate_height_defect_nonneg> d⟩

theorem <normalized_neron_tate_height_ratio_pos> (d : <ModularJacobianNeronTateHeightDatum>) :
    0 < <normalizedNeronTateHeightRatio> d := by
  dsimp [<normalizedNeronTateHeightRatio>]
  exact div_pos d.height_pos d.capacity_pos

theorem <normalized_neron_tate_height_ratio_le_one_of_bounded> (d : <ModularJacobianNeronTateHeightDatum>)
    (h : <IsNeronTateHeightBounded> d) : <normalizedNeronTateHeightRatio> d ≤ 1 := by
  dsimp [<IsNeronTateHeightBounded>] at h
  dsimp [<normalizedNeronTateHeightRatio>]
  exact (div_le_one d.capacity_pos).mpr h

theorem <bounded_of_normalized_neron_tate_height_ratio_le_one> (d : <ModularJacobianNeronTateHeightDatum>)
    (h : <normalizedNeronTateHeightRatio> d ≤ 1) : <IsNeronTateHeightBounded> d := by
  dsimp [<normalizedNeronTateHeightRatio>] at h
  dsimp [<IsNeronTateHeightBounded>]
  exact (div_le_one d.capacity_pos).mp h

theorem <neron_tate_height_bounded_iff_normalized_le_one> (d : <ModularJacobianNeronTateHeightDatum>) :
    <IsNeronTateHeightBounded> d ↔ <normalizedNeronTateHeightRatio> d ≤ 1 :=
  ⟨<normalized_neron_tate_height_ratio_le_one_of_bounded> d, <bounded_of_normalized_neron_tate_height_ratio_le_one> d⟩

end <Project>
```
