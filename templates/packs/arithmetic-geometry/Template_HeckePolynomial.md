# Template_HeckePolynomial - Hecke Characteristic Polynomials & Spectral Splittings

Use this template for **Hecke characteristic polynomials**, **eigenvalue roots**,
**spectral projection operators**, and **stationary Markov current decomposition**.

In arithmetic geometry and Fermat's Last Theorem / modular forms:
The Hecke operator T_p on cusp forms S_k(\Gamma_0(N)) has characteristic polynomial:
H(X) = X^2 - a_p * X + p^(k-1).
By Deligne's theorem (Ramanujan-Petersson conjecture), its roots satisfy
|\alpha| = |\beta| = p^((k-1)/2).
The spectral projectors P_\alpha = (T_p - \beta * I) / (\alpha - \beta) and
P_\beta = (\alpha * I - T_p) / (\alpha - \beta) satisfy P_\alpha + P_\beta = I and
P_\alpha * P_\beta = 0, decomposing cohomology and modular symbol spaces.

In stochastic consensus and Markov non-equilibrium networks:
* Hecke polynomial models the characteristic polynomial of Markov transition averaging operators.
* The splitting H(X) = (X - \lambda_1) * (X - \lambda_2) decomposes distributions into stationary flow and transient modes.
* The spectral gap \Delta = \lambda_1 - \lambda_2 > 0 governs exponential convergence to stationarity.
* Spectral projection operators guarantee exact preservation of total probability mass.

## Main results
* `HeckePolynomialDatum` - parameters (traceAp, pLevel, weightK, spectralGap, rootDominant, rootSubdominant)
* `heckeDiscriminant` - polynomial discriminant \Delta_H = a_p^2 - 4 * (\lambda_1 * \lambda_2)
* `evalHeckePoly` - polynomial evaluation H(x) = (x - \lambda_1) * (x - \lambda_2)
* `spectralProjectorDominant` - dominant projection operator weight P_1(x) = (x - \lambda_2) / \Delta
* `spectralProjectorSubdominant` - subdominant projection operator weight P_2(x) = (\lambda_1 - x) / \Delta
* `heckeRelaxationRate` - relaxation rate \rho = \lambda_2 / \lambda_1
* `IsSpectralSeparated` - strictly positive spectral gap predicate
* `IsRamanujanBound` - Ramanujan-Petersson trace bound |a_p| \le 2 * c
* `hecke_eval_root_dominant` - root vanishing at dominant eigenvalue H(\lambda_1) = 0
* `hecke_eval_root_subdominant` - root vanishing at subdominant eigenvalue H(\lambda_2) = 0
* `discriminant_eq_gap_sq` - discriminant equals the square of the spectral gap
* `discriminant_nonneg` - non-negativity of the polynomial discriminant
* `projectors_sum_identity` - partition of unity P_1(x) + P_2(x) = 1
* `projector_dominant_at_dominant` - dominant projector at dominant root equals 1
* `projector_dominant_at_subdominant` - dominant projector at subdominant root vanishes
* `projector_subdominant_at_dominant` - subdominant projector at dominant root vanishes
* `projector_subdominant_at_subdominant` - subdominant projector at subdominant root equals 1
* `spectral_separated_of_datum` - datum validity implies strictly positive spectral separation
* `hecke_poly_factorization` - polynomial expansion H(x) = x^2 - a_p * x + \lambda_1 * \lambda_2
* `relaxation_rate_lt_one` - relaxation rate strictly less than 1 under positive dominant root
* `relaxation_rate_nonneg` - relaxation rate non-negative under non-negative roots

## References
* FLT: `Hecke/HeckePolynomial.lean`, `Theorems/Thm_Hecke_eigenvalues.lean`
* Shimura, G. (1971), *Introduction to the Arithmetic Theory of Automorphic Functions*, Princeton University Press
* Deligne, P. (1974), *La conjecture de Weil. I*, Publ. Math. IHES 43, 273-307
* Wiles, A. (1995), *Modular elliptic curves and Fermat's Last Theorem*, Ann. of Math. 141, 443-551

## Tags
template, hecke-polynomial, spectral-splitting, ramanujan-bound, markov-relaxation, partition-of-unity, eigen-projection

```lean
/-
Copyright (c) 2026 <Project> Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
SPDX-License-Identifier: Apache-2.0
-/

import Mathlib.Data.Real.Basic
import Mathlib.Tactic

set_option autoImplicit false

namespace <Project>.ProofSkills.HeckePolynomial

/-- Datum specifying Hecke operator trace, level parameter, modular weight, spectral gap,
    dominant eigenvalue, and subdominant eigenvalue. -/
structure HeckePolynomialDatum where
  traceAp : ℝ
  pLevel : ℝ
  weightK : ℝ
  spectralGap : ℝ
  rootDominant : ℝ
  rootSubdominant : ℝ
  p_pos : 0 < pLevel
  gap_pos : 0 < spectralGap
  roots_ordered : rootSubdominant ≤ rootDominant
  trace_eq : rootDominant + rootSubdominant = traceAp
  det_bound : 0 ≤ rootDominant * rootSubdominant
  gap_def : spectralGap = rootDominant - rootSubdominant

/-- Discriminant of the Hecke quadratic polynomial: \Delta_H = a_p^2 - 4 * (\lambda_1 * \lambda_2). -/
def heckeDiscriminant (d : HeckePolynomialDatum) : ℝ :=
  d.traceAp ^ 2 - 4 * (d.rootDominant * d.rootSubdominant)

/-- Evaluation of the Hecke characteristic polynomial: H(x) = (x - \lambda_1) * (x - \lambda_2). -/
def evalHeckePoly (d : HeckePolynomialDatum) (x : ℝ) : ℝ :=
  (x - d.rootDominant) * (x - d.rootSubdominant)

/-- Dominant spectral projection operator weight: P_1(x) = (x - \lambda_2) / \Delta. -/
def spectralProjectorDominant (d : HeckePolynomialDatum) (x : ℝ) : ℝ :=
  (x - d.rootSubdominant) / d.spectralGap

/-- Subdominant spectral projection operator weight: P_2(x) = (\lambda_1 - x) / \Delta. -/
def spectralProjectorSubdominant (d : HeckePolynomialDatum) (x : ℝ) : ℝ :=
  (d.rootDominant - x) / d.spectralGap

/-- Hecke relaxation rate: \rho = \lambda_2 / \lambda_1. -/
def heckeRelaxationRate (d : HeckePolynomialDatum) : ℝ :=
  d.rootSubdominant / d.rootDominant

/-- Predicate certifying strictly positive spectral separation. -/
def IsSpectralSeparated (d : HeckePolynomialDatum) : Prop :=
  0 < d.spectralGap

/-- Predicate certifying the Ramanujan-Petersson trace bound: |a_p| \le 2 * c. -/
def IsRamanujanBound (d : HeckePolynomialDatum) (c : ℝ) : Prop :=
  |d.traceAp| ≤ 2 * c

/-- Root vanishing: H(\lambda_1) = 0. -/
theorem hecke_eval_root_dominant (d : HeckePolynomialDatum) :
    evalHeckePoly d d.rootDominant = 0 := by
  dsimp [evalHeckePoly]
  ring

/-- Root vanishing: H(\lambda_2) = 0. -/
theorem hecke_eval_root_subdominant (d : HeckePolynomialDatum) :
    evalHeckePoly d d.rootSubdominant = 0 := by
  dsimp [evalHeckePoly]
  ring

/-- The discriminant equals the square of the spectral gap. -/
theorem discriminant_eq_gap_sq (d : HeckePolynomialDatum) :
    heckeDiscriminant d = d.spectralGap ^ 2 := by
  have h_trace := d.trace_eq
  have h_gap := d.gap_def
  dsimp [heckeDiscriminant]
  rw [← h_trace, h_gap]
  ring

/-- Non-negativity of the Hecke discriminant. -/
theorem discriminant_nonneg (d : HeckePolynomialDatum) :
    0 ≤ heckeDiscriminant d := by
  rw [discriminant_eq_gap_sq]
  exact sq_nonneg d.spectralGap

/-- Partition of unity: P_1(x) + P_2(x) = 1. -/
theorem projectors_sum_identity (d : HeckePolynomialDatum) (x : ℝ) :
    spectralProjectorDominant d x + spectralProjectorSubdominant d x = 1 := by
  dsimp [spectralProjectorDominant, spectralProjectorSubdominant]
  have h_gap_pos := d.gap_pos
  have h_gap_ne : d.spectralGap ≠ 0 := ne_of_gt h_gap_pos
  have h_gap := d.gap_def
  calc
    (x - d.rootSubdominant) / d.spectralGap + (d.rootDominant - x) / d.spectralGap
      = ((x - d.rootSubdominant) + (d.rootDominant - x)) / d.spectralGap := by ring
    _ = (d.rootDominant - d.rootSubdominant) / d.spectralGap := by ring
    _ = d.spectralGap / d.spectralGap := by rw [← h_gap]
    _ = 1 := div_self h_gap_ne

/-- Dominant projector evaluation at dominant eigenvalue: P_1(\lambda_1) = 1. -/
theorem projector_dominant_at_dominant (d : HeckePolynomialDatum) :
    spectralProjectorDominant d d.rootDominant = 1 := by
  dsimp [spectralProjectorDominant]
  have h_gap := d.gap_def
  have h_gap_pos := d.gap_pos
  have h_gap_ne : d.spectralGap ≠ 0 := ne_of_gt h_gap_pos
  rw [← h_gap]
  exact div_self h_gap_ne

/-- Dominant projector evaluation at subdominant eigenvalue: P_1(\lambda_2) = 0. -/
theorem projector_dominant_at_subdominant (d : HeckePolynomialDatum) :
    spectralProjectorDominant d d.rootSubdominant = 0 := by
  dsimp [spectralProjectorDominant]
  ring

/-- Subdominant projector evaluation at dominant eigenvalue: P_2(\lambda_1) = 0. -/
theorem projector_subdominant_at_dominant (d : HeckePolynomialDatum) :
    spectralProjectorSubdominant d d.rootDominant = 0 := by
  dsimp [spectralProjectorSubdominant]
  ring

/-- Subdominant projector evaluation at subdominant eigenvalue: P_2(\lambda_2) = 1. -/
theorem projector_subdominant_at_subdominant (d : HeckePolynomialDatum) :
    spectralProjectorSubdominant d d.rootSubdominant = 1 := by
  dsimp [spectralProjectorSubdominant]
  have h_gap := d.gap_def
  have h_gap_pos := d.gap_pos
  have h_gap_ne : d.spectralGap ≠ 0 := ne_of_gt h_gap_pos
  rw [← h_gap]
  exact div_self h_gap_ne

/-- Every valid datum has strictly positive spectral separation. -/
theorem spectral_separated_of_datum (d : HeckePolynomialDatum) :
    IsSpectralSeparated d := by
  dsimp [IsSpectralSeparated]
  exact d.gap_pos

/-- Polynomial expansion: H(x) = x^2 - a_p * x + \lambda_1 * \lambda_2. -/
theorem hecke_poly_factorization (d : HeckePolynomialDatum) (x : ℝ) :
    evalHeckePoly d x = x^2 - d.traceAp * x + (d.rootDominant * d.rootSubdominant) := by
  dsimp [evalHeckePoly]
  have h_trace := d.trace_eq
  rw [← h_trace]
  ring

/-- If dominant eigenvalue is positive, the relaxation rate is strictly less than 1. -/
theorem relaxation_rate_lt_one (d : HeckePolynomialDatum) (h_pos : 0 < d.rootDominant) :
    heckeRelaxationRate d < 1 := by
  dsimp [heckeRelaxationRate]
  rw [div_lt_one h_pos]
  have h_gap := d.gap_def
  have h_gap_pos := d.gap_pos
  linarith

/-- If both eigenvalues are non-negative with positive dominant, relaxation rate is non-negative. -/
theorem relaxation_rate_nonneg (d : HeckePolynomialDatum) (h1 : 0 < d.rootDominant)
    (h2 : 0 ≤ d.rootSubdominant) :
    0 ≤ heckeRelaxationRate d := by
  dsimp [heckeRelaxationRate]
  exact div_nonneg h2 (le_of_lt h1)

end <Project>.ProofSkills.HeckePolynomial
```
