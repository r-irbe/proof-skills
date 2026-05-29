# 01 — Evaluation framework

**Status:** RECONSTRUCTED stub (R27 audit). Documents current pipeline behaviour. Replace with authoritative design doc when one is written.

## 1. Goals

Provide a reproducible way to evaluate Lean / applied / research / AI skill outputs from multiple LLM entrants against rubric-scored ground truth, producing pairwise match data for Glicko-2 ratings.

## 2. Components

- **Cases** (`scripts/eval/cases/*.yaml`) — one YAML per smoke-eval case. Each YAML names the case (`id:`), the targeted skill (`skill:`), the rubric to score against (`ensemble_rubric:`), and the prompt + expected output anchors.
- **Rubrics** (`scripts/eval/graders/rubrics/*.yaml`) — 7 rubrics on a 1–5 ordinal scale. Each rubric has dense per-score-level definitions and an `aggregation:` block (default: minority-veto, floor=2, threshold=4, pass_floor=4).
- **Graders** (`scripts/eval/graders/`) — `llm_judge.py` (LLM-based ensemble), `deterministic.py` (regex / substring checks).
- **Multi-model dispatch** (`scripts/eval/multi_model.py`) — reads (output, judge) pairs per case dir, emits pairwise match rows.
- **ELO refresh** (`scripts/elo/`) — Glicko-2 global ratings (`glicko2.py`) and per-rubric ratings (`per_rubric_elo.py`).
- **Live matches** (`scripts/elo/matches/*-live.csv`) — append-only pair history.
- **Baselines** (`scripts/elo/baseline_ratings*.json`) — rating lockfiles; the regression gates compare against these.

## 3. Rubric ladder

All rubrics share the same shape:

```yaml
name: <slug>
scale: [1, 2, 3, 4, 5]
description: |
  <when to apply literally>
definitions:
  1: <empty/broken/forbidden>
  2: <parses but fundamental failure>
  3: <discharges but stylistically wrong>
  4: <correct, minor issues>
  5: <minimal, idiomatic, methodology-perfect>
aggregation:
  policy: minority_veto
  floor: 2
  threshold: 4
  pass_floor: 4
```

## 4. Judging

### 4.1 Calibration corpora

`lab/evals/known-bad/<cluster>/` holds calibration transcripts: handcrafted bad answers that anchor the LLM judge's lower rubric scores. The active corpus has 7 clusters. Per cluster there is a README plus per-transcript `.transcript.md` files and `_replies/` directories of captured model judgments.

### 4.2 LLM judge ensemble

Judges score independently on the rubric scale. The current live ensemble is **median-of-4** over `{claude-opus-4.7-high, claude-haiku-4.5, claude-sonnet-4.6, gpt-5.4}`, with `_judge_agg: median-of-4-mean-mid` (mean of the two middle values when ensemble size is even).

Per-judge replies are persisted at `scripts/eval/judge_runs/<case>/judge-<entrant>@r<round>-<judge>.json`. The canonical per-entrant grade is `judge-<entrant>.json` with the aggregated score.

### 4.3 Pairwise emission

`multi_model.py` reads each case directory, normalizes scores to `[0, 1]` (`score / max_scale`), and emits one row per unordered (entrant_A, entrant_B) pair:

- `|s_A − s_B| ≥ draw_threshold` (default 0.15 in normalized space) → `winner = a` (or `b`)
- otherwise → `winner = draw`

The CSV shape is `case_id,model_a,model_b,winner,reasoning_effort_a,reasoning_effort_b` — consumed by the authoritative `glicko2.py` replay. `elo.py` is retained only as a legacy vanilla-ELO dashboard helper.

## 5. Regression gates

- **Global** (`scripts/elo/check_regression.py`): tolerance ±75 pts vs `baseline_ratings.json`.
- **Per-rubric** (`scripts/elo/check_per_rubric_regression.py`): tolerance ±100 pts vs `baseline_ratings_per_rubric.json` for each (rubric, entrant) pair.

`eval-smoke.yml :: glicko2` runs both gates on the largest committed
`scripts/elo/matches/*-live.csv`. Per-rubric replay depends on PyYAML because it
reads case YAML metadata before bucketing rows by `ensemble_rubric`; CI installs
that dependency in the Glicko-2 job and treats `per_rubric_elo.py` failures as
hard failures.

Both gates support `--refresh` to lock in a new baseline when a round intentionally moves ratings (e.g., after a bug-fix round like R26 Item 3).
