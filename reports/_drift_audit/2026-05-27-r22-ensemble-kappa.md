# Round 22 — 3-judge B1 R22 ensemble drift audit

**Date:** 2026-05-27
**Corpus:** 36 R21 smoke cases × gpt-5.4 solver, 3-judge ensemble
**Judges:** opus_R20 (claude-opus-4.7-high), sonnet_R21 (claude-sonnet-4.6), opus_R22 (claude-opus-4.6)

## Pairwise quadratic-weighted Cohen's κ (5-point rubric)

| Pair | κ (quad) | Exact agree | Agree ±1 |
|---|---:|---:|---:|
| opus_R20 vs sonnet_R21 | **0.834** | 66.7% | 97.2% |
| opus_R20 vs opus_R22 | **0.841** | 69.4% | 97.2% |
| sonnet_R21 vs opus_R22 | **0.933** | 80.6% | 100.0% |

## Interpretation (Landis & Koch 1977 bands)

Sub-0.40 = poor/fair; 0.40–0.60 = moderate; 0.60–0.80 = substantial; >0.80 = almost perfect.

## What this confirms

The R22 3rd judge (claude-opus-4.6) was added to test whether the 2-judge median (opus_R20 + sonnet_R21) from R21 was stable. Of 36 cases, 7 shifted score (mostly +1: opus-4.6 was systematically slightly less harsh than the prior pair). The 4-entrant Glicko-2 leaderboard moved within the 75-pt regression tolerance: gpt-5.4 drifted from 1569.8 → 1548.9 (Δ=-20.9), all others within ±37.

## Match volume after R22 ingestion

388 → 604 rows (+216 from 36 cases × 6 pairwise pairs).
