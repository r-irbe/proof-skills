# Lab — Calibration & Evaluation Corpora

This directory holds the **lab** material: calibration transcripts that ground
the LLM-judge graders, design notes for the ELO/multi-model evaluation
pipeline, and the orchestration recipes for live judging.

It is **complementary to** (not a replacement for) `scripts/eval/`:

| Location | Purpose | Audience |
| --- | --- | --- |
| `lab/evals/known-bad/` | Calibration corpora — handcrafted bad answers that anchor the LLM judge's lower rubric scores. | Rubric authors, calibration runs. |
| `lab/evals/known-bad/_replies/` | Captured model replies for each known-bad transcript — used to anchor judge calibration empirically. | Calibration aggregation. |
| `lab/design/` | Pipeline design docs (eval framework, ELO, multi-model runner, zettelkasten, cluster workflow). Reconstructed in R27 audit. See `lab/design/README.md` for the index. | Maintainers extending the eval pipeline. |
| `scripts/eval/` | Executable pipeline: graders, dispatchers, aggregators. | CI + Round-N pass runners. |
| `scripts/eval/cases/` | YAML case registry — one file per smoke-eval case. | CI smoke run. |
| `scripts/eval/graders/rubrics/` | YAML rubrics referenced by both calibration and live judging. | Both. |
| `scripts/eval/judge_runs/` | Live multi-model run artifacts (`output-<model>.lean`, `judge-<model>.json`). | Round-N aggregations. |
| `scripts/elo/matches/` | Pairwise match CSVs (one row per (case, A, B) pair). | Glicko-2 input. |
| `scripts/elo/example_runs/` | Archived Glicko-2 outputs. | Leaderboard trend tracking. |

## The 6 calibration clusters

| Cluster | Rubric file (`scripts/eval/graders/rubrics/`) | Transcripts |
| --- | --- | --- |
| `lean-proof` | `lean-proof-quality.yaml` | Adversarial proofs: omega/linarith abuse, banned tactics, decide-as-search, sorry-in-comment camouflage. |
| `lean-doc` | `lean-doc-quality.yaml` | Doc/spec failures: empty docs, contradictory blueprints, hallucinated Mathlib anchors. |
| `lean-setup-import` | `lean-setup-import-quality.yaml` | Build failures: fabricated modules, syntactically broken `lakefile`, deep internal imports. |
| `mathlib-lookup` | `mathlib-lookup-quality.yaml` | Lookup failures: Coq-style names, wrong namespace/signature, fabricated lemmas. |
| `research-synthesis` | `research-synthesis-quality.yaml` | Synthesis failures: fabricated citations, single-perspective takes, misattribution. |
| `applied-domain` | `applied-domain-quality.yaml` | Domain failures: GDPR mis-application, fabricated CVE references, single-option recommendations with no trade-off. |

## End-to-end workflow

```
                            ┌─────────────────────────┐
                            │  scripts/eval/cases/    │  case registry
                            │     <case>.yaml         │  (deterministic + smoke)
                            └────────────┬────────────┘
                                         │
                ┌────────────────────────▼─────────────────────────┐
                │  Solver dispatch (per case × per model)          │
                │  → output-<model>.lean                           │
                │  saved under scripts/eval/judge_runs/<case>/      │
                └────────────────────────┬─────────────────────────┘
                                         │
                ┌────────────────────────▼─────────────────────────┐
                │  Judge dispatch (per case, randomized A/B/C       │
                │  ordering, opus-only or ensemble)                 │
                │  → judge-<model>.json                             │
                └────────────────────────┬─────────────────────────┘
                                         │
                ┌────────────────────────▼─────────────────────────┐
                │  scripts/eval/multi_model.py                      │
                │  → appends pairwise rows to                       │
                │     scripts/elo/matches/<run>.csv                 │
                └────────────────────────┬─────────────────────────┘
                                         │
                ┌────────────────────────▼─────────────────────────┐
                │  scripts/elo/glicko2.py                           │
                │  → scripts/elo/example_runs/<date>/               │
                │       ratings.json + leaderboard.md               │
                └───────────────────────────────────────────────────┘
```

## Calibration workflow

The known-bad corpus serves two functions:

1. **Authoring anchor** — when designing a rubric, sample 1-2 transcripts
   per intended score level (1 through 5) and confirm that the rubric
   wording maps each transcript to the intended score.

2. **Live anchor** — periodically re-run the LLM judge on the known-bad
   corpus (`scripts/eval/graders/llm_judge.py` + `lab/evals/known-bad/<cluster>/*.transcript.md`)
   and verify each transcript still receives ≤2/5. This catches rubric drift
   over time and across judge model versions.

The `_replies/` sub-directories under each cluster hold real model replies
generated against the same prompts, used to anchor the calibration empirically
(see `reports/_calibration/.../ensemble-2026-05-27.json` for the latest
captured ensemble).

## Adding a new known-bad transcript

```bash
# 1. Pick the cluster and create a transcript file:
$EDITOR lab/evals/known-bad/<cluster>/my-new-bad-case.transcript.md

# 2. The transcript follows the format:
cat > lab/evals/known-bad/<cluster>/my-new-bad-case.transcript.md <<'TXT'
---
expected_score_band: 1-2   # what the judge should produce
failure_mode: "fabricated-citation"  # short tag for cross-referencing
---

# Prompt
<the prompt that elicited the bad answer>

# Bad response
<the actual bad response a model produced or one you handcrafted>
TXT

# 3. Add 1-2 anchor replies under _replies/ (optional but recommended):
mkdir -p lab/evals/known-bad/<cluster>/_replies/my-new-bad-case
$EDITOR lab/evals/known-bad/<cluster>/_replies/my-new-bad-case/claude-haiku-4.5.json

# 4. Re-run the calibration ensemble to verify the rubric scores it ≤2:
python3 scripts/eval/graders/llm_judge.py \
    --rubric scripts/eval/graders/rubrics/<cluster>-quality.yaml \
    --transcript lab/evals/known-bad/<cluster>/my-new-bad-case.transcript.md
```

## Adding a new live-eval case

```bash
# 1. Register the case in scripts/eval/cases/<case-id>.yaml
$EDITOR scripts/eval/cases/my-new-case.yaml

# 2. Decide which rubric covers it; update scripts/eval/case_rubric_map.yaml
#    if it's not auto-routed.

# 3. Dispatch solvers (model fleet × case):
#    See scripts/eval/dispatch_solver.md for the orchestration recipe.

# 4. Dispatch judges (1 per case, randomized A/B/C order):
#    See scripts/eval/dispatch_judge.md for the orchestration recipe.

# 5. Aggregate to ELO matches:
python3 scripts/eval/multi_model.py \
    --runs-dir scripts/eval/judge_runs \
    --case my-new-case \
    --rubric scripts/eval/graders/rubrics/<rubric>.yaml \
    --out scripts/elo/matches/<date>-live.csv \
    --draw-threshold 0.15 \
    --append

# 6. Re-run Glicko-2:
python3 scripts/elo/glicko2.py \
    --matches scripts/elo/matches/<date>-live.csv \
    --out scripts/elo/example_runs/<date>/
```

## See also

- `references/AUTHORING.md` — how to author a new v2 skill.
- `scripts/eval/multi_model.py` — pairwise CSV aggregator (canonical API).
- `scripts/elo/glicko2.py` — Glicko-2 rating implementation.
- `scripts/elo/check_regression.py` — ELO regression CI gate (Round 19+).
- `scripts/eval/case_rubric_map.yaml` — canonical case → rubric mapping.

## Live evaluation history

The harness has carried six successive evaluation rounds. Each round
appends rows to `scripts/elo/matches/2026-05-27-live.csv` and archives
the resulting Glicko-2 leaderboard under
`scripts/elo/example_runs/<date>-<letter>/`.

| Round | Archive | Games/entrant | New rows | What landed |
|---|---|---:|---:|---|
| R16-d | `2026-05-27-d/` | 12 | +15 | Initial multi-model bench (5 cases × 3 models). |
| R18-e | `2026-05-27-e/` | 84 | +108 | Breadth suite (36 phase-18 cases × 3 models). |
| R19-adv `2026-05-27-f-adv/` | 90 | +18 | 15 adversarial cases (ambiguous / IDK / known-failure). |
| **R19-B `2026-05-27-g/`** | **186** | **+108** | **3-judge B1 ensemble re-judging of the 36 phase-18 cases.** |

Leaderboard trajectory:

| Round | Sonnet 4.6 | Opus 4.7-high | Haiku 4.5 |
|---|---:|---:|---:|
| R16-d | 1281 ±138 | 1683 ±138 | 1537 ±138 |
| R18-e | 1584 ±56 | 1524 ±56 | 1392 ±56 |
| R19-adv | 1566 ±48 | 1542 ±48 | 1392 ±48 |
| **R19-B (current)** | **1571 ±32** | **1547 ±32** | **1382 ±33** |

CIs tightened from ±138 to ±32 as the match volume grew from 36 to
558 rows (3 entrants × 186 games / 2 sides per game).

## Drift audit (Cohen's κ, Round 19)

3-judge ensemble on 108 (case, model) rating pairs, quadratic-weighted
κ on the 5-point rubric:

| Pair | κ | Exact agree | Agree ±1 |
|---|---:|---:|---:|
| opus_R18 vs sonnet_B1 | 0.777 | 63.0% | 95.4% |
| haiku_B1 vs sonnet_B1 | 0.687 | 53.7% | 84.3% |
| opus_R18 vs haiku_B1  | 0.537 | 38.9% | 75.0% |

Substantial agreement between opus and sonnet judges; haiku is the
outlier (consistently more lenient). Confirms the R18 leaderboard's
sonnet-leader result is not a self-bias artifact. Report:
`reports/_drift_audit/2026-05-27-b1-ensemble-kappa.md`.

## Reproducing a round

```bash
# 1. Pick a corpus of cases:
ls scripts/eval/cases/*.yaml | head -10

# 2. For each (case, model) pair, dispatch a solver
#    (use the Copilot CLI `task` tool — see
#     scripts/eval/graders/DISPATCH.md for the orchestration recipe).
#    Saves output to scripts/eval/judge_runs/<case>/output-<model>.lean

# 3. Build judge prompts (one per case, randomized A/B/C ordering):
python3 scripts/eval/multi_model.py build-judge-prompts \
    --runs-dir scripts/eval/judge_runs \
    --cases scripts/eval/cases/ \
    --rubric scripts/eval/graders/rubrics/lean-proof-quality.yaml \
    --out-dir _judge_prompts_workspace/<round-id> \
    --seed 42

# 4. Dispatch judge agents (one per prompt — or N per prompt for ensemble).
#    Save raw JSON replies as judge-<model>.json (or @b1-<judge>.json
#    for ensemble runs).

# 5. Aggregate per-case medians to pairwise ELO rows:
python3 scripts/eval/multi_model.py aggregate-rows \
    --runs-dir scripts/eval/judge_runs \
    --cases scripts/eval/cases/ \
    --out scripts/elo/matches/<date>-live.csv \
    --append

# 6. Refresh Glicko-2 and verify regression gate:
python3 scripts/elo/glicko2.py \
    --matches scripts/elo/matches/<date>-live.csv \
    --out scripts/elo/example_runs/<date>-<letter>/

python3 scripts/elo/check_regression.py \
    --current scripts/elo/example_runs/<date>-<letter>/ratings.json
# CI fails if any entrant drops > 75 points vs baseline_ratings.json.
```

## Round runbook (template)

Each round is summarised in `plan.md` of the maintainer's session. The
canonical structure:

1. **Phase A** — quick wins / housekeeping (no LLM dispatch).
2. **Phase B** — judge ensemble work.
3. **Phase C** — adversarial / case-corpus expansion.
4. **Phase D** — solver-side experiments (long-prompt, reasoning-effort,
   new model family).
5. **Phase E** — aggregate / commit / superrepo bump / next HITL form.

Round 20 (in progress) adds gpt-5.4 as a fourth solver model and
fixes 11 lean-* cases that were applying `lean-proof-quality` to
prose-only tasks (annotation `ensemble_rubric: lean-doc-quality`
added to each affected YAML).

