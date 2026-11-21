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

Maintain bidirectional fidelity between papers/reports and Lean 4 declarations across requirement extraction,
LaTeX report compilation, theorem/metric sync, concordance checking, and anonymized supplement generation.

## Routing
- **USE FOR:** claim extraction (`requirements`), blueprint-to-LaTeX reports (`report`), paper/concordance sync
  (`sync`), standalone tree-shaken supplements (`supplement`), and readability/terminology review (`feedback`).
- **DO NOT USE FOR:** step-by-step pedagogical narratives (`@lean-pedagogical-exposition`) or `@[blueprint]` tags
  (`@lean-blueprint`).

## Workflow
1. **Select Mode** -- `requirements` (paper -> 3-part spec), `report` (`blueprint_to_report.py`), `sync`
  (`metric_sync.py` + `Concordance.lean`), `supplement` (`altproof tree-shake --anonymize --verify-build`), or
  `feedback`.
2. **Verify Concordance, `.bib` & Terminology** -- Run `scripts/lean/check_citations.py` and
  `scripts/lean/paper_supplement_audit.py` for 1-to-1 theorem parity, `.bib`/`filecontents*` byte parity, and zero
  coined/spliced mathematical misnomers.
3. **Enforce Three-Tier Provenance & Scope** -- Partition credit across upstream (`Mathlib`/`Cslib`), adapted or
  newly proved classical theory (preserving SPDX notices), and novel domain results; cite only executed checkers
  (`Lean.Kernel.Environment.replay`).
4. **Compile & Validate Typography** -- Enforce three-tier `INV-001` Unicode, Knuth Ch. 18 inline math, zero
  Overfull boxes, and clean LaTeX/BibTeX compilation within the page budget.

## Recovery & STOP
- Never cite a `sorry`-bearing, facade-stub, or missing Lean declaration as verified; strengthen the Lean proof or
  calibrate the paper claim to match exact proved hypotheses.
- Remove `@[deprecated]` shims from `.lean` files; log renames in an external Markdown ledger (`GT-66`).
- Re-derive module/theorem/constant counts from a clean build + cold replay census.

## Handoffs
- **Predecessors:** `lean-blueprint`, `lean-verification-gate`, `lean-review-council`.
- **Successors:** `lean-specification`, `lean-pedagogical-exposition`, `lean-retro-methodology`.

## Detailed reference
- **Layer-1 Card**: [`references/cards/lean-doc-sync-tables.md`](../../references/cards/lean-doc-sync-tables.md)
- **Handbook**: [`../../references/handbooks/lean-doc-sync-handbook.md`](../../references/handbooks/lean-doc-sync-handbook.md)
- **Supplement Protocol**:
  [`../../references/protocols/double-blind-paper-and-supplement-release.md`](../../references/protocols/double-blind-paper-and-supplement-release.md)

## See also
- [`../lean-pedagogical-exposition/SKILL.md`](../lean-pedagogical-exposition/SKILL.md) -- Textbook-grade mathematical proof narratives
- [`../lean-blueprint/SKILL.md`](../lean-blueprint/SKILL.md) -- Lean `@[blueprint]` DAG scaffolding
