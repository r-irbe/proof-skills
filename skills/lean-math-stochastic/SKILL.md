---
name: "lean-math-stochastic"
description: |
  USE FOR: probability theory, stochastic processes, Markov chains, time-series analysis, ergodic theory, row-stochastic matrices, mixing times, spectral gaps, stationary distributions, and any stochastic dynamics in Lean 4.
  DO NOT USE FOR: deterministic dynamical systems (use @lean-math-dynamical); abstract measure-theoretic typeclass plumbing (use @lean-math-foundations); pure topology (use @lean-math-analysis); writing one specific proof (use @lean-proof).
  TRIGGERS: probability, stochastic, Markov chain, time series, ergodic, mixing time, spectral gap, stationary distribution, row-stochastic, martingale.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-proof", "skill:lean-research"]
  successors: ["skill:lean-proof", "skill:lean-proof-review", "skill:lean-math-foundations", "skill:lean-math-analysis"]
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-math-stochastic/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Lean 4 Stochastic Mathematics

Guide to formalizing probability, stochastic processes, and time series in Lean 4.

## Routing

- **USE FOR:** probability theory, stochastic processes, Markov chains, time-series analysis, ergodic theory, row-stochastic matrices, mixing times, spectral gaps, stationary distributions, and any stochastic dynamics in Lean 4.
- **DO NOT USE FOR:** deterministic dynamical systems (delegate to `@lean-math-dynamical`); abstract measure-theoretic typeclass plumbing (delegate to `@lean-math-foundations`); pure topology (delegate to `@lean-math-analysis`); writing one specific proof (delegate to `@lean-proof`).
- **TRIGGERS:** probability, stochastic, Markov chain, time series, ergodic, mixing time, spectral gap, stationary distribution, row-stochastic, martingale.

## Workflow

1. Identify the stochastic class (Part 1) — discrete-time chain, continuous-time process, martingale, stationary process, time-series model.
2. Pick the matching Mathlib API (`Probability.*`, `MeasureTheory.*`) and apply the pattern below.
3. Handoff to `@lean-proof`; if a measurability-instance gap blocks the proof, handoff to `@lean-math-foundations`; if a convergence step needs an analytic lemma, handoff to `@lean-math-analysis`.

## Recovery & STOP

- STOP if the proof needs a measurability instance not yet synthesised — handoff to `@lean-math-foundations`. (Recall `IsFiniteMeasure.toSigmaFinite` is a priority-100 instance — `[SigmaFinite μ]` is usually free given `[IsFiniteMeasure μ]`.)
- STOP if the result you need is a deterministic dynamical-systems claim — re-route to `@lean-math-dynamical`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-proof` (mid-proof probabilistic goal), `skill:lean-research` (ergodic / martingale API survey).
- **Successors:** `skill:lean-proof` (apply the stochastic pattern), `skill:lean-proof-review` (audit the proof), `skill:lean-math-foundations` (measurability / SigmaFinite plumbing), `skill:lean-math-analysis` (convergence step).

---

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

As of Lean 4 / Mathlib 4.28, **Mathlib does NOT have a general Perron-Frobenius theorem** for real matrices. Workarounds:

| Problem | Project approach |
|---|---|
| Finite irreducible Markov chain: stationary distribution exists | Prove directly from column sums = 1 via `field_simp + ring` |
| Convergence to stationary | Use Doeblin's condition + geometric mixing bounds (proven in StochasticCCV) |
| 3×3 doubly stochastic: uniform is stationary | `uniformQ_stationary_doubly_stochastic` theorem |

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

These are concrete pin-relative facts that have bitten this project in the past — keep them in mind when reading "old" Mathlib citations:

- **`IsFiniteMeasure.toSigmaFinite`** — priority-100 instance at `MeasureTheory/Measure/Typeclasses/SFinite.lean:577`. Don't manually `apply` it; let typeclass synthesis handle it. Used in `Mathlib/Probability/Independence/Basic.lean:704` as a reference example.
- **`supermartingale_of_condExp_sub_nonneg_nat`** — at `Probability/Martingale/Basic.lean:424` at pin `949174649e0f` (drifted from `:431`). Preferred over `submartingale_nat` for `ConditionalRS`-style bridges.
- **`stdSimplex.le_one`** — at `Mathlib/Analysis/Convex/StdSimplex.lean:304`, inside `namespace stdSimplex` (requires `[IsOrderedRing S]`). Returns single-coordinate `s x ≤ 1`; prefer this over `(mem_Icc_of_mem_stdSimplex h x).2` for single-coord queries.

When a Mathlib-symbol claim in a project doc reads as "this lemma does not exist at the pin", **re-verify before chain-trusting**. Grep `.lake/packages/mathlib/Mathlib/...` at the current pin; stale verdicts are the most common source of W19/W20-style design errors.

---

## See also

- [`../../templates/Template_Dynamics.md`](../../templates/Template_Dynamics.md) — Template: Markov chains, mixing time, ergodic patterns
- [`../../templates/Template_Analysis.md`](../../templates/Template_Analysis.md) — Template: Measure-theoretic and analytic patterns
