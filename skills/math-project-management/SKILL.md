---
name: "math-project-management"
description: |
  USE FOR: Project and product management for mathematical formalization projects. Covers dependency-aware scheduling, risk management for unprovable theorems, progress tracking, milestone planning, resource allocation across proof workstreams, technical debt management, and stakeholder communication. Use when planning formalization campaigns, tracking multi-module efforts, or managing the intersection of research and engineering in formal mathematics.
  DO NOT USE FOR: product-level PM (use @math-product-management); retro methodology (use @lean-retro-methodology); engineering discipline view (use @applied-engineering-disciplines).
  TRIGGERS: project management, dependency scheduling, risk management for proofs, formalization PM.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:math-product-management', 'skill:lean-retro-methodology', 'skill:lean-zettelkasten']
metadata:
  version: "0.2.0"
  source_spec: "skills/math-project-management/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# Mathematical Project & Product Management

Methodology for managing large-scale formal mathematics projects as engineering endeavors.

---

## Routing

- **USE FOR:** Project and product management for mathematical formalization projects. Covers dependency-aware scheduling, risk management for unprovable theorems, progress tracking, milestone planning, resource allocation across proof workstreams, technical debt management, and stakeholder communication. Use when planning formalization campaigns, tracking multi-module efforts, or managing the intersection of research and engineering in formal mathematics.
- **DO NOT USE FOR:** product-level PM (use @math-product-management); retro methodology (use @lean-retro-methodology); engineering discipline view (use @applied-engineering-disciplines).
- **TRIGGERS:** project management, dependency scheduling, risk management for proofs, formalization PM.

## Workflow

1. Frame the project question: dependency scheduling, risk management, capacity, or sequencing.
2. Pick the matching template (dependency-aware schedule, risk-register, capacity planner).
3. Produce the artifact; emit explicit risks for unprovable theorems with mitigation options.
4. Hand off: to `@math-product-management` for upstream PM, to `@lean-retro-methodology` for retro, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the question is product-level — delegate to `@math-product-management`.
- STOP if the engineering-discipline lens dominates — delegate to `@applied-engineering-disciplines`.
- STOP if the dependency graph is unavailable — escalate to blueprint / audit skills first.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:math-product-management`, `skill:lean-retro-methodology`, `skill:lean-zettelkasten`.

---

## Detailed reference

Full content for `math-project-management` lives in
[`references/math-project-management-handbook.md`](../../references/math-project-management-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

| Section | Topic |
|---|---|
| Part 1 | Formalization Project Structure |
| Part 2 | Risk Management |
| Part 3 | Progress Tracking |
| Part 4 | Technical Debt Management |
| Part 5 | Stakeholder Communication |
| Part 6 | Research Council Integration |

---

## See also

- [`../../references/math-project-management-handbook.md`](../../references/math-project-management-handbook.md) — Full handbook (extracted from this skill)
- [`../math-product-management/SKILL.md`](../math-product-management/SKILL.md) — Successor
- [`../lean-retro-methodology/SKILL.md`](../lean-retro-methodology/SKILL.md) — Successor
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor

