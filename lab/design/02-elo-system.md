# 02 — ELO / Glicko-2 system

**Status:** RECONSTRUCTED stub (R27 audit). Documents current pipeline behaviour.

## 1. Why Glicko-2

Glicko-2 was chosen over plain ELO because:
- Per-player rating deviation (RD) is tracked and shrinks with games played.
- Volatility σ captures recent rating consistency.
- 95% confidence intervals on ratings are first-class, surfaced in `leaderboard.md` and `leaderboard.html`.
- The `τ` system constant (default 0.5) controls how fast ratings respond to surprising results; small enough to keep stable rankings, large enough to react to a bug-fix round.

## 2. Pairwise comparison protocol

### 2.1 One match row per (case, entrant_A, entrant_B)

For each case, for each unordered pair of entrants A, B with judged scores `s_A`, `s_B`:

- Normalise each score to `[0, 1]` via `score / rubric.max_scale`.
- Compute `Δ = s_A − s_B`.
- Emit `winner ∈ {a, b, draw}`:
  - `|Δ| < draw_threshold` (default 0.15) → `draw`
  - `Δ ≥ draw_threshold` → `a`
  - `Δ ≤ -draw_threshold` → `b`

### 2.2 Draw-threshold tuning

`0.15` in normalized space corresponds to `0.75` on the 1–5 rubric scale (i.e., a 4 vs 4.5 is a draw; a 3 vs 4 is a win). This was chosen to match the granularity of `median-of-4-mean-mid` (which produces half-integer scores).

### 2.3 Reasoning-effort suffixes

Entrants with `@<effort>` suffixes (e.g., `claude-opus-4.7@default-effort`, `gpt-5.4@long`) are treated as **distinct players**. The CSV columns `reasoning_effort_a` and `reasoning_effort_b` preserve the suffix; `model_a` / `model_b` hold the bare model name.

## 3. Glicko-2 period model

- Period size: 100 games (per `glicko2.py --period-size`).
- Each match is processed in the next period; ratings update at period boundary.
- Initial RD = 350.0, initial σ = 0.06.
- Players unseen for a period have RD increase per Glicko-2 rules.

## 4. Per-rubric stratification

`per_rubric_elo.py` re-runs Glicko-2 over subsets of `live.csv` bucketed by the case's rubric metadata (read from the case YAML; see `lab/design/01-eval-framework.md §2`). Smoke cases use `ensemble_rubric:` and adversarial cases may use `grader:` values such as `lean-proof-quality`. Used to surface per-domain skill differences masked by the global aggregate.

R27 made smoke-case bucketing explicit; the active smoke suite now has 50 cases with `ensemble_rubric:` set, so per-rubric replay no longer relies on fallback heuristics for smoke rows. R35 extended the metadata loader to include nested adversarial-case YAML and `grader:` rubric labels before falling back to ID heuristics.

## 5. Regression gates

See `lab/design/01-eval-framework.md §5`.

## 6. Archive layout

```
scripts/elo/example_runs/<DATE>-<letter>-<sprint-tag>/
  ratings.json/
    ratings.json
    leaderboard.md
  per_rubric/
    <rubric>-matches.csv
    <rubric>/
      ratings.json
      leaderboard.md
    per-rubric-summary.md
```

Each round (R21, R22, ...) writes a new archive directory. Baselines are refreshed from one of these archives via `check_regression.py --refresh --current <archive>/ratings.json`.
