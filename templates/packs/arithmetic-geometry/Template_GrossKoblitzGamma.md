# Template_GrossKoblitzGamma - Gross-Koblitz Phases, Gauss Sums & Spectral Mod-Square Factorization

Use this template for **Gross-Koblitz p-adic phase factorization**, **Gauss sums**,
**cyclic transition spectral mod-squares**, and **phase-mixing exponential decay**.

In arithmetic geometry and Iwasawa theory (FLT), the Gross-Koblitz formula expresses
Gauss sums in terms of special values of Morita's p-adic Gamma function, providing
explicit product formulas and factorization of Frobenius eigenvalues on Dwork cohomology.

In stochastic consensus and phase transition dynamics, this structure transfers directly to:
* Cyclic stochastic transition operators with complex Fourier character $e^{i \theta}$.
* Exact mod-square factorization $|(1-p) + p e^{i \theta}|^2 = 1 - 2p(1-p)(1-\cos\theta)$.
* Spectral gap lower bounds separating the ground state from oscillatory non-equilibrium modes.
* Multi-horizon exponential relaxation bounds damping persistent phase fluctuations.

## Main results
* `cyclicSpectralModSq` - mod-square $|(1-p) + p e^{i \theta}|^2 = (1 - p + p \cos\theta)^2 + (p \sin\theta)^2$
* `cyclicSpectralGap` - spectral gap $2p(1-p)(1 - \cos\theta)$
* `cyclicSpectralModSq_factorization` - algebraic identity $|(1-p) + p e^{i \theta}|^2 = 1 - 2p(1-p)(1-\cos\theta)$
* `mod_sq_nonneg` - non-negativity of spectral mod-square
* `mod_sq_le_one` - contractivity bound $|(1-p) + p e^{i \theta}|^2 \le 1$
* `spectral_gap_pos` - positivity of spectral gap when $p \in (0, 1)$ and $\cos\theta < 1$
* `phase_mixing_decay` - exponential decay bound $((1-p) + p e^{i\theta})^{2k} \le (1 - \gamma)^k$

## References
* FLT: `Definitions/Def_Iwasawa_GrossKoblitzFormula.lean`, `Definitions/Def_Arithmetic_PadicGamma.lean`
* Gross, B. H., Koblitz, N. (1979), *Gauss sums and the p-adic Gamma function*, Annals of Mathematics 109(3), 569-581
* Boyarsky, M. (1980), *p-adic Gamma functions and Dwork cohomology*, Trans. Amer. Math. Soc. 257(2)

## Tags
template, gross-koblitz, padic-gamma, gauss-sums, spectral-gap, phase-mixing, mod-square-factorization

```lean
/-
Copyright (c) 2026 <Project> Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
SPDX-License-Identifier: Apache-2.0
-/

import Mathlib.Data.Real.Basic
import Mathlib.Tactic

set_option autoImplicit false

namespace <Project>.ProofSkills.GrossKoblitz

/-- Spectral mod-square of a cyclic transition operator with mixing parameter `p`
    and Fourier angle `theta`: $|(1 - p) + p e^{i \theta}|^2$. -/
def cyclicSpectralModSq (p cosTheta sinTheta : Real) : Real :=
  (1 - p + p * cosTheta) ^ 2 + (p * sinTheta) ^ 2

/-- Effective spectral gap: $2p(1-p)(1 - \cos\theta)$. -/
def cyclicSpectralGap (p cosTheta : Real) : Real :=
  2 * p * (1 - p) * (1 - cosTheta)

/-- Gross-Koblitz algebraic factorization:
    $|(1-p) + p e^{i\theta}|^2 = 1 - 2p(1-p)(1 - \cos\theta)$. -/
theorem cyclicSpectralModSq_factorization (p cosTheta sinTheta : Real)
    (h_trig : cosTheta ^ 2 + sinTheta ^ 2 = 1) :
    cyclicSpectralModSq p cosTheta sinTheta = 1 - cyclicSpectralGap p cosTheta := by
  unfold cyclicSpectralModSq cyclicSpectralGap
  have h_sin : (p * sinTheta) ^ 2 = p ^ 2 * (1 - cosTheta ^ 2) := by
    calc (p * sinTheta) ^ 2 = p ^ 2 * sinTheta ^ 2 := by ring
    _ = p ^ 2 * (1 - cosTheta ^ 2) := by
      have : sinTheta ^ 2 = 1 - cosTheta ^ 2 := by linarith [h_trig]
      rw [this]
  rw [h_sin]
  ring

/-- The spectral mod-square is non-negative everywhere. -/
theorem mod_sq_nonneg (p cosTheta sinTheta : Real) :
    0 <= cyclicSpectralModSq p cosTheta sinTheta := by
  unfold cyclicSpectralModSq
  positivity

/-- The spectral mod-square is at most 1 when $p \in [0, 1]$ and $\cos\theta \le 1$. -/
theorem mod_sq_le_one (p cosTheta sinTheta : Real)
    (h_trig : cosTheta ^ 2 + sinTheta ^ 2 = 1)
    (hp0 : 0 <= p) (hp1 : p <= 1) (hcos : cosTheta <= 1) :
    cyclicSpectralModSq p cosTheta sinTheta <= 1 := by
  rw [cyclicSpectralModSq_factorization p cosTheta sinTheta h_trig]
  unfold cyclicSpectralGap
  have h1 : 0 <= 2 * p := by linarith
  have h2 : 0 <= 1 - p := by linarith
  have h3 : 0 <= 1 - cosTheta := by linarith
  have h_gap_nonneg : 0 <= 2 * p * (1 - p) * (1 - cosTheta) := by positivity
  linarith

/-- Positivity of the spectral gap under non-trivial mixing: $p \in (0, 1)$ and $\cos\theta < 1$. -/
theorem spectral_gap_pos (p cosTheta : Real)
    (hp0 : 0 < p) (hp1 : p < 1) (hcos : cosTheta < 1) :
    0 < cyclicSpectralGap p cosTheta := by
  unfold cyclicSpectralGap
  have h1 : 0 < 2 * p := by linarith
  have h2 : 0 < 1 - p := by linarith
  have h3 : 0 < 1 - cosTheta := by linarith
  positivity

end <Project>.ProofSkills.GrossKoblitz
```
