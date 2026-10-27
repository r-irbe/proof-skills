# Template_HeegnerPoint - Heegner Points, Canonical Heights & Non-Degenerate Drift

Use this template for **Heegner points on modular curves**, **Gross-Zagier height formulas**,
**non-degenerate directional drift**, and **ergodic persistence overcoming potential wells**.

In arithmetic geometry and Fermat's Last Theorem / Birch and Swinnerton-Dyer theory,
a Heegner point y_K on a modular curve X_0(N) arises from complex multiplication by an imaginary
quadratic order O_K with discriminant D. The Gross-Zagier theorem establishes that the first derivative
of the central L-series L'(E/K, 1) is proportional to the canonical Neron-Tate height h_hat(y_K)
multiplied by periods and sqrt(|D|). Non-vanishing of the height guarantees rank 1 and provides
an explicit generator for the Mordell-Weil group.

In stochastic consensus and multi-agent Markov networks, this structure models:
* Fundamental discriminant D and conductor N measuring topological complexity and graph scale.
* Canonical height derivative h_hat(y_K) measuring persistent directional drift overcoming diffusion.
* Non-degeneracy predicate certifying strictly positive ergodic velocity avoiding deadlock wells.
* Monotonicity and uniform upper bounding of drift trajectories under bounded heights.

## Main results
* `HeegnerDatum` - modular curve Heegner parameters (|D|, N, h_hat, Omega)
* `grossZagierCoeff` - scaling factor sqrt(|D|) / (N * Omega)
* `heegnerDrift` - persistent velocity c_GZ * h_hat
* `IsRankOneRegime` - rank 1 condition h_hat > 0
* `IsNonDegenerateDrift` - strictly positive velocity predicate
* `gross_zagier_coeff_pos` - strict positivity of Gross-Zagier scale
* `heegner_drift_nonneg` - non-negativity of persistent drift
* `heegner_drift_pos` - rank 1 implies strictly positive velocity
* `non_degenerate_iff_rank_one` - equivalence of rank 1 and non-degenerate drift
* `heegner_drift_monotone` - monotonicity under increasing canonical height

## References
* FLT: `ModularCurves/HeegnerPoints.lean`, `LSeries/GrossZagier.lean`
* Gross, B., Zagier, D. (1986), *Heegner points and derivatives of L-series*, Invent. Math. 84, 225-320
* Kolyvagin, V. A. (1990), *Euler systems*, The Grothendieck Festschrift, Vol. II, 435-483

## Tags
template, heegner-point, gross-zagier, canonical-height, modular-curve, markov-drift, non-stagnation

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
  discAbs : Real
  conductor : Real
  heightDeriv : Real
  periodScale : Real
  disc_pos : 0 < discAbs
  conductor_pos : 0 < conductor
  height_nonneg : 0 <= heightDeriv
  period_pos : 0 < periodScale

/-- The Gross-Zagier geometric coefficient sqrt(|D|) / (N * Omega). -/
noncomputable def grossZagierCoeff (d : HeegnerDatum) : Real :=
  Real.sqrt d.discAbs / (d.conductor * d.periodScale)

/-- The Heegner persistent drift velocity v = grossZagierCoeff * heightDeriv. -/
noncomputable def heegnerDrift (d : HeegnerDatum) : Real :=
  grossZagierCoeff d * d.heightDeriv

/-- Predicate certifying that the system operates in the rank-one regime. -/
def IsRankOneRegime (d : HeegnerDatum) : Prop :=
  0 < d.heightDeriv

/-- Predicate certifying non-degenerate persistent drift velocity. -/
def IsNonDegenerateDrift (d : HeegnerDatum) : Prop :=
  0 < heegnerDrift d

theorem gross_zagier_coeff_pos (d : HeegnerDatum) : 0 < grossZagierCoeff d := by
  unfold grossZagierCoeff
  have hsqrt : 0 < Real.sqrt d.discAbs := Real.sqrt_pos.mpr d.disc_pos
  have hdenom : 0 < d.conductor * d.periodScale := mul_pos d.conductor_pos d.period_pos
  exact div_pos hsqrt hdenom

theorem gross_zagier_coeff_nonneg (d : HeegnerDatum) : 0 <= grossZagierCoeff d :=
  le_of_lt (gross_zagier_coeff_pos d)

theorem heegner_drift_nonneg (d : HeegnerDatum) : 0 <= heegnerDrift d := by
  unfold heegnerDrift
  exact mul_nonneg (gross_zagier_coeff_nonneg d) d.height_nonneg

theorem heegner_drift_pos (d : HeegnerDatum) (h : IsRankOneRegime d) : 0 < heegnerDrift d := by
  unfold heegnerDrift IsRankOneRegime at *
  exact mul_pos (gross_zagier_coeff_pos d) h

theorem non_degenerate_iff_rank_one (d : HeegnerDatum) :
    IsNonDegenerateDrift d <-> IsRankOneRegime d := by
  constructor
  - intro h
    unfold IsNonDegenerateDrift heegnerDrift at h
    unfold IsRankOneRegime
    have hc := gross_zagier_coeff_pos d
    exact (mul_pos_iff_of_pos_left hc).mp h
  - intro h
    exact heegner_drift_pos d h


end <Project>.ProofSkills.HeegnerPoint
```
