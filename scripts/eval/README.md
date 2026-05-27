# Eval runner (v0, advisory)

> **Status:** v0. Lives under `scripts/eval/` and is **not** wired
> into the real eval pipeline in `scripts/` or `lab/evals/runners/`. The
> point is to validate the contract — YAML cases → deterministic grader →
> JSONL + Markdown — before promoting it.

## What it is

A ~300-LOC Python 3 script that:

1. Loads YAML test cases (PyYAML if installed; a tiny regex fallback parser
   otherwise — enough for the case schema below).
2. "Invokes" the model. For now this is a literal `echo` of
   `input.expected_output_substring` — a placeholder so the grading path
   has realistic text to chew on. The real runner will dispatch to a
   background agent (see `lab/design/03-multi-model-runner.md`).
3. Grades the output with a **deterministic** regex grader:
   * every pattern in `expected.contains[]` must match;
   * no pattern in `expected.not_contains[]` may match.
4. Writes `<out>/<case_id>.json` per case and `<out>/summary.md` overall.
5. Returns a non-zero exit if any case failed — drop-in regression check.

## Layout

```
scripts/eval/
├── README.md                ← this file
├── run_eval.py              ← CLI entry point
├── graders/
│   ├── __init__.py
│   └── deterministic.py     ← regex grader
└── cases/
    ├── lean-proof-omega.yaml
    ├── lean-setup-import.yaml
    ├── mathlib-lookup-finset.yaml
    ├── lean-mwe-minimize.yaml
    └── lean-quality-no-sorry.yaml
```

## Case schema

Minimal subset assumed by both the YAML loader fallback and the grader:

```yaml
id: lean-quality-no-sorry          # stable identifier (also used as filename)
title: "Quality gate: no sorry"     # human-readable
skill: lean-quality                 # which skill bucket this exercises
difficulty: trivial                 # informational
input:
  prompt: |                         # what we would send a model
    Prove 1 + 1 = 2 in Lean 4.
  expected_output_substring: |      # PROTOTYPE placeholder for model output
    theorem one_plus_one : (1 : Nat) + 1 = 2 := by
      rfl
expected:
  contains:                         # all regexes must match (multi-line)
    - "theorem\\s+one_plus_one"
    - "by\\s+rfl"
  not_contains:                     # none of these regexes may match
    - "\\bsorry\\b"
    - "\\badmit\\b"
grader: deterministic               # informational; selected via CLI flag
tags: [lean, quality, lint]
```

When `lab/design/01-eval-framework.md` lands, the canonical schema there
will supersede this. The runner only depends on `id`, `skill`,
`input.expected_output_substring`, and `expected.{contains,not_contains}`.

## How to run

From this directory:

```bash
python3 run_eval.py \
    --cases 'cases/*.yaml' \
    --out ./out/eval-test \
    --grader deterministic
```

> **Why `./out/...` and not `/tmp/...`?** The dev environment running
> this prototype rejects writes to `/tmp`. Use any path you like in your
> own shell — `--out /tmp/eval-test` works fine on a normal machine.

Exit codes:

| code | meaning                                       |
| ---- | --------------------------------------------- |
| 0    | every case passed                             |
| 1    | at least one case failed                      |
| 2    | the `--cases` glob matched nothing            |

## Self-test output

Running the runner against its own cases:

```
$ python3 run_eval.py --cases 'cases/*.yaml' --out ./out/eval-test --grader deterministic
[PASS] lean-mwe-minimize  score=1.00
[PASS] lean-proof-omega  score=1.00
[PASS] lean-quality-no-sorry  score=1.00
[PASS] lean-setup-import  score=1.00
[PASS] mathlib-lookup-finset  score=1.00

5/5 passed → out/eval-test/summary.md
```

`out/eval-test/summary.md`:

```markdown
# Eval run summary

- **Cases run:** 5
- **Passed:** 5
- **Failed:** 0
- **Pass rate:** 100.0%

| Case | Skill | Grader | Score | Result |
| --- | --- | --- | --- | --- |
| `lean-mwe-minimize` | lean-mwe | deterministic | 1.00 | ✅ PASS |
| `lean-proof-omega` | lean-proof | deterministic | 1.00 | ✅ PASS |
| `lean-quality-no-sorry` | lean-quality | deterministic | 1.00 | ✅ PASS |
| `lean-setup-import` | lean-setup | deterministic | 1.00 | ✅ PASS |
| `mathlib-lookup-finset` | mathlib-lookup | deterministic | 1.00 | ✅ PASS |
```

A negative-control case (`contains: [goodbye]` but output is `hello`)
correctly exits `1` and renders a `## Failures` section in `summary.md`
listing the missing pattern.

## Baseline gate (`baseline.py`)

The deterministic suite is hard-gated against a committed baseline
at `scripts/eval/baselines/smoke/baseline.json`. This is a minimal
subset of the design in `lab/design/01-eval-framework.md §5`,
covering only pass/score (no cost, latency, or LLM-judge fields —
those are unblocked when W8 Phase 2 lands).

```sh
# After run_eval.py has populated ./out/eval-test/
python3 scripts/eval/baseline.py --run-dir ./out/eval-test --mode diff

# Refresh the baseline after intentionally expanding the case set
python3 scripts/eval/baseline.py --run-dir ./out/eval-test --mode write
# (then commit scripts/eval/baselines/smoke/baseline.json under PR review)
```

The diff exits 1 on:
- **hard regression** (baseline passed → run failed), or
- **score regression** (baseline score > run score on a passing case).

It reports (but does not block on) *positive regressions* — cases
that were red in the baseline and are now green. Refresh the baseline
to lock the improvement in.

This script powers the `eval-smoke` CI workflow
(`.github/workflows/eval-smoke.yml`) which runs on every push +
pull request and blocks merges on regressions.

## What's deliberately missing

This is a prototype; the following belong in the real runner, not here:

- multi-model dispatch / background-agent invocation
- token & cost telemetry, budget gates
- LLM-judge grader, weighted multi-grader composition
- per-rep variance buckets, pairwise outcomes for ELO
- JSONL event stream (`run.jsonl`) and OTLP spans
- parallelism, retries, timeouts
- nightly / effort-sweep workflows (require API budget)

See `lab/design/03-multi-model-runner.md` for what the production
runner will look like.
