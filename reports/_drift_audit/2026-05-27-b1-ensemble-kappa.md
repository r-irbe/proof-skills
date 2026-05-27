# Round 19 — 3-judge B1 ensemble drift audit

**Date:** 2026-05-27
**Corpus:** 36 phase18 smoke cases × 3 solvers = 108 (case, model) rating pairs
**Judges:** opus_R18 (claude-opus-4.7-high), haiku_B1 (claude-haiku-4.5),
sonnet_B1 (claude-sonnet-4.6) — all judging the same outputs through
the same `lean-proof-quality` rubric in randomized ABC order.

## Pairwise quadratic-weighted Cohen's κ (5-point rubric)

| Pair | κ (quad) | Exact agree | Agree ±1 |
|---|---:|---:|---:|
| opus_R18 vs sonnet_B1 | **0.777** | 63.0% | 95.4% |
| haiku_B1 vs sonnet_B1 | **0.687** | 53.7% | 84.3% |
| opus_R18 vs haiku_B1  | **0.537** | 38.9% | 75.0% |

**Interpretation (Landis & Koch 1977 bands):** opus/sonnet → *substantial*
agreement; haiku/sonnet → *substantial* agreement; opus/haiku →
*moderate* agreement. The two stronger models converge; haiku is the
outlier (consistently more lenient: more 4s and 5s where opus/sonnet
score 3).

## What this rules out

R18 leaderboard had `sonnet > opus` by ~60 ELO. A common worry was
"sonnet judges favor sonnet solvers." With κ(opus_R18, sonnet_B1)=0.78
and 95.4% within ±1, the 3-judge ensemble confirms the R18 ranking
is **not** a self-bias artifact — opus and sonnet judges substantially
agree on the same outputs. The B1 ensemble re-judging shifted the
leaderboard by < 14 ELO per entrant (within the regression-gate
tolerance of 75).

## What this surfaces

Haiku as a judge is **moderate-only**. Down-weighting haiku in
future ensembles (or using minority-veto with haiku's score ignored
when it disagrees by ≥2 with both opus and sonnet) would tighten
the calibration without losing breadth.

## Match volume after B1 ingestion

- ELO match rows: 171 (post-R19-adv) → **279** (after B1 ensemble = +108)
- Games per entrant: 84 → **186** — surpasses the 100-game design
  target. CIs tightened from ±56 to ±32.

## Final leaderboard (Glicko-2, `2026-05-27-g/`)

| Rank | Player | Rating | RD | 95% CI | Games |
|---|---|---:|---:|---|---:|
| 1 | `claude-sonnet-4.6`     | 1571.0 | 32.2 | [1507, 1635] | 186 |
| 2 | `claude-opus-4.7-high`  | 1547.0 | 31.7 | [1484, 1610] | 186 |
| 3 | `claude-haiku-4.5`      | 1381.5 | 33.1 | [1315, 1448] | 186 |

Sonnet vs opus CIs still overlap (gap 24 points; combined CI band
~125 points wide) → not statistically significant at n=186. The
trend has now persisted across R18 + R19 with two independent judge
pools, increasing the prior that sonnet genuinely leads on the
breadth suite, but a 4-judge ensemble + reasoning-effort sweep is
needed for separation.
