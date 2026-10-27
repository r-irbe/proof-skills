---
name: "lean-math-stochastic-handbook"
description: "Unified reference handbook for @lean-math-stochastic (Lean 4 formalization + domain mathematical theory)."
extracted_from: "skills/lean-math-stochastic/SKILL.md"
---

# Stochastic Mathematics Encyclopaedia (Lean 4)

> **Layering note.** This file holds the deep encyclopaedia content
> previously embedded in [`skills/lean-math-stochastic/SKILL.md`](../skills/lean-math-stochastic/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow / Recovery /
> Handoffs) and the high-frequency pitfalls / recipes; this file holds the
> full reference content. Zero fidelity loss vs the pre-layering revision.

## Part 1 — Probability in Mathlib

### 1.1 Architecture

```
MeasurableSpace α       -- σ-algebra
   ↓
MeasureTheory.Measure α  -- measure
   ↓
MeasureTheory.ProbabilityMeasure α  -- normalized to 1
   ↓
MeasureTheory.ae μ       -- almost-everywhere filter
```

### 1.2 Key Namespaces

| Namespace | Content | Project usage |
|---|---|---|
| `MeasureTheory.Measure` | Measures, probability | Stochastic CCV |
| `MeasureTheory.Integral` | Lebesgue integration | Expected values |
| `ProbabilityTheory` | Random variables, independence | (Extended models) |
| `MeasureTheory.ae` | Almost-everywhere reasoning | Convergence statements |
| `Mathlib.LinearAlgebra.Matrix` | Matrix operations | Stochastic matrices |
| `Mathlib.Analysis.Matrix` | Matrix norms | Spectral gap |

### 1.3 Random Variables

```lean
-- A random variable is a measurable function:
-- X : Ω → α where (Ω, ℱ, P) is a probability space

-- Expected value:
-- 𝔼[X] = ∫ ω, X ω ∂P

-- Variance:
-- Var[X] = 𝔼[(X - 𝔼[X])²]
```

---

## Part 2 — Markov Chains

### 2.1 Transition Matrix

the project's `StochasticCCV` module centers on Markov chains:

```lean
-- Row-stochastic matrix: rows sum to 1, entries nonneg
structure StochMatrix (n : ℕ) where
  mat : Matrix (Fin n) (Fin n) ℝ
  nonneg : ∀ i j, 0 ≤ mat i j
  row_sum : ∀ i, ∑ j, mat i j = 1

-- OKD iterate: x_{n+1} = P * x_n
-- Or in row form: π_{n+1} = π_n * P
```

### 2.2 Stationary Distribution

```lean
-- π is stationary for P iff π * P = π (left eigenvector for eigenvalue 1)
def IsStationary (π : Fin n → ℝ) (P : StochMatrix n) : Prop :=
  ∀ j, ∑ i, π i * P.mat i j = π j

-- Existence: prove directly from column sums (Mathlib 4.28 has no general Perron-Frobenius)
-- Uniqueness: irreducible + aperiodic → unique stationary distribution
```

### 2.3 Convergence to Stationary

```lean
-- Fundamental theorem of Markov chains:
-- Under irreducibility + aperiodicity:
-- ‖P^n x₀ - π‖₁ ≤ C * (1 - γ)^n
-- where γ = spectral gap

-- Project formalization:
-- L¹ distance to stationary decays geometrically
-- Rate governed by second-largest eigenvalue
```

### 2.4 Spectral Gap

```lean
-- For a reversible Markov chain with stationary π:
-- eigenvalues: 1 = λ₁ ≥ λ₂ ≥ ... ≥ λ_n > -1
-- spectral gap: γ = 1 - max(|λ₂|, |λ_n|)
-- mixing time: t_mix ≈ 1/γ * ln(1/ε)

-- Project StochasticCCV: spectral gap bounds OKD convergence rate
```

---

## Part 3 — Project Stochastic Patterns

### 3.1 OKD Dynamics on the Simplex

```lean
-- OKD (Organizational Knowledge Dynamics) operates on the 3-simplex:
-- (observation, knowledge, decision) with o + k + d = 1

-- Each Project stage applies a stochastic matrix:
-- Stage E: emphasizes observation
-- Stage A: transitions toward knowledge
-- Stage S: balances all components
-- Stage C: emphasizes knowledge consolidation
-- Stage I: emphasizes decision

-- The full pipeline: P_pipeline = P_E * P_A * P_S * P_C * P_I
-- Birkhoff's theorem: product of stochastic matrices is stochastic
```

### 3.2 Birkhoff's Contraction

```lean
-- Birkhoff's contraction coefficient:
-- τ(P) = (1 - min_ij P_ij / max_ij P_ij) / (1 + min_ij P_ij / max_ij P_ij)
-- ‖P*x - P*y‖₁ ≤ τ(P) * ‖x - y‖₁

-- In Project: τ(P) < 1 for positive stochastic matrices
-- → convergence to stationary distribution
```

### 3.3 Decide Proofs for Stochastic Properties

```lean
-- Project Nat-scaled stochastic matrices:
-- entries are Nat (×100), rows sum to 100

-- Row-sum check:
example : 30 + 40 + 30 = 100 := by decide

-- Nonnegativity is trivial for Nat
-- Convergence bounds use the real-valued analysis layer
```

---

## Part 4 — Time Series Analysis

Extracted to single canonical reference:
[`references/lean4-time-series-patterns.md`](../../references/lean4-time-series-patterns.md).
That file owns the formalisation-approaches table, the project
connections table, the EWMA recurrence + convergence sketch, and the
pitfall list.

---

## Part 5 — Ergodic Theory

Extracted to single canonical reference:
[`references/lean4-ergodic-theory.md`](../../references/lean4-ergodic-theory.md).
That file owns Birkhoff's theorem statement, the Mathlib API
entry-points, the mixing-rate ↔ spectral-gap bridge, and the pitfall
list.

---

## Part 6 — Stochastic Stability

### 6.1 Almost-Sure Stability

```lean
-- x_n → x* almost surely (P-a.s.)
-- In Lean: Filter.Tendsto (trajectory f) atTop (nhds x*) (ae P)

-- Key tools:
-- Borel-Cantelli lemma
-- Martingale convergence theorem
-- Lyapunov function + supermartingale argument
```

### 6.2 Mean-Square Stability

```lean
-- E[‖x_n - x*‖²] → 0 as n → ∞
-- Weaker than a.s. but easier to prove
-- Use: Lyapunov with V(x) = E[‖x - x*‖²]
```

### 6.3 Project Stochastic-Deterministic Bridge

```lean
-- The Project formalization uses deterministic models (Nat-scaled)
-- but the paper discusses stochastic aspects.
-- Bridge strategy:
-- 1. Prove deterministic contraction/stability
-- 2. Show that stochastic perturbations are bounded
-- 3. Conclude stochastic stability via comparison principle
```

---

## Part 7 — Research Council Integration

Consolidated into the single canonical routing matrix:
[`references/research-council-skill-map.md`](../../references/research-council-skill-map.md)
(see the "Stochastic" section).  When dispatching a question to a
council member, cite that table rather than restating the rows here.

---

## Part 8 — Project Stochastic Module Reference

### 8.1 StochasticCCV Module Stats

- **File:** `StochasticCCV.lean`
- **Current size:** 2,289 lines / 123 theorems
- **Scope:** Doubly-stochastic matrices, OKD simplex dynamics, Doeblin mixing, convergence proofs

### 8.2 Perron-Frobenius Absence from Mathlib

As of Lean 4 / Mathlib 4.30, **Mathlib does NOT have a general Perron-Frobenius theorem** for real matrices. Workarounds (all proven in the corpus's `StochMatrix3/4/5` line):

| Problem | Approach (proven) |
|---|---|
| Stationary distribution exists — row-identical kernels | Explicit common row: `rowDistribution` is stationary (no PF, no topology) |
| Stationary distribution exists — strictly positive kernels | Brouwer on the simplex: `step` maps the convex compact simplex to itself, continuous ⇒ fixed point (see §8.5) |
| Stationary distribution uniqueness (strictly positive) | Two stationary π₁ π₂: `dist(π₁,π₂) = dist(Tπ₁,Tπ₂) ≤ r·dist(π₁,π₂)` with r < 1 ⇒ π₁ = π₂ |
| Convergence to stationary | Doeblin δ-bound ⇒ `ContractionMapping` instance (rate `1 − nδ/100`) ⇒ geometric convergence `Tendsto` |
| Stationary sensitivity / gate monotonicity | Perturbation bound: `dist(π_P, π_Q) ≤ ‖T_P π_Q − T_Q π_Q‖₁ / (nδ/100)` |
| Doubly stochastic: uniform is stationary | Column sums = 1 via `field_simp + ring` |

```lean
-- Column stochasticity → uniform is stationary (no PF needed):
-- Each column sums to 1 → (1/n) * ∑ column = 1/n
-- Proved by: field_simp + ring (or norm_num for concrete matrices)
theorem uniformQ_stationary_doubly_stochastic :
    ∀ j, ∑ i, uniformQ i * P.mat i j = uniformQ j := by
  simp [uniformQ]
  field_simp
  ring
```

### 8.5 Finite Markov chain existence pattern (pin-compatible, PROVEN)

The general existence theorem — every strictly positive finite stochastic
matrix has a stationary distribution — is provable **without PF and without
Brouwer** (Mathlib at pin `c5ea003` has neither; verified 2026-09-02:
`exists_fixedPoint_of_convexCompact`, `IsCompact.exists_fixedPoint`,
`Brouwer` are all unknown identifiers).  Two routes:

#### Route A — Doeblin–Cauchy (PRIMARY; proven in `StageMatrix5.lean`)

Every strictly positive `n×n` stochastic matrix is a Doeblin contraction
with factor `r = 1 − n·δ/100 < 1` (take `δ = 1`): the one-step L¹
contraction `‖c₁P − c₂P‖₁ ≤ r·‖c₁ − c₂‖₁` holds for equal-mass vectors.
Then:

1. **Uniform start** `u = (1/n, …, 1/n)`; iterates `xₖ = u·Pᵏ` form an
   **explicit Cauchy sequence**: `‖xₘ − xₙ‖₁ ≤ rᵐ·‖u − x₀‖₁ ≤ rᵐ·2`.
2. **Completeness**: `cauchySeq_tendsto_of_complete` gives a pointwise
   limit `π` (ℝ is complete; no Brouwer needed).
3. **Limit in the simplex**: `∑π = 1` via mass preservation +
   `tendsto_nhds_unique`; `π ≥ 0` via `ge_of_tendsto` of non-negative
   iterates.
4. **Limit is a fixed point**: triangle inequality
   `‖π − πP‖₁ ≤ ‖π − xₙ₊₁‖₁ + ‖xₙ₊₁ − πP‖₁`; both terms → 0 (the second
   by the contraction applied to the tail).  Hence `πP = π`, i.e.
   `∀ j, ∑ i, π i · P[i][j] = π j`.

Key Mathlib pieces: `cauchySeq_tendsto_of_complete`, `tendsto_nhds_unique`,
`ge_of_tendsto`, `tendsto_pow_atTop_nhds_zero_of_lt_one`,
`Finset.sum_add_distrib` (the sum-of-sums vs sum-of-pointwise-sum trap:
`Finset.sum_le_sum` gives `∑(a+b)`, the goal needs `∑a + ∑b`).
Reference implementation: `<Project>/StochasticCCV/StageMatrix5.lean`
`stationary_exists_of_strictlyPositive` (154 lines, 0 sorry/admit/axiom,
LSpec-tested).  Uniqueness of the stationary distribution then follows
from the same contraction (`stationary_unique` in the same module).

#### Route B — Brouwer (FUTURE; blocked at this pin)

When Mathlib lands a Brouwer fixed-point theorem for convex compact sets
(the upstream PR is tracked in mathlib), the classical route becomes
available:

1. **State space**: `stdSimplex ℝ (Fin n)` — `convex_stdSimplex`,
   `isCompact_stdSimplex` already exist at this pin.
2. **Invariance**: `T c = c·P` maps the simplex to itself (non-negativity
   + row sums = 1).
3. **Continuity**: `T` is a finite linear combination of coordinates.
4. **Fixed point**: Brouwer yields `∃ π ∈ Δ, T π = π`.
5. **Stationarity**: `T π = π` is exactly the balance equation.

Until then, Route A is the honest, pin-compatible proof.  The corpus's
`CCVR` module already installs `CCVR.equivStdSimplex` + `Convex`/`IsCompact`
corollaries for the 3-simplex — mirror for `Fin n` when Route B opens.

### 8.3 Doubly-Stochastic Uniqueness

Project proves stationary distribution properties without Perron-Frobenius via:

1. **Column stochasticity → uniform stationary:** `field_simp + ring` on the column-sum condition
2. **Birkhoff approximation:** empirical average of ergodic chain converges to uniform distribution
3. **Integer multiplicity artifact:** multiple integer fixpoints exist in the Nat-scaled model — this is a rounding artifact, not a contradiction of uniqueness

### 8.4 IVT for Equilibrium Existence

For equilibrium existence proofs in related dynamical systems:

```lean
-- Import: Mathlib.Topology.Order.IntermediateValue
-- Key theorem: IsPreconnected.intermediate_value₂ (f vs g = const pattern)

-- For continuous f : ℝ → ℝ with f a ≤ 0 ≤ f b (a ≤ b):
isPreconnected_Icc.intermediate_value₂
  (left_mem_Icc.mpr hab) (right_mem_Icc.mpr hab)
  hf.continuousOn continuous_const.continuousOn
  (le_of_lt ha) (le_of_lt hb)
-- → ∃ c ∈ Set.Icc a b, f c = 0
```

---

---

## Inline Pitfalls & Recovery Recipes (from `skills/lean-math-stochastic/SKILL.md`)

# Lean 4 Stochastic Mathematics

Guide to formalizing probability, stochastic processes, and time series in Lean 4.

## Routing

- **USE FOR:** probability theory, stochastic processes, Markov chains, time-series analysis, ergodic theory, row-stochastic matrices, mixing times,
  spectral gaps, stationary distributions, and any stochastic dynamics in Lean 4.
- **DO NOT USE FOR:** deterministic dynamical systems (delegate to `@lean-math-dynamical`); abstract measure-theoretic typeclass plumbing (delegate to
  `@lean-math-foundations`); pure topology (delegate to `@lean-math-analysis`); writing one specific proof (delegate to `@lean-proof`).
- **TRIGGERS:** probability, stochastic, Markov chain, time series, ergodic, mixing time, spectral gap, stationary distribution, row-stochastic, martingale.

## Workflow

1. Identify the stochastic class (Part 1) — discrete-time chain, continuous-time process, martingale, stationary process, time-series model.
2. Pick the matching Mathlib API (`Probability.*`, `MeasureTheory.*`) and apply the pattern below.
3. Handoff to `@lean-proof`; if a measurability-instance gap blocks the proof, handoff to `@lean-math-foundations`; if a convergence step needs an analytic
   lemma, handoff to `@lean-math-analysis`.

## Recovery & STOP

- STOP if the proof needs a measurability instance not yet synthesised — handoff to `@lean-math-foundations`. (Recall `IsFiniteMeasure.toSigmaFinite` is a
  priority-100 instance — `[SigmaFinite μ]` is usually free given `[IsFiniteMeasure μ]`.)
- STOP if the result you need is a deterministic dynamical-systems claim — re-route to `@lean-math-dynamical`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-proof` (mid-proof probabilistic goal), `skill:lean-research` (ergodic / martingale API survey).
- **Successors:** `skill:lean-proof` (apply the stochastic pattern), `skill:lean-proof-review` (audit the proof), `skill:lean-math-foundations`
  (measurability / SigmaFinite plumbing), `skill:lean-math-analysis` (convergence step).

## Detailed reference

Full encyclopaedia content (Parts 1 through 8) lives in
[`references/lean4-math-stochastic.md`](../../references/lean4-math-stochastic.md). Load that file
when authoring; the SKILL.md only carries the dispatch contract and
the high-frequency pitfalls / recipes (kept inline below).

| Part | Topic | Covers |
|---|---|---|
| Part 1 | Probability in Mathlib | ProbabilityMeasure, MeasurableSpace, Random variables |
| Part 2 | Markov Chains | transition kernels, row-stochastic matrices, stationary distributions |
| Part 3 | Repository Stochastic Patterns | host-repository stochastic bridge modules |
| Part 4 | Time Series Analysis | stationarity, autocovariance, spectral density |
| Part 5 | Ergodic Theory | MeasurePreserving, Ergodic, Birkhoff pointwise ergodic |
| Part 6 | Stochastic Stability | stochastic Lyapunov, mean-square stability |
| Part 7 | Research Council Integration | stochastic-domain dispatch matrix |
| Part 8 | Repository Stochastic Module Reference | local stochastic-module patterns + IVT |

## Part 9 — Common Pitfalls (Probability & Stochastic Processes)

| Pitfall | Symptom | Recovery |
|---|---|---|
| Missing `[SigmaFinite μ]` when `[IsFiniteMeasure μ]` is in scope | Believe `condExp` lemmas won't apply | None needed — `IsFiniteMeasure.toSigmaFinite` is a priority-100 instance in `Mathlib/MeasureTheory/Measure/Typeclasses/SFinite.lean:577`; it derives `SigmaFinite` automatically (and via `isFiniteMeasure_trim`, `SigmaFinite (μ.trim hm)` for any `hm`) |
| `condExp` requires `StronglyMeasurable`, you have only `Measurable` | `condExp_of_stronglyMeasurable` won't elaborate | On a second-countable codomain, `Measurable.stronglyMeasurable` upgrades automatically |
| Ergodic conditions skipped | Birkhoff's pointwise ergodic theorem won't apply | Verify `MeasurePreserving` *and* `Ergodic` separately; `ergodic_iff_measure_inv` is the bridge |
| Time-series stationarity drift | Mixing-time blowup; spectral gap "shrinks" through iterations | Confirm `StationaryProcess` instance, not just `IsStationary` on the sampled prefix |
| Martingale not from `condExp` | `Martingale` typeclass won't instantiate from raw inequalities | Use `submartingale_nat` or `supermartingale_of_condExp_sub_nonneg_nat`; the latter currently lives at `Probability/Martingale/Basic.lean:424` (drifted from `:431` at an older pin) |
| Confusing `Measure ℝ` default with `volume` | Integral of a constant gives unexpected value | Be explicit: `MeasureTheory.MeasureSpace.volume` — most "intuitive" Lebesgue results assume `volume` |

---

## Part 10 — Mathlib-Pin Notes (verified 2026-05)

These are concrete pin-relative facts that have bitten downstream projects in the past — keep them in mind when reading "old" Mathlib citations:

- **`IsFiniteMeasure.toSigmaFinite`** — priority-100 instance at `MeasureTheory/Measure/Typeclasses/SFinite.lean:577`. Don't manually `apply` it; let
  typeclass synthesis handle it. Used in `Mathlib/Probability/Independence/Basic.lean:704` as a reference example.
- **`supermartingale_of_condExp_sub_nonneg_nat`** — at `Probability/Martingale/Basic.lean:424` at pin `949174649e0f` (drifted from `:431`). Preferred over
  `submartingale_nat` for `ConditionalRS`-style bridges.
- **`stdSimplex.le_one`** — at `Mathlib/Analysis/Convex/StdSimplex.lean:304`, inside `namespace stdSimplex` (requires `[IsOrderedRing S]`). Returns
  single-coordinate `s x ≤ 1`; prefer this over `(mem_Icc_of_mem_stdSimplex h x).2` for single-coord queries.
- **Big-operator binder notation scope** — at Mathlib `d13f23b` (Lean v4.34.1) the `∑`/`∏` binder notation is declared *unscoped*
  (`Algebra/BigOperators/Group/Finset/Defs.lean:181,192`): it is available with no `open` of any kind, and `open scoped BigOperators` gates only the `𝔼`
  (Finset.expect) notation. The umbrella import `Mathlib.Algebra.BigOperators.Basic` is deleted; use `Mathlib.Algebra.BigOperators.Group.Finset.Basic`.
  Binder forms (`x ∈ s`, `x < n`, `x ≤ n`, `with p x` filters, the `(a, b) with a + b = n` antidiagonal, product binders) come from the `bigOpBinder`
  grammar; body precedence is 67 (between `*` at 70 and `+` at 65), so a body with top-level `+` or `=` needs parens. Re-verify at your pin; notation-scope
  drift is a recurring pin-drift class.

When a Mathlib-symbol claim in a project doc reads as "this lemma does not exist at the pin", **re-verify before chain-trusting**. Grep
`.lake/packages/mathlib/Mathlib/...` at the current pin; stale verdicts are the most common source of W19/W20-style design errors.

---

## See also

- [`../../references/lean4-math-stochastic.md`](../../references/lean4-math-stochastic.md) — Stochastic Mathematics Encyclopaedia (full encyclopaedia,
  extracted from this skill)
- [`../../templates/Template_Dynamics.md`](../../templates/Template_Dynamics.md) — Template: Markov chains, mixing time, ergodic patterns
- [`../../templates/Template_Analysis.md`](../../templates/Template_Analysis.md) — Template: Measure-theoretic and analytic patterns

---

## Merged Domain Companion: `lean-math-stochastic` (Unified into `@lean-math-stochastic`)

# Measure Theory & Probability Mathematics

Measure-theoretic and probabilistic foundations for stochastic models, convergence guarantees, mixing time analysis, ergodic properties, and uncertainty
quantification.

---

## Routing

- **USE FOR:** Measure theory, probability theory, stochastic processes, ergodic theory, and concentration inequalities. Use for mathematical reasoning
  about probability spaces, random variables, convergence, mixing, and probabilistic arguments. Covers both theoretical foundations and applied
  probabilistic methodology.
- **DO NOT USE FOR:** Lean proofs in this domain (use @lean-math-stochastic); time-series analysis (use @lean-math-stochastic); topology/analysis (use
  @lean-math-analysis).
- **TRIGGERS:** measure theory, probability, stochastic process, ergodic theory, concentration inequality, Radon-Nikodym.

## Workflow

1. Classify the question: measure space, σ-algebra, integration, conditional, martingale, ergodic, or concentration.
2. Pick the matching section; identify the Mathlib namespace (`MeasureTheory`, `ProbabilityTheory`).
3. Produce the mathematical answer; cite the relevant Mathlib lemma and verify it exists at the current pin (per the `verification discipline` memory).
4. Hand off: to `@lean-math-stochastic` for the Lean proof, to `@lean-research` for pin-verification, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the question is purely time-series — delegate to `@lean-math-stochastic`.
- STOP if topology/analysis dominates — delegate to `@lean-math-analysis`.
- STOP if a Mathlib symbol cited cannot be verified at the current pin — escalate to `@lean-research`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-math-stochastic`, `skill:lean-research`, `skill:lean-zettelkasten`.

---

## Detailed reference

Full content for `lean-math-stochastic` lives in
[`references/lean-math-stochastic-handbook.md`](../../references/lean-math-stochastic-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

| Section | Topic |
|---|---|
| Part 1 | Measure Theory Foundations |
| Part 2 | Probability Theory |
| Part 3 | Concentration Inequalities |
| Part 4 | Stochastic Processes |
| Part 5 | Ergodic Theory |
| Part 6 | Bayesian Methods |
| Part 7 | Extreme Value Theory |
| Part 8 | Project-specific Probabilistic Models |
| Part 9 | Formalization Connections |

---

## See also

- [`../../references/lean-math-stochastic-handbook.md`](../../references/lean-math-stochastic-handbook.md) — Full handbook (extracted from this skill)
- [`../lean-math-stochastic/SKILL.md`](../lean-math-stochastic/SKILL.md) — Successor
- [`../lean-research/SKILL.md`](../lean-research/SKILL.md) — Successor
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor

# Math Measure Probability Handbook

> **Layering note.** This file holds the deep content previously
> embedded in [`skills/lean-math-stochastic/SKILL.md`](../skills/lean-math-stochastic/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow /
> Recovery / Handoffs) + a parts index. This file holds the full
> encyclopaedia. Zero fidelity loss vs the pre-layering revision.

---

## Part 1 — Measure Theory Foundations

### 1.1 Measure Space Hierarchy

```
Set → σ-algebra → Measure → Probability measure → Signed measure → Complex measure
  Ω      𝓕        μ: 𝓕→[0,∞]   P: 𝓕→[0,1]      ν: 𝓕→ℝ           μ: 𝓕→ℂ
```

### 1.2 Key Measure-Theoretic Constructs

| Construct | Definition | Project usage |
|---|---|---|
| σ-algebra 𝓕 | Closed under complement & countable union | Event space for knowledge states |
| Filtration (𝓕_t) | Increasing family of σ-algebras | Information available up to time t |
| Measurable function | f⁻¹(B) ∈ 𝓕 for Borel B | Knowledge metric as random variable |
| Radon-Nikodym derivative | dν/dμ — density of ν w.r.t. μ | Likelihood ratio for regime detection |
| Product measure | μ × ν on Ω₁ × Ω₂ | Independent subsystem coupling |
| Pushforward measure | f_*μ(B) = μ(f⁻¹(B)) | State transformation probability |

### 1.3 Convergence Modes

```
Almost sure (a.s.):  P(Xₙ → X) = 1
In probability:      ∀ε>0, P(|Xₙ - X| > ε) → 0
In Lᵖ (mean):       E[|Xₙ - X|ᵖ] → 0
In distribution:     Fₙ(x) → F(x) at continuity points

Implications:
  a.s. → in probability → in distribution
  Lᵖ → in probability → in distribution
  (but NOT: in probability → a.s.)
```

### 1.4 Key Theorems

| Theorem | Statement | Project application |
|---|---|---|
| Monotone Convergence | E[lim fₙ] = lim E[fₙ] for fₙ↑ | Quality metric convergence |
| Dominated Convergence | E[lim fₙ] = lim E[fₙ] under |fₙ|≤g | Bounded metric analysis |
| Fubini-Tonelli | Iterated integrals equal double integral | Multi-timescale decomposition |
| Lebesgue Decomposition | ν = ν_ac + ν_s | Continuous vs jump dynamics |
| Radon-Nikodym | Density exists iff absolute continuity | Change of measure for regimes |
| Egorov | a.e. convergence → near-uniform convergence | Uniform quality convergence |

---

## Part 2 — Probability Theory

### 2.1 Random Variables and Distributions

```
Discrete: P(X = x) given by mass function
  Important: Bernoulli, Binomial, Poisson, Geometric

Continuous: f_X(x) density, P(a ≤ X ≤ b) = ∫_a^b f_X
  Important: Normal, Exponential, Gamma, Beta, Uniform

project-relevant distributions:
  - Beta(α,β): trust scores, confidence parameters
  - Dirichlet(α₁,...,αₖ): simplex-valued (trust simplex)
  - Gamma(k,θ): waiting times between phase transitions
  - Wishart(V,n): covariance matrices for multi-dimensional states
```

### 2.2 Conditional Probability & Independence

```
Conditional probability: P(A|B) = P(A∩B)/P(B)
Bayes' theorem: P(H|E) = P(E|H)·P(H) / P(E)

Independence:
  P(A∩B) = P(A)·P(B)  (pairwise)
  P(∩ᵢAᵢ) = Πᵢ P(Aᵢ)  (mutual)

Conditional independence:
  X ⊥ Y | Z  iff  P(X,Y|Z) = P(X|Z)·P(Y|Z)

Project use: conditional independence in causal DAGs,
  Bayesian updating of knowledge state beliefs
```

### 2.3 Expectation, Variance, Moments

```
E[X] = ∫ x dP_X
Var(X) = E[(X - E[X])²] = E[X²] - (E[X])²
Cov(X,Y) = E[(X-μ_X)(Y-μ_Y)]

Moment generating function: M_X(t) = E[e^{tX}]
Characteristic function: φ_X(t) = E[e^{itX}]

For vectors: Covariance matrix Σ where Σᵢⱼ = Cov(Xᵢ, Xⱼ)
```

---

## Part 3 — Concentration Inequalities

### 3.1 Key Inequalities

| Inequality | Bound | Use Case |
|---|---|---|
| Markov | P(X ≥ a) ≤ E[X]/a | Crude bound on quality score |
| Chebyshev | P(|X-μ|≥kσ) ≤ 1/k² | Deviation bound |
| Chernoff | P(X ≥ a) ≤ min_t E[e^{t(X-a)}] | Exponential tail bound |
| Hoeffding | P(|S̄ₙ-μ|≥t) ≤ 2exp(-2n²t²/Σ(bᵢ-aᵢ)²) | Bounded average |
| Bernstein | Sharper than Hoeffding with variance info | Quality metric average |
| McDiarmid | Bounded differences → concentration | Stability of scored functions |
| Azuma-Hoeffding | For martingales with bounded increments | Sequential quality tracking |

### 3.2 Project Applications

```
Quality gate threshold: Use Hoeffding to bound
  P(quality_score deviates from true quality by > ε)
  ≤ 2·exp(-2nε²)
  
  So n = O(1/ε²) observations suffice for reliable gating.

Trust score stability: McDiarmid for trust composition
  Changing one evidence source changes trust by ≤ cᵢ
  P(|trust - E[trust]| > t) ≤ 2·exp(-2t²/Σcᵢ²)
```

---

## Part 4 — Stochastic Processes

### 4.1 Process Classification

| Process | Definition | Project model |
|---|---|---|
| Markov chain (discrete) | P(Xₙ₊₁|X₀,...,Xₙ) = P(Xₙ₊₁|Xₙ) | Knowledge regime transitions |
| Markov chain (continuous) | Generator matrix Q | Continuous-time phase dynamics |
| Brownian motion | Continuous Gaussian process with stationary increments | Stochastic perturbation model |
| Diffusion process | dXₜ = μ(Xₜ)dt + σ(Xₜ)dWₜ | Knowledge state SDE |
| Poisson process | Count process with exponential inter-arrivals | Phase transition events |
| Renewal process | Generalized Poisson with arbitrary inter-arrivals | Knowledge update arrivals |
| Martingale | E[Xₙ₊₁|𝓕ₙ] = Xₙ | Fair game / unbiased estimators |

### 4.2 Markov Chain Theory

```
Transition matrix: P where Pᵢⱼ = P(Xₙ₊₁=j | Xₙ=i)

Key properties:
  Irreducibility: any state reachable from any other
  Aperiodicity: gcd of return times = 1
  Positive recurrence: expected return time finite

Fundamental theorem: Irreducible + aperiodic + positive recurrent
  → unique stationary distribution π where πP = π

Convergence rate: ||P^n(x,·) - π||_TV ≤ C·ρⁿ  (geometric mixing)
  where ρ = 1 - spectral gap of P
```

### 4.3 Stochastic Differential Equations (SDEs)

```
Itô SDE: dXₜ = μ(Xₜ,t)dt + σ(Xₜ,t)dWₜ

Itô's Lemma: For f(Xₜ,t):
  df = (∂f/∂t + μ·∂f/∂x + ½σ²·∂²f/∂x²)dt + σ·∂f/∂x dWₜ

Project knowledge state SDE:
  dK = f(K)dt + g(K)dW   (deterministic drift + stochastic perturbation)
  
  Lyapunov for SDE: LV(x) = μ·∇V + ½ tr(σσᵀ·∇²V) ≤ -αV
  ensures stochastic stability in mean
```

---

## Part 5 — Ergodic Theory

### 5.1 Ergodic Theorems

```
Birkhoff (pointwise): (1/n)Σf(Tⁱx) → ∫f dμ  a.e.
  for measure-preserving T on (Ω, 𝓕, μ)

Von Neumann (mean): (1/n)Σf(Tⁱx) → ∫f dμ  in L²

project application:
  Time averages of knowledge metrics converge to
  spatial averages (ensemble averages) in ergodic regime.
  → Long-running Project cycle converges to steady-state quality.
```

### 5.2 Mixing and Spectral Gap

```
Mixing: The system "forgets" its initial condition.

Strong mixing: |P(A ∩ T⁻ⁿB) - P(A)P(B)| → 0

Spectral gap: λ₁ = 1 (trivial), λ₂ < 1
  Gap = 1 - λ₂ > 0  ⟹  exponential mixing

Mixing time: t_mix(ε) = min{t : max_x ||P^t(x,·) - π||_TV ≤ ε}
  t_mix ≤ O(1/gap · log(1/ε))

project implication:
  Spectral gap > 0 ⟹ knowledge process converges to equilibrium
  Larger gap ⟹ faster convergence to steady-state quality
```

### 5.3 Entropy and Information

```
Shannon entropy: H(X) = -Σ p(x) log p(x)
Kullback-Leibler divergence: D_KL(P||Q) = Σ p(x) log(p(x)/q(x))
Mutual information: I(X;Y) = H(X) + H(Y) - H(X,Y)
Conditional entropy: H(X|Y) = H(X,Y) - H(Y)

Entropy rate for stochastic processes:
  h = lim_{n→∞} H(Xₙ|X₁,...,Xₙ₋₁)

Project: entropy tracks knowledge uncertainty reduction across stages
  Innovation stage should minimize entropy of knowledge representation
```

---

## Part 6 — Bayesian Methods

### 6.1 Bayesian Framework

```
Prior: π(θ) — initial belief about parameters
Likelihood: L(θ|data) = P(data|θ)
Posterior: π(θ|data) ∝ L(θ|data)·π(θ)
Evidence: P(data) = ∫ L(θ|data)·π(θ) dθ

Conjugate priors:
  Normal likelihood + Normal prior → Normal posterior
  Bernoulli likelihood + Beta prior → Beta posterior
  Multinomial + Dirichlet → Dirichlet posterior (trust simplex!)
```

### 6.2 Project Bayesian Applications

```
Trust updating:
  Prior: Beta(α₀, β₀) on source reliability
  Each verification: success → α+=1, failure → β+=1
  Posterior: Beta(α₀+s, β₀+f)
  Mean trust: (α₀+s)/(α₀+β₀+s+f)

Knowledge regime belief:
  Prior: Dirichlet(α) over K regimes
  Observations update: α_k += observation count in regime k
  Regime probability: softmax of updated Dirichlet
```

### 6.3 Model Selection

```
Bayesian Information Criterion: BIC = -2·log L + k·log n
Akaike Information Criterion: AIC = -2·log L + 2k
Bayesian model averaging: P(Y|data) = Σ P(Y|M_i,data)·P(M_i|data)

Use for: selecting number of knowledge regimes,
  choosing complexity of quality gate models
```

---

## Part 7 — Extreme Value Theory

### 7.1 EVT Foundations

```
Three extreme value distributions (Fisher-Tippett-Gnedenko):
  Gumbel (Type I):   exp(-exp(-x))         — light tails
  Fréchet (Type II):  exp(-x^{-α})         — heavy tails
  Weibull (Type III): exp(-(-x)^c), x ≤ 0  — bounded support

Generalized Extreme Value:
  H_ξ(x) = exp(-(1+ξx)^{-1/ξ})
  ξ = 0: Gumbel, ξ > 0: Fréchet, ξ < 0: Weibull

Project use: model extreme knowledge quality events,
  tail risk in governance decision-making
```

### 7.2 Peaks Over Threshold

```
Generalized Pareto Distribution (GPD):
  P(X > u+y | X > u) ≈ (1 + ξ·y/σ)^{-1/ξ}

Use for: rare catastrophic events in knowledge lifecycle
  (sudden quality collapse, trust breach, critical phase transition)
```

---

## Part 8 — Project-specific Probabilistic Models

### 8.1 Knowledge Phase Portrait as Probability Space

```
State space: S = [0,1]^d (d-dimensional quality vector)
σ-algebra: Borel subsets of S
Probability: P_t = evolved measure under dynamics

Phase classification:
  P(regime = k | observation) via posterior inference
  Uses Bayesian updating with Dirichlet prior on regime probabilities
```

### 8.2 Quality Gate as Hypothesis Test

```
H₀: artifact quality meets threshold (q ≥ q_min)
H₁: artifact quality below threshold (q < q_min)

Type I error (α): reject good artifact
Type II error (β): accept bad artifact

Gate design: choose threshold to minimize β
  subject to α ≤ α_max (governance constraint)
  
Neyman-Pearson lemma: optimal test uses likelihood ratio
```

### 8.3 Multi-timescale Probability

```
Fast process: τ_fast ~ O(1)     — individual measurements
Medium process: τ_med ~ O(10)   — quality gate evaluations  
Slow process: τ_slow ~ O(100)   — regime transitions

Averaging principle:
  On slow timescale, fast variables are at quasi-equilibrium
  P_slow(x) = ∫ P(x, y_fast) dy_fast ≈ P(x | y_fast = ȳ(x))
```

---

## Part 9 — Formalization Connections

### 9.1 Current Lean Coverage

| Concept | Module | Status |
|---|---|---|
| Spectral gap bounds | StochasticCCV | ✅ Proven |
| Mixing time sufficiency | StochasticCCV | ✅ Proven |
| Ergodic average bounds | StochasticCCV | ✅ Proven |
| Noise stability region | StochasticCCV | ✅ Proven |
| TrustSimplex (Dirichlet structure) | ProvenanceChain | ✅ Proven |

### 9.2 Formalization Frontiers

- Stochastic Lyapunov theory (Itô calculus in Lean)
- Concentration inequality library (Hoeffding, McDiarmid)
- Ergodic theorem for Project Markov chains
- Bayesian posterior consistency for quality gates
- EVT for rare catastrophic transition events

---

## Merged Domain Companion: `lean-math-stochastic` (Unified into `@lean-math-stochastic`)

# Time Series Analysis & Temporal Mathematics

Comprehensive methodology for temporal mathematics — the computational backbone of phase trajectory computation, early warning signal detection, and
multi-timescale architectures.

---

## Routing

- **USE FOR:** Time series analysis, signal processing, temporal pattern detection, and multi-scale temporal dynamics. Use for mathematical reasoning about
  time-varying data, smoothing, derivative estimation, spectral analysis, changepoint detection, and temporal trajectory computation. Covers both theory
  and computational methodology.
- **DO NOT USE FOR:** measure-theoretic / probabilistic basis (use @lean-math-stochastic); Lean proofs (use @lean-math-stochastic); nonlinear dynamics
  (use @lean-math-dynamical).
- **TRIGGERS:** time series, signal processing, temporal pattern, multi-scale temporal, spectral analysis.

## Workflow

1. Classify the signal: stationary / non-stationary, univariate / multivariate, discrete / continuous time.
2. Pick the matching section (autocorrelation, spectral, wavelet, change-point, multi-scale).
3. Produce the analytical answer; identify the Mathlib (or external) tool needed for implementation.
4. Hand off: to `@lean-math-stochastic` if a probabilistic guarantee is needed, to `@lean-math-stochastic` for measure-theoretic basis, to
   `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the question is purely measure-theoretic — delegate to `@lean-math-stochastic`.
- STOP if nonlinear-dynamics methods are what's needed — delegate to `@lean-math-dynamical`.
- STOP if a Mathlib pin-verified lemma is required — escalate to `@lean-research`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-math-stochastic`, `skill:lean-math-stochastic`, `skill:lean-zettelkasten`.

---

## Detailed reference

Full content for `lean-math-stochastic` lives in
[`references/lean-math-stochastic-handbook.md`](../../references/lean-math-stochastic-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

| Section | Topic |
|---|---|
| Part 1 | Project Temporal Context |
| Part 2 | Smoothing and Derivative Estimation |
| Part 3 | Spectral Analysis |
| Part 4 | Changepoint Detection |
| Part 5 | Stochastic Time Series Models |
| Part 6 | Multi-Scale Temporal Methods |
| Part 7 | Connections to Formalization |

---

## See also

- [`../../references/lean-math-stochastic-handbook.md`](../../references/lean-math-stochastic-handbook.md) — Full handbook (extracted from this skill)
- [`../lean-math-stochastic/SKILL.md`](../lean-math-stochastic/SKILL.md) — Successor
- [`../lean-math-stochastic/SKILL.md`](../lean-math-stochastic/SKILL.md) — Successor
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor

# Math Time Series Handbook

> **Layering note.** This file holds the deep content previously
> embedded in [`skills/lean-math-stochastic/SKILL.md`](../skills/lean-math-stochastic/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow /
> Recovery / Handoffs) + a parts index. This file holds the full
> encyclopaedia. Zero fidelity loss vs the pre-layering revision.

---

## Part 1 — Project Temporal Context

the project's phase trajectory computation (paper §Phase Trajectory Computation) requires:

| Computation | Mathematical Foundation | Section |
|---|---|---|
| State vector construction | Sampling theory, measurement models | §Data Acquisition |
| Derivative estimation | Numerical differentiation, smoothing | §Derivative Estimation |
| Momentum computation | Moving averages, exponential smoothing | §Derived Quantities |
| EWS detection | Changepoint analysis, variance tracking | §Early Warning Signals |
| Phase classification | Time-series clustering, regime detection | §Phase Classification |
| Multi-timescale decomposition | Wavelet analysis, EMD | §Multi-Timescale |

---

## Part 2 — Smoothing and Derivative Estimation

### 2.1 Smoothing Methods

| Method | Formula | Properties | Project Use |
|---|---|---|---|
| Moving Average (MA) | ŷ_t = (1/k)Σy_{t-i} | Simple, lagging | Baseline trend |
| Exponential (EMA) | ŷ_t = αy_t + (1-α)ŷ_{t-1} | Weighted recency, tunable | Momentum M₃ |
| Savitzky-Golay | Polynomial least-squares on window | Preserves peaks, smooth derivatives | Derivative estimation |
| Kalman filter | State-space model with noise | Optimal for linear Gaussian | State estimation |
| Gaussian Process | Bayesian nonparametric | Uncertainty quantification | Confidence bands |

### 2.2 Numerical Differentiation

```
First derivative (central difference): ẋ_t ≈ (x_{t+h} - x_{t-h}) / 2h
Second derivative: ẍ_t ≈ (x_{t+h} - 2x_t + x_{t-h}) / h²

Better: Savitzky-Golay differentiation
  - Fit polynomial of degree p to window of width 2m+1
  - Differentiate polynomial analytically
  - Result: smooth derivative estimate with known error bounds
```

### 2.3 Multi-Scale Derivative Estimation

the project's multi-timescale architecture requires derivatives at different scales:
```
Fast (experience):   ẋ_fast  — computed on τ_fast  window (minutes/hours)
Medium (structure):  ẋ_mid   — computed on τ_mid   window (days/weeks)
Slow (innovation):   ẋ_slow  — computed on τ_slow  window (weeks/months)

Separation criterion: τ_{slow}/τ_{fast} > 10 for reliable decomposition
```

---

## Part 3 — Spectral Analysis

### 3.1 Fourier Methods

| Method | Input | Output | Project Use |
|---|---|---|---|
| DFT/FFT | Uniformly sampled time series | Frequency spectrum | Periodicity detection |
| Periodogram | Time series | Power spectral density | Dominant timescales |
| Welch's method | Long time series | Smoothed PSD | Robust spectral estimation |
| Lomb-Scargle | Irregularly sampled data | PSD for irregular data | Missing data handling |

### 3.2 Wavelet Analysis

```
Continuous wavelet transform (CWT):
  W(a,b) = ∫ x(t) ψ*((t-b)/a) dt/√a

  a = scale (inverse frequency), b = time location
  → Time-frequency decomposition (localized spectra)

Discrete wavelet transform (DWT):
  Multiresolution analysis: x = Σ_j D_j + A_J
  D_j = detail at scale 2^j (high frequency at scale j)
  A_J = approximation at coarsest scale (low frequency trend)
```

**project application**: Decompose knowledge trajectory into timescale components → validate multi-timescale architecture.

### 3.3 Empirical Mode Decomposition (EMD)

```
EMD: x(t) = Σ_k IMF_k(t) + residual(t)

IMFs (Intrinsic Mode Functions):
  - Each IMF captures an oscillatory component
  - Data-driven (no basis function choice needed)
  - Adaptive to nonlinear/nonstationary dynamics
```

Better for Project than Fourier (knowledge dynamics are nonstationary).

---

## Part 4 — Changepoint Detection

### 4.1 Methods for Regime Change Detection

| Method | Type | Detects | Speed |
|---|---|---|---|
| CUSUM | Parametric | Mean shift | Fast, online |
| PELT | Penalized likelihood | Mean/variance shifts | Fast offline |
| Bayesian Online | Bayesian | Any distributional change | Online, with uncertainty |
| Hidden Markov Model | Model-based | Regime switching | Needs model spec |
| Kernel-based (MMD) | Nonparametric | Distributional change | Flexible, slower |

### 4.2 Project Phase Transition Detection

```
Knowledge state: x(t) = [C(t), V(t), R(t), D(t), M(t)]

Phase transition ≡ changepoint in regime classification:
  1. Track classification: regime(t) = classify(x(t))
  2. Detect when regime(t) changes
  3. Validate: is this a true transition or noise?

Validation criteria:
  - Duration: new regime persists for ≥ minimum_dwell_time
  - Confidence: quality gate conditions clearly switch
  - Consistency: multiple indicators agree (C, V, R, D all support new regime)
```

### 4.3 Early Warning Signals (EWS)

Before a catastrophic transition (cusp bifurcation), detect:
```
1. Rising autocorrelation: lag-1 AC → 1 (critical slowing down)
2. Rising variance: Var(x_t) → ∞ (amplitude increases)
3. Rising skewness: skew(x_t) ≠ 0 (asymmetry develops)
4. Flickering: bimodal distribution (system samples both basins)

Project computation:
  - Window: rolling window of size W
  - Metric: Kendall τ trend test on each EWS indicator
  - Threshold: Kendall τ > 0.3 → "approaching transition"
```

---

## Part 5 — Stochastic Time Series Models

### 5.1 Classical Models

| Model | Equation | Properties | Project Relevance |
|---|---|---|---|
| AR(p) | x_t = Σ φ_i x_{t-i} + ε_t | Linear, stationary | Baseline comparison |
| MA(q) | x_t = ε_t + Σ θ_i ε_{t-i} | Finite memory | Moving average smoothing |
| ARMA(p,q) | Combines AR + MA | Parsimonious | General linear model |
| ARIMA(p,d,q) | ARMA on differenced series | Handles trends | Non-stationary data |
| GARCH(p,q) | Conditional variance model | Models volatility clusters | Volatility V(t) modeling |

### 5.2 Regime-Switching Models

```
Markov-switching AR:
  x_t = φ_{s_t} x_{t-1} + σ_{s_t} ε_t
  s_t ~ Markov(P)  (regime indicator)

  → Each regime has its own AR parameters
  → Transition probabilities capture phase switching
  → Project: regimes = {Exploration, Transition, Mastery, Crisis}
```

### 5.3 State-Space Models

```
State equation:   x_{t+1} = Ax_t + Bu_t + w_t   (hidden state evolution)
Observation:      y_t = Cx_t + v_t              (noisy measurement)

Kalman filter: optimal state estimation given observations
Kalman smoother: uses future as well as past observations

Project: x = [C, V, R, D, M], y = quality gate scores, u = governance inputs
```

---

## Part 6 — Multi-Scale Temporal Methods

### 6.1 Timescale Separation Analysis

```
Given: time series x(t) with multiple timescales

Method 1: Wavelet decomposition
  → Separate into scale bands corresponding to Project timescales
  → Verify that energy is concentrated at expected scales

Method 2: Singular Spectrum Analysis (SSA)
  → Embed time series in delay coordinates
  → SVD → extract principal components (oscillatory + trend)
  → Group components by timescale

Method 3: Multi-scale entropy
  → Coarse-grain at different scales
  → Compute SampEn at each scale
  → Complex systems show high entropy across scales
```

### 6.2 Project Multi-Timescale Validation

To validate the 4-timescale architecture from data:
```
1. Collect trajectory data from all Project stages
2. Decompose using wavelets or SSA
3. For each decomposed component:
   a. Estimate characteristic timescale (autocorrelation time or spectral peak)
   b. Assign to Project level (Experience/Articulation/Structuring/Innovation)
4. Verify separation: τ_{i+1}/τ_i > 10 for adjacent levels
5. Verify coupling: cross-correlation between levels exists but is weak
```

---

## Part 7 — Connections to Formalization

### 7.1 What Can Be Formalized in Lean

| Concept | Formalizability | Current Status |
|---|---|---|
| Convergence of smoothed estimates | ✅ (via Mathlib analysis) | Partially covered |
| EWS threshold crossing | ✅ (decidable Nat comparison) | In PipelineAdaptive |
| Phase classification | ✅ (decidable finite cases) | In PhaseClassification |
| Spectral gap bounds | ✅ (algebraic) | In StochasticCCV |
| ARIMA forecast bounds | 🟡 (requires probability theory) | Not yet |
| Wavelet decomposition properties | 🟡 (sparse Mathlib coverage) | Not yet |
| Changepoint detection guarantees | 🟡 (depends on statistical theory) | Not yet |

### 7.2 Research Frontiers for Formalization

- Formal verification of EWS detection algorithms
- Proven error bounds for numerical differentiation
- Certified changepoint detection (false positive rate bounds)
- Formal connection between time-series stability and Lyapunov stability

---
## Goal-Shape Templates (templates)

| Goal Shape | Target Typeclass / Lemma | Proof Template |
| :--- | :--- | :--- |
| `Measurable (fun x => f (g x))` | `measurability` / `fun_prop` | `by measurability` (or `by fun_prop`) |
| `∀ᵐ x ∂μ, P x ∧ Q x` | `filter_upwards` | `filter_upwards [hP, hQ] with x hxP hxQ using ⟨hxP, hxQ⟩` |
| `∫ x, (f x + g x) ∂μ = ∫ x, f x ∂μ + ∫ x, g x ∂μ` | `integral_add` | `exact integral_add hf_int hg_int` |
| Scaled simplex `w₁ + w₂ + w₃ = 100` | Scaled `Nat` simplex (`x 100`) | `by omega` |
| Markov kernel row-stochasticity `∑ j, P i j = 1` | `Finset.sum` / `PMF` | `simp only [...]; ring` (or `omega` on scaled `Nat`) |

## Intent-to-Tactic Phrasebook (phrasebook)

| Mathematical Intent | Lean 4 / Mathlib Tactic | Notes |
| :--- | :--- | :--- |
| Discharge measurability of composite function | `by measurability` or `by fun_prop` | Handles arithmetic, continuous, and borel maps |
| Combine finitely many `∀ᵐ x ∂μ` hypotheses | `filter_upwards [h1, h2] with x hx1 hx2` | Avoids manual null-set union bookkeeping |
| Bound expectation / integral monotonically | `apply integral_mono_ae hf hg` | Pair with `filter_upwards` for pointwise bound |
| Prove probability bound in `[0, 1]` | `positivity` / `linarith` | For `ENNReal`, check `≠ ⊤` before `ENNReal.toReal` |

## Error-to-Fix Table (errors)

| Error / Symptom | Root Cause | Fix |
| :--- | :--- | :--- |
| `ENNReal` subtraction cancellation fails | `∞ - ∞ = 0` and truncated subtraction in `ℝ≥0∞` | Prove finiteness `h : x ≠ ⊤` before using `ENNReal.sub_add_cancel` |
| `integral_add` fails to apply | Missing `Integrable f μ` side conditions | Establish `hf : Integrable f μ` before linearity rewrites |
| Scaled integer probability underflow | `100 - p` truncates if `p <= 100` is missing | Include `hp : p <= 100` in structure invariants and pass to `omega` |
