# Template_HeegnerPoint - Heegner Points, Canonical Heights & Non-Degenerate Markov Drift

Use this template for **Heegner points on modular curves**, **Gross-Zagier height derivative relations**,
**non-degenerate Markov drift trajectories**, and **ergodic stagnation avoidance**.

In arithmetic geometry and Iwasawa theory (FLT), Heegner points y_K in E(K) on modular curves
X_0(N) associated with imaginary quadratic fields K provide explicit global points of infinite order.
The Gross-Zagier formula (1986) proves that the canonical Neron-Tate height h(y_K) is proportional
to the central derivative of the L-function:
L'(E/K, 1) = (Omega / sqrt(|D|)) * h(y_K)
Non-vanishing of the derivative L'(E/K, 1) != 0 guarantees that the Heegner point has infinite order,
proving that the Mordell-Weil rank is at least 1.

In stochastic consensus and multi-agent dynamics, this structure transfers directly to:
* A Heegner datum specifying discriminant |D|, conductor N, period scale Omega, and height h.
* Gross-Zagier drift coefficient c = Omega / sqrt(|D|) > 0.
* Non-equilibrium drift rate v = c * h.
* Rank-1 regime certification: h > 0 implies strictly positive drift rate v > 0.
* Non-degenerate drift equivalence: v > 0 <-> h > 0.
* Zero drift equivalence: v = 0 <-> h = 0.
* Uniform upper bounds on drift rate under bounded canonical height.
* Monotonicity of drift rate with respect to height for constant period geometry.

## Main results
* `HeegnerDatum` - fundamental discriminant, conductor, height derivative, and period scale
* `grossZagierCoeff` - drift coupling coefficient c = Omega / sqrt(|D|)
* `heegnerDrift` - macroscopic drift rate v = c * h
* `IsRankOneRegime` - predicate certifying strictly positive canonical height
* `IsNonDegenerateDrift` - predicate certifying strictly positive drift rate
* `gross_zagier_coeff_pos` - strict positivity of the coupling coefficient
* `heegner_drift_nonneg` - non-negativity of the drift rate
* `heegner_drift_pos` - strict positivity of drift in rank-1 regime
* `non_degenerate_iff_rank_one` - equivalence of non-degenerate drift and rank-1 status
* `heegner_drift_zero_iff` - vanishing drift iff canonical height vanishes
* `heegner_drift_upper_bound` - linear upper bound under bounded height
* `heegner_drift_monotone` - monotonicity of drift with respect to height

## References
* FLT: `Heegner/HeegnerPoint.lean`, `GrossZagier/GrossZagierFormula.lean`
* Gross, B. H., Zagier, D. B. (1986), *Heegner points and derivatives of L-series*, Invent. Math. 84, 225-320
* Kolyvagin, V. A. (1988), *Euler systems*, The Grothendieck Festschrift, Vol. II, 435-483

## Tags
template, heegner-point, gross-zagier, canonical-height, markov-drift, non-degenerate-trajectory, rank-one-regime

```lean
/-
Copyright (c) 2026 <Project> Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
SPDX-License-Identifier: Apache-2.0
-/

import Mathlib.Data.Real.Basic
import Mathlib.Tactic

set_option autoImplicit false

namespace <Project>.ProofSkills.HeegnerPoint

/-- A Heegner datum specifying discriminant, conductor, period scale, and canonical height. -/
structure HeegnerDatum where
  discAbs : Real       -- |D|, fundamental discriminant absolute value
  conductor : Real     -- N, conductor of the Markov network
  heightDeriv : Real   -- h(y_K), canonical height derivative of Heegner state
  periodScale : Real   -- Omega, period / Petersson norm scale
  disc_pos : 0 < discAbs
  conductor_pos : 0 < conductor
  height_nonneg : 0 <= heightDeriv
  period_pos : 0 < periodScale

/-- Gross-Zagier drift coefficient c = Omega / sqrt(|D|). -/
def grossZagierCoeff (d : HeegnerDatum) : Real :=
  d.periodScale / Real.sqrt d.discAbs

/-- Gross-Zagier drift rate L'(1) = (Omega / sqrt(|D|)) * h(y_K). -/
def heegnerDrift (d : HeegnerDatum) : Real :=
  grossZagierCoeff d * d.heightDeriv

/-- Predicate for rank-1 regime: canonical height is strictly positive. -/
def IsRankOneRegime (d : HeegnerDatum) : Prop :=
  0 < d.heightDeriv

/-- Predicate for non-degenerate drift trajectory: drift rate is strictly positive. -/
def IsNonDegenerateDrift (d : HeegnerDatum) : Prop :=
  0 < heegnerDrift d

/-- The Gross-Zagier drift coefficient is strictly positive. -/
theorem gross_zagier_coeff_pos (d : HeegnerDatum) : 0 < grossZagierCoeff d := by
  dsimp [grossZagierCoeff]
  apply div_pos d.period_pos
  exact Real.sqrt_pos.mpr d.disc_pos

/-- The Gross-Zagier drift coefficient is non-negative. -/
theorem gross_zagier_coeff_nonneg (d : HeegnerDatum) : 0 <= grossZagierCoeff d := by
  exact le_of_lt (gross_zagier_coeff_pos d)

/-- The Heegner drift rate is always non-negative. -/
theorem heegner_drift_nonneg (d : HeegnerDatum) : 0 <= heegnerDrift d := by
  dsimp [heegnerDrift]
  exact mul_nonneg (gross_zagier_coeff_nonneg d) d.height_nonneg

/-- In a rank-1 regime, the Heegner drift rate is strictly positive. -/
theorem heegner_drift_pos (d : HeegnerDatum) (h : IsRankOneRegime d) : 0 < heegnerDrift d := by
  dsimp [heegnerDrift]
  exact mul_pos (gross_zagier_coeff_pos d) h

/-- Non-degenerate drift is equivalent to being in a rank-1 regime. -/
theorem non_degenerate_iff_rank_one (d : HeegnerDatum) :
    IsNonDegenerateDrift d <-> IsRankOneRegime d := by
  constructor
  · intro hnd
    dsimp [IsNonDegenerateDrift, heegnerDrift] at hnd
    by_contra h_neg
    have hle : d.heightDeriv <= 0 := le_of_not_gt h_neg
    have hzero : d.heightDeriv = 0 := le_antisymm hle d.height_nonneg
    rw [hzero, mul_zero] at hnd
    exact lt_irrefl 0 hnd
  · intro hr1
    dsimp [IsNonDegenerateDrift]
    exact heegner_drift_pos d hr1

/-- Zero drift occurs if and only if the canonical height vanishes. -/
theorem heegner_drift_zero_iff (d : HeegnerDatum) :
    heegnerDrift d = 0 <-> d.heightDeriv = 0 := by
  dsimp [heegnerDrift]
  have hcoeff_ne : grossZagierCoeff d != 0 := ne_of_gt (gross_zagier_coeff_pos d)
  constructor
  · intro h
    cases mul_eq_zero.mp h with
    | inl h1 => exact False.elim (hcoeff_ne h1)
    | inr h2 => exact h2
  · intro h
    rw [h, mul_zero]

/-- The Heegner drift satisfies an upper bound proportional to bounded height. -/
theorem heegner_drift_upper_bound (d : HeegnerDatum) (M : Real) (hM : d.heightDeriv <= M) :
    heegnerDrift d <= grossZagierCoeff d * M := by
  dsimp [heegnerDrift]
  exact mul_le_mul_of_nonneg_left hM (gross_zagier_coeff_nonneg d)

/-- Monotonicity of drift with respect to canonical height. -/
theorem heegner_drift_monotone (d1 d2 : HeegnerDatum)
    (heq : grossZagierCoeff d1 = grossZagierCoeff d2)
    (hle : d1.heightDeriv <= d2.heightDeriv) :
    heegnerDrift d1 <= heegnerDrift d2 := by
  dsimp [heegnerDrift]
  rw [heq]
  exact mul_le_mul_of_nonneg_left hle (gross_zagier_coeff_nonneg d2)

/-- A rank-1 Heegner trajectory is strictly non-degenerate (non-zero drift). -/
theorem heegner_trajectory_nondegenerate (d : HeegnerDatum) (h : IsRankOneRegime d) :
    heegnerDrift d != 0 := by
  exact ne_of_gt (heegner_drift_pos d h)

end <Project>.ProofSkills.HeegnerPoint
```
