---
name: "lean-math-stochastic"
description: |
  USE FOR: probability theory, stochastic processes, Markov chains, time-series analysis, ergodic theory.
  DO NOT USE FOR: deterministic dynamical systems (@lean-math-dynamical).
  TRIGGERS: probability, stochastic, Markov chain, time series, ergodic.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
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
- **USE FOR:** probability theory, stochastic processes, Markov chains, time-series analysis, ergodic theory,
  row-stochastic
  matrices,
  mixing times,
  spectral gaps, stationary distributions, and any stochastic dynamics in Lean 4.
- **DO NOT USE FOR:** deterministic dynamical systems (delegate to `@lean-math-dynamical`); abstract
  measure-theoretic typeclass
  plumbing
  (delegate to
  `@lean-math-foundations`); pure topology (delegate to `@lean-math-analysis`); writing one specific proof
  (delegate to
  `@lean-proof`).
## Workflow
1. Identify the stochastic class (Part 1) — discrete-time chain, continuous-time process, martingale,
  stationary process,
  time-series model.
2. Pick the matching Mathlib API (`Probability.*`, `MeasureTheory.*`) and apply the pattern below.
3. Handoff to `@lean-proof`; if a measurability-instance gap blocks the proof, handoff to
  `@lean-math-foundations`; if a
  convergence step
   needs an analytic
   lemma, handoff to `@lean-math-analysis`.
## Recovery & STOP
- STOP if the proof needs a measurability instance not yet synthesised — handoff to `@lean-math-foundations`.
  (Recall
  `IsFiniteMeasure.toSigmaFinite` is a
  priority-100 instance — `[SigmaFinite μ]` is usually free given `[IsFiniteMeasure μ]`.)
- STOP if the result you need is a deterministic dynamical-systems claim — re-route to `@lean-math-dynamical`.
## Handoffs
- **Predecessors:** `agent:gateway`, `skill:lean-proof` (mid-proof probabilistic goal), `skill:lean-research`
  (ergodic /
  martingale API
  survey).
- **Successors:** `skill:lean-proof` (apply the stochastic pattern), `skill:lean-proof-review` (audit the
  proof),
  `skill:lean-math-foundations`
  (measurability / SigmaFinite plumbing), `skill:lean-math-analysis` (convergence step).
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-math-stochastic-handbook.md`](../../references/lean-math-stochastic-handbook.md) .
## See also
- [`../../references/lean-math-stochastic-handbook.md`](../../references/lean-math-stochastic-handbook.md) --
  Complete
  `lean-math-stochastic` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
