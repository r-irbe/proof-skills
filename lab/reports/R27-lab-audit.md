# R27 — Lab audit + documentation pass

**Date:** 2026-05-28
**Status:** Audit + documentation-only round (no LLM dispatches, no ELO change).
**Archive:** `scripts/elo/example_runs/2026-05-27-o-r27-audit/`
**Live matches:** `scripts/elo/matches/2026-05-27-live.csv` (unchanged from R26)
**Baselines:** unchanged

## Scope

HITL-selected items for R27:
- **lab_audit** — sanity-check rubric definitions vs current judge behaviour
- **doc_pass** — update docs, repair references, capture current behaviour

Output is documentation + config-only changes — no entrant or judge dispatches.

---

## Findings

### Finding 1 — `lab/design/` directory was missing entirely
- 44 non-vendor references across the repo (rubrics, READMEs, reports, zettelkasten, multi_model.py docstring, `_judge_prompts_workspace/`) cited 6 distinct files under `lab/design/`.
- Directory was absent from the fork and not in upstream (`vendor/leanprover-skills/`) or git history.
- **Fix shipped:** Created `lab/design/` with stubs documenting current pipeline behaviour:
  - `README.md` (index)
  - `01-eval-framework.md` (rubrics, judge calibration, score aggregation)
  - `02-elo-system.md` (pairwise emission, draw threshold, Glicko-2)
  - `03-multi-model-runner.md` (entrant roster, solver-prompt template, judge ensemble)
  - `04-template-v2-migration.md` (historical case-YAML migration)
  - `05-zettelkasten.md` (note-graph conventions)
  - `07-cluster-workflow.md` (upstream-contribution Wave/Move system)

### Finding 2 — 29/41 cases lacked explicit `ensemble_rubric:` field
- 12 cases had explicit `ensemble_rubric:`; the other 29 (71%) relied on a hard-coded heuristic fallback in `per_rubric_elo.py:53-65` based on case-id prefix.
- This is opaque (one would have to read the script to know how a case is bucketed) and fragile (the heuristic could change without alerting case authors).
- **Fix shipped:** All 29 unlabeled cases now carry explicit `ensemble_rubric: <name>  # R27 audit: explicit (was implicit fallback)`.
- Post-audit rubric distribution:

  | Rubric | R26 (impl. fallback) | R27 (explicit) |
  |---|---:|---:|
  | applied-domain-quality | ~20 cases | 25 cases |
  | lean-proof-quality | 9 cases | 11 cases |
  | lean-doc-quality | 0 cases | 2 cases |
  | lean-setup-import-quality | 0 cases | 1 case |
  | lean-tactic-discipline-quality | 0 cases | 1 case |
  | mathlib-lookup-quality | 0 cases | 1 case |
  | research-synthesis-quality | 0 cases | 0 cases |

### Finding 3 — `research-synthesis-quality` rubric has zero cases
- The rubric exists at `scripts/eval/graders/rubrics/research-synthesis-quality.yaml` and `lab/README.md` lists it as one of the "6 calibration clusters" with content under `lab/evals/known-bad/research-synthesis/`.
- No case YAML targets it.
- **Status:** content gap, not a config gap. Recommend a follow-up round to add 2-3 research-synthesis smoke cases (e.g., a research-council prompt with a fabricated-citation calibration anchor).

### Finding 4 — Newly-explicit rubric buckets are sparse (3 rows each)
- `lean-setup-import-quality`, `lean-tactic-discipline-quality`, `mathlib-lookup-quality` each have exactly 1 case → 3 pairwise rows after the explicit labeling.
- Per-rubric Glicko-2 needs ≥ ~30 rows per bucket to produce meaningful ratings.
- **Status:** Documented in `lab/design/02-elo-system.md`. Either add more cases per rubric or accept that those rubrics' per-rubric leaderboards are illustrative only until coverage grows.

### Finding 5 — `lean-proof-quality` is the catch-all for structure/def cases
- 8 of the 11 `lean-proof-quality` cases (the lean-* R26 cases) produce `structure` / `def` rather than actual proofs.
- The rubric's "one-step discipline" criterion does not strictly apply, but judges interpreted it sensibly in R26 (spread tripled 88→256 pts after the prose-fix).
- **Status:** documented as a deliberate catch-all in `lab/design/01-eval-framework.md`. Not splitting into a separate `lean-definition-quality` rubric for now — would need a new calibration corpus.

### Finding 6 — Per-rubric gate emits "(new rubric in current run)" gracefully
- After the explicit labeling, three new rubric buckets appeared in the per-rubric run (`lean-setup-import-quality`, `lean-tactic-discipline-quality`, `mathlib-lookup-quality`).
- `check_per_rubric_regression.py` handles this with `(new rubric in current run)` notice and does NOT fail the gate.
- This is correct behaviour but underdocumented — `lab/design/01-eval-framework.md §5` now mentions it.

---

## Verification

After R27 changes:
- Per-rubric ELO refresh: `python3 scripts/elo/per_rubric_elo.py --matches scripts/elo/matches/2026-05-27-live.csv --cases scripts/eval/cases --out scripts/elo/example_runs/2026-05-27-o-r27-audit/per_rubric` ✓
- Bucket distribution post-audit: `{'lean-proof-quality': 288, 'applied-domain-quality': 859, 'lean-tactic-discipline-quality': 3, 'lean-setup-import-quality': 3, 'mathlib-lookup-quality': 3, 'lean-doc-quality': 74}`
- Per-rubric regression gate: **PASS** (no regressions > 100 pts across all (rubric, entrant) pairs in shared rubrics; new rubrics gracefully skipped).
- Global regression gate: **PASS** (no rating changes — only case-YAML labels were added).

## Deferred to future rounds

- **R28 candidates:** add cases for `research-synthesis-quality` (Finding 3); grow `lean-setup-import-quality`, `lean-tactic-discipline-quality`, `mathlib-lookup-quality` to ≥ 4 cases each (Finding 4).
- R25 carry-over items 1, 2, 6, 7 (5th-judge, drift κ, CI wiring, CI columns).
- R26 secondaries B1, B2 (drift κ, CI wiring).

## Files changed

- New: `lab/design/{README,01-eval-framework,02-elo-system,03-multi-model-runner,04-template-v2-migration,05-zettelkasten,07-cluster-workflow}.md`
- Modified: 29 `scripts/eval/cases/*.yaml` (added `ensemble_rubric:` line)
- New: `lab/reports/R27-lab-audit.md` (this file)
- New: `scripts/elo/example_runs/2026-05-27-o-r27-audit/per_rubric/` (verification archive)
