# Proof Skill Template: Discrete-to-Continuous Scaling Limits

## 1. Domain & Scope
- **Category**: Asymptotic Analysis / Projective Limits / Dynamical Scaling.
- **Role**: Formalizes transitions from discrete Markov towers, grid approximations, and auxiliary parameter sequences to continuous stationary states and generator invariants.
- **Origin**: Adapted from the Taylor-Wiles-Diamond patching method in Fermat's Last Theorem (`Algebra.PatchingDatum`, `Algebra.PatchingLevel`, `nonempty_patchingLevel_bot`) and EASCI Markov scaling limits (`EASCI.ScalingLimit`).

---

## 2. Mathematical Contract

A scaling limit proof establishes that a sequence of discrete objects $\{X_n\}_{n \in \mathbb{N}}$ defined at discrete steps $\tau_n \to 0$ converges to an invariant state of a continuous infinitesimal operator $L$:

1. **Discrete Approximation Tower**:
   Operators $P_n$ act on state space $E$ with step size $\tau_n > 0$ where $\tau_n \to 0$.
2. **Uniform Boundedness / Compactness**:
   The orbit or state distributions $\pi_n$ remain in a compact or uniformly bounded metric subspace (e.g. standard probability simplex $\Delta^K$ or bounded Sobolev ball).
3. **Exact Defect Telescoping**:
   The infinitesimal difference satisfies an exact algebraic bound:
   $$\|(P_n - I) \pi_n\| \le C \cdot \epsilon_n \quad (\epsilon_n \to 0).$$
4. **Projective Limit Assembly**:
   The sequence admits a cluster point $\pi_\infty$ via projective limit completion ($\varprojlim$) or sequential compactness.
5. **Specialization & Regularity Transfer**:
   By strong convergence and operator continuity, the defect vanishes identically in the limit:
   $$L \pi_\infty = 0.$$

---

## 3. Standard Lean 4 Proof Blueprint

```lean
import Mathlib.Topology.MetricSpace.Basic
import Mathlib.Topology.Algebra.Filter
import Mathlib.LinearAlgebra.Dimension.Finrank

open Filter Topology

set_option autoImplicit false

namespace ProofSkills.ScalingLimit

/-- Discrete-to-continuous operator tower. -/
structure OperatorTower (E : Type*) [NormedAddCommGroup E] [NormedSpace ℝ E] where
  τ : ℕ → ℝ
  hτ_pos : ∀ n, 0 < τ n
  hτ_lim : Tendsto τ atTop (nhds 0)
  P : ℕ → (E →L[ℝ] E)
  L : E →L[ℝ] E
  generator_convergence : ∀ x : E,
    Tendsto (fun n => (1 / τ n) • (P n x - x)) atTop (nhds (L x))

/-- Discrete stationary sequence with cluster point. -/
structure DiscreteStationarySequence {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
    (T : OperatorTower E) where
  π : ℕ → E
  h_stationary : ∀ n, T.P n (π n) = π n
  π_inf : E
  h_converge : Tendsto π atTop (nhds π_inf)

/-- Master scaling limit transfer theorem. -/
theorem operator_scaling_limit_invariant {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
    (T : OperatorTower E) (S : DiscreteStationarySequence T) :
    T.L S.π_inf = 0 := by
  -- 1. Establish that discrete defect vanishes identically at each level n
  have h_zero : ∀ n, (1 / T.τ n) • (T.P n (S.π n) - S.π n) = 0 := by
    intro n
    rw [S.h_stationary n, sub_self, smul_zero]
  -- 2. By joint continuity and strong convergence, transfer defect to continuous generator
  sorry

end ProofSkills.ScalingLimit
```

---

## 4. Verification Checklist

- [ ] `autoImplicit false` declared at file root.
- [ ] Explicit step size sequence $\tau_n$ with verified convergence $\tau_n \to 0$.
- [ ] Defect telescoping inequality documented and bound verified.
- [ ] Zero reliance on unverified axioms; pure kernel reduction.
