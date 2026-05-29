# Eval harness

Status: **active**. This directory holds the deterministic smoke runner, the
provider-neutral LLM-judge replay tools, and the multi-model match converter
used by the live Glicko-2 corpus.

The repository currently tracks 50 deterministic smoke cases, 48 adversarial
case definitions, 7 known-bad calibration corpora, and replayable solver/judge
artifacts under `judge_runs/`.

## Layout

```text
scripts/eval/
├── run_eval.py                 # deterministic smoke runner
├── baseline.py                 # committed-baseline diff/write helper
├── multi_model.py              # judge artifacts -> pairwise match CSV rows
├── baselines/smoke/            # deterministic baseline lockfile
├── cases/                      # 50 smoke case YAML files
├── graders/
│   ├── deterministic.py        # regex contains/not_contains grader
│   ├── llm_judge.py            # prompt builder + JSON parser + aggregation
│   ├── DISPATCH.md             # local-agent dispatch protocol
│   ├── prompts/judge.txt       # strict JSON judge prompt template
│   └── rubrics/*.yaml          # active judge rubrics
└── judge_runs/<case>/          # persisted solver outputs + judge JSON
```

## Deterministic smoke suite

`run_eval.py` loads `scripts/eval/cases/*.yaml`, echoes each case's canonical
answer, and validates it with the deterministic regex grader. It is a cheap
schema and regression gate, not a solver benchmark.

```bash
python3 scripts/eval/run_eval.py \
  --cases 'scripts/eval/cases/*.yaml' \
  --out ./_eval-out \
  --grader deterministic
```

Exit codes:

| Code | Meaning |
|---:|---|
| 0 | every case passed |
| 1 | at least one case failed |
| 2 | the `--cases` glob matched nothing |

## Baseline gate

The smoke suite is hard-gated against
`scripts/eval/baselines/smoke/baseline.json`.

```bash
python3 scripts/eval/baseline.py \
  --run-dir ./_eval-out \
  --baseline scripts/eval/baselines/smoke/baseline.json \
  --mode diff

python3 scripts/eval/baseline.py \
  --run-dir ./_eval-out \
  --baseline scripts/eval/baselines/smoke/baseline.json \
  --mode write
```

`diff` exits non-zero on pass-to-fail regressions or score drops. Use `write`
only after intentionally adding or changing smoke cases, then commit the
updated baseline under review.

## LLM judge replay

`graders/llm_judge.py` never calls an API. It builds judge prompts and
aggregates captured JSON replies. Model dispatch is intentionally external and
documented in `graders/DISPATCH.md`, so CI can replay durable artifacts for
free.

```bash
python3 scripts/eval/graders/llm_judge.py build \
  --rubric scripts/eval/graders/rubrics/lean-proof-quality.yaml \
  --task-file /path/to/task.md \
  --response-file /path/to/output.lean

python3 scripts/eval/graders/llm_judge.py grade \
  --rubric scripts/eval/graders/rubrics/lean-proof-quality.yaml \
  --replies scripts/eval/judge_runs/<case>/judge-*.json \
  --out scripts/eval/judge_runs/<case>/grade.json
```

Captured judge JSON files are the source of truth for rating-affecting rows.
Do not fabricate solver outputs, judge replies, or match rows.

## Calibration corpora

Known-bad corpora live under `lab/evals/known-bad/<rubric>/`. Each transcript
has persisted judge replies in `_replies/`, and `calibrate_judge.py` replays
them without model calls.

```bash
python3 scripts/eval/calibrate_judge.py check \
  --skill-dir lab/evals/known-bad/lean-proof \
  --rubric scripts/eval/graders/rubrics/lean-proof-quality.yaml \
  --min-flag-rate 0.90
```

The current active corpora cover:

| Corpus | Rubric |
|---|---|
| `applied-domain` | `applied-domain-quality` |
| `lean-doc` | `lean-doc-quality` |
| `lean-proof` | `lean-proof-quality` |
| `lean-setup-import` | `lean-setup-import-quality` |
| `lean-tactic-discipline` | `lean-tactic-discipline-quality` |
| `mathlib-lookup` | `mathlib-lookup-quality` |
| `research-synthesis` | `research-synthesis-quality` |

## Multi-model match conversion

`multi_model.py` reads co-located artifacts from `judge_runs/<case>/`:

```text
output-<entrant>.lean
judge-<entrant>.json
```

It emits pairwise rows compatible with `scripts/elo/glicko2.py`.

```bash
python3 scripts/eval/multi_model.py \
  --case-id mathlib-lookup-list-nodup \
  --run-dir scripts/eval/judge_runs/mathlib-lookup-list-nodup \
  --out scripts/elo/matches/2026-05-29-r31-gpt55-expanded.csv
```

Use `--append` only when adding audited rows to the live corpus. Keep
round-specific CSV archives for every rating-affecting batch.

## CI coverage

`.github/workflows/eval-smoke.yml` hard-gates:

| Job | Gate |
|---|---|
| `eval-smoke` | deterministic suite + baseline diff |
| `skill-conformance` | v2 schema, handoff DAG, tier, handbook links |
| `glicko2` | Glicko-2 tests, global replay, per-rubric replay, regression locks |
| `llm-judge-grader` | stored judge replay + match conversion smoke |
| `judge-calibration` | known-bad corpus flag-rate checks |

The expensive solver/judge dispatches are offline/local-agent operations; CI
checks the persisted replay artifacts and derived outputs.
