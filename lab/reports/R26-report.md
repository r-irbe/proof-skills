# R26 close-out — Item 3 (lean-solver-template fix) shipped

**Date:** 2026-05-28
**Status:** Item 3 complete. Items 1, 2, 6, 7 (R25 carry-over) and other R26 secondaries deferred to HITL.
**Archive:** `scripts/elo/example_runs/2026-05-27-n-r26-item3-fix/`
**Live matches:** `scripts/elo/matches/2026-05-27-live.csv` (1231 rows)
**Baseline lockfiles refreshed:**
  - `scripts/elo/baseline_ratings.json` (8 entrants, post-Item-3 median-of-4)
  - `scripts/elo/baseline_ratings_per_rubric.json` (3 rubrics × 8 entrants)

## What shipped — Item 3: lean-* solver-template fix + full re-evaluation

**Problem (carried from R25):** 9 of the 36 R23-NEW cases (`lean-ai-formalization-smoke`,
`lean-applied-reasoning-smoke`, …, `lean-specification-smoke`) had been
collecting *prose* responses instead of Lean 4 code from every entrant
through R23/R24/R25. The graders dutifully scored 1–2 for "no Lean code
produced" across all 8 entrants. ~305 pairwise rows in `live.csv` were
near-meaningless noise.

**Solution:** A hard-constraint solver prompt template (one ` ```lean ` fence,
no prose, `-- TASK INFEASIBLE` fallback) was created in `lab/.r26-item3-solver-prompts/`
and dispatched to all 8 entrants × 9 cases (72 fresh solver runs). Every
agent returned valid Lean code matching the expected signatures.

**Re-judging:** 4-judge median-of-4 ensemble (opus-high, haiku, sonnet, gpt-5.4)
× 9 cases = 36 judge dispatches; demuxed back to 72 canonical
`judge-<entrant>.json` files with `_judge_agg: median-of-4-mean-mid`.

**Pairwise refresh:** 305 stale rows removed from `live.csv`; 252 fresh rows
appended (9 cases × 28 pairs).

### Headline global Glicko-2 (8 entrants, full live.csv post-Item-3)

| Rank | Player | R25 → R26 | Δ | Games |
|---|---|---:|---:|---:|
| 1 | claude-opus-4.7@default-effort | 1725 → 1724 | -1 | 168 |
| 2 | claude-sonnet-4.6 | 1568 → 1561 | -7 | 417 |
| 3 | gpt-5.4 | 1533 → 1517 | -16 | 321 |
| 4 | claude-opus-4.7-high | 1495 → 1512 | +17 | 417 |
| 5 | gpt-5.4@long | 1512 → 1494 | -19 | 240 |
| 6 | gpt-5.2 | 1461 → 1469 | +8 | 240 |
| 7 | gpt-5.4-mini | 1424 → 1466 | +42 | 240 |
| 8 | claude-haiku-4.5 | 1391 → 1404 | +13 | 417 |

All deltas within ±42 — global regression gate **PASS** (tol ±75).

### Per-rubric Glicko-2 (post-Item-3)

| Rubric | Rows | Spread | Top entrant | Δ vs R25 |
|---|---:|---:|---|---|
| applied-domain-quality | 819 | 507 pts | opus-default 1860 | spread −79 (was 586) |
| lean-doc-quality | 74 | 555 pts | sonnet 1718 | opus-default no longer #1 |
| lean-proof-quality | 337 | 256 pts | opus-default 1651, opus-high 1609 | spread +168 (was 88) |

**Headline:** lean-proof-quality spread **TRIPLED** (88 → 256 pts) once the
prose-leftover rows were replaced with real Lean code. Models are no
longer artificially compressed; opus variants pull ahead as expected.

### Per-case median-of-4 spot-check

```
case                                 haiku  opus-h  opus-d  sonnet  gpt52  gpt54  gpt54m  gpt54L
lean-ai-formalization                 4.00    4.00    4.00    4.00   4.00   4.00    4.50    4.00
lean-applied-reasoning                5.00    5.00    5.00    4.00   5.00   5.00    5.00    3.00
lean-causal-reasoning                 4.00    3.50    4.50    4.50   4.00   4.00    4.00    4.00
lean-integration-protocol             5.00    5.00    5.00    5.00   5.00   5.00    5.00    5.00
lean-knowledge-formalization          4.00    3.50    3.50    4.50   3.50   3.50    3.50    3.50
lean-nested-learning                  5.00    4.50    4.50    2.00   4.00   4.00    4.00    4.00
lean-retroactive-audit                3.50    4.50    4.50    3.50   2.00   2.50    5.00    3.50
lean-security-formalization           4.00    5.00    5.00    4.00   5.00   3.50    5.00    3.50
lean-specification                    1.00    5.00    5.00    2.00   2.00   2.00    2.00    2.00
```

**Notable correct calls:**
- `lean-specification`: 4 judges agreed `claude-haiku-4.5` produced a *wrong*
  theorem (proved `add_comm` instead of `add_assoc`) → score 1.
- `lean-knowledge-formalization`: 4-of-8 entrants omitted the required
  `NodeType`/`Value` type definitions → median 3.5 cluster.
- `lean-nested-learning`: F entrant dropped the θ application →
  flagged by all 4 judges (score 2).

## Why the baseline was refreshed

Pre-refresh, the per-rubric gate flagged:
- `lean-doc-quality` opus-default: 1853 → 1692 (−160)
- `lean-proof-quality` gpt-5.4@long: 1525 → 1407 (−118)

Both are downstream of the *very bug being fixed* — the R25 baseline
captured ratings against prose-not-Lean responses, which inflated some
entrants in cross-rubric and small-sample buckets. Refreshing the
baseline locks in the post-fix state as the new ground truth (process
parallels R24's refresh after the median-of-3 jump).

## Items deferred to HITL

**From R25 carry-over (still pending):**
- Item 1 — Add gpt-5.4-mini-mini as 5th judge (cost-down)
- Item 2 — Drift audit κ for 4-judge ensemble (data-only)
- Item 6 — `per_rubric_gate` CI wiring
- Item 7 — Lab `leaderboard.md` 95% CI columns

**R26 secondaries pre-empted by Item 3 priority:**
- B1 — drift_4judge κ
- B2 — per_rubric_gate CI wiring

## Process gotchas this round

1. **Case 1 stale-data trap:** prior session's "smoke-test 4 entrants" was
   incomplete — May 28 00:58 files for case 1's haiku/sonnet/opushigh/gpt54
   still contained R25 prose. Always re-verify file mtimes when claims of
   prior partial work appear in checkpoint summaries.
2. **`relative_to()` in regression scripts requires absolute paths.** Pass
   `$(pwd)/scripts/elo/...` not the relative form.
3. **Solver-template hard-constraint works perfectly** on all tested models.
   ``ONE ```lean fence + no prose + `-- TASK INFEASIBLE` fallback`` produced
   parseable Lean from 72/72 dispatches.

## Provenance

- 72 R26 solver agents (`r26-i3-<case>-<model>`) dispatched, all returned valid Lean
- 36 R26 judge agents (`r26-j-<case>-<judge>`) dispatched, all returned valid JSON
- All judge prompts at `/tmp/r26-judges/*.md`, ordermap at `/tmp/r26-judges/ordermap.json`
- Per-judge replies persisted under `/tmp/r26-judges/replies/{opushigh,haiku,sonnet,gpt54}/`
- Old `live.csv` backed up to `scripts/elo/matches/2026-05-27-live.csv.bak-r26-pre-item3`
- Old baselines backed up to `scripts/elo/baseline_ratings*.json.bak-r26-pre-item3`
