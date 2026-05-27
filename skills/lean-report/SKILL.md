---
name: "lean-report"
description: |
  USE FOR: converting a Lean 4 project blueprint into a publication-grade LaTeX report — blueprint artifact ingestion (extracted LaTeX nodes, dependency DAG, JSON metadata), per-chapter narrative generation with mathematical prose, dependency-driven cross-referencing, figure generation (dependency graphs, module maps, coverage tables), and LaTeX → PDF compilation via the 6-stage INGEST → PLAN → NARRATE → ILLUSTRATE → ASSEMBLE → COMPILE pipeline.
  DO NOT USE FOR: generating the blueprint itself (use @lean-blueprint); writing one chapter without the pipeline (use @lean-doc-improvement); reviewing a finished report (use @lean-review-council); spec lifecycle (use @lean-specification).
  TRIGGERS: blueprint to report, generate report, latex pdf, project-report.tex, narrate chapter, dependency figure, blueprint compile.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
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

Convert a Lean 4 project blueprint (extracted LaTeX nodes, dependency graphs, JSON metadata) into a publication-grade LaTeX report with natural language narrative, mathematical exposition, and visual dependency maps.

---

## Routing

- **USE FOR:** converting a Lean 4 project blueprint into a publication-grade LaTeX report via the 6-stage INGEST → PLAN → NARRATE → ILLUSTRATE → ASSEMBLE → COMPILE pipeline; ingesting blueprint artifacts (LaTeX nodes, dependency DAG, JSON metadata); generating per-chapter mathematical prose with `\leanref` cross-references; producing TikZ dependency figures; running `latexmk` to PDF.
- **DO NOT USE FOR:** generating the blueprint itself (delegate to `@lean-blueprint`); writing one chapter without the pipeline (delegate to `@lean-doc-improvement`); reviewing a finished report (delegate to `@lean-review-council`); spec lifecycle (delegate to `@lean-specification`).
- **TRIGGERS:** blueprint to report, generate report, latex pdf, `project-report.tex`, narrate chapter, dependency figure, blueprint compile.

## Workflow

1. Verify prerequisites (Part 12.1 below — blueprint artifacts exist, LaTeX toolchain present).
2. First-time: run Part 12.2 (INGEST → PLAN → NARRATE → ILLUSTRATE → ASSEMBLE → COMPILE). Each stage's contract is in the handbook (Parts 3–8).
3. Incremental: run Part 12.3 — re-blueprint, re-ingest, diff, narrate only changed chapters, recompile.
4. On compilation error consult Part 13 (Troubleshooting) below; on output-artifact question consult Part 14 below.
5. Handoff to `@lean-doc-feedback` once the PDF lands so the doc-sync skill can record the new artifact in the project's tracking matrix.

## Recovery & STOP

- STOP if `\cref` references emit "??" after two latexmk passes — the blueprint is out of sync; re-run INGEST per Part 12.3.
- STOP if narration drifts from Lean source (Part 13 final row) — the source changed after narration; re-run NARRATE for affected chapters only.
- STOP if the figures stage produces empty TikZ outputs — `dot2tex` is optional but required for dependency graphs; install or fall back to module-map-only figures.

## Handoffs

- **Predecessors:** `agent:gateway` (top-level invocation), `skill:lean-blueprint` (produces the blueprint artifacts this skill consumes), `skill:lean-doc-requirements` (chapter-scope decisions).
- **Successors:** `skill:lean-doc-feedback` (record the PDF artifact + cross-references), `skill:lean-doc-improvement` (per-chapter post-narration edits), `skill:lean-review-council` (review the report for project-level coherence), `skill:lean-enforcement` (CI gate that confirms PDF builds on a clean checkout).

---

## Detailed reference

Full pipeline content (Parts 1–11) lives in
[`references/lean-report-handbook.md`](../../references/lean-report-handbook.md).
Load that file when authoring or debugging stage internals; the SKILL.md
only carries the dispatch contract and the high-frequency operational
sections (Parts 12–14 kept inline below).

| Section | Topic | Covers |
|---|---|---|
| Part 1 | Inputs and Outputs | What this skill consumes / produces |
| Part 2 | Pipeline Architecture | Six-stage DAG overview |
| Part 3 | Stage 1 — INGEST | Blueprint artifact extraction |
| Part 4 | Stage 2 — PLAN | Chapter outline + narrative arc derivation |
| Part 5 | Stage 3 — NARRATE | Per-chapter prose generation rules |
| Part 5B | Lean 4.28 Features for Report Generation | Pin-relative Lean+Mathlib features |
| Part 6 | Stage 4 — ILLUSTRATE | TikZ figure generation |
| Part 7 | Stage 5 — ASSEMBLE | Master-document merging |
| Part 8 | Stage 6 — COMPILE | latexmk pipeline + diagnostics |
| Part 9 | Audit Integration | Tracking-matrix hooks |
| Part 10 | Project-specific Configuration | Per-project tunables |
| Part 11 | Integration with Gateway (SK-07) | Cross-skill dispatch |

## Part 12 — Execution Checklist

### 12.1 Prerequisites

```bash
# 1. Verify blueprint exists
ls .lake/build/blueprint/library/*.tex   # extracted nodes
ls blueprint/web/index.html              # web build exists

# 2. Verify LaTeX toolchain
which latexmk pdflatex biber
kpsewhich tikz.sty pgfplots.sty cleveref.sty thmtools.sty

# 3. Verify optional tools
which dot2tex   # for dependency graph conversion (optional)
```

### 12.2 First-Time Generation

```bash
# 1. Create report directory structure
mkdir -p report/{chapters,front,back,figures,macros,build}

# 2. Run INGEST stage
python3 scripts/blueprint_to_report.py ingest \
  --blueprint-dir .lake/build/blueprint \
  --coverage docs/tracking/coverage_matrix.md \
  --output report/report_context.json

# 3. Run PLAN stage
python3 scripts/blueprint_to_report.py plan \
  --context report/report_context.json \
  --output report/report_plan.json

# 4. Run NARRATE stage (agent-driven, one chapter at a time)
# Each chapter: read plan → read module → generate prose
# See §5 for generation rules

# 5. Run ILLUSTRATE stage
python3 scripts/blueprint_to_report.py illustrate \
  --context report/report_context.json \
  --output-dir report/figures/

# 6. Run ASSEMBLE stage
# Merge all chapters into master document (see §7.1)

# 7. Run COMPILE stage
cd report && latexmk -pdf project-report.tex
```

### 12.3 Incremental Updates

After new theorems are proven:

```bash
# 1. Re-run blueprint (SK-61):
lake build :blueprint && leanblueprint all

# 2. Re-ingest:
python3 scripts/blueprint_to_report.py ingest --update

# 3. Identify changed chapters:
python3 scripts/blueprint_to_report.py diff \
  --old report/report_context.json \
  --new report/report_context_updated.json

# 4. Re-narrate affected chapters only

# 5. Recompile:
cd report && latexmk -pdf project-report.tex
```

---

## Part 13 — Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| No blueprint artifacts found | SK-61 not run | Run `generate blueprint` first |
| `nodes.json` missing | `:blueprintJson` not built | Run `lake build :blueprintJson` |
| LaTeX won't compile | Missing package | Install full TeX Live: `tlmgr install <pkg>` |
| Undefined `\cref` | `cleveref` not loaded | Add `\usepackage{cleveref}` after `hyperref` |
| Cross-references show "??" | Need 2nd pass | Run `latexmk` (auto-handles multi-pass) |
| Theorem count mismatch | Blueprint outdated | Rebuild blueprint, re-ingest |
| Margin notes overflow | Too many `\leanref` | Reduce to key theorems only |
| Figure won't render | Missing TikZ library | Add `\usetikzlibrary{...}` |
| Bibliography empty | `.bib` not found | Check `\addbibresource` path |
| PDF too large | Embedded high-res figures | Use `\includegraphics[draft]` for draft builds |
| Narration inconsistent with Lean | Source changed after narration | Re-run INGEST + NARRATE for affected chapters |
| Scaling notation unclear | Missing §scaling-convention | Ensure Ch 1 defines the $\times 100$ convention |

---

## Part 14 — Output Artifacts Summary

The complete report generation pipeline produces:

| Artifact | Location | Purpose |
|---|---|---|
| Report context | `report/report_context.json` | Serialized ingestion data |
| Report plan | `report/report_plan.json` | Chapter outlines + narrative arcs |
| Chapter files | `report/chapters/ch_*.tex` | Per-module natural language chapters |
| Front matter | `report/front/` | Abstract, introduction |
| Back matter | `report/back/` | Appendices, bibliography |
| Figures | `report/figures/` | TikZ source + PDF figures |
| Macros | `report/macros/common.tex` | Shared LaTeX commands |
| Master document | `report/project-report.tex` | Top-level LaTeX source |
| Compiled PDF | `report/build/project-report.pdf` | Final output |
| Build log | `report/build/project-report.log` | Compilation diagnostics |

---

## See also

- [`../../references/lean-report-handbook.md`](../../references/lean-report-handbook.md) — Full pipeline encyclopaedia (extracted from this skill)
- [`../lean-blueprint/SKILL.md`](../lean-blueprint/SKILL.md) — Produces the blueprint artifacts this skill consumes
- [`../lean-doc-feedback/SKILL.md`](../lean-doc-feedback/SKILL.md) — Records the resulting PDF in the project's doc-sync matrix
- [`../lean-review-council/SKILL.md`](../lean-review-council/SKILL.md) — Reviews the report for project-level coherence
