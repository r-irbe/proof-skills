---
name: "lean-doc-sync"
description: |
  USE FOR: syncing papers and Lean 4: requirement extraction, blueprint-to-LaTeX reports, and metric sync.
  DO NOT USE FOR: proof walkthrough prose (@lean-pedagogical-exposition) or @[blueprint] tags (@lean-blueprint).
  TRIGGERS: doc sync, update paper, blueprint to report, doc requirements, doc feedback, latex pdf.
tier: warm
runtime_targets:
- copilot-cli
- claude-code
- antigravity
- pi
- cursor
- gemini-cli
dispatch_targets: []
handoffs:
  predecessors:
  - skill:lean-blueprint
  - skill:lean-verification-gate
  - skill:lean-review-council
  successors:
  - skill:lean-specification
  - skill:lean-pedagogical-exposition
  - skill:lean-retro-methodology
metadata:
  version: 0.5.0
  source_spec: Unified from lean-doc-requirements, lean-doc-improvement, lean-doc-feedback,
    and lean-report
  last_reviewed: 2026-11
---

# Lean 4 Paper, Requirement & Report Synchronization

Maintain bidirectional fidelity between informal papers/reports and formal Lean 4 declarations across the full
lifecycle: pre-proof requirement extraction, post-proof LaTeX report generation, theorem-count synchronization, and
readability review.

## Routing
- **USE FOR:** extracting formalizable claims from papers (`requirements` mode), compiling blueprint artifacts into
  LaTeX/PDF reports (`report` mode), updating paper theorem counts/citations (`sync` mode), and auditing draft
  readability (`feedback` mode).
- **DO NOT USE FOR:** authoring step-by-step pedagogical proof narratives (`@lean-pedagogical-exposition`) or
  annotating Lean declarations with `@[blueprint]` (`@lean-blueprint`).

## Workflow
1. **Select Mode** -- `requirements` (paper -> 3-part spec queue), `report` (`scripts/lean/blueprint_to_report.py`
  -> LaTeX), `sync` (`scripts/lean/metric_sync.py` -> update appendix counts & `[T<chap>.<idx>]` anchors), or
  `feedback` (flag undefined terms & broken citations).
2. **Verify Identifier & Citation Parity** -- Run `scripts/lean/check_citations.py` so every Lean theorem/module
  cited in prose physically exists and is `sorry`-free.
3. **Enforce Honest Scope** -- Distinguish kernel-checked theorems from external hypotheses or idealized model
  assumptions; never overclaim formal coverage.
4. **Compile & Validate Typography** -- Enforce `INV-001` scoped Unicode and verify clean LaTeX/Markdown compilation with zero unresolved references.

## Recovery & STOP
- Never cite a `sorry`-bearing or non-existent Lean declaration as "formally verified" in any paper or report; halt and route back to `@lean-proof`.
- Re-derive module/theorem counts from a clean build census rather than copying historical numbers from prose.

## Handoffs
- **Predecessors:** `lean-blueprint`, `lean-verification-gate`, `lean-review-council`.
- **Successors:** `lean-specification`, `lean-pedagogical-exposition`, `lean-retro-methodology`.

## Detailed reference
- **Layer-1 Fast Lookup Card (read first)**: [`references/cards/lean-doc-sync-tables.md`](../../references/cards/lean-doc-sync-tables.md)
- Full handbook: [`../../references/handbooks/lean-doc-sync-handbook.md`](../../references/handbooks/lean-doc-sync-handbook.md)

## See also
- [`../lean-pedagogical-exposition/SKILL.md`](../lean-pedagogical-exposition/SKILL.md) -- Textbook-grade mathematical proof narratives
- [`../lean-blueprint/SKILL.md`](../lean-blueprint/SKILL.md) -- Lean `@[blueprint]` DAG scaffolding
