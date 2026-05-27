# Lab — Calibration & Evaluation Corpora

This directory holds the **lab** material: calibration transcripts that ground
the LLM-judge graders, design notes for the ELO/multi-model evaluation
pipeline, and the orchestration recipes for live judging.

It is **complementary to** (not a replacement for) `scripts/eval/`:

| Location | Purpose | Audience |
| --- | --- | --- |
| `lab/evals/known-bad/` | Calibration corpora — handcrafted bad answers that anchor the LLM judge's lower rubric scores. | Rubric authors, calibration runs. |
| `lab/evals/known-bad/_replies/` | Captured model replies for each known-bad transcript — used to anchor judge calibration empirically. | Calibration aggregation. |
| `lab/design/` | Long-form design docs for ELO, multi-model dispatch, rubric authoring. | Maintainers extending the eval pipeline. |
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
