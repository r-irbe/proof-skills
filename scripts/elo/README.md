# ELO calculator for model A/B evals (v0)

Status: **v0 (advisory)**. Single-file Python, stdlib only, no pandas. Lives under
`scripts/` because we are still figuring out whether ELO is the right
aggregation for our pairwise judge outputs.

## What it does

Given a CSV of pairwise model comparisons (one row per match, with a winner
field), compute a classic Elo rating per `(model, reasoning_effort)` tuple —
each tuple is its own player. Emit:

- `ratings.json` — machine-readable ratings + game counts
- `leaderboard.md` — sorted Markdown table
- top-5 to stdout

## Formula

Standard Elo, updated after every match in CSV order:

```
E_a = 1 / (1 + 10 ** ((R_b - R_a) / 400))
R_a' = R_a + K * (S_a - E_a)
```

Constants for this prototype:

| Parameter | Value | Notes |
|-----------|-------|-------|
| `K`       | 32    | Standard hobby/chess default. Tunable via `--k`. |
| `R0`      | 1500  | Initial rating for any unseen player. |
| Draw      | `S = 0.5` for both sides | |

Each `(model, reasoning_effort)` pair gets its own rating. So
`claude-opus-4.7@high` and `claude-opus-4.7` (no effort tag) are separate
players, and meeting each other is a legitimate match.

## CSV schema

```
case_id, model_a, model_b, winner, reasoning_effort_a, reasoning_effort_b
```

`winner ∈ {a, b, draw}`. Empty effort fields are treated as "no effort tag"
(the model name alone becomes the player id).

## How to run

```bash
python3 elo.py --matches sample_matches.csv --out out/
```

Optional flags: `--k 16`, `--r0 1500`.

To regenerate the synthetic dataset:

```bash
python3 gen_sample.py --out sample_matches.csv --per-pair 8
```

## Self-test output

Run on the bundled `sample_matches.csv` (120 matches = 8 per pair × 15 pairs,
6 players, seed 42):

```
$ python3 elo.py --matches sample_matches.csv --out out/
Processed 120 matches across 6 players (K=32, R₀=1500).
Top 5:
  1. claude-opus-4.7@high                      1666.0  (40 games)
  2. claude-opus-4.7                           1662.9  (40 games)
  3. claude-sonnet-4.6                         1493.4  (40 games)
  4. gpt-5.4                                   1420.5  (40 games)
  5. gpt-5-mini                                1388.4  (40 games)
```

Full leaderboard (`out/leaderboard.md`):

| Rank | Player | Rating | Games |
|-----:|--------|-------:|------:|
| 1 | claude-opus-4.7@high | 1666.0 | 40 |
| 2 | claude-opus-4.7 | 1662.9 | 40 |
| 3 | claude-sonnet-4.6 | 1493.4 | 40 |
| 4 | gpt-5.4 | 1420.5 | 40 |
| 5 | gpt-5-mini | 1388.4 | 40 |
| 6 | claude-haiku-4.5 | 1368.8 | 40 |

### Does it recover the constructed ordering?

The synthetic data was generated from these hand-picked true ratings:

| Player | True rating |
|--------|------------:|
| claude-opus-4.7@high | 1800 |
| claude-opus-4.7      | 1700 |
| claude-sonnet-4.6    | 1600 |
| gpt-5.4              | 1500 |
| gpt-5-mini           | 1490 |
| claude-haiku-4.5     | 1350 |

Constructed order: **opus-high > opus > sonnet > gpt-5.4 ≈ gpt-5-mini > haiku**.
Recovered order: **opus-high > opus > sonnet > gpt-5.4 > gpt-5-mini > haiku**.
Rank order matches exactly. The gpt-5.4 / gpt-5-mini gap (true Δ=10 Elo) is
overstated as ~32 Elo by the prototype — expected, since 8 head-to-head
matches between players that close is well within sampling noise.

The opus-high / opus pair (true Δ=100) collapses to Δ≈3 in the recovered
ratings. That's because they only play each other 8 times directly; most of
their other 32 games are against weaker players, where both win
overwhelmingly and Elo updates are small. This is a known limitation of
running Elo on a small, partly-disconnected match graph and is worth
flagging if we move past prototype.

## Sensitivity

All runs use the same `sample_matches.csv` (or a prefix of it) and seed 42.

### K-factor: K=16 vs K=32 (full 120 matches)

| Player | K=32 | K=16 | Δ |
|--------|-----:|-----:|--:|
| claude-opus-4.7@high | 1666.0 | 1622.2 | −43.8 |
| claude-opus-4.7      | 1662.9 | 1598.5 | −64.4 |
| claude-sonnet-4.6    | 1493.4 | 1494.3 | +0.9  |
| gpt-5.4              | 1420.5 | 1447.1 | +26.6 |
| gpt-5-mini           | 1388.4 | 1430.6 | +42.2 |
| claude-haiku-4.5     | 1368.8 | 1407.3 | +38.5 |

Rank order is identical. Spread (top minus bottom) shrinks from 297 Elo to
215 Elo: K=16 dampens every update by half, so 120 matches isn't enough to
push ratings as far from R₀. K=32 gives crisper separation here; K=16 would
be the safer choice once we have many more matches and care about stability
over reactivity.

### Sample size: 50 vs 100 vs 120 matches (K=32)

| Player | 50 matches | 100 matches | 120 matches | True |
|--------|-----------:|------------:|------------:|-----:|
| claude-opus-4.7@high | 1618.0 | 1705.3 | 1666.0 | 1800 |
| claude-opus-4.7      | 1527.2 | 1586.3 | 1662.9 | 1700 |
| claude-sonnet-4.6    | 1486.5 | 1488.2 | 1493.4 | 1600 |
| gpt-5.4              | 1472.4 | 1445.6 | 1420.5 | 1500 |
| gpt-5-mini           | 1437.7 | 1401.2 | 1388.4 | 1490 |
| claude-haiku-4.5     | 1458.1 | 1373.4 | 1368.8 | 1350 |

- At **50 matches** (~3 games per pair) the ordering is broken: haiku ends
  up above gpt-5-mini, and gpt-5.4 sinks below sonnet's expected gap. Top-1
  is right; the rest is noise.
- At **100 matches** the full ordering is recovered.
- At **120 matches** the ordering is the same as 100, with slightly tighter
  separation at the top.

Practical floor for this 6-player setup looks like ~80–100 matches (≈ 5–7
per pair). Below that, individual rank flips are common; above that, ratings
keep drifting but the ordering is stable.

## Known limitations (prototype)

1. **Order-dependent.** Elo updates in sequence, so shuffling the CSV gives
   different ratings. Fine for prototyping; for a real eval we'd want either
   Bradley–Terry MLE or multiple-shuffle averaging.
2. **Sparse graph problem.** With few direct head-to-heads between top
   players, gaps between them get understated (see opus-high vs opus above).
3. **No uncertainty.** Ratings come out as point estimates. No confidence
   intervals, no "X is significantly better than Y" test.
4. **Draw handling is naive.** A draw always splits 0.5/0.5 regardless of
   rating gap. Fine; just noted.

## Files

- `elo.py` — the calculator. Pure `compute_elo(matches, k, r0)` plus a CLI.
- `gen_sample.py` — synthetic data generator (deterministic, seed 42).
- `sample_matches.csv` — 120-match dataset used for the self-test.
- `out/ratings.json`, `out/leaderboard.md` — last run's outputs.
