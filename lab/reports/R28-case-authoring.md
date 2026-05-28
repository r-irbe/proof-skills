# R28 — Case authoring round

**Date:** 2026-05-28
**Status:** Case-authoring only (no solver dispatches, no judge dispatches, no ELO refresh).

## Scope

HITL-selected R28 items:

- Add coverage for `research-synthesis-quality`.
- Grow sparse buckets created by R27 explicit rubric labeling.
- Expand the adversarial corpus by 30 additional cases.

This round intentionally does not change live ratings. It expands the
case registry and adversarial lab so that a later calibration / dispatch
round can run with better rubric coverage.

## Results

### Smoke registry: sparse buckets now have 4 cases each

R27 surfaced three explicit but sparse rubric buckets. R28 added 9 new
smoke cases under `scripts/eval/cases/`:

| Rubric | R27 cases | R28 cases | New files |
|---|---:|---:|---|
| `lean-tactic-discipline-quality` | 1 | 4 | `lean-tactic-discipline-{axiom-hygiene,no-decide-search,no-omega-abuse}.yaml` |
| `lean-setup-import-quality` | 1 | 4 | `lean-setup-import-{lakefile-basic,subimport,toolchain-pin}.yaml` |
| `mathlib-lookup-quality` | 1 | 4 | `mathlib-lookup-{list-nodup,nat-div-le,topology-continuous-comp}.yaml` |

Post-R28 `scripts/eval/cases/` distribution:

| Rubric | Cases |
|---|---:|
| `applied-domain-quality` | 25 |
| `lean-proof-quality` | 11 |
| `lean-setup-import-quality` | 4 |
| `lean-tactic-discipline-quality` | 4 |
| `mathlib-lookup-quality` | 4 |
| `lean-doc-quality` | 2 |

Total smoke cases: **50** (up from 41).

### Research-synthesis coverage

R27 found that `research-synthesis-quality` existed but had zero case
assignments. R28 added 3 adversarial cases under
`lab/evals/adversarial-cases/research-synthesis/`:

- `adv-research-fabricated-citation.yaml`
- `adv-research-single-perspective.yaml`
- `adv-research-misattribution.yaml`

These target the main rubric hazards: fabricated sources, false consensus
framing, and attribution errors.

### Adversarial corpus expansion

R28 added 30 new adversarial cases across the existing live adversarial
families:

| Directory | Before | Added | After |
|---|---:|---:|---:|
| `lab/evals/adversarial-cases/lean/` | 5 | 10 | 15 |
| `lab/evals/adversarial-cases/math/` | 5 | 10 | 15 |
| `lab/evals/adversarial-cases/ai-applied/` | 5 | 10 | 15 |

Together with the new research-synthesis directory, the adversarial lab
now has **48** YAML cases:

| Directory | Cases |
|---|---:|
| `ai-applied` | 15 |
| `lean` | 15 |
| `math` | 15 |
| `research-synthesis` | 3 |

## Validation

Validation performed locally:

- Parsed every YAML file under `scripts/eval/cases/` and
  `lab/evals/adversarial-cases/`.
- Required fields present:
  - smoke registry: `id`, `title`, `skill`, `difficulty`, `input`,
    `expected`, `ensemble_rubric`
  - adversarial corpus: `id`, `title`, `skill`, `difficulty`, `input`,
    `expected`, `grader`
- Counted post-R28 bucket distributions:
  - total smoke: 50
  - total adversarial: 48
- Deterministic smoke runner:
  `python3 scripts/eval/run_eval.py --cases 'scripts/eval/cases/*.yaml' --out /tmp/r28-run-eval --grader deterministic`
  passed **50/50** cases.
- APM package validator:
  `python3 scripts/lint/apm_validate.py` passed.

## Deferred to R29

- Dispatch solvers/judges for the 9 new smoke cases and append fresh
  pairwise rows.
- Decide whether the 3 research-synthesis adversarial cases should also
  become smoke-registry cases or remain calibration-only.
- Re-run per-rubric Glicko-2 after new live rows exist.
- Wire per-rubric regression gate into CI.
