# R35 rubric-map fix

Date: 2026-05-29

## Summary

R35 fixes the per-rubric Glicko-2 metadata loader so adversarial cases in
`lab/evals/adversarial-cases/` participate in rubric bucketing. Before this
fix, `per_rubric_elo.py` loaded only `scripts/eval/cases`, so every `adv-*`
match row missed YAML metadata and fell through the ID fallback path.

Global ratings are unchanged. This is a methodology correction for the
per-rubric split only.

## Implementation

- `scripts/elo/per_rubric_elo.py` now accepts repeated `--cases` inputs.
- Each `--cases` input may be a directory, a YAML file, or a quoted glob.
- Directory inputs are traversed recursively with `*.yaml`, which covers the
  nested adversarial corpus layout.
- Rubric resolution order is now:
  1. `ensemble_rubric`
  2. `grader` when it already names a `*-quality` rubric
  3. skill / case-id fallback
  4. `applied-domain-quality`
- Malformed case YAML and unmapped `adv-*` rows produce warnings instead of
  silent fallback.

## Row-count delta

The live corpus has 1,554 pairwise rows. The per-rubric row-count delta is:

| Rubric | Before: smoke metadata only | After: smoke + adversarial metadata | Delta |
|---|---:|---:|---:|
| `applied-domain-quality` | 859 | 844 | -15 |
| `lean-doc-quality` | 74 | 74 | 0 |
| `lean-proof-quality` | 288 | 297 | +9 |
| `lean-setup-import-quality` | 111 | 111 | 0 |
| `lean-tactic-discipline-quality` | 111 | 111 | 0 |
| `mathlib-lookup-quality` | 111 | 117 | +6 |

Adversarial rows before R35: 45/45 fell into `applied-domain-quality`.

Adversarial rows after R35:

| Rubric | Rows | Case IDs |
|---|---:|---|
| `applied-domain-quality` | 30 | `adv-ambiguous-prompt-applied`, `adv-contradictory-constraints`, `adv-divide-by-zero-stats`, `adv-fabricated-cve`, `adv-idk-probe-ai-future`, `adv-misapplied-clt`, `adv-non-pd-covariance`, `adv-overdetermined-system`, `adv-prove-collatz`, `adv-restated-question` |
| `lean-proof-quality` | 9 | `adv-empty-prompt-lean`, `adv-prompt-injection-in-error`, `adv-prove-unprovable` |
| `mathlib-lookup-quality` | 6 | `adv-fabricated-mathlib-anchor`, `adv-lean3-vs-lean4-naming` |

## Baseline refresh

Refreshed archive:

```bash
python3 scripts/elo/per_rubric_elo.py \
  --matches scripts/elo/matches/2026-05-27-live.csv \
  --cases scripts/eval/cases \
  --cases lab/evals/adversarial-cases \
  --out scripts/elo/example_runs/2026-05-29-r35-rubric-map-fix-per-rubric
```

Refreshed baseline:

- `scripts/elo/baseline_ratings_per_rubric.json`
- source archive:
  `scripts/elo/example_runs/2026-05-29-r35-rubric-map-fix-per-rubric`
- reason: baseline now protects the corrected adversarial-case rubric mapping.

## Dispatch recommendation

Use the two-root command in CI and local replays:

```bash
python3 scripts/elo/per_rubric_elo.py \
  --matches scripts/elo/matches/2026-05-27-live.csv \
  --cases scripts/eval/cases \
  --cases lab/evals/adversarial-cases \
  --out <archive>
```

Do not refresh the global baseline for this change: match rows and global
ratings did not change.
