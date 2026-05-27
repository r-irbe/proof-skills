---
name: "lean-integration-protocol"
description: |
  USE FOR: Cross-skill integration protocol defining how all 39 skills work together. Covers the complete lifecycle from document to proof to document, inter-cluster communication, workflow templates for common tasks, and the master orchestration patterns. Use when coordinating multi-skill workflows or diagnosing cross-skill issues.
  DO NOT USE FOR: any single-skill execution (use that skill directly); the review council itself (use @lean-review-council); the gateway (use @lean-gateway).
  TRIGGERS: integration protocol, skill integration, cross-skill, skill lifecycle, inter-cluster routing.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-review-council', 'skill:lean-enforcement', 'skill:lean-zettelkasten']
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-integration-protocol/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# SK-40: Integration Protocol

Defines how all skills in the project ecosystem work together as a coherent system.

---

## Routing

- **USE FOR:** Cross-skill integration protocol defining how all 39 skills work together. Covers the complete lifecycle from document to proof to document, inter-cluster communication, workflow templates for common tasks, and the master orchestration patterns. Use when coordinating multi-skill workflows or diagnosing cross-skill issues.
- **DO NOT USE FOR:** any single-skill execution (use that skill directly); the review council itself (use @lean-review-council); the gateway (use @lean-gateway).
- **TRIGGERS:** integration protocol, skill integration, cross-skill, skill lifecycle, inter-cluster routing.

## Workflow

1. Identify the cross-skill question: which skills, what data flows, which handoffs.
2. Pick the lifecycle section of the body matching the flow (document → spec → proof → doc, or council ↔ research).
3. Produce the integration recipe — explicit sequence of skill invocations + artifact handoffs.
4. Hand off: to `@lean-review-council` for council orchestration, to `@lean-enforcement` for CI, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the question is about a single skill's execution — delegate to that skill directly.
- STOP if the integration target is the gateway itself — delegate to `@lean-gateway`.
- STOP if the protocol would create a cycle — surface the cycle and request HITL design judgment.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-review-council`, `skill:lean-enforcement`, `skill:lean-zettelkasten`.

---

## Detailed reference

Full content for `lean-integration-protocol` lives in
[`references/lean-integration-protocol-handbook.md`](../../references/lean-integration-protocol-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

| Section | Topic |
|---|---|
| Part 1 | The Three Lifecycles |
| Part 2 | Standard Workflow Templates |
| Part 3 | Inter-Cluster Communication Protocols |
| Part 4 | Feedback Loop Inventory |
| Part 5 | Personas and Roles (Complete) |
| Part 6 | Conflict Resolution |
| Part 7 | Bootstrapping a New Project |
| Part 8 | Retrofitting an Existing Project (RETRO Protocol Summary) |
| Part 9 | Integration Anti-Patterns |

---

## See also

- [`../../references/lean-integration-protocol-handbook.md`](../../references/lean-integration-protocol-handbook.md) — Full handbook (extracted from this skill)
- [`../lean-review-council/SKILL.md`](../lean-review-council/SKILL.md) — Successor
- [`../lean-enforcement/SKILL.md`](../lean-enforcement/SKILL.md) — Successor
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor

