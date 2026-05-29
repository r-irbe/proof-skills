# Glicko-2 leaderboard and match corpus

Status: **active**. `glicko2.py` is the authoritative rating pipeline for live
model comparisons. `elo.py` remains only as a legacy vanilla-ELO dashboard
helper for quick local experiments.

The live corpus is `matches/2026-05-27-live.csv` and currently contains 1,554
evidence-backed pairwise rows. Every row must trace to persisted solver output
and judge JSON artifacts under `scripts/eval/judge_runs/`.

## Which tool to use

| Task | Tool |
|---|---|
| Release leaderboard with uncertainty bands | `glicko2.py` |
| Per-rubric leaderboard replay | `per_rubric_elo.py` |
| Regression gate against lockfiles | `check_regression.py` |
| Synthetic sanity-data generation | `gen_sample.py` |
| Legacy single-number dashboard | `elo.py` |

## Match CSV schema

```csv
case_id,model_a,model_b,winner,reasoning_effort_a,reasoning_effort_b
```

`winner` is `a`, `b`, or `draw`. Empty effort fields are treated as the model's
default effort. Effort-tagged variants are distinct players; for example
`gpt-5.4` and `gpt-5.4@long` are separate entrants.

## Glicko-2 replay

```bash
python3 scripts/elo/glicko2_test.py

python3 scripts/elo/glicko2.py \
  --matches scripts/elo/matches/2026-05-27-live.csv \
  --out scripts/elo/example_runs/2026-05-29-r31-gpt55-expanded
```

Outputs:

| File | Meaning |
|---|---|
| `ratings.json` | machine-readable rating, RD, volatility, games, and 95% CI per player |
| `leaderboard.md` | sorted Markdown table |

The 95% interval is `[rating - 2*RD, rating + 2*RD]`.

## Per-rubric replay

Per-rubric ratings join match rows back to case YAML labels. Smoke cases use
`ensemble_rubric:`; adversarial cases may use `grader:` values such as
`lean-proof-quality`.

```bash
python3 scripts/elo/per_rubric_elo.py \
  --matches scripts/elo/matches/2026-05-27-live.csv \
  --cases scripts/eval/cases \
  --cases lab/evals/adversarial-cases \
  --out scripts/elo/example_runs/2026-05-29-r35-rubric-map-fix-per-rubric
```

Sparse buckets are expected to have wider uncertainty and should be interpreted
as coverage diagnostics until they have enough cases and games.

## Regression gates

Global and per-rubric lockfiles protect against accidental leaderboard drift.

```bash
python3 scripts/elo/check_regression.py \
  --current scripts/elo/example_runs/2026-05-29-r31-gpt55-expanded/ratings.json

python3 scripts/elo/check_per_rubric_regression.py \
  --archive scripts/elo/example_runs/2026-05-29-r31-gpt55-expanded-per-rubric
```

The CI workflow runs the same checks. Update the lockfiles only when a
rating-affecting batch has been audited and intentionally accepted.

## Current release archives

| Archive | Contents |
|---|---|
| `example_runs/2026-05-29-r31-gpt55-expanded/` | Latest global R31 replay |
| `example_runs/2026-05-29-r31-gpt55-expanded-per-rubric/` | Latest per-rubric R31 replay |
| `matches/2026-05-29-r31-gpt55-expanded.csv` | R31-only pairwise rows |
| `matches/2026-05-27-live.csv` | Live cumulative corpus |

Historical dated archives remain in place for auditability, but active docs and
leaderboards should cite the latest R31 directories above.

## Data hygiene

Do not hand-edit rating-affecting rows without preserving the artifact trail:

1. Persist `output-<entrant>.lean` under `scripts/eval/judge_runs/<case>/`.
2. Persist `judge-<entrant>.json` with the exact judge score and rationale.
3. Generate rows through `scripts/eval/multi_model.py`.
4. Archive the batch-specific CSV before appending to the live corpus.
5. Re-run global and per-rubric Glicko-2, then update lockfiles only after the
   regression gates pass for an intentional change.
