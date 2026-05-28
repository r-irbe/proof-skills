# R22 baseline rows: rationale for leaving as-is

**Date:** 2026-05-27
**Round:** R25 item 8
**Decision:** keep 604 R22 baseline rows in `2026-05-27-live.csv`
unchanged; do **not** re-judge under the R24 ensemble methodology.

## Context

R22 (the "baseline" set) consists of 604 pairwise match rows derived
from 4-judge ensemble grading of cases that span the original R18+
calibrated suite plus the R19 adversarial cases. Those rows underpin
the Glicko-2 baseline lockfile (`baseline_ratings.json`) and serve as
the floor for the CI regression gate.

R24 introduced a **different** ensemble: median-of-3 across
`{claude-opus-4.7-high, claude-haiku-4.5, claude-sonnet-4.6}` over
the R23-NEW 36-case slice (128 entrant-case triples). The R23 ELO
archive (single-judge opus-high) was re-judged under that R24 mix.

A reasonable question at R25 close-out: "should the R22 rows also be
re-judged under the R24 ensemble for methodological uniformity?"

## Answer: no. Three reasons.

### 1. Different judge mix, different case slice

The R22 rows include cases that no longer appear in the R23/R24
working set (e.g. several `adv-*` adversarial cases and early
`lean-doc-*` smoke cases). Re-judging requires either
(a) preserving the original outputs (we do — `output-*.lean`
files are co-located) and dispatching the new ensemble, OR
(b) skipping cases with missing outputs. Option (a) costs
~ 604 / 3 (avg pair-per-case) × 3 judges ≈ 600 fresh judge
dispatches with no first-order improvement to the leaderboard
order (R24 already lifted those R22 baselines by ≤ ±64 pts after
the broader R24 refresh).

### 2. Archive lineage protection

`baseline_ratings.json` cites `source_archive:
2026-05-27-k-r24` and `created_round: R24`. The lockfile commitment
is that this exact match set produced those ratings; modifying the
underlying CSV invalidates the lockfile's audit trail. The
regression gate's whole value proposition is *bit-identical
reproducibility*: rebuild the archive, re-emit the ratings, expect
the same numbers. Re-judging R22 rows without rotating the source
archive breaks that contract.

### 3. The R22 → R24 deltas are already documented

For each of the 4 R22 baseline entrants (haiku-4.5, opus-4.7-high,
sonnet-4.6, gpt-5.4), R24 brought a Δ within ±64 ELO points — well
inside the gate tolerance of 75 pt. Those Δs ARE the result of the
new R24 ensemble methodology applied to the R23-NEW slice; the R22
rows did not need updating to produce them. The system already
internalised the methodology shift via Glicko-2 period processing
of the new R23-NEW matches; older R22 matches are simply
unchanged history.

## Practical implication for future rounds

Treat R22 the same way you treat the original 41 deterministic
smoke cases: it is **frozen baseline data**. New rounds add new
matches; they do not overwrite history. This preserves Glicko-2's
period semantics (each round = one period; ratings evolve forward).

If a future round needs methodological consistency across the
entire history (e.g. switch to median-of-5 ensemble at scale),
the right pattern is to:

1. Dispatch the new ensemble on archived `output-*.lean` files.
2. Write a **new** match CSV (`2026-05-27-live-Y.csv`).
3. Cut a new archive (`2026-05-27-Y/`).
4. Bump the lockfile to point at the new archive with the new
   methodology tag.
5. Document the migration in `reports/_archive/r{Y}-methodology-
   refresh.md`.

R22 stays as it is. The R25 leaderboard is computed on the
1 284-row `live.csv` (604 R22 + 680 R24 ensemble) as the
canonical match-history snapshot.

## See also

- `lab/leaderboard.md` (current rankings)
- `lab/reports/R24-report.md` §"Methodology" (R22 ensemble vs R24)
- `scripts/elo/baseline_ratings.json` (lockfile referencing R24
  archive)
- `reports/_drift_audit/2026-05-27-r24-ensemble-kappa.md`
  (judge-agreement evidence for the methodology shift)
- `scripts/elo/example_runs/2026-05-27-l-r25-per-rubric/` (R25
  item 4 — per-rubric Glicko-2 split confirming the R22 baselines
  hold across all 3 rubrics)
