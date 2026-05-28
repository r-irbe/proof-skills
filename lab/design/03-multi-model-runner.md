# 03 — Multi-model runner

**Status:** RECONSTRUCTED stub (R27 audit).

## 1. Entrant roster

As of R26, the live roster (in `scripts/elo/baseline_ratings.json`) is:

| Player | Model | Effort suffix |
|---|---|---|
| `claude-opus-4.7@default-effort` | Claude Opus 4.7 | default-effort |
| `claude-opus-4.7-high` | Claude Opus 4.7 (high reasoning) | — |
| `claude-sonnet-4.6` | Claude Sonnet 4.6 | — |
| `claude-haiku-4.5` | Claude Haiku 4.5 | — |
| `gpt-5.4` | GPT-5.4 | — |
| `gpt-5.4@long` | GPT-5.4 (long-context variant) | long |
| `gpt-5.4-mini` | GPT-5.4 mini | — |
| `gpt-5.2` | GPT-5.2 | — |

Adding a new entrant requires (a) extending the dispatch loop in the round's `lab/.r<N>-*-solver-prompts/` workspace, (b) running a backfill against existing cases, (c) re-running ELO with the new entrant present.

## 2. Solver-prompt template (R26-Item-3-validated)

For Lean cases the hard-constraint template is:

```
<task description>

Write ONLY a single Lean 4 code block:

```lean
<your code>
```

DO NOT write any prose, commentary, or explanation outside the code block.
If the task is infeasible, output the single line `-- TASK INFEASIBLE` inside the code block.
```

This template returned valid Lean from 72/72 dispatches across 9 cases × 8 entrants in R26 Item 3. Without it, prior rounds (R23–R25) collected prose for 9 lean-* cases and burned ~305 noise pairwise rows in `live.csv`.

The 9 solver prompts that validated the template are persisted at `lab/.r26-item3-solver-prompts/`.

## 3. Judge ensemble

Current ensemble (median-of-4):
1. `claude-opus-4.7-high`
2. `claude-haiku-4.5`
3. `claude-sonnet-4.6`
4. `gpt-5.4`

Aggregation: mean of the two middle values when ensemble size is even (`_judge_agg: median-of-4-mean-mid`). Stored alongside `_individual_scores` and `_judges` in each canonical `judge-<entrant>.json` for reproducibility.

R25 carry-over considers adding `gpt-5.4-mini-mini` as a 5th judge for cost-down median-of-5.

## 4. Dispatch loop

Solver and judge dispatches use the agent harness. Per-round agent-id conventions:

- Solvers: `r<N>-<phase>-<case-prefix>-<model-suffix>` (e.g. `r26-i3-laif-haiku`)
- Judges: `r<N>-j-<case-prefix>-<judge-suffix>` (e.g. `r26-j-laif-opushigh`)

Case prefixes (R26 lean-*): `laif/lar/lcr/lip/lkf/lnl/lra/lsf/ls`.
Model suffixes: `haiku/sonnet/opushigh/opus/gpt54/gpt54mini/gpt52/gpt54long`.

## 5. Blind labelling for judges

Per case, judge prompts shuffle the 8 entrant responses into A–H with a per-case seed (`r26-<case_id>-judge-<date>`). The label→entrant map is persisted at `<workspace>/ordermap.json` and used at demux time to write per-entrant scores.

This blinding prevents judges from being biased by entrant identity.

## 6. Cost / latency notes

- 4 judges × 9 cases = 36 dispatches takes ~2 minutes wall-clock in parallel (R26 observed).
- 8 entrants × 9 cases = 72 solver dispatches takes ~90 seconds in parallel.
- No rate-limit hits observed with 9 simultaneous background agents per wave.
