# ELO match input CSVs

This directory holds the **input** CSVs consumed by `elo.py` and
`glicko2.py` — one row per pairwise match. Each file represents
one batch of matches (e.g. a single eval run, a nightly suite, a
human-curated bench).

## Provenance

Match rows are produced by `scripts/eval/multi_model.py` from
`(output-<player>.lean, judge-<player>.json)` pairs under
`scripts/eval/judge_runs/<case>/`. The LLM-judge dispatch (the
expensive step) is documented in
`scripts/eval/graders/DISPATCH.md`.

## Schema

```
case_id, model_a, model_b, winner, reasoning_effort_a, reasoning_effort_b
```

- `winner ∈ {a, b, draw}`
- Empty effort columns mean "no `@effort` suffix on the player id"

This is the same shape as `../sample_matches.csv` (synthetic data
from `../gen_sample.py`). Real-world match CSVs live here.

## Naming

`<YYYY-MM-DD>-<label>.csv`, e.g.:

- `2026-05-27-live.csv` — first live W8/W9 demo (3 entrants × 1 case
  = 3 pairs; opus-4.7-high & sonnet-4.6 tied 5/5, haiku-4.5 lost on
  missing `-- goal:` narration)

## Running Glicko-2

```sh
python3 scripts/elo/glicko2.py \
    --matches scripts/elo/matches/<file>.csv \
    --out ./_glicko-out
```
