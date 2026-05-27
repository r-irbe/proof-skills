# Round 23 — single-judge multi-entrant expansion

**Date:** 2026-05-27 (j-archive)
**Archive:** `scripts/elo/example_runs/2026-05-27-j-r23/`
**Match CSV at close:** `scripts/elo/matches/2026-05-27-live.csv`
(1283 rows, +680 vs R22-close 603 rows)
**Predecessor report:** `lab/reports/R21-R22-report.md`

## TL;DR

Four new entrants joined the leaderboard in R23; three are
brand-new model families (`gpt-5.4-mini`, `gpt-5.2`,
`gpt-5.4@long`), one is a reasoning-effort variant of an existing
family (`claude-opus-4.7@default-effort`). The R22 ranked four
all remain within the 75-pt regression-tolerance band; the
default-effort opus variant lands at the top of the board.

| Rank | Player | Δ vs R22 | Status |
|---|---|---:|---|
| 1 | `claude-opus-4.7@default-effort` | NEW | new entrant |
| 2 | `claude-sonnet-4.6` | −2.4 | stable |
| 3 | `gpt-5.4` | −10.5 | stable |
| 4 | `claude-opus-4.7-high` | −10.7 | stable |
| 5 | `gpt-5.2` | NEW | new entrant |
| 6 | `gpt-5.4@long` | NEW | new entrant |
| 7 | `gpt-5.4-mini` | NEW | new entrant |
| 8 | `claude-haiku-4.5` | −7.8 | stable |

## Headline findings

1. **opus-default beats opus-high.** The default-effort opus
   variant (#1, 1670 ± 36) substantially outranks the high-effort
   variant (#4, 1498 ± 22), a 172-point gap. This is the cleanest
   refutation in this session's data of the "more reasoning effort
   ⇒ better grade" assumption. Plausible cause: terse-prompt
   convention rewards focused answers; extended chain-of-thought
   tends to over-explain. Worth a Round 24 controlled re-run with
   a paired identical prompt across both variants.
2. **gpt-5.2 ≥ gpt-5.4@long.** The smaller-prompt baseline
   (gpt-5.2, #5 at 1473) outscores the long-prompt variant of
   gpt-5.4 (#6 at 1467) by 5 points. Round 20 already established
   that verbose responses are penalised under the rubric's brevity
   axis; gpt-5.4@long replicates that finding for a different
   family.
3. **gpt-5.4-mini < gpt-5.4.** As expected. 95-point gap is
   consistent with the model-card capability delta between the
   families.

## Methodology

### Solvers (4 new entrants × 36 cases)

* `claude-opus-4.7@default-effort` — 20 cases (E1 prompt set).
* `claude-opus-4.7-high@long` — 20 cases (E1 long-effort sweep).
  Not promoted to rated entrant this round (collected as
  control data; ELO-eligible only after a paired-design re-run).
* `gpt-5.4@long` — 36 cases (C1 ≤25-sentence solver prompt).
* `gpt-5.4-mini` — 36 cases (D1-mini default prompt).
* `gpt-5.2` — 36 cases (D1-gpt52 default prompt).

Outputs at `scripts/eval/judge_runs/<case>/output-<player>.lean`.
128 new output files this round.

### Judges (single-judge, claude-opus-4.7-high)

Single canonical judge per (case, output). 128 canonical
`judge-<player>.json` files added.

Rationale for solo over ensemble: cost. Round 22 dispatched
108 judges (36 cases × 3-judge ensemble) and Round 23 needed
to judge 128 outputs against the same per-case scale; a 3-judge
ensemble would have been 384 judge dispatches plus a separate
1080 calibration replays. Solo opus-4.7-high is well-correlated
with sonnet-4.6 in R22 (κ=0.83 quadratic-weighted) so the
single-judge approximation is acceptable for an exploratory
round.

This means there is **no Cohen's κ drift audit for R23**.
Drift sensitivity will be re-established in R24 if the new
entrants are kept in the rotation.

#### Rubric resolution per case

A critical bug was caught and corrected mid-round. The first
36 judge prompts uniformly used `lean-proof-quality` regardless
of case cluster. For non-Lean cases (`ai-*`, `applied-*`, `math-*`
clusters) the prose-style responses lack any Lean code, so the
rubric scored every output at 1 → all draws → zero ELO signal.

The fix is now baked into `/tmp/round22/r23_judge/build_prompts.py`:

| Case prefix | Rubric (default) |
|---|---|
| `ai-*`, `applied-*`, `math-*` | `applied-domain-quality` |
| `lean-doc-*` | `lean-doc-quality` |
| any other `lean-*` | `lean-proof-quality` |

Explicit `ensemble_rubric:` in the case YAML overrides the
default (12 cases pin a specific rubric). Final R23 rubric mix
across the 36 cases: 23 `applied-domain-quality`, 11
`lean-proof-quality`, 2 `lean-doc-quality`.

Four `lean-*` cases produced all-1 grades across all entrants
because the R23 solver responses are prose, not Lean. These
contribute draws to the ELO; no harm but no signal.

### ELO append discipline

`scripts/eval/multi_model.py` produces every pairwise row for
each case dir it sees, but R22 already shipped the rated 4
entrants. To avoid double-counting old-vs-old pairs, R23 filters
the raw multi_model output to keep only rows where at least one
side is one of the four R23 NEW entrants. 896 raw rows → 680
filtered rows appended to the live CSV.

## Regression gate

```
claude-haiku-4.5:      1369.96 → 1399.03  Δ=+29.07  [ok]
claude-opus-4.7-high:  1528.54 → 1498.01  Δ=−30.53  [ok]
claude-sonnet-4.6:     1564.27 → 1571.92  Δ=+7.65   [ok]
gpt-5.4:               1569.80 → 1538.38  Δ=−31.42  [ok]
(new) claude-opus-4.7@default-effort: 1670.14
(new) gpt-5.2:                         1472.69
(new) gpt-5.4-mini:                    1443.34
(new) gpt-5.4@long:                    1467.19
```

All 4 baseline entrants within ±32 points (well under the
75-pt CI tolerance). PASS.

Note: `scripts/elo/baseline_ratings.json` does not include the
4 new R23 entrants. The regression gate does NOT seed them — a
new baseline lockfile should be cut once their ratings stabilise
(Round 24 plan: add at least 20 paired matches per new entrant
before promoting them to the locked baseline).

## File deltas

* Outputs: 128 new `output-*.lean` files across 36 case dirs.
* Judges: 128 new canonical `judge-*.json` files (single-pass
  metadata `_judge_pass: "single"` + `_rubric: <name>`).
* Matches CSV: +680 rows.
* Archive dir: new `scripts/elo/example_runs/2026-05-27-j-r23/`.

## Open follow-ons (Round 24 candidates)

1. **Paired opus-default vs opus-high re-run.** Replicate the
   default-vs-high gap on a controlled subset (20 cases, identical
   prompts, identical judge) before treating the gap as a stable
   finding.
2. **Promote `claude-opus-4.7-high@long` to a rated entrant.** Its
   outputs exist; needs judging then ELO-appending.
3. **Lift R23 to 3-judge ensemble.** Re-judge the 36 cases with
   haiku + sonnet for ensemble median; restore Cohen's κ surface.
4. **Refresh baseline lockfile.** Once the 4 new entrants have
   ≥200 games each (currently 140–236), promote them into
   `baseline_ratings.json`.
5. **Trim all-draw cases.** 4 `lean-*` cases produced all-1 scores
   for the R23 entrants (prose-not-Lean). Either reword the case
   prompt to demand Lean output, or move them out of the Lean
   rubric cluster.
