---
name: "math-time-series"
description: |
  USE FOR: Time series analysis, signal processing, temporal pattern detection, and multi-scale temporal dynamics. Use for mathematical reasoning about time-varying data, smoothing, derivative estimation, spectral analysis, changepoint detection, and the temporal aspects of the project's knowledge trajectory computation. Covers both theory and computational methodology.
  DO NOT USE FOR: measure-theoretic / probabilistic basis (use @math-measure-probability); Lean proofs (use @lean-math-stochastic); nonlinear dynamics (use @math-nonlinear-dynamics).
  TRIGGERS: time series, signal processing, temporal pattern, multi-scale temporal, spectral analysis.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-math-stochastic', 'skill:math-measure-probability', 'skill:lean-zettelkasten']
metadata:
  version: "0.2.0"
  source_spec: "skills/math-time-series/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# Time Series Analysis & Temporal Mathematics

Comprehensive methodology for temporal mathematics — the computational backbone of the project's phase trajectory computation, early warning signal detection, and multi-timescale architecture.

---

## Routing

- **USE FOR:** Time series analysis, signal processing, temporal pattern detection, and multi-scale temporal dynamics. Use for mathematical reasoning about time-varying data, smoothing, derivative estimation, spectral analysis, changepoint detection, and the temporal aspects of the project's knowledge trajectory computation. Covers both theory and computational methodology.
- **DO NOT USE FOR:** measure-theoretic / probabilistic basis (use @math-measure-probability); Lean proofs (use @lean-math-stochastic); nonlinear dynamics (use @math-nonlinear-dynamics).
- **TRIGGERS:** time series, signal processing, temporal pattern, multi-scale temporal, spectral analysis.

## Workflow

1. Classify the signal: stationary / non-stationary, univariate / multivariate, discrete / continuous time.
2. Pick the matching section (autocorrelation, spectral, wavelet, change-point, multi-scale).
3. Produce the analytical answer; identify the Mathlib (or external) tool needed for implementation.
4. Hand off: to `@lean-math-stochastic` if a probabilistic guarantee is needed, to `@math-measure-probability` for measure-theoretic basis, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the question is purely measure-theoretic — delegate to `@math-measure-probability`.
- STOP if nonlinear-dynamics methods are what's needed — delegate to `@math-nonlinear-dynamics`.
- STOP if a Mathlib pin-verified lemma is required — escalate to `@lean-research`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-math-stochastic`, `skill:math-measure-probability`, `skill:lean-zettelkasten`.

---

## Detailed reference

Full content for `math-time-series` lives in
[`references/math-time-series-handbook.md`](../../references/math-time-series-handbook.md).
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

- [`../../references/math-time-series-handbook.md`](../../references/math-time-series-handbook.md) — Full handbook (extracted from this skill)
- [`../lean-math-stochastic/SKILL.md`](../lean-math-stochastic/SKILL.md) — Successor
- [`../math-measure-probability/SKILL.md`](../math-measure-probability/SKILL.md) — Successor
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor

