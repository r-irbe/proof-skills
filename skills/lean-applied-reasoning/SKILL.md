---
name: "lean-applied-reasoning"
description: |
  USE FOR: Applied reasoning for intelligence analysis, strategy creation and analysis, brainstorming methodologies, investigative reasoning, and domain-specific decision-making. Use when formalizing strategic frameworks, situational analysis, hypothesis generation workflows, decision-under-uncertainty models, or when connecting theoretical formalization to practical operational contexts. Bridges mathematical formalization to real-world application domains.
  DO NOT USE FOR: pure intelligence-analysis methodology (use @applied-intelligence-analysis); strategy analysis methodology (use @applied-strategy-analysis); legal reasoning methodology (use @applied-legal-reasoning).
  TRIGGERS: applied reasoning, intelligence formalisation, strategy formalisation, investigative reasoning, domain-specific reasoning.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-proof-review', 'skill:lean-enforcement', 'skill:lean-zettelkasten']
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-applied-reasoning/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# Lean 4 Applied Reasoning & Strategy

Guide to formalizing applied reasoning — from intelligence analysis to strategic decision-making — in Lean 4.

---

## Routing

- **USE FOR:** Applied reasoning for intelligence analysis, strategy creation and analysis, brainstorming methodologies, investigative reasoning, and domain-specific decision-making. Use when formalizing strategic frameworks, situational analysis, hypothesis generation workflows, decision-under-uncertainty models, or when connecting theoretical formalization to practical operational contexts. Bridges mathematical formalization to real-world application domains.
- **DO NOT USE FOR:** pure intelligence-analysis methodology (use @applied-intelligence-analysis); strategy analysis methodology (use @applied-strategy-analysis); legal reasoning methodology (use @applied-legal-reasoning).
- **TRIGGERS:** applied reasoning, intelligence formalisation, strategy formalisation, investigative reasoning, domain-specific reasoning.

## Workflow

1. Classify the applied-reasoning task: intelligence-formalisation, strategy-formalisation, investigative-reasoning, or domain-specific reasoning.
2. Pick the corresponding body section; identify the Lean primitives + Mathlib lemmas it depends on.
3. Write the Lean encoding; verify Mathlib primitives exist at the current pin.
4. Hand off: to `@lean-proof-review` for review, to `@lean-enforcement` for CI, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the question is purely methodological (no Lean) — delegate to the matching applied-* skill.
- STOP if Mathlib primitives are missing — escalate to `@lean-research`.
- STOP if the spec is informal — delegate to `@lean-specification` first.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-proof-review`, `skill:lean-enforcement`, `skill:lean-zettelkasten`.

---

## Detailed reference

Full content for `lean-applied-reasoning` lives in
[`references/lean-applied-reasoning-handbook.md`](../../references/lean-applied-reasoning-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

| Section | Topic |
|---|---|
| Part 1 | Intelligence Analysis Formalization |
| Part 2 | Strategy Formalization |
| Part 3 | Brainstorming Methodology |
| Part 4 | Investigative Reasoning (Project Core Domain) |
| Part 5 | Decision Under Uncertainty |
| Part 6 | Project & Product Management for Mathematics |
| Part 7 | Research Council Integration |

---

## See also

- [`../../references/lean-applied-reasoning-handbook.md`](../../references/lean-applied-reasoning-handbook.md) — Full handbook (extracted from this skill)
- [`../lean-proof-review/SKILL.md`](../lean-proof-review/SKILL.md) — Successor
- [`../lean-enforcement/SKILL.md`](../lean-enforcement/SKILL.md) — Successor
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor
