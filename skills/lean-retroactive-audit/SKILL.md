---
name: "lean-retroactive-audit"
description: |
  USE FOR: Apply the review council system retroactively to an existing large Lean 4 project. Use when onboarding an existing codebase to the council review framework. Covers module discovery, dependency analysis, incremental audit scheduling, baseline establishment, gap analysis, and the catch-up RALPH cycle for bringing an existing project to full review coverage.
  DO NOT USE FOR: building a new council (use @lean-review-council); single proof review (use @lean-proof-review); RETRO methodology (use @lean-retro-methodology).
  TRIGGERS: retroactive audit, council onboarding, existing project audit, legacy Lean review.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-review-council', 'skill:lean-retro-methodology', 'skill:lean-zettelkasten']
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-retroactive-audit/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# Lean 4 Retroactive Audit

Systematic methodology for applying the 5-member review council, Zettelkasten, and specification framework to a large existing Lean 4 codebase that was developed before these systems were in place.

---

## Routing

- **USE FOR:** Apply the review council system retroactively to an existing large Lean 4 project. Use when onboarding an existing codebase to the council review framework. Covers module discovery, dependency analysis, incremental audit scheduling, baseline establishment, gap analysis, and the catch-up RALPH cycle for bringing an existing project to full review coverage.
- **DO NOT USE FOR:** building a new council (use @lean-review-council); single proof review (use @lean-proof-review); RETRO methodology (use @lean-retro-methodology).
- **TRIGGERS:** retroactive audit, council onboarding, existing project audit, legacy Lean review.

## Workflow

1. Survey the existing project: count theorems, sorries, native_decide, axiom totals, council coverage gaps.
2. Pick the audit playbook from the body matching the project scale (Solo / Small / Medium / Large).
3. Execute the audit; produce a per-module readiness report with sequencing for council onboarding.
4. Hand off: to `@lean-review-council` for the first council session, to `@lean-retro-methodology` for RETRO, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the project is new — delegate to `@lean-specification` to start from scratch.
- STOP if the audit reveals architectural blockers — request HITL strategy decision.
- STOP if scope drifts into per-proof review — delegate single-proof items to `@lean-proof-review`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-review-council`, `skill:lean-retro-methodology`, `skill:lean-zettelkasten`.

---

## Detailed reference

Full content for `lean-retroactive-audit` lives in
[`references/lean-retroactive-audit-handbook.md`](../../references/lean-retroactive-audit-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

| Section | Topic |
|---|---|
| Part 1 | The Retroactive Challenge |
| Part 2 | Phase 0: Discovery |
| Part 3 | Phase 1: Baseline Establishment |
| Part 4 | Phase 2: Incremental Deep Audit |
| Part 5 | Phase 3: Gap Analysis and Extension |
| Part 6 | Phase 4: Steady-State Transition |
| Part 7 | Parallel Audit Dispatch |

---

## See also

- [`../../references/lean-retroactive-audit-handbook.md`](../../references/lean-retroactive-audit-handbook.md) — Full handbook (extracted from this skill)
- [`../lean-review-council/SKILL.md`](../lean-review-council/SKILL.md) — Successor
- [`../lean-retro-methodology/SKILL.md`](../lean-retro-methodology/SKILL.md) — Successor
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor

