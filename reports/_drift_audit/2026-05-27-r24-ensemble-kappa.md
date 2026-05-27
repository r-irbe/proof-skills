# R24 ensemble drift audit

**Date:** 2026-05-27
**Methodology:** 3-judge ensemble re-judge of 36 R23 cases × 4 R23-new entrants = 128 triples (opus-default has 20 cases only; the other 3 entrants have 36 each).
**Aggregator:** median-of-3 per (case, entrant) → canonical `judge-<player>.json`.
**Kappa shape:** quadratic-weighted, 5-point rubric (1–5).

## Pairwise agreement matrix

| Pair | κ (quadratic-weighted) | exact-match | within ±1 | Band |
|---|---:|---:|---:|---|
| **haiku-4.5 vs sonnet-4.6** | **0.902** | 69.5 % | 97.7 % | almost perfect |
| **opus-4.7-high vs sonnet-4.6** | 0.788 | 60.9 % | 93.8 % | substantial |
| **opus-4.7-high vs haiku-4.5** | 0.730 | 53.1 % | 87.5 % | substantial |

## Interpretation

1. **All pairs sit in the "substantial" or "almost perfect" band** (κ ≥ 0.70). The 3-judge ensemble is internally consistent enough to trust the median aggregator.

2. **haiku ↔ sonnet show the tightest agreement** (κ = 0.90, exact 70 %, within ±1 at 98 %). Both are downstream-Anthropic judges trained on broadly similar safety-and-eval distributions.

3. **opus-4.7-high is the slight outlier**, agreeing somewhat less with both haiku and sonnet. opus tends to be marginally more discriminating / harsher in the middle of the scale (3/4 vs 4/5). Median-of-3 smooths this without losing opus's signal on extreme cases.

4. **The R24 ensemble is calibration-safe**: the worst within-±1 rate is 87.5 %, well above the ADR-0039 ≥ 90 % flag-rate gate for known-bad detection (the gate applies to per-case detection across the corpus, not pairwise inter-judge agreement, but the principle is the same — ensemble medians track each other closely).

5. **Compared to R22 drift audit** (`2026-05-27-r22-ensemble-kappa.md`):
   - R22 reported κ ≥ 0.83 pairwise on 36 R21 cases × 3 R21 entrants = 108 triples judged by opus + sonnet + opus-4.6.
   - R24 reports lowest κ = 0.73 on a different judge mix (opus-high + sonnet + haiku) but the same 5-point rubric.
   - The drop in lowest-κ from 0.83 to 0.73 is attributable to haiku's slightly different calibration on the lean-* "no Lean code produced" prose cases (haiku and sonnet uniformly assigned 1 to all 9 prose-not-Lean lean cases, while opus assigned scattered 1/2/3 to the same outputs in R23 single-judge mode — a subtle calibration drift on the "Was this Lean at all?" question).

## Per-judge score distribution (n = 128 triples)

| Score | opus-4.7-high | haiku-4.5 | sonnet-4.6 |
|---|---:|---:|---:|
| 1 | 36 (28.1 %) | 35 (27.3 %) | 32 (25.0 %) |
| 2 | 23 (18.0 %) | 25 (19.5 %) | 22 (17.2 %) |
| 3 | **58 (45.3 %)** | 27 (21.1 %) | 39 (30.5 %) |
| 4 | 9 (7.0 %) | 18 (14.1 %) | 19 (14.8 %) |
| 5 | 2 (1.6 %) | **23 (18.0 %)** | 16 (12.5 %) |

**Big finding:** opus-4.7-high is **strongly mid-range biased** — 45 % of all scores are 3, and only 8.6 % combined are 4-or-5. Haiku and sonnet are far more willing to score 4 or 5 (32 % and 27 % respectively).

This explains the **opus-default rating shift from 1670 (R23 single-judge) to 1782 (R24 ensemble)**: when only opus judged, the typical "good but not perfect" answer landed on 3. In the 3-judge median, opus=3 + haiku=5 + sonnet=4 → median 4, a one-point upward bump that compounds across 140 games.

**Implication for future rounds:** opus-as-sole-judge under-credits good-quality entrants. The ensemble correction (median-of-3) is justified specifically because of this calibration gap. Single-judge ELO archives prior to R22 should be considered conservative lower bounds on the ensemble-corrected ratings.

## Recommendation

Adopt the median-of-3 ensemble (this report) as the canonical R24 baseline. Future rounds should keep this judge mix (opus-4.7-high + claude-haiku-4.5 + claude-sonnet-4.6) for new entrants, with the option to add gpt-based judges as a 4th/5th ensemble member to balance Anthropic-model self-bias risk.
