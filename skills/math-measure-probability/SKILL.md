---
name: "math-measure-probability"
description: |
  USE FOR: Measure theory, probability theory, stochastic processes, ergodic theory, and concentration inequalities. Use for mathematical reasoning about probability spaces, random variables, convergence, mixing, and probabilistic arguments. Covers both theoretical foundations and applied probabilistic methodology.
  DO NOT USE FOR: Lean proofs in this domain (use @lean-math-stochastic); time-series analysis (use @math-time-series); topology/analysis (use @math-topology-analysis).
  TRIGGERS: measure theory, probability, stochastic process, ergodic theory, concentration inequality, Radon-Nikodym.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-math-stochastic', 'skill:lean-research', 'skill:lean-zettelkasten']
metadata:
  version: "0.2.0"
  source_spec: "skills/math-measure-probability/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# Measure Theory & Probability Mathematics

Measure-theoretic and probabilistic foundations for stochastic models, convergence guarantees, mixing time analysis, ergodic properties, and uncertainty quantification.

---

## Routing

- **USE FOR:** Measure theory, probability theory, stochastic processes, ergodic theory, and concentration inequalities. Use for mathematical reasoning about probability spaces, random variables, convergence, mixing, and probabilistic arguments. Covers both theoretical foundations and applied probabilistic methodology.
- **DO NOT USE FOR:** Lean proofs in this domain (use @lean-math-stochastic); time-series analysis (use @math-time-series); topology/analysis (use @math-topology-analysis).
- **TRIGGERS:** measure theory, probability, stochastic process, ergodic theory, concentration inequality, Radon-Nikodym.

## Workflow

1. Classify the question: measure space, σ-algebra, integration, conditional, martingale, ergodic, or concentration.
2. Pick the matching section; identify the Mathlib namespace (`MeasureTheory`, `ProbabilityTheory`).
3. Produce the mathematical answer; cite the relevant Mathlib lemma and verify it exists at the current pin (per the `verification discipline` memory).
4. Hand off: to `@lean-math-stochastic` for the Lean proof, to `@lean-research` for pin-verification, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the question is purely time-series — delegate to `@math-time-series`.
- STOP if topology/analysis dominates — delegate to `@math-topology-analysis`.
- STOP if a Mathlib symbol cited cannot be verified at the current pin — escalate to `@lean-research`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-math-stochastic`, `skill:lean-research`, `skill:lean-zettelkasten`.

---

## Detailed reference

Full content for `math-measure-probability` lives in
[`references/math-measure-probability-handbook.md`](../../references/math-measure-probability-handbook.md).
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

- [`../../references/math-measure-probability-handbook.md`](../../references/math-measure-probability-handbook.md) — Full handbook (extracted from this skill)
- [`../lean-math-stochastic/SKILL.md`](../lean-math-stochastic/SKILL.md) — Successor
- [`../lean-research/SKILL.md`](../lean-research/SKILL.md) — Successor
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor
