---
name: "lean-report"
description: |
  USE FOR: converting a Lean 4 project blueprint into a publication-grade LaTeX report: blueprint artifact ingestion.
  DO NOT USE FOR: generating the blueprint itself (@lean-blueprint).
  TRIGGERS: blueprint to report, generate report, latex pdf.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-blueprint", "skill:lean-doc-requirements"]
  successors: ["skill:lean-doc-feedback", "skill:lean-doc-improvement", "skill:lean-review-council", "skill:lean-enforcement"]
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-report/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# SK-62: Blueprint-to-Report Generator
Convert a Lean 4 project blueprint (extracted LaTeX nodes, dependency graphs, JSON metadata) into a
publication-grade LaTeX report
with
natural language
narrative, mathematical exposition, and visual dependency maps.
---
## Routing
- **USE FOR:** converting a Lean 4 project blueprint into a publication-grade LaTeX report via the 6-stage
  INGEST → PLAN → NARRATE
  →
  ILLUSTRATE → ASSEMBLE
  → COMPILE pipeline; ingesting blueprint artifacts (LaTeX nodes, dependency DAG, JSON metadata); generating
  per-chapter
  mathematical prose
with `\leanref`
  cross-references; producing TikZ dependency figures; running `latexmk` to PDF.
- **DO NOT USE FOR:** generating the blueprint itself (delegate to `@lean-blueprint`); writing one chapter
  without the pipeline
  (delegate to
## Workflow
1. Verify prerequisites (Part 12.1 below — blueprint artifacts exist, LaTeX toolchain present).
2. First-time: run Part 12.2 (INGEST → PLAN → NARRATE → ILLUSTRATE → ASSEMBLE → COMPILE). Each stage's
  contract is in the handbook
  (Parts
   3–8).
3. Incremental: run Part 12.3 — re-blueprint, re-ingest, diff, narrate only changed chapters, recompile.
4. On compilation error consult Part 13 (Troubleshooting) below; on output-artifact question consult Part 14
  below.
5. Handoff to `@lean-doc-feedback` once the PDF lands so the doc-sync skill can record the new artifact in the
  repository's
  tracking matrix.
## Recovery & STOP
- STOP if `\cref` references emit "??" after two latexmk passes — the blueprint is out of sync; re-run INGEST
  per Part 12.3.
- STOP if narration drifts from Lean source (Part 13 final row) — the source changed after narration; re-run
  NARRATE for affected
  chapters
  only.
- STOP if the figures stage produces empty TikZ outputs — `dot2tex` is optional but required for dependency
  graphs; install or
  fall back to
  module-map-only
  figures.
## Handoffs
- **Predecessors:** `agent:gateway` (top-level invocation), `skill:lean-blueprint` (produces the blueprint
  artifacts this skill
  consumes),
  `skill:lean-doc-requirements` (chapter-scope decisions).
- **Successors:** `skill:lean-doc-feedback` (record the PDF artifact + cross-references),
  `skill:lean-doc-improvement`
  (per-chapter
  post-narration edits),
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-report-handbook.md`](../../references/lean-report-handbook.md) .
## See also
- [`../../references/lean-report-handbook.md`](../../references/lean-report-handbook.md) -- Complete
  `lean-report` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
