---
name: lean-math-analysis-handbook
description: Unified reference handbook for @lean-math-analysis (Lean 4 formalization
  + domain mathematical theory).
extracted_from: skills/lean-math-analysis/SKILL.md
---

# Real Analysis & Topology Encyclopaedia (Lean 4)

> **Layering note.** This file holds the deep encyclopaedia content
> previously embedded in [`skills/lean-math-analysis/SKILL.md`](../skills/lean-math-analysis/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow / Recovery /
> Handoffs) and the high-frequency pitfalls / recipes; this file holds the
> full reference content. Zero fidelity loss vs the pre-layering revision.

## Part 1 -- Mathlib's Analysis Architecture

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

## Part 2 -- Continuity and Limits

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

## Part 3 -- Differentiation

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

## Part 4 -- Metric Spaces and Contraction

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

## Part 5 -- Convex Analysis

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

## Part 6 -- Measure Theory Essentials

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


---

## Part 7 -- Research Council Integration

Consolidated into the single canonical routing matrix:
[`research-council-skill-map.md`](research-council-skill-map.md)
(see the "Analysis" section).  When dispatching a question to a
council member, cite that table rather than restating the rows here.

---

## Part 8 -- Project Analysis Module Reference

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

---

## Inline Pitfalls & Recovery Recipes (from `skills/lean-math-analysis/SKILL.md`)

# Lean 4 Real Analysis & Topology

Guide to formalizing analysis and topology in Lean 4 using Mathlib's filter-based approach.

## Routing

- **USE FOR:** real analysis, functional analysis, topology, and measure theory in Lean 4 / Mathlib -- continuous functions, derivatives, integrals, metric
  / normed spaces, filter-based convergence, contraction mappings, convex analysis, spectral theory, and the real-valued bridges from a Nat-scaled model.
- **DO NOT USE FOR:** stochastic / probabilistic convergence (delegate to `@lean-math-stochastic`); deterministic dynamical-system stability proofs
  (delegate to `@lean-math-dynamical`); pure optimization (delegate to `@lean-math-optimization`); typeclass-tower reasoning (delegate to
  `@lean-math-foundations`); writing one specific proof (delegate to `@lean-proof`).
- **TRIGGERS:** continuous, derivative, integral, metric space, normed space, filter, convergence, topology, measure space, contraction, Banach.

## Workflow

1. Map the problem to Mathlib's filter-based architecture (Part 1) -- most analysis goals can be phrased as `Tendsto ... atTop` or `ContinuousAt`.
2. Locate the relevant Part below (continuity, derivatives, integrals, normed spaces, measure theory) and apply the pattern.
3. If the result is a concrete proof obligation, handoff to `@lean-proof`; if it depends on a foundational instance, handoff to `@lean-math-foundations`.

## Recovery & STOP

- STOP if the lemma you need is not in Mathlib at the current pin -- escalate to `@lean-research` to verify, then `@lean-proof` to author a local helper.
- STOP if a classical-only result is invoked and the project has documented constructive constraints -- escalate to `@lean-review-council`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-proof` (mid-proof convergence goal), `skill:lean-research` (when a survey turns up an analysis API).
- **Successors:** `skill:lean-proof` (apply the analysis pattern), `skill:lean-proof-review` (audit the resulting proof), `skill:lean-math-foundations`
  (when the goal collapses to a typeclass-tower issue).

## Detailed reference

Full encyclopaedia content (Parts 1 through 8) lives in
[`references/lean4-math-analysis.md`](../../references/lean4-math-analysis.md). Load that file
when authoring; the SKILL.md only carries the dispatch contract and
the high-frequency pitfalls / recipes (kept inline below).

| Part | Topic | Covers |
|---|---|---|
| Part 1 | Mathlib's Analysis Architecture | filter-based convergence, topological-space layering |
| Part 2 | Continuity and Limits | Continuous, ContinuousAt, ContinuousOn, Tendsto |
| Part 3 | Differentiation | HasDerivAt, deriv, fderiv, mean-value theorem |
| Part 4 | Metric Spaces and Contraction | MetricSpace, LipschitzWith, ContractingWith, completeness |
| Part 5 | Convex Analysis | ConvexOn, ConvexHull, Jensen's inequality |
| Part 6 | Measure Theory Essentials | MeasureSpace, MeasureTheory.integral, intervalIntegral |
| Part 7 | Research Council Integration | (also kept inline below) -- analysis-domain dispatch matrix |
| Part 8 | Host-Repository Analysis Extensions | repository-local Lyapunov / contraction / convex-on-Nat bridges |

## Part 8 -- Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| `ℝ` vs `ℝ≥0` confusion | Type mismatch on nonneg results | Use `.toReal` or `NNReal.coe_*` lemmas |
| Filter direction wrong | `atTop` vs `atBot` | Check: are you going to ∞ or 0? |
| Missing `CompleteSpace` | Contraction theorem won't apply | Add hypothesis or use `instCompleteSpaceReal` |
| `norm` vs `abs` | `‖x‖` vs `|x|` for `ℝ` | They're definitionally equal on `ℝ`, but `rw [Real.norm_eq_abs]` may help |
| Derivative of composed function | `HasDerivAt` won't compose automatically | Use `HasDerivAt.comp` explicitly |
| Measure vs volume | Wrong default measure | Specify `volume` or `MeasureTheory.MeasureSpace.volume` |

---

## Part 9 -- Tactic Priority for Analysis Goals

When a goal sits in the analysis family, try these in order before reaching for manual `.comp` chains:

1. **`fun_prop`** -- Mathlib's general property-prover for `Continuous`, `Measurable`, `Differentiable`, `StronglyMeasurable` on composed functions. Prefer
   this over manual `Continuous.comp` / `Differentiable.comp` chains.
2. **`continuity`** -- older specialised continuity solver; still helpful when `fun_prop` misses a Mathlib lemma.
3. **`measurability`** -- for `Measurable` / `AEMeasurable` / `StronglyMeasurable` goals; complements `fun_prop`.
4. **`positivity`** -- for `0 < x` / `0 ≤ x` goals involving `exp`, `log`, norms, integrals; pairs well with `gcongr` for inequality chaining.
5. **`gcongr`** -- generalised congruence; replaces a long `MonoOn.*` chain for `≤` between integrals, norms, suprema, etc.
6. **`bound`** -- newer Mathlib bound-prover; useful when `positivity` can't close (e.g., requires a hypothesis to bound).
7. **`norm_num` / `nlinarith`** -- pure numeric / nonlinear arithmetic; last-resort closers for concrete numeric bounds.

If nothing fires, fall back to explicit `apply HasDerivAt.comp`, `apply Continuous.comp`, etc. -- but those are last-resort.

---

## Part 10 -- Filter-Convergence Escape Hatches

When `Tendsto` won't simp:

- **`eventually_atTop`** rewrites `∀ᶠ n in atTop, P n` to `∃ N, ∀ n ≥ N, P n` -- switch when classical existence is easier than filter algebra.
- **`Filter.tendsto_atTop_atTop`** -- discrete `f n → ∞`: prove `∀ b, ∃ N, ∀ n ≥ N, b ≤ f n`.
- **`Tendsto.comp`** -- composition of limits; the most common building block.
- **`Filter.eventually_iff_exists_mem`** -- convert between `∀ᶠ` and explicit set membership.
- **`Metric.tendsto_atTop`** -- for metric-space convergence, use the `ε / δ` form directly when filter-arithmetic gets stuck.

When integration limits won't compute:

- **`MeasureTheory.integral_congr_ae`** -- change the integrand on a null set without re-proving integrability.
- **`MeasureTheory.intervalIntegral.integral_congr`** -- change of variables on a compact interval.
- **`MeasureTheory.lintegral_lt_top_iff_finite_set_of_pos`** -- when proving an `lintegral` is finite, this often beats direct estimation.

---

## See also

- [`../../references/lean4-math-analysis.md`](../../references/lean4-math-analysis.md) -- Real Analysis & Topology Encyclopaedia (full encyclopaedia,
  extracted from this skill)
- [`../../templates/Template_Analysis.md`](../../templates/Template_Analysis.md) -- Template: Real analysis (continuity, Lipschitz, sqrt)
- [`../../references/lean4-proof-strategy.md`](../../references/lean4-proof-strategy.md) -- Proof strategy & error priority
- [`../../references/lean4-tactic-hierarchy.md`](../../references/lean4-tactic-hierarchy.md) -- Tactic priority for analysis goals

---

## Merged Domain Companion: `lean-math-analysis` (Unified into `@lean-math-analysis`)

# Math Topology & Real Analysis

Topological and analytic foundations for dynamical systems, convergence proofs, and contraction mappings.

---

## Routing

- **USE FOR:** Point-set topology, functional analysis, real analysis, and topological methods for dynamical systems. Use for reasoning about continuity,
  compactness, fixed-point theorems, Banach spaces, metric spaces, convergence, and the topological foundations underlying Lyapunov stability, contraction
  mappings, and phase portrait analysis.
- **DO NOT USE FOR:** Lean analysis proofs (use @lean-math-analysis); algebraic structures (use @lean-math-foundations); measure theory (use
  @lean-math-stochastic).
- **TRIGGERS:** point-set topology, functional analysis, real analysis, continuity, compactness, topological method.

## Workflow

1. Classify the question: point-set topology, functional analysis, real analysis, or topological dynamics.
2. Pick the matching section of the body; identify the Mathlib `Topology` / `Analysis` namespace.
3. Produce the answer; cite the relevant Mathlib lemma and verify it at the current pin.
4. Hand off: to `@lean-math-analysis` for the Lean proof, to `@lean-math-stochastic` if measure-theoretic structure surfaces, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the question is algebraic-structural -- delegate to `@lean-math-foundations`.
- STOP if measure theory dominates -- delegate to `@lean-math-stochastic`.
- STOP if a pin-verified Mathlib lemma is required -- escalate to `@lean-research`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-math-analysis`, `skill:lean-math-foundations`, `skill:lean-zettelkasten`.

---

## Part 1 -- Metric Spaces & Topology

### 1.1 Metric Space Fundamentals

| Concept | Definition | Common use |
|---|---|---|
| Metric | $d(x,y) \ge 0$, $d(x,y) = 0 \iff x=y$, triangle inequality | Trust distance, L1 on simplex |
| Open ball | $B(x,r) = \{y : d(x,y) < r\}$ | Neighborhoods in phase space |
| Cauchy sequence | $\forall \epsilon > 0, \exists N, \forall m,n > N: d(x_m, x_n) < \epsilon$ | Convergence of governance |
| Completeness | Every Cauchy sequence converges | Banach fixed-point applicability |
| Compactness | Every open cover has finite subcover | Bounded phase space |
| Total boundedness | $\forall \epsilon, \exists$ finite $\epsilon$-net | Finite approximation of state space |

### 1.2 Key Fixed-Point Theorems

| Theorem | Statement | Common application |
|---|---|---|
| **Banach** | Contraction on complete metric space ⟹ unique fixed point | Bellman operator, governance Lyapunov |
| **Brouwer** | Continuous map $B^n → B^n$ has fixed point | Trust equilibrium existence |
| **Schauder** | Continuous map on compact convex ⟹ fixed point | Infinite-dimensional generalizations |
| **Kakutani** | Upper-hemicontinuous correspondence ⟹ fixed point | Nash equilibrium existence |
| **Tarski** | Monotone function on complete lattice ⟹ fixed point | Lattice-ordered quality gates |
| **Knaster-Tarski** | Monotone on CPO ⟹ least/greatest fixed points | Order-theoretic gate properties |

### 1.3 Contraction Mapping Theory

The central tool for contraction-based convergence:

**Banach Contraction Principle:**
If $T: X → X$ is a contraction ($d(Tx,Ty) \le \alpha d(x,y)$, $\alpha < 1$) on a complete metric space, then:
- Unique fixed point $x^* = Tx^*$
- Iteration converges: $d(T^n x, x^*) \le \frac{\alpha^n}{1-\alpha} d(x, Tx)$
- Rate: geometric $O(\alpha^n)$

**Common extensions:**
- Asymptotic regularity: weaker than contraction, still converges
- Non-expansive mappings + additional conditions
- Composition of contractions: product of rates
- Multiscale contractions: hierarchical convergence bounds

---

## Part 2 -- Topological Dynamics

### 2.1 Dynamical Systems on Metric Spaces

For $\phi_t : X → X$ continuous:
- **Orbit**: $\mathcal{O}(x) = \{\phi_t(x) : t \ge 0\}$
- **$\omega$-limit set**: $\omega(x) = \bigcap_{T>0} \overline{\{\phi_t(x) : t \ge T\}}$
- **Invariant set**: $A$ where $\phi_t(A) = A$ for all $t$
- **Attracting set**: $\exists$ neighborhood $U$ with $\phi_t(U) \subseteq U$ and $\bigcap_t \phi_t(U) = A$

### 2.2 Compactness Arguments

Bounded phase spaces such as quality measures in $[0,1]^n$ are compact:
- **Bolzano-Weierstrass**: Every sequence has convergent subsequence
- **Arzela-Ascoli**: Equicontinuous + pointwise bounded ⟹ compact in $C(X)$
- **Prokhorov**: Tight probability measures ⟹ compact (for stochastic CCV)

### 2.3 Stability Topology

| Stability Type | Topological Characterization |
|---|---|
| Lyapunov stable | $\forall$ neighborhood $U$, $\exists V \subseteq U$ with $\phi_t(V) \subseteq U$ |
| Asymptotically stable | Lyapunov stable + $\omega(x) = \{x^*\}$ for nearby $x$ |
| Globally asymptotically stable | Asymptotically stable with basin $= X$ |
| Exponentially stable | $d(\phi_t(x), x^*) \le C e^{-\alpha t} d(x, x^*)$ |

---

## Part 3 -- Functional Analysis Essentials

### 3.1 Banach Spaces

- **Norm**: $\|x\| \ge 0$, homogeneity, triangle inequality
- **Complete normed space** = Banach space
- **Commonly relevant**: $\ell^\infty$ (value functions), $\ell^1$ (simplex measures), $L^p$ (distributional properties)

### 3.2 Key Operators

| Operator | Type | Common use |
|---|---|---|
| Bellman operator $T$ | Contraction on $\ell^\infty$ | Value iteration |
| Stochastic transition $P$ | Linear on simplex | Stochastic dynamics |
| Lyapunov map $V \mapsto V \circ \phi$ | Nonlinear, monotone | Stability analysis |
| Gradient $\nabla f$ | Linear map $X → X^*$ | Optimization |

### 3.3 Spectral Theory

- **Spectrum**: $\sigma(A) = \{\lambda : (A - \lambda I) \text{ not invertible}\}$
- **Spectral radius**: $\rho(A) = \max |\sigma(A)|$
- **Spectral gap**: $1 - \rho_2$ where $\rho_2$ = second-largest eigenvalue modulus
- **Perron-Frobenius**: Non-negative matrix ⟹ dominant eigenvalue real, positive
- **Common use**: spectral gaps of stochastic transition matrices govern mixing time

---

## Part 4 -- Convergence Theory

### 4.1 Types of Convergence

| Type | Definition | Strength | Common use |
|---|---|---|---|
| Pointwise | $f_n(x) → f(x)$ for each $x$ | Weakest | -- |
| Uniform | $\sup_x |f_n(x) - f(x)| → 0$ | Stronger | Value iteration |
| $L^p$ | $\|f_n - f\|_p → 0$ | Intermediate | Distributional |
| Weak | $\langle f_n, g \rangle → \langle f, g \rangle$ for all $g$ | Weakest in Banach | -- |
| In measure | $\mu(\{|f_n - f| > \epsilon\}) → 0$ | Probabilistic | Stochastic CCV |
| Almost sure | $f_n(\omega) → f(\omega)$ a.e. | Strong probabilistic | Ergodic limits |

### 4.2 Rate of Convergence

- **Linear**: $\|x_{n+1} - x^*\| \le c \|x_n - x^*\|$, $c < 1$
- **Superlinear**: $\|x_{n+1} - x^*\| / \|x_n - x^*\| → 0$
- **Quadratic**: $\|x_{n+1} - x^*\| \le C \|x_n - x^*\|^2$
- **Sublinear**: $\|x_n - x^*\| \le C/n^\alpha$ -- common for SGD

---

## Part 5 -- Filter Theory (Lean/Mathlib Perspective)

Mathlib uses filters for convergence:

### 5.1 Key Filters

| Filter | Lean Name | Captures |
|---|---|---|
| Neighborhood | `nhds a` | Convergence to point $a$ |
| At infinity | `Filter.atTop` | Limit as $n → ∞$ |
| Eventually | `Filter.Eventually` | "for sufficiently large $n$" |
| Frequently | `Filter.Frequently` | Infinitely often |
| Cofinite | `Filter.cofinite` | All but finitely many |

### 5.2 Tendsto

$f$ converges to $L$ along filter $F$:
```
Filter.Tendsto f F (nhds L) ↔ ∀ U ∈ nhds L, f⁻¹(U) ∈ F
```

### 5.3 Common Patterns

- `Filter.Tendsto f atTop (nhds L)`: sequence converges
- `Filter.Tendsto f atTop atTop`: diverges to infinity
- `Filter.Eventually (P ∘ f) atTop`: eventually holds

---

## Part 6 -- Host-Repository Lean Extension Points

Do not assume repository-local Lean modules, tactics, or namespaces exist unless the host repository explicitly provides them. Map local modules by
mathematical role:

| Local extension point | Topological foundation | Typical structures |
|---|---|---|
| Lyapunov/stability module | metric stability, Banach contraction | Lyapunov functions, sublevel sets |
| RL/value-function module | $\ell^\infty$ contraction | Bellman contraction, value functions |
| Stochastic-dynamics module | L1 metric, spectral gap | transition step, spectral gap |
| Bifurcation/catastrophe module | bifurcation topology | discriminants, critical sets |
| Safety/trust module | product metric spaces | multi-agent trust distance |
| Tactic-helper module | contraction lemma library | iterate bounds, convexity bounds |

---

## Part 7 -- Research Methodology

### 7.1 Topological Proof Strategies

1. **Contraction**: Verify metric and rate → apply Banach
2. **Compactness**: Establish bounded state space → extract convergent subsequence
3. **Monotone convergence**: Find ordering + bounded → limit exists
4. **Barrier/Lyapunov**: Construct sublevel set → show invariance + decrease
5. **Spectral**: Compute eigenvalues → bound convergence via spectral gap

### 7.2 Key References

- Munkres (2000) -- Topology (point-set foundations)
- Rudin (1991) -- Functional Analysis
- Granas & Dugundji (2003) -- Fixed Point Theory
- Kreyszig (1989) -- Introductory Functional Analysis
- Brezis (2011) -- Functional Analysis, Sobolev Spaces

---
## Goal-Shape Templates (templates)

| Goal Shape | Target Typeclass / Lemma | Proof Template |
| :--- | :--- | :--- |
| `Continuous (fun x => f (g x))` | `fun_prop` / `continuity` | `by fun_prop` |
| `Tendsto (fun x => f x + g x) l (𝓝 (a + b))` | `Tendsto.add` | `exact hf.add hg` |
| `HasDerivAt f f' x` | `HasDerivAt` rules | `exact (hf.mul hg).add ...` |
| `dist (f x) (f y) ≤ K * dist x y` | `LipschitzWith` | `rw [dist_eq_norm]; ...` |

## Intent-to-Tactic Phrasebook (phrasebook)

| Mathematical Intent | Lean 4 / Mathlib Tactic | Notes |
| :--- | :--- | :--- |
| Prove continuity, differentiability, or measurability | `by fun_prop` | Supersedes legacy `continuity` for most composite expressions |
| Work with eventualities `∀ᶠ x in l, P x` | `filter_upwards [h1, h2] with x hx1 hx2` | Avoids unfolding `Filter.Eventually` |
| Convert normed distance `dist x y` to `‖x - y‖` | `simp only [dist_eq_norm]` | Bridges `MetricSpace` and `NormedAddCommGroup` |
| Apply Extreme Value Theorem on compact set | `IsCompact.exists_isMinOn` / `IsCompact.exists_isMaxOn` | Requires `hs : IsCompact s`, `hne : s.Nonempty`, `hf : ContinuousOn f s` |

## Error-to-Fix Table (errors)

| Error / Symptom | Root Cause | Fix |
| :--- | :--- | :--- |
| `deriv f x` rewrites fail | `deriv f x` returns `0` if `f` is not differentiable at `x` | Prove `HasDerivAt f f' x` first, then apply `HasDerivAt.deriv` |
| `(ε, δ)` proof explosion on limit goal | Unfolded `Metric.tendsto_nhds` prematurely | Keep `Tendsto` abstract and compose `Tendsto.comp` / `Tendsto.add` |
| Punctured vs full neighborhood mismatch | `𝓝[≠] x` vs `𝓝 x` | Use `tendsto_nhdsWithin_of_tendsto_nhds` to weaken `𝓝 x` to `𝓝[s] x` |

---

## Annex: Legacy Quick-Reference Supplement (Analysis)

# Real Analysis & Topology Encyclopaedia (Lean 4)

> **Layering note.** This file holds the deep encyclopaedia content
> previously embedded in [`skills/lean-math-analysis/SKILL.md`](../skills/lean-math-analysis/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow / Recovery /
> Handoffs) and the high-frequency pitfalls / recipes; this file holds the
> full reference content. Zero fidelity loss vs the pre-layering revision.

## Part 1 -- Mathlib's Analysis Architecture

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

## Part 2 -- Continuity and Limits

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

## Part 3 -- Differentiation

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

## Part 4 -- Metric Spaces and Contraction

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

## Part 5 -- Convex Analysis

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

## Part 6 -- Measure Theory Essentials

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


---

## Part 7 -- Research Council Integration

Consolidated into the single canonical routing matrix:
[`research-council-skill-map.md`](research-council-skill-map.md)
(see the "Analysis" section).  When dispatching a question to a
council member, cite that table rather than restating the rows here.

---

## Part 8 -- Project Analysis Module Reference

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

---

## Annex: Intermediate Value Theorem (IVT) Idioms

# IVT patterns in Lean 4 / Mathlib

A canonical reference for the **intermediate-value theorem** as it lives
in Mathlib, the bracketing pattern used to prove root existence, and
typical project applications (sign-change in catastrophe-theory cubics,
equilibrium existence for Markov chains).  Every consumer skill that
needs an IVT bracket should link here rather than restate the lemma.

## 1. The canonical Mathlib incantation

```lean
-- Import: Mathlib.Topology.Order.IntermediateValue
-- Key theorem: IsPreconnected.intermediate_value₂

-- For continuous f : ℝ → ℝ with f a ≤ 0 ≤ f b (with hab : a ≤ b):
isPreconnected_Icc.intermediate_value₂
  (left_mem_Icc.mpr hab) (right_mem_Icc.mpr hab)
  hf.continuousOn continuous_const.continuousOn
  (le_of_lt ha) (le_of_lt hb)
-- → ∃ c ∈ Set.Icc a b, f c = 0
```

## 2. Alternative API entry-points

```lean
-- intermediate_value_uIcc : Set.uIcc (unordered interval) variant
-- intermediate_value_Icc  : gives Set.Icc (f a) (f b) ⊆ f '' Set.Icc a b
--                          (use this when you want a value, not just existence)
```

`intermediate_value_Icc` is the right choice when the surrounding proof
already has a specific target value `y ∈ Set.Icc (f a) (f b)`.
`IsPreconnected.intermediate_value₂` is the right choice when you only
need *some* zero of `f - g`.

## 3. Project application -- `asymmetric_three_roots_ivt`

Sign analysis for the cusp polynomial `x³ - 3x + 1 = 0`, on the
intervals `[a, b]` with `a = -3`, `b = 1`:

```lean
-- f(-2) = -8 + 6 + 1 = -1 < 0
-- f(-1) = -1 + 3 + 1 =  3 > 0  → root in (-2, -1)
-- f( 0) =           1 > 0
-- f( 1) = 1 - 3 + 1 = -1 < 0   → root in (0, 1)
-- f( 2) = 8 - 6 + 1 =  3 > 0   → root in (1, 2)
```

The three brackets each feed one `IsPreconnected.intermediate_value₂`
invocation; the `three_distinct_roots` statement then unions the
witnesses with `Distinct.of_lt`.

## 4. Polynomial continuity (the usual prerequisite)

```lean
-- Polynomial functions are continuous; `fun_prop` closes the goal.
example (a b : ℝ) : Continuous (fun x : ℝ => x^3 + a*x + b) := by fun_prop

-- Manually: continuous_pow + Continuous.mul + Continuous.add
```

## 5. Common pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Forgetting `hab : a ≤ b` | "could not unify Icc" | Add the explicit `le` hypothesis |
| Pre-rotated sign hypotheses | "expected `≤ 0`, got `0 ≤`" | Use `neg_le_neg_iff` to flip |
| `f` not continuous on the closed interval | `intermediate_value` fails | Discharge with `Continuous.continuousOn hf` |
| Searching for `IVT` by name | symbol not found | Mathlib uses `intermediate_value_*` and `IsPreconnected.intermediate_value_*` |

## 6. Where the canonical block was duplicated before this extraction

| Location | Lines (pre-extraction) |
|---|---|
| `skills/lean-math-analysis §8.2` | ~12 |
| `skills/lean-math-dynamical §Part 8` | ~20 |
| `skills/lean-math-stochastic §8.4` | ~10 |

All three now `See also`-link this file.

---

## Annex: Banach Contraction Mapping Catalog

# Contraction & Banach fixed-point catalog

Single canonical reference for every place a Lean 4 + Mathlib4 project
reasons about **contraction maps**: the `ContractingWith` bundle, the
Banach fixed-point theorem, geometric decay from a contraction factor,
and the inventory of host-repository contraction theorems.  All consumer
skills (analysis, dynamical, optimization, AI safety) link here.

## 1. Mathlib API entry-points

```lean
import Mathlib.Topology.MetricSpace.Contracting

-- ContractingWith K f : Prop
-- where K : ℝ≥0, K < 1, dist (f x) (f y) ≤ K * dist x y

-- Fixed point existence + uniqueness:
-- ContractingWith.fixedPoint  (complete metric space required)
-- ContractingWith.tendsto_iterate_fixedPoint  → convergence to fixed point

-- For lattice-side (Knaster-Tarski):
import Mathlib.Order.FixedPoints
-- CompleteLattice.fixedPoint_lfp, CompleteLattice.fixedPoint_gfp
```

## 2. Geometric decay from a contraction factor

The bread-and-butter lemma: if a process satisfies
`‖x_{n+1} - x*‖ ≤ α · ‖x_n - x*‖` with `0 ≤ α < 1`, then
`‖x_n - x*‖ ≤ α^n · ‖x_0 - x*‖ → 0`.

```lean
theorem convergence_from_contraction (hα : α < 1) (hα0 : 0 ≤ α) :
    Filter.Tendsto (fun n => α^n * d₀) Filter.atTop (nhds 0) :=
  (tendsto_pow_atTop_nhds_zero_of_lt_one hα0 hα).const_mul d₀ |>.congr
    (fun n => (mul_comm _ _))
```

Key Mathlib lemma: `tendsto_pow_atTop_nhds_zero_of_lt_one`.
Adjacent: `tendsto_pow_atTop_nhds_zero_of_norm_lt_one` (normed case).

## 3. Project pattern -- affine trust contraction

```lean
theorem trust_contraction (α : ℝ) (hα : 0 ≤ α) (hα1 : α < 1)
    (target : ℝ) (x : ℝ) :
    |α * x + (1 - α) * target - target| = α * |x - target| := by
  ring_nf
  rw [abs_mul, abs_of_nonneg hα]
```

This pattern recurs whenever an iteration is convex-combination of a
state and a fixed target.  The right-hand side is exactly the geometric
decay setup from §2.

## 4. Project contraction theorem index

| Theorem | Location | Description |
|---|---|---|
| `trust_L1_contraction` | `AgenticSafety.lean` | L¹ trust contraction bound |
| `trust_L1_exact` | `AgenticSafety.lean` (line 2075) | Exact L¹ trust equality |
| `okdStep_L1_contraction` | `StochasticCCV.lean` | L¹ contraction for OKD step |
| `ContractingWith.fixedPoint` | Mathlib | Banach fixed point (complete metric space) |
| `BellmanOperator.contracting` | `ReinforcementLearning.lean` | Bellman operator is `γ`-contraction |

## 5. Lyapunov direct method (the discrete-time bridge)

For `x_{n+1} = f(x_n)` with equilibrium `x* = 0`:

1. **Find** a Lyapunov function `V : State → ℝ` with:
   - `V(0) = 0`
   - `V(x) > 0` for `x ≠ 0`
   - `V(f(x)) - V(x) ≤ 0` (stability) or `< 0` (asymptotic stability)
   - `V(f(x)) ≤ c · V(x)` with `c < 1` (exponential stability)

2. **Formalize**:

```lean
structure LyapunovFn (State : Type) where
  V : State → ℝ
  V_nonneg : ∀ x, 0 ≤ V x
  V_zero : V equilibrium = 0
  V_pos : ∀ x, x ≠ equilibrium → 0 < V x
  V_decrease : ∀ x, V (f x) ≤ V x
  -- or: V_contract : ∃ c < 1, ∀ x, V (f x) ≤ c * V x
```

For `V(x) = x²` non-negativity, use `sq_nonneg`, `mul_self_nonneg`, or
`positivity`.  The deprecated `proj_lyapunov` tactic is gone -- use the
underlying tactics (`positivity`, `nlinarith [sq_nonneg x, ...]`, `ring`,
`norm_num`) directly.

## 6. Project Lyapunov-function inventory

| Module | Lyapunov function | Key property | Proof technique |
|---|---|---|---|
| LyapunovStability | `V(q) = (q - q*)²` | Quadratic, `V ≥ 0` | `sq_nonneg` + `nlinarith` |
| LyapunovStability | Cusp energy `E(x;a,b)` | Critical-point analysis | `HasDerivAt` + calculus |
| AgenticSafety | Trust distance `|t - t*|` | Contraction by `α` | `abs_mul` + geometric decay |
| ReinforcementLearning | Bellman residual `‖V - V*‖` | Contraction by `γ` | Banach fixed point |
| StochasticCCV | L¹ distance to stationary | Spectral-gap decay | Matrix analysis |

## 7. Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Missing `CompleteSpace` | `ContractingWith.fixedPoint` won't apply | Add hypothesis or use `instCompleteSpaceReal` |
| `ℝ` vs `ℝ≥0` confusion | type mismatch on the contraction factor | Use `.toReal` or `NNReal.coe_*` lemmas |
| Trying `apply ContractingWith.fixedPoint` cold | "could not synthesise instance" | Bundle the `ContractingWith` first, then `apply` |
| Geometric-decay forgotten | `Tendsto` proof loops | Use `tendsto_pow_atTop_nhds_zero_of_lt_one` directly |

## 8. Where the contraction block was duplicated before this extraction

| Location | Lines (pre-extraction) |
|---|---|
| `lean-math-foundations §4.3` | ~12 |
| `lean-math-analysis §4.2 + §8.3` | ~35 |
| `lean-math-dynamical §Part 2` | ~55 |
| `lean-math-optimization §3.2` | ~25 |
| `lean-ai-formalization §2.3` | ~10 |

All five now `See also`-link this file.

