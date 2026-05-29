# R31 — GPT-5.5 expanded smoke-suite comparison

**Date:** 2026-05-29  
**Status:** Eight-case expansion shipped; `gpt-5.5` is no longer a one-case pilot.  
**Archive:** `scripts/elo/example_runs/2026-05-29-r31-gpt55-expanded/`  
**Per-rubric archive:** `scripts/elo/example_runs/2026-05-29-r31-gpt55-expanded-per-rubric/`  
**Evidence:** `scripts/eval/judge_runs/{case}/` for the eight R31 cases below.

## Scope

R31 expands the R29 `gpt-5.5` pilot from one case to the remaining eight R28
smoke cases:

- `lean-tactic-discipline-axiom-hygiene`
- `lean-tactic-discipline-no-decide-search`
- `lean-tactic-discipline-no-omega-abuse`
- `lean-setup-import-lakefile-basic`
- `lean-setup-import-subimport`
- `lean-setup-import-toolchain-pin`
- `mathlib-lookup-nat-div-le`
- `mathlib-lookup-topology-continuous-comp`

Each case has persisted solver outputs for the nine-entrant roster:

| Entrant | Games added |
|---|---:|
| `claude-opus-4.7-high` | 64 |
| `claude-opus-4.7@default-effort` | 64 |
| `claude-sonnet-4.6` | 64 |
| `claude-haiku-4.5` | 64 |
| `gpt-5.5` | 64 |
| `gpt-5.4` | 64 |
| `gpt-5.4@long` | 64 |
| `gpt-5.4-mini` | 64 |
| `gpt-5.2` | 64 |

Together with the R29 `mathlib-lookup-list-nodup` pilot, `gpt-5.5` now has 72
live comparison games.

## Judge method

Judging used the same blinded median-of-4 method as R29. The four judges were
`opushigh`, `haiku`, `sonnet`, and `gpt54`; aliases were mapped back only after
all judge outputs completed. For even ensemble size, the canonical score is the
mean of the two middle scores.

| Case | `claude-opus-4.7-high` | `claude-opus-4.7@default-effort` | `claude-sonnet-4.6` | `claude-haiku-4.5` | `gpt-5.5` | `gpt-5.4` | `gpt-5.4@long` | `gpt-5.4-mini` | `gpt-5.2` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `lean-tactic-discipline-axiom-hygiene` | 5.0 | 5.0 | 5.0 | 3.0 | 4.0 | 3.0 | 3.0 | 1.0 | 4.0 |
| `lean-tactic-discipline-no-decide-search` | 5.0 | 4.0 | 3.0 | 3.5 | 3.5 | 4.0 | 4.0 | 1.0 | 4.0 |
| `lean-tactic-discipline-no-omega-abuse` | 5.0 | 5.0 | 4.0 | 4.0 | 2.5 | 4.0 | 4.0 | 1.0 | 4.0 |
| `lean-setup-import-lakefile-basic` | 4.5 | 5.0 | 3.0 | 2.0 | 5.0 | 3.0 | 4.0 | 1.0 | 4.0 |
| `lean-setup-import-subimport` | 3.0 | 5.0 | 2.0 | 4.0 | 4.0 | 4.5 | 4.5 | 3.0 | 4.5 |
| `lean-setup-import-toolchain-pin` | 4.5 | 5.0 | 4.5 | 4.0 | 4.0 | 4.5 | 5.0 | 2.0 | 3.0 |
| `mathlib-lookup-nat-div-le` | 4.0 | 4.0 | 4.0 | 4.0 | 4.0 | 4.0 | 4.0 | 4.0 | 4.0 |
| `mathlib-lookup-topology-continuous-comp` | 4.0 | 4.0 | 4.0 | 3.0 | 2.5 | 3.0 | 3.0 | 3.0 | 4.0 |

## Rating result

R31 added 288 pairwise rows to
`scripts/elo/matches/2026-05-27-live.csv`, bringing the live corpus to 1,554
rows. Glicko-2 replay produced:

| Rank | Player | Rating | RD | 95% CI | Games |
|---|---|---:|---:|---|---:|
| 1 | `claude-opus-4.7@default-effort` | 1694.7 | 30.9 | [1633, 1757] | 240 |
| 2 | `claude-sonnet-4.6` | 1551.5 | 21.7 | [1508, 1595] | 489 |
| 3 | `claude-opus-4.7-high` | 1543.2 | 21.4 | [1500, 1586] | 489 |
| 4 | `gpt-5.5` | 1536.7 | 42.3 | [1452, 1621] | 72 |
| 5 | `gpt-5.4` | 1516.1 | 21.9 | [1472, 1560] | 393 |

`gpt-5.5` moved from the provisional R29 one-case lead to a more credible
mid-top placement: rank 4 overall, with a much narrower but still larger RD
than the long-running entrants.

## Validation

- Deterministic smoke suite: 50/50 cases passed.
- Deterministic baseline diff: no hard or score regressions; nine newer cases
  remain reported as baseline-new rather than blockers.
- Global Glicko-2 regression gate: passed against `baseline_ratings.json`.
- Per-rubric Glicko-2 regression gate: passed against
  `baseline_ratings_per_rubric.json`.
- APM package validation: passed.
- `git diff --check`: passed.

