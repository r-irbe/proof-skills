# lab/design — design notes for the ELO / multi-model evaluation pipeline

**Status (R27 audit, 2026-05-28):** these docs were referenced from 44 places
across the repo (rubrics, READMEs, reports, zettelkasten) but the directory
was missing from the fork. R27 audit reconstructed minimal stubs that
document the pipeline's *current* behaviour, with pointers to authoritative
implementing code.

Each file below is a *living* description of the current implementation, not
a frozen spec. When you change the pipeline, update the matching design doc
in the same commit.

| File | Topic | Implementing code |
|---|---|---|
| [`01-eval-framework.md`](01-eval-framework.md) | Rubrics, judge calibration, score aggregation | `scripts/eval/graders/` |
| [`02-elo-system.md`](02-elo-system.md) | Pairwise match emission, draw threshold, Glicko-2 | `scripts/eval/multi_model.py`, `scripts/elo/glicko2.py` |
| [`03-multi-model-runner.md`](03-multi-model-runner.md) | Entrant dispatch, solver-prompt template, judge ensemble | `scripts/eval/multi_model.py`, `lab/.r26-item3-solver-prompts/` |
| [`04-template-v2-migration.md`](04-template-v2-migration.md) | W6 template-v2 historical migration record | `lab/reports/` archive |
| [`05-zettelkasten.md`](05-zettelkasten.md) | Note-graph conventions | `zettelkasten/` |
| [`07-cluster-workflow.md`](07-cluster-workflow.md) | Cluster cascade (Wave/Move labels) for upstream contribution skills | `references/upstream/` |

> **Numbering gap.** There is no `06-*.md` — the original W4–W7 wave designs
> appear to have skipped 06. The audit did not reconstruct a placeholder for it.

## Cross-referencing conventions

When a rubric YAML or report cites a design section, use this form:

```yaml
# in rubric YAML description: field
description: |
  Score the methodological quality of a Lean 4 proof response. Used by the
  LLM-judge grader per `lab/design/01-eval-framework.md §4.2`.
```

The section numbering is fluid — if a section moves, search-and-replace the
references in the same commit.
