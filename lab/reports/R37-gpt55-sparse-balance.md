# R37 — GPT-5.5 sparse-balance pass

**Date:** 2026-05-29  
**Status:** Sparse-bucket backfill shipped.  
**Archive:** `scripts/elo/example_runs/2026-05-29-r37-gpt55-sparse-balance/`  
**Per-rubric archive:** `scripts/elo/example_runs/2026-05-29-r37-gpt55-sparse-balance-per-rubric/`  
**Match rows:** `scripts/elo/matches/2026-05-29-r37-gpt55-sparse-balance.csv`

## Scope

R37 adds `gpt-5.5` evidence to five under-covered smoke cases:

| Case | Rubric | Canonical `gpt-5.5` score |
|---|---|---:|
| `lean-doc-improvement-smoke` | `lean-doc-quality` | 5 |
| `lean-doc-requirements-smoke` | `lean-doc-quality` | 5 |
| `lean-setup-import` | `lean-setup-import-quality` | 4 |
| `lean-quality-no-sorry` | `lean-tactic-discipline-quality` | 5 |
| `mathlib-lookup-finset` | `mathlib-lookup-quality` | 5 |

Only rows involving `gpt-5.5` were appended, so R37 balances sparse evidence
without duplicating old-vs-old matches that were already represented in the
live corpus.

## Judging

The five new outputs use the same median-of-4 judge roster as R31:
`claude-opus-4.7-high`, `claude-haiku-4.5`, `claude-sonnet-4.6`, and
`gpt-5.4`. Per-judge JSON artifacts are persisted beside each output under
`scripts/eval/judge_runs/<case>/`.

`lean-doc-requirements-smoke` required a correction pass after an early draft
included a non-existent theorem name in a commented skeleton. The final artifact
is a requirements-only template with explicit downstream `#check` obligations
and no fabricated proof dependency.

## Rating result

R37 appended 25 pairwise rows to
`scripts/elo/matches/2026-05-27-live.csv`, bringing the live corpus to 1,579
rows. `gpt-5.5` now has 97 live games across 14 smoke cases.

| Rank | Player | Rating | RD | 95% CI | Games |
|---|---|---:|---:|---|---:|
| 1 | `claude-opus-4.7@default-effort` | 1689.7 | 30.8 | [1628, 1751] | 242 |
| 2 | `gpt-5.5` | 1604.5 | 36.4 | [1532, 1677] | 97 |
| 3 | `claude-sonnet-4.6` | 1546.6 | 21.6 | [1503, 1590] | 494 |
| 4 | `claude-opus-4.7-high` | 1541.0 | 21.3 | [1498, 1584] | 494 |
| 5 | `gpt-5.4` | 1514.2 | 21.9 | [1470, 1558] | 395 |

The global jump is driven by two strong doc-quality wins plus solid scores in
the sparse setup, tactic-discipline, and Mathlib lookup buckets. The uncertainty
band is still wider than the long-running entrants, but the evidence is no
longer concentrated in one rubric.

## Per-rubric effect

| Rubric | Rows after R37 | `gpt-5.5` rank | `gpt-5.5` games |
|---|---:|---:|---:|
| `lean-doc-quality` | 90 | 1 | 16 |
| `lean-setup-import-quality` | 114 | 3 | 27 |
| `lean-tactic-discipline-quality` | 114 | 5 | 27 |
| `mathlib-lookup-quality` | 120 | 3 | 27 |

These buckets remain sparse compared with `applied-domain-quality` and
`lean-proof-quality`, so R37 should be read as a balancing step rather than a
final per-rubric verdict.

## Validation

- Deterministic smoke suite: 50/50 cases passed.
- Deterministic baseline diff: no hard, score, positive, new, or dropped-case
  regressions.
- Global Glicko-2 regression gate: passed.
- Per-rubric Glicko-2 regression gate: passed.
- APM package validation: passed.
- Skill conformance hard gate: passed.
- `git diff --check`: passed.
