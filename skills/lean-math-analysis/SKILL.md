---
name: lean-math-analysis
description: Real analysis, functional analysis, topology, and measure theory in Lean 4 / Mathlib. Use when formalizing continuous functions, derivatives, integrals, metric spaces, normed spaces, filters, convergence, or topological properties. Covers project-relevant analysis — Lyapunov functions, contraction mappings, convex analysis, spectral theory, and the real-valued bridges from the project's Nat-scaled model.
---

# Lean 4 Real Analysis & Topology

Guide to formalizing analysis and topology in Lean 4 using Mathlib's filter-based approach.

---

## Part 1 — Mathlib's Analysis Architecture

### 1.1 The Filter-First Philosophy

Mathlib uses **filters** as the universal convergence abstraction. All limits, continuity, and topological notions are filter-based:

```lean
-- Tendsto: the universal limit concept
-- f tends to l along filter F ↔ for any neighborhood U of l, f⁻¹(U) ∈ F
Filter.Tendsto f F (nhds l)

-- Special cases:
-- Sequence limit: Tendsto f atTop (nhds l)
-- Function limit at a: Tendsto f (nhds a) (nhds l)
-- Function limit at infinity: Tendsto f atTop atTop
```

### 1.2 Key Namespaces

| Namespace | Content | Project usage |
|---|---|---|
| `Mathlib.Topology.Basic` | Open/closed sets, continuity | Phase region topology |
| `Mathlib.Topology.MetricSpace` | Metric spaces, distance, balls | Trust metric, contraction |
| `Mathlib.Topology.Order` | Order topology | Threshold analysis |
| `Mathlib.Analysis.Calculus.Deriv` | Derivatives (1D) | Cusp potential derivatives |
| `Mathlib.Analysis.Calculus.FDeriv` | Fréchet derivatives (nD) | Gradient of Lyapunov |
| `Mathlib.Analysis.NormedSpace` | Normed vector spaces | RL value functions |
| `Mathlib.Analysis.InnerProductSpace` | Hilbert spaces | (If needed for spectral) |
| `Mathlib.Analysis.SpecificLimits` | Geometric series, etc. | Contraction convergence |
| `Mathlib.MeasureTheory` | Measure, integration | Stochastic CCV |
| `Mathlib.Analysis.Convex` | Convex sets and functions | Trust simplex, phase portrait |

---

## Part 2 — Continuity and Limits

### 2.1 Continuity Patterns

```lean
-- Continuous: globally continuous
-- ContinuousAt: continuous at a point
-- ContinuousOn: continuous on a set

-- Proving continuity (common approach):
-- 1. Structure: use continuity lemma combinator
theorem my_continuous : Continuous (fun x => x^2 + 3*x) := by
  fun_prop  -- Mathlib's automation for function properties

-- 2. Manual: compose continuous functions
theorem my_continuous' : Continuous (fun x : ℝ => x^2 + 3*x) := by
  apply Continuous.add
  · exact continuous_pow 2
  · exact continuous_const.mul continuous_id
```

### 2.2 Limits and Convergence

```lean
-- Sequence converges to l
theorem seq_limit : Filter.Tendsto (fun n : ℕ => (1 : ℝ) / n) atTop (nhds 0) := by
  exact tendsto_const_div_atTop_nhds_0_nat 1

-- Geometric series convergence (key for contraction)
-- |r| < 1 → ∑ r^n converges
-- Mathlib: hasSum_geometric_of_lt_one

-- Rate of convergence (Project contraction)
-- After n iterations: |x_n - x*| ≤ α^n * |x_0 - x*|
-- Use: pow_le_pow_of_le_one
```

### 2.3 Project Convergence Patterns

| Project concept | Analysis formulation | Key Mathlib lemma |
|---|---|---|
| Trust contraction | Geometric decay `α^n * d₀` | `pow_le_pow_of_le_one` |
| Value iteration | Banach fixed point | `ContractingWith.fixedPoint` |
| Lyapunov decay | `V(x_{n+1}) ≤ c * V(x_n)`, `c < 1` | Custom + `tendsto_pow_atTop_nhds_zero_of_lt_one` |
| OKD mixing | `‖P^n - π‖ ≤ (1-γ)^n` | Spectral gap + geometric bound |
| Phase boundary | Continuity of classification at threshold | `ContinuousAt` + `Filter.Eventually` |

---

## Part 3 — Differentiation

### 3.1 HasDerivAt (1D)

```lean
-- HasDerivAt f f' x: f has derivative f' at x
-- Project cusp module uses this extensively

theorem cusp_potential_deriv (x a b : ℝ) :
    HasDerivAt (fun x => x^4/4 + a*x^2/2 + b*x) (x^3 + a*x + b) x := by
  have h1 := (hasDerivAt_pow 4 x).div_const 4
  have h2 := ((hasDerivAt_pow 2 x).const_mul (a/2))
  have h3 := hasDerivAt_id x |>.const_mul b
  convert h1.add (h2.add h3) using 1
  ring

-- Critical points: f'(x) = 0
-- Second derivative test: HasDerivAt f' f'' x
-- Hessian positive → local minimum (Lyapunov)
```

### 3.2 FDeriv (Fréchet, multi-dimensional)

```lean
-- HasFDerivAt f f' x: f has Fréchet derivative f' at x
-- f' : E →L[ℝ] F (continuous linear map)

-- For Project: gradient of Lyapunov function V: ℝⁿ → ℝ
-- ∇V(x) · f(x) < 0 for stability
```

### 3.3 Derivative Tactics

```lean
-- Automatic differentiation:
-- `fun_prop` can often prove HasDerivAt goals
-- `simp [HasDerivAt]` + `ring` for cleanup
-- For complex expressions: decompose with have + convert
```

---

## Part 4 — Metric Spaces and Contraction

### 4.1 Metric Space Basics

```lean
-- dist : α → α → ℝ (nonneg, symmetric, triangle inequality)
-- edist : α → α → ℝ≥0∞ (extended nonneg reals)

-- Ball:
-- Metric.ball x r = { y | dist x y < r }
-- Metric.closedBall x r = { y | dist x y ≤ r }

-- Key: ℝ, ℝⁿ, C(X,Y) are all metric spaces in Mathlib
```

### 4.2 Contraction Mapping Theorem

Extracted to single canonical reference:
[`references/lean4-contraction-catalog.md`](../../references/lean4-contraction-catalog.md).
That file owns the `ContractingWith` API, fixed-point lemma list, the
affine trust-contraction pattern, and the project contraction-theorem
index.  When citing a Banach lemma, link there rather than restating
the API in this file.

### 4.3 Normed and Banach Spaces

```lean
-- NormedAddCommGroup: ‖x‖ (norm)
-- NormedSpace 𝕜 E: scalar multiplication compatible with norm
-- CompleteSpace: every Cauchy sequence converges (Banach)

-- Project relevance:
-- RL value functions live in Banach spaces
-- Bellman operator is a contraction on (V, ‖·‖_∞)
```

---

## Part 5 — Convex Analysis

### 5.1 Convex Sets

```lean
-- Convex ℝ s : Prop
-- ∀ x ∈ s, ∀ y ∈ s, ∀ a b, 0 ≤ a → 0 ≤ b → a + b = 1 → a • x + b • y ∈ s

-- Project simplex is convex:
-- { (r,s,k) ∈ ℝ³ | r + s + k = 1, r ≥ 0, s ≥ 0, k ≥ 0 }
-- Mathlib: stdSimplex ℝ (Fin 3)
```

### 5.2 Convex Functions

```lean
-- ConvexOn ℝ s f : f is convex on s
-- Key for Lyapunov: V is often convex → sublevel sets are convex → stability

-- Jensen's inequality: ConvexOn.smul_le_sum
```

### 5.3 Project Convex Combination Pattern

```lean
-- Phase portrait uses convex combinations:
-- x_new = λ * x_stable + (1-λ) * x_current
-- Proof pattern:
theorem convex_in_simplex (hλ : 0 ≤ λ) (hλ1 : λ ≤ 1)
    (hx : x ∈ s) (hy : y ∈ s) (hs : Convex ℝ s) :
    λ • x + (1 - λ) • y ∈ s :=
  hs hx hy hλ (sub_nonneg.mpr hλ1) (add_sub_cancel _ _)
```

---

## Part 6 — Measure Theory Essentials

### 6.1 When Measure Theory Appears

- **StochasticCCV:** Row-stochastic matrices, stationary distributions
- **Probabilistic convergence:** Almost-sure convergence, `MeasureTheory.ae`
- **Ergodic theory:** Mixing time, spectral gap

### 6.2 Key Types

```lean
-- MeasurableSpace α: σ-algebra on α
-- MeasureTheory.Measure α: a measure on α
-- MeasureTheory.ProbabilityMeasure α: normalized to 1

-- Lebesgue integral: ∫ x, f x ∂μ
-- Mathlib: MeasureTheory.integral

-- Almost everywhere: MeasureTheory.ae μ
-- filter for "all but measure-zero"
```

### 6.3 Probability in the project

```lean
-- Stochastic matrix: each row sums to 1
-- P : Matrix (Fin n) (Fin n) ℝ
-- ∀ i, ∑ j, P i j = 1
-- ∀ i j, 0 ≤ P i j

-- Stationary distribution: π P = π
-- Convergence: P^n → 1_π (under irreducibility + aperiodicity)
```

---

## Part 7 — Research Council Integration

Consolidated into the single canonical routing matrix:
[`references/research-council-skill-map.md`](../../references/research-council-skill-map.md)
(see the "Analysis" section).  When dispatching a question to a
council member, cite that table rather than restating the rows here.

---

## Part 8 — Project Analysis Module Reference

### 8.1 LyapunovStability Module Stats

- **File:** `LyapunovStability.lean`
- **Current size:** 2,353 lines / 127 theorems
- **Scope:** Quadratic Lyapunov functions, cusp energy, convergence rates, contraction theorem library

### 8.2 IVT Patterns

Extracted to single canonical reference:
[`references/lean4-ivt-patterns.md`](../../references/lean4-ivt-patterns.md).
That file owns the full incantation, polynomial-continuity prerequisite,
project `asymmetric_three_roots_ivt` application, and the pitfall table.

### 8.3 Contraction Theorem Library

Extracted to single canonical reference:
[`references/lean4-contraction-catalog.md`](../../references/lean4-contraction-catalog.md).
That file owns the `ContractingWith` API, geometric-decay lemma, the
affine trust-contraction pattern, the project contraction-theorem
index, and the Lyapunov direct-method bridge.

---

## Part 8 — Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| `ℝ` vs `ℝ≥0` confusion | Type mismatch on nonneg results | Use `.toReal` or `NNReal.coe_*` lemmas |
| Filter direction wrong | `atTop` vs `atBot` | Check: are you going to ∞ or 0? |
| Missing `CompleteSpace` | Contraction theorem won't apply | Add hypothesis or use `instCompleteSpaceReal` |
| `norm` vs `abs` | `‖x‖` vs `|x|` for `ℝ` | They're definitionally equal on `ℝ`, but `rw [Real.norm_eq_abs]` may help |
| Derivative of composed function | `HasDerivAt` won't compose automatically | Use `HasDerivAt.comp` explicitly |
| Measure vs volume | Wrong default measure | Specify `volume` or `MeasureTheory.MeasureSpace.volume` |

---

## See also

- [`../../templates/Template_Analysis.md`](../../templates/Template_Analysis.md) — Template: Real analysis (continuity, Lipschitz, sqrt)
- [`../../references/lean4-proof-strategy.md`](../../references/lean4-proof-strategy.md) — Proof strategy & error priority
- [`../../references/lean4-tactic-hierarchy.md`](../../references/lean4-tactic-hierarchy.md) — Tactic priority for analysis goals
