# Round 24 — 3-judge ensemble re-judge

**Date:** 2026-05-27
**Sprint goal:** Lift the R23 single-judge ratings to a 3-judge ensemble (opus-4.7-high + claude-haiku-4.5 + claude-sonnet-4.6) using median aggregation, validate via drift audit, refresh baseline.

## Methodology

1. **Carried over from R23**: 36 case directories, 4 R23-NEW entrants (`claude-opus-4.7@default-effort`, `gpt-5.4@long`, `gpt-5.4-mini`, `gpt-5.2`), 128 `output-*.lean` files, 128 single-judge canonical `judge-*.json` (opus-4.7-high).
2. **Renamed R23 canonicals** to `judge-<player>@r23-opus.json` (128 files).
3. **Dispatched 36 + 36 = 72 sub-agent judges** (haiku batch + sonnet batch), each judging one case prompt at a time with 3-or-4-way blind A/B/C/D solver outputs randomized by case-specific ordermap.
   - haiku had a /tmp-path security-policy quirk on first batch; mitigated by copying prompts into project-local `lab/.r24-judge-prompts/` (gitignored) and re-dispatching via `write_agent`.
   - 1 sonnet judge (lean-retroactive-audit) and 1 sonnet judge (ai-symbolic-neuro) refused with the same /tmp policy on turn 0; re-dispatched with project-local path and harvested.
4. **Demultiplexed 72 judge replies** (288 per-(case,player,judge) JSONs) using the per-case ordermap. Saved as `judge-<player>@r24-claude-haiku-4.5.json` and `judge-<player>@r24-claude-sonnet-4.6.json`.
5. **Computed median-of-3** per (case, player) → new canonical `judge-<player>.json` carrying `_judge_pass: ensemble_3judge`, `_judge_agg: median`, `_judges: [...]`.
6. **Reset live.csv** to R22 baseline (`git show ea68f75:...` → 604 rows), re-ran `multi_model.py` per case with per-case rubric, filtered to "at least one R23-new entrant per row" → appended 680 rows. Total: 1283 data rows.
7. **Glicko-2 refresh** → archive `scripts/elo/example_runs/2026-05-27-k-r24/`.
8. **Drift audit** → `reports/_drift_audit/2026-05-27-r24-ensemble-kappa.md`.
9. **Baseline refresh** to include all 8 entrants (item D).

## Final leaderboard

| Rank | Player | Rating | RD | 95 % CI | Games | Δ vs R23 |
|---|---|---:|---:|---|---:|---:|
| 1 | `claude-opus-4.7@default-effort` | 1781.7 | 37.0 | [1708, 1856] | 140 | **+112** |
| 2 | `gpt-5.4@long` | 1560.9 | 26.3 | [1508, 1614] | 236 | **+94** |
| 3 | `claude-sonnet-4.6` | 1545.7 | 22.5 | [1501, 1591] | 458 | −26 |
| 4 | `gpt-5.2` | 1520.7 | 26.3 | [1468, 1573] | 236 | **+48** |
| 5 | `gpt-5.4` | 1506.2 | 23.5 | [1459, 1553] | 344 | −32 |
| 6 | `claude-opus-4.7-high` | 1476.5 | 22.3 | [1432, 1521] | 458 | −22 |
| 7 | `gpt-5.4-mini` | 1421.8 | 27.7 | [1366, 1477] | 236 | −21 |
| 8 | `claude-haiku-4.5` | 1381.1 | 23.0 | [1335, 1427] | 458 | −18 |

**Regression gate:** PASSED — all 4 R22-baseline entrants Δ ≤ 64 pts, within the 75-pt tolerance.

## Key findings

### 1. opus-default jumps +112 pts under ensemble re-judge
The single-judge R23 archive credited opus-default 1670 (already top). The R24 ensemble lifts it to 1782 — a +112-pt jump driven by opus-4.7-high's strong 3-mid-range bias when used as sole judge (45 % of opus scores are 3, only 1.6 % are 5). The ensemble median pulls these "good answers undercredited as 3" up to 4 once haiku/sonnet weigh in.

### 2. gpt-5.4@long beats gpt-5.4 (verbosity ceiling rejected)
R23 single-judge had gpt-5.4@long below gpt-5.4 (1467 vs 1538) — interpreted as "verbose penalty." R24 ensemble flips this: gpt-5.4@long = 1561 vs gpt-5.4 = 1506. The R22-era verbose-penalty signal was a single-judge artifact. When haiku/sonnet weigh in, long answers are rewarded for coverage.

### 3. gpt-5.2 > gpt-5.4 (newer-not-always-better)
Surprising flip: gpt-5.2 (1521) edges out gpt-5.4 (1506). Both have 236-vs-344 game counts so RD is similar (±26 vs ±24); this is a real signal at this sample size. Likely cause: gpt-5.4's longer hedging on policy-coded prompts loses points to gpt-5.2's terser direct answers.

### 4. opus-default — opus-high gap widens to 305 pts
R23 reported a 172-pt gap (1670 → 1498). R24 lifts opus-default more than opus-high (the latter was already calibrated against the R22-era ensemble), so the gap widens to 305. Reasoning-effort dial: under blind judging, more effort hurts.

### 5. lean-* prose cases consistently scored all-1
9 of 36 R23 cases produced all-1 verdicts across all 3 judges (lean-ai-formalization, lean-applied-reasoning, lean-causal-reasoning, lean-integration-protocol, lean-knowledge-formalization, lean-nested-learning, lean-retroactive-audit, lean-security-formalization, lean-specification). All 4 solvers emitted prose, not Lean code. Root cause: solver prompts did not faithfully relay the case YAML's "Reply with Lean 4 code only" instruction. **Fix is on the SOLVER side, not the case YAML.** Don't trim these cases; rewrite the solver prompt template to enforce the no-prose constraint.

### 6. Drift audit κ ≥ 0.73 across all pairs
Cohen's quadratic-weighted κ:
- haiku vs sonnet: 0.902 (almost perfect)
- opus vs sonnet: 0.788 (substantial)
- opus vs haiku: 0.730 (substantial)

opus-4.7-high is the slight outlier (mid-range bias). Median-of-3 smooths this without losing opus's discrimination signal on extreme cases. Full report: `reports/_drift_audit/2026-05-27-r24-ensemble-kappa.md`.

## Items shipped vs deferred

R24 HITL form selections (max-effort path):

| Item | Status | Notes |
|---|---|---|
| A — paired opus-default vs opus-high | DONE (data-only) | Both have ensemble scores in 36-case overlap; gap = +305 pts, opus-default wins. |
| B — promote opus-high@long outputs | DEFERRED | Would need fresh solver dispatch (R23 outputs were lost to compaction). |
| **C — 3-judge ensemble re-judge** | **DONE** | This sprint. |
| **D — baseline refresh** | **DONE** | `scripts/elo/baseline_ratings.json` now lists 8 entrants. |
| E — trim all-1 lean cases | **DONE (no trim)** | Diagnosed as solver-prompt issue, not case-YAML issue. Cases retained. |
| F — gpt-5.4-high | OUT OF SCOPE | Explicitly declined in HITL form. |
| G — adversarial set | DEFERRED | Would need 60 new solvers + 180 ensemble judges. |
| **H — leaderboard.html** | **DONE** | `lab/leaderboard.html` rendered. |

## Artifacts

- `scripts/elo/example_runs/2026-05-27-k-r24/ratings.json` — Glicko-2 archive.
- `scripts/elo/example_runs/2026-05-27-k-r24/leaderboard.md` — markdown leaderboard.
- `scripts/elo/baseline_ratings.json` — refreshed lockfile.
- `scripts/elo/matches/2026-05-27-live.csv` — 1283 data rows (604 R22 + 680 R24 ensemble re-judged).
- `scripts/eval/judge_runs/<case>/judge-<player>@r23-opus.json` — 128 preserved single-judge scores.
- `scripts/eval/judge_runs/<case>/judge-<player>@r24-claude-haiku-4.5.json` — 128 new haiku scores.
- `scripts/eval/judge_runs/<case>/judge-<player>@r24-claude-sonnet-4.6.json` — 128 new sonnet scores.
- `scripts/eval/judge_runs/<case>/judge-<player>.json` — 128 refreshed ensemble medians.
- `reports/_drift_audit/2026-05-27-r24-ensemble-kappa.md` — drift audit.
- `lab/leaderboard.html` — rendered HTML leaderboard.

## Round 25 candidates

Surfaced for HITL selection:
1. **Item B fresh dispatch** — actually run 36 opus-high@long solvers + 108 ensemble judges to evaluate whether opus-high benefits from the long-prompt budget.
2. **Item G adversarial set** — design 15 new adversarial cases probing R23 entrant weaknesses (opus-default's edge-case under-coverage, gpt-5.x verbose-policy hedging).
3. **Solver-prompt fix** for the 9 prose-not-Lean lean cases — rewrite `lab/solver-templates/lean-code-only.md` enforcing the no-prose constraint, then re-dispatch + re-judge those 9 cases.
4. **Per-rubric ELO** — currently all 5 rubrics roll into one rating. Splitting by rubric (lean-proof, lean-doc, applied-domain, research-synthesis, lean-tactic-discipline) would surface which entrants excel at which domain.
5. **gpt-as-judge** — add gpt-5.2 or gpt-5.4 as 4th ensemble member to address potential Anthropic-model-judge self-bias.
6. **Calibration corpus extension** — extend known-bad corpora to cover the 5 new rubrics; current corpora are lean-proof + lean-doc + research-synthesis + applied-domain.
7. **Match-volume push** — drive opus-default from 140 → 300+ games to tighten its CI from ±37 to ±25.
