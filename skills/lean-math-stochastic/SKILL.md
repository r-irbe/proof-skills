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

- **`IsFiniteMeasure.toSigmaFinite`** — priority-100 instance at `MeasureTheory/Measure/Typeclasses/SFinite.lean:577`. Don't manually `apply` it; let typeclass synthesis handle it. Used in `Mathlib/Probability/Independence/Basic.lean:704` as a reference example.
- **`supermartingale_of_condExp_sub_nonneg_nat`** — at `Probability/Martingale/Basic.lean:424` at pin `949174649e0f` (drifted from `:431`). Preferred over `submartingale_nat` for `ConditionalRS`-style bridges.
- **`stdSimplex.le_one`** — at `Mathlib/Analysis/Convex/StdSimplex.lean:304`, inside `namespace stdSimplex` (requires `[IsOrderedRing S]`). Returns single-coordinate `s x ≤ 1`; prefer this over `(mem_Icc_of_mem_stdSimplex h x).2` for single-coord queries.

When a Mathlib-symbol claim in a project doc reads as "this lemma does not exist at the pin", **re-verify before chain-trusting**. Grep `.lake/packages/mathlib/Mathlib/...` at the current pin; stale verdicts are the most common source of W19/W20-style design errors.

---

## See also

- [`../../references/lean4-math-stochastic.md`](../../references/lean4-math-stochastic.md) — Stochastic Mathematics Encyclopaedia (full encyclopaedia, extracted from this skill)
- [`../../templates/Template_Dynamics.md`](../../templates/Template_Dynamics.md) — Template: Markov chains, mixing time, ergodic patterns
- [`../../templates/Template_Analysis.md`](../../templates/Template_Analysis.md) — Template: Measure-theoretic and analytic patterns
