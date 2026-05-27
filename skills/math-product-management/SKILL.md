---
name: "math-product-management"
description: |
  USE FOR: Product management for mathematical formalization projects — roadmap creation, stakeholder management, feature prioritization for formal verification artifacts, theorem portfolio management, release planning, and the business/academic value analysis of formal proofs. Complements math-project-management (scheduling/execution) with strategic product thinking.
  DO NOT USE FOR: project-level scheduling (use @math-project-management); strategy methodology (use @applied-strategy-analysis); engineering discipline view (use @applied-engineering-disciplines).
  TRIGGERS: product management, roadmap, stakeholder management, feature prioritization, formal verification PM.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:math-project-management', 'skill:lean-retro-methodology', 'skill:lean-zettelkasten']
metadata:
  version: "0.2.0"
  source_spec: "skills/math-product-management/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# Math Product Management

Strategic product thinking applied to formal verification projects. While math-project-management handles execution (schedules, tasks, milestones), this skill handles strategy (what to build, for whom, why, and in what order).

---

## Routing

- **USE FOR:** Product management for mathematical formalization projects — roadmap creation, stakeholder management, feature prioritization for formal verification artifacts, theorem portfolio management, release planning, and the business/academic value analysis of formal proofs. Complements math-project-management (scheduling/execution) with strategic product thinking.
- **DO NOT USE FOR:** project-level scheduling (use @math-project-management); strategy methodology (use @applied-strategy-analysis); engineering discipline view (use @applied-engineering-disciplines).
- **TRIGGERS:** product management, roadmap, stakeholder management, feature prioritization, formal verification PM.

## Workflow

1. Frame the product question: roadmap, prioritisation, stakeholder communication, or scope decision.
2. Pick the matching template; identify data inputs needed (theorem counts, dependency graph, coverage matrix).
3. Produce the artifact (roadmap, RICE table, stakeholder brief).
4. Hand off: to `@math-project-management` for scheduling, to `@lean-retro-methodology` for retro-driven re-prioritisation, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the question is operational scheduling — delegate to `@math-project-management`.
- STOP if a strategic-analysis lens dominates — delegate to `@applied-strategy-analysis`.
- STOP if data inputs are missing — escalate to audit / blueprint skills first.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:math-project-management`, `skill:lean-retro-methodology`, `skill:lean-zettelkasten`.

---

## Detailed reference

Full content for `math-product-management` lives in
[`references/math-product-management-handbook.md`](../../references/math-product-management-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

| Section | Topic |
|---|---|
| Part 1 | Product vs. Project Management |
| Part 2 | Theorem Portfolio Management |
| Part 3 | Stakeholder Analysis |
| Part 4 | Roadmap Planning |
| Part 5 | Value Analysis |
| Part 6 | Decision Frameworks |
| Part 7 | Metrics and Analytics |
| Part 8 | Cross-References |

---

## See also

- [`../../references/math-product-management-handbook.md`](../../references/math-product-management-handbook.md) — Full handbook (extracted from this skill)
- [`../math-project-management/SKILL.md`](../math-project-management/SKILL.md) — Successor
- [`../lean-retro-methodology/SKILL.md`](../lean-retro-methodology/SKILL.md) — Successor
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor

