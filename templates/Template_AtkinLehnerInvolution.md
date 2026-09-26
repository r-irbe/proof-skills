# Template_AtkinLehnerInvolution - Involutive Symmetries, Eigenspace Splitting & Time-Reversal Isometries

Use this template for **Atkin-Lehner operators**, **involutive symmetries** ($W^2 = I$),
**time-reversal dynamics** in stochastic processes, and **eigenspace spectral decomposition** ($V = V^+ \oplus V^-$).

In modular form theory and arithmetic geometry (FLT), the Atkin-Lehner involution $W_N$
acts on modular curves $X_0(N)$ and cusp forms $S_k(\Gamma_0(N))$ as an order-2 isometry
exchanging cusps ($0 \leftrightarrow \infty$) and splitting the space of observables into
self-dual (+1) and anti-self-dual (-1) eigenspaces.

In stochastic processes and non-equilibrium thermodynamics, this structure mirrors time-reversal
symmetry: when a Markov transition matrix admits an involutive symmetry preserving its
stationary distribution $\pi$, the state space decomposes into orthogonal symmetric and
anti-symmetric observable subspaces under the weighted inner product $\langle x, y \rangle_\pi$:
$$\langle x^+, y^- \rangle_\pi = 0$$

## Main results
* `AtkinLehnerInvolution` - involutive operator $W^2 = \text{id}$ preserving stationary measure $\pi$
* `atkinLehner_isometry` - norm and inner product preservation $\langle W^* x, W^* y \rangle_\pi = \langle x, y \rangle_\pi$
* `symmObservable` / `antiSymmObservable` - canonical projections onto $+1$ and $-1$ eigenspaces
* `eigenspace_orthogonality` - orthogonal decomposition $\langle x^+, y^- \rangle_\pi = 0$
* `observable_reconstruction` - exact reconstruction $x = x^+ + x^-$

## References
* Mathlib: `Mathlib.Algebra.Homology.Flip`
* FLT: `Definitions/Def_ModularCurve_AtkinLehner.lean`
* Atkin & Lehner (1970), *Hecke Operators on $\Gamma_0(m)$*, Math. Ann. 185
* Onsager (1931), *Reciprocal Relations in Irreversible Processes*

## Tags
template, atkin-lehner, involution, time-reversal, spectral-splitting, eigenspace-decomposition, isometry, markov-symmetry

```lean
/-
Copyright (c) 2026 <Project> Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
SPDX-License-Identifier: Apache-2.0
-/

import Mathlib.Data.Fintype.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Data.Real.Basic
import Mathlib.Tactic

set_option autoImplicit false

namespace <Project>.ProofSkills.AtkinLehner

open scoped BigOperators

variable {N : ℕ}

/-- Abstract finite Markov system with stationary distribution `π`. -/
structure MarkovSystem (N : ℕ) where
  P : Fin N → Fin N → ℝ
  π : Fin N → ℝ
  pi_nonneg : ∀ i, 0 ≤ π i
  pi_sum_one : ∑ i : Fin N, π i = 1
  row_stochastic : ∀ i, ∑ j : Fin N, P i j = 1

/-- An Atkin-Lehner involution on a Markov system is an involutive bijection `W : Fin N → Fin N`
    that preserves the stationary distribution: `π(W(i)) = π(i)`. -/
structure AtkinLehnerInvolution (ms : MarkovSystem N) where
  W : Fin N → Fin N
  involutive : ∀ i : Fin N, W (W i) = i
  pi_invariant : ∀ i : Fin N, ms.π (W i) = ms.π i

variable {ms : MarkovSystem N}

/-- Bijectivity of the involution operator. -/
theorem atkinLehner_bijective (al : AtkinLehnerInvolution ms) :
    Function.Bijective al.W :=
  Function.bijective_iff_has_inverse.mpr ⟨al.W, al.involutive, al.involutive⟩

/-- Pullback action on observables: `(W* x)(i) = x(W(i))`. -/
def atkinLehnerPullback (al : AtkinLehnerInvolution ms) (x : Fin N → ℝ) : Fin N → ℝ :=
  fun i => x (al.W i)

/-- Involutive property of the pullback: `W* (W* x) = x`. -/
theorem atkinLehnerPullback_involutive (al : AtkinLehnerInvolution ms) (x : Fin N → ℝ) :
    atkinLehnerPullback al (atkinLehnerPullback al x) = x := by
  ext i
  simp only [atkinLehnerPullback, al.involutive i]

/-- Weighted inner product `⟨x, y⟩_π = ∑_i π_i x_i y_i`. -/
def innerPi (ms : MarkovSystem N) (x y : Fin N → ℝ) : ℝ :=
  ∑ i : Fin N, ms.π i * x i * y i

/-- The Atkin-Lehner operator is an isometry: `⟨W* x, W* y⟩_π = ⟨x, y⟩_π`. -/
theorem atkinLehner_isometry (al : AtkinLehnerInvolution ms) (x y : Fin N → ℝ) :
    innerPi ms (atkinLehnerPullback al x) (atkinLehnerPullback al y) = innerPi ms x y := by
  unfold innerPi atkinLehnerPullback
  have h_step : (∑ i : Fin N, ms.π i * x (al.W i) * y (al.W i)) =
                ∑ i : Fin N, ms.π (al.W i) * x (al.W i) * y (al.W i) := by
    refine Finset.sum_congr rfl (fun i _ => ?_)
    rw [al.pi_invariant i]
  rw [h_step]
  let hequiv := Equiv.ofBijective al.W (atkinLehner_bijective al)
  exact Equiv.sum_comp hequiv (fun i => ms.π i * x i * y i)

/-- Symmetric (+1 eigenspace) projection: `x⁺ = (x + W* x) / 2`. -/
def symmObservable (al : AtkinLehnerInvolution ms) (x : Fin N → ℝ) : Fin N → ℝ :=
  fun i => (x i + atkinLehnerPullback al x i) / 2

/-- Anti-symmetric (-1 eigenspace) projection: `x⁻ = (x - W* x) / 2`. -/
def antiSymmObservable (al : AtkinLehnerInvolution ms) (x : Fin N → ℝ) : Fin N → ℝ :=
  fun i => (x i - atkinLehnerPullback al x i) / 2

/-- Exact reconstruction: `x = x⁺ + x⁻`. -/
theorem observable_reconstruction (al : AtkinLehnerInvolution ms) (x : Fin N → ℝ) :
    x = fun i => symmObservable al x i + antiSymmObservable al x i := by
  ext i
  unfold symmObservable antiSymmObservable
  ring

/-- Orthogonal decomposition: symmetric and anti-symmetric subspaces are orthogonal. -/
theorem eigenspace_orthogonality (al : AtkinLehnerInvolution ms) (x y : Fin N → ℝ) :
    innerPi ms (symmObservable al x) (antiSymmObservable al y) = 0 := by
  let xp := symmObservable al x
  let ym := antiSymmObservable al y
  have h_iso := atkinLehner_isometry al xp ym
  have h_xp : atkinLehnerPullback al xp = xp := by
    ext i
    unfold symmObservable atkinLehnerPullback
    have h_inv : al.W (al.W i) = i := al.involutive i
    simp only [h_inv]
    ring
  have h_ym : atkinLehnerPullback al ym = - ym := by
    ext i
    unfold antiSymmObservable atkinLehnerPullback
    have h_inv : al.W (al.W i) = i := al.involutive i
    simp only [h_inv, Pi.neg_apply]
    ring
  rw [h_xp, h_ym] at h_iso
  unfold innerPi at h_iso
  have h_neg : (∑ i : Fin N, ms.π i * xp i * (- ym i)) = - ∑ i : Fin N, ms.π i * xp i * ym i := by
    rw [← Finset.sum_neg_distrib]
    refine Finset.sum_congr rfl (fun i _ => by ring)
  rw [h_neg] at h_iso
  linarith
```
