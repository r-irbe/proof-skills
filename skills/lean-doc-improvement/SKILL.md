---
name: "lean-doc-improvement"
description: |
  USE FOR: Update academic papers, technical reports, and documentation based on results from Lean 4 formalization. Use when formal verification reveals paper imprecisions, missing hypotheses, sharper bounds, new insights, or when metrics need synchronization. Covers paper appendix updates, verification tables, erratum entries, insight propagation, and metric synchronization between Lean and documents.
  DO NOT USE FOR: extracting requirements from papers (use @lean-doc-requirements); blueprint generation (use @lean-blueprint); report compilation (use @lean-report).
  TRIGGERS: update paper, doc improvement, paper revision, documentation update from Lean, doc-feedback consumer.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-doc-feedback', 'skill:lean-report', 'skill:lean-zettelkasten']
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-doc-improvement/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# Lean 4 Results-to-Document Improvement

Systematically update documents when Lean formalization produces new insights, corrections, or metrics.

---

## Routing

- **USE FOR:** Update academic papers, technical reports, and documentation based on results from Lean 4 formalization. Use when formal verification reveals paper imprecisions, missing hypotheses, sharper bounds, new insights, or when metrics need synchronization. Covers paper appendix updates, verification tables, erratum entries, insight propagation, and metric synchronization between Lean and documents.
- **DO NOT USE FOR:** extracting requirements from papers (use @lean-doc-requirements); blueprint generation (use @lean-blueprint); report compilation (use @lean-report).
- **TRIGGERS:** update paper, doc improvement, paper revision, documentation update from Lean, doc-feedback consumer.

## Workflow

1. Triage the change: which paper/document needs updating, which Lean result triggers it, and what's the delta.
2. Pick the section/template from the body matching the update class (definition, theorem, proof-strategy, errata).
3. Produce the patch with precise pointers to the Lean source + before/after text.
4. Hand off: to `@lean-doc-feedback` for the doc-sync record, to `@lean-report` if the paper feeds into a report, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the question is about extracting requirements from the paper — delegate to `@lean-doc-requirements`.
- STOP if a fresh blueprint is needed — delegate to `@lean-blueprint`.
- STOP if the Lean result is wrong (not the paper) — delegate to `@lean-proof-review` first.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-doc-feedback`, `skill:lean-report`, `skill:lean-zettelkasten`.

---

## Detailed reference

Full content for `lean-doc-improvement` lives in
[`references/lean-doc-improvement-handbook.md`](../../references/lean-doc-improvement-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

| Section | Topic |
|---|---|
| Part 1 | Trigger Events |
| Part 2 | Document Update Types |
| Part 3 | Update Workflow |
| Part 4 | LaTeX Integration Patterns |
| Part 5 | Feedback to Other Skills |
| Part 6 | Metric Dashboard |

---

## See also

- [`../../references/lean-doc-improvement-handbook.md`](../../references/lean-doc-improvement-handbook.md) — Full handbook (extracted from this skill)
- [`../lean-doc-feedback/SKILL.md`](../lean-doc-feedback/SKILL.md) — Successor
- [`../lean-report/SKILL.md`](../lean-report/SKILL.md) — Successor
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor

