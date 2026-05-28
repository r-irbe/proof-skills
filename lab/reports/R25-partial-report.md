# R25 partial close-out — items 4, 5, 8 shipped

**Date:** 2026-05-27
**Status:** Partial. 3 of 8 R25 HITL-selected items shipped this session.
**Archive:** `scripts/elo/example_runs/2026-05-27-m-r25-median4/`
**Live matches:** `scripts/elo/matches/2026-05-27-live.csv` (1283 rows)
**Baseline lockfile:** `scripts/elo/baseline_ratings.json` (8 entrants, median-of-4 methodology)

## What shipped

### Item 4 — Per-rubric Glicko-2 split (data-only)
Archive: `scripts/elo/example_runs/2026-05-27-l-r25-per-rubric/`
3 separate Glicko-2 runs over the R24 match data (1283 rows), bucketed by
the YAML `ensemble_rubric` field.

| Rubric | Rows | Spread | Top entrant | Notes |
|---|---:|---:|---|---|
| applied-domain-quality | 819 | 586 pts | opus-default 1921 | gpt-5.4@long 1593 #2 |
| lean-doc-quality | 74 | 690 pts | opus-default 1853 | sonnet 1698 #2 |
| lean-proof-quality | 390 | 88 pts | opus-default 1560 | opus-high 1547 #2 |

**Headline:** the lean-proof rubric is *much* tighter than applied-domain
(88pt vs 586pt spread). Models are nearly indistinguishable on actual
Lean code; differentiation happens on prose-heavy applied rubrics.
See `scripts/elo/example_runs/2026-05-27-l-r25-per-rubric/per-rubric-summary.md`.

### Item 5 — Add gpt-5.4 as 4th judge (128 dispatches + demux + Glicko-2 refresh)
36 cases × 1 gpt-5.4 judge per case (with all R23-NEW entrants A/B/C/D
labeled in randomized order) → 128 new per-judge JSONs at
`scripts/eval/judge_runs/<case>/judge-<entrant>@r24-gpt-5.4.json`. Demux
back to per-entrant files. 128 canonical files refreshed to
`_judge_agg: median-of-4-mean-mid` (mean of the two middle values when
ensemble size is even). 680 new pairwise rows appended to live.csv.

**Headline (8 entrants, median-of-4 ensemble vs R24 median-of-3):**

| Rank | Player | R24 → R25 | Δ |
|---|---|---:|---:|
| 1 | claude-opus-4.7@default-effort | 1782 → 1725 | -57 |
| 2 | claude-sonnet-4.6 | 1546 → 1568 | +22 |
| 3 | gpt-5.4 | 1506 → 1533 | +27 |
| 4 | gpt-5.4@long | 1561 → 1512 | -48 |
| 5 | claude-opus-4.7-high | 1477 → 1495 | +19 |
| 6 | gpt-5.2 | 1521 → 1461 | -60 |
| 7 | gpt-5.4-mini | 1422 → 1424 | +2 |
| 8 | claude-haiku-4.5 | 1381 → 1391 | +10 |

All deltas within ±60 — regression gate PASS (tolerance ±75).

**Why opus-default dropped 57pt:** R24's +112 jump was driven by opus's
mid-range bias (45% of opus scores = 3) being one of 3 votes. Adding
gpt-5.4 as a 4th vote, where gpt-5.4 floors safety-flavoured applied
prompts to 1, breaks that single-judge leverage. opus-default still
leads cleanly, but by a more defensible margin.

**Why gpt-5.4@long dropped 48pt:** the verbose ≤25-sentence prompt gets
penalised harder by gpt-5.4 (the new judge) than by the prior 3-judge
mix that had no gpt-x voters.

### Item 8 — R22 baseline rationale doc (data-only)
`reports/_archive/r22-baseline-rationale.md` — documents the contract
that R22 (sonnet-4.6 lead, 604 rows) stays frozen as the regression-gate
baseline reset point. Three reasons:
1. R22 is the last archive with a homogeneous judge-mix (no R23 entrants).
2. Refreshing the R22 baseline under R24/R25 ensembles would silently
   invalidate the historical record of ranking shifts.
3. The gate contract is "no entrant drops > ±75 vs the lockfile" — that
   only works if the lockfile baselines were computed under a *similar*
   ensemble.

## What did NOT ship this session

| # | Item | Why deferred | Dispatch volume |
|---|---|---|---:|
| 1 | opus-high@long fresh 36 solvers | Heavy LLM dispatch | 36 + 108 = 144 |
| 2 | 30 adversarial cases | Heavy LLM dispatch + case-design | 30 × 4 × 3 = 360+ |
| 3 | Solver-template fix for 9 prose-not-Lean cases | Heavy LLM dispatch | ~72 + 27 = ~100 |
| 6 | Calibration corpora for 3 missing rubrics | Medium LLM dispatch | 45 |
| 7 | Match-volume push (tighten R23-NEW pairs) | Heavy LLM dispatch | 144+ |

Total deferred dispatch volume: **~800 LLM sub-agent calls**, well over
what fits in a single sequential session with verification gates.

## Cumulative commits

- Fork `r-irbe/proof-skills` main: `9cf320b` (R24) → `<R25 partial>` (this commit).
- Superrepo `wave-3`: `fbe08c8` (R24) → `<R25 bump>` (forthcoming).

## R26 HITL questions

See the form in plan.md. Key priorities to choose between:
- Solver-template fix (item 3) — fixes a known data-quality issue.
- Calibration corpora (item 6) — extends the CI gate to 3 currently-uncovered
  rubrics.
- Opus-high@long (item 1) — directly tests whether the verbose penalty
  generalises to opus or is gpt-only.
- 60 new cases (items 2+7) — biggest dataset-volume push, weakest per-dispatch
  leverage.
- Drift audit on the 4-judge ensemble (6 pairs vs R24's 3) — purely
  analytical, gives a stronger trust signal for the new gate methodology.
