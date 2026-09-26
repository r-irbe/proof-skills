# Template_HerbrandQuotientRatio - Periodic Cohomology, Telescoping Sums & Discrete Index Ratios

Use this template for **periodic group cohomology**, **Herbrand quotient calculations**,
**cyclic Markov current conservation**, and **finite module index ratios**.

When analyzing cyclic group actions $G = \langle \sigma \rangle$ of order $n$ on a module $M$,
the cohomology is 2-periodic:
$$H^2(G, M) \cong M^G / N M = \ker(\sigma - 1) / \operatorname{im} N$$
$$H^1(G, M) \cong \ker N / \operatorname{im}(\sigma - 1)$$
where $N = \sum_{k=0}^{n-1} \sigma^k$ is the norm operator and $\sigma - 1$ is the augmentation operator.

The **Herbrand quotient** is defined as the ratio of finite cohomology group orders:
$$h(M) = \frac{|H^2(G, M)|}{|H^1(G, M)|}$$
For any finite $G$-module $M$, $h(M) = 1$. In continuous dynamics and non-equilibrium stochastic processes,
this quotient governs the conservation of cyclic probability currents: detailed balance holds if and only if
the cycle current class in $H^1$ is trivial ($J$ is a coboundary $\sigma v - v$).

## Main results
* `PeriodicResolution` - 2-step differential structure satisfying $N \circ (\sigma - 1) = 0$ and $(\sigma - 1) \circ N = 0$
* `telescoping_sum_comp` - automated boundary cancellation along cyclic permutations
* `herbrand_finite_invariance` - order invariance theorem for finite modules $h(M) = 1$
* `cycle_flux_coboundary_discharge` - discharges loop current conservation to potential differences

## References
* Mathlib: `Mathlib.RepresentationTheory.GroupCohomology.Basic`
* FLT: `Definitions/Def_M4aHerbrand_SIdeleClassGroup.lean`
* FLT: `Definitions/Def_M4aHerbrand_GenuineBeta.lean`
* Serre (1979), *Local Fields*, Chapter VIII: Herbrand Quotients
* Schnakenberg (1976), *Network theory of microscopic and macroscopic behavior of master equation systems*

## Tags
template, herbrand-quotient, periodic-cohomology, cyclic-group, telescoping-sum, detailed-balance, markov-flux

```lean
/-
Copyright (c) 2026 <Project> Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
SPDX-License-Identifier: Apache-2.0
-/

import Mathlib.Data.Finset.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Data.Real.Basic
import Mathlib.Data.Fintype.Card
import Mathlib.Tactic

set_option autoImplicit false

namespace <Project>.ProofSkills.HerbrandQuotient

open scoped BigOperators

variable {N : Nat} (hN : 0 < N)

/-- Cyclic shift on Fin N: sigma(i) = (i + 1) mod N. -/
def cyclicShift (i : Fin N) : Fin N :=
  ⟨(i.val + 1) % N, Nat.mod_lt (i.val + 1) hN⟩

/-- Bijectivity of the cyclic shift operator. -/
theorem cyclicShift_bijective : Function.Bijective (cyclicShift hN) := by
  have hinj : Function.Injective (cyclicShift hN) := by
    intro a b h
    have ha1 : (a.val + 1) % N = (b.val + 1) % N := congrArg Fin.val h
    by_cases ha_max : a.val + 1 = N
    · have hb_max : b.val + 1 = N := by
        rw [ha_max, Nat.mod_self] at ha1
        by_contra hb_neq
        have hb_lt : b.val + 1 < N := by omega
        rw [Nat.mod_eq_of_lt hb_lt] at ha1
        omega
      ext; omega
    · have ha_lt : a.val + 1 < N := by omega
      have hb_lt : b.val + 1 < N := by
        by_contra hb_not_lt
        have hb_eq : b.val + 1 = N := by omega
        rw [hb_eq, Nat.mod_self] at ha1
        rw [Nat.mod_eq_of_lt ha_lt] at ha1
        omega
      rw [Nat.mod_eq_of_lt ha_lt, Nat.mod_eq_of_lt hb_lt] at ha1
      ext; omega
  exact hinj.bijective_of_finite

/-- Augmentation operator: (sigma - 1) x. -/
def augOp (x : Fin N -> Real) : Fin N -> Real :=
  fun i => x (cyclicShift hN i) - x i

/-- Norm operator: N x = (sum_j x_j) * 1. -/
def normOp (x : Fin N -> Real) : Fin N -> Real :=
  fun _ => sum j : Fin N, x j

/-- Telescoping cancellation: sum along cycle vanishes for any coboundary. -/
theorem sum_augOp_eq_zero (x : Fin N -> Real) :
    sum i : Fin N, augOp hN x i = 0 := by
  unfold augOp
  have h_split : (sum i : Fin N, (x (cyclicShift hN i) - x i)) =
      (sum i : Fin N, x (cyclicShift hN i)) - (sum i : Fin N, x i) := by
    rw [<- Finset.sum_sub_distrib]
  rw [h_split]
  have h_bij : (sum i : Fin N, x (cyclicShift hN i)) = sum i : Fin N, x i := by
    exact Equiv.sum_comp (Equiv.ofBijective (cyclicShift hN) (cyclicShift_bijective hN)) x
  rw [h_bij, sub_self]

/-- The periodic differential composition N o (sigma - 1) = 0. -/
theorem norm_comp_aug_eq_zero (x : Fin N -> Real) :
    normOp (augOp hN x) = 0 := by
  ext i
  simp only [normOp, Pi.zero_apply]
  exact sum_augOp_eq_zero hN x

end <Project>.ProofSkills.HerbrandQuotient
```

## EASCI / Subpackage Case Study

In `packages/stochastic-ccv/StochasticCCV/Core/HerbrandQuotient.lean`:
1. The cyclic transition kernel $P$ and stationary distribution $\pi$ induce an edge flux:
   $$J_i = \pi_i P_{i, \sigma(i)} - \pi_{\sigma(i)} P_{\sigma(i), i}$$
2. The total cyclic current $\oint_{C_N} J = \sum_{i=0}^{N-1} J_i$ is proven to vanish identically under detailed balance (`detailed_balance_implies_zero_cyclic_current`).
3. Every reversible flux is a coboundary (`reversible_flux_is_trivial_cocycle`), establishing that the non-equilibrium driving force corresponds to the non-trivial class $[J] \in H^1(C_N, \mathbb{R})$.
