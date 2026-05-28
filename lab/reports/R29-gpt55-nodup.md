# R29 — GPT-5.5 nodup pilot

**Date:** 2026-05-28
**Status:** One-case live comparison shipped; `gpt-5.5` added to the leaderboard.
**Archive:** `scripts/elo/example_runs/2026-05-27-p-r29-gpt55-nodup/`
**Evidence:** `scripts/eval/judge_runs/mathlib-lookup-list-nodup/`

## Scope

R29 staged the first `gpt-5.5` comparison against the existing live roster on a
single R28 smoke case: `mathlib-lookup-list-nodup`.

Entrants:

| Entrant | Games added |
|---|---:|
| `claude-opus-4.7-high` | 8 |
| `claude-opus-4.7@default-effort` | 8 |
| `claude-sonnet-4.6` | 8 |
| `claude-haiku-4.5` | 8 |
| `gpt-5.5` | 8 |
| `gpt-5.4` | 8 |
| `gpt-5.4@long` | 8 |
| `gpt-5.4-mini` | 8 |
| `gpt-5.2` | 8 |

The one-case setup intentionally keeps cost low while proving that the pipeline
can dispatch, judge, aggregate, and rate `gpt-5.5` without fabricating data.

## Mathlib correction

The case was corrected to the current Mathlib declaration:

```lean
theorem List.nodup_append' {l₁ l₂ : List α} :
    Nodup (l₁ ++ l₂) ↔ Nodup l₁ ∧ Nodup l₂ ∧ Disjoint l₁ l₂
```

The stale unprimed name `List.nodup_append` is forbidden, but the forbidden
regex had to be changed from `List\.nodup_append\b` to
`List\.nodup_append(?!')\b`. In regex syntax, `\b` matches before an apostrophe,
so the old pattern incorrectly rejected the valid `List.nodup_append'` name.

## Judge method

Each entrant has a persisted solver output and canonical judge JSON under the
case directory. Scores use median-of-4 aggregation with the current four-judge
mix; for even ensemble size, the canonical score is the mean of the two middle
scores.

| Entrant | Aggregated score |
|---|---:|
| `claude-opus-4.7-high` | 2.0 |
| `claude-opus-4.7@default-effort` | 2.0 |
| `claude-sonnet-4.6` | 4.0 |
| `claude-haiku-4.5` | 2.0 |
| `gpt-5.5` | 3.5 |
| `gpt-5.4` | 4.0 |
| `gpt-5.4@long` | 4.0 |
| `gpt-5.4-mini` | 2.0 |
| `gpt-5.2` | 2.0 |

`scripts/eval/multi_model.py` was fixed to preserve fractional judge scores:
median-of-4 aggregation can produce `.5` values, and truncating them to `int`
would distort pairwise outcomes.

## Rating result

36 pairwise rows were appended to
`scripts/elo/matches/2026-05-27-live.csv`, then Glicko-2 was refreshed.

| Rank | Player | Rating | RD | 95% CI | Games |
|---|---|---:|---:|---|---:|
| 1 | `gpt-5.5` | 1730.6 | 121.3 | [1488, 1973] | 8 |
| 2 | `claude-opus-4.7@default-effort` | 1695.4 | 34.7 | [1626, 1765] | 176 |
| 3 | `claude-sonnet-4.6` | 1567.6 | 24.4 | [1519, 1616] | 425 |
| 4 | `gpt-5.4` | 1525.8 | 24.7 | [1476, 1575] | 329 |
| 5 | `claude-opus-4.7-high` | 1506.3 | 23.9 | [1458, 1554] | 425 |

`gpt-5.5` leads in this archive, but it has only 8 games from one case and a
very wide CI. Treat this as a pipeline-admission result, not a settled model
ranking.

## Verification

- Deterministic smoke suite: 50/50 cases passed.
- Global regression gate: passed for
  `scripts/elo/example_runs/2026-05-27-p-r29-gpt55-nodup/ratings.json`.
- Per-rubric Glicko-2 and per-rubric regression gate: passed; the
  `mathlib-lookup-quality` bucket is new/sparse and therefore illustrative.

## Follow-ups

- Dispatch the remaining R28 smoke cases with `gpt-5.5` included.
- Re-run per-rubric Glicko-2 after `mathlib-lookup-quality` has more than a
  one-case pilot.
- Keep the `List.nodup_append'` case as a regression guard for Mathlib API
  lookup drift.
