# Known-bad calibration corpus (`lean-proof` skill)

Per `lab/design/01-eval-framework.md §4.2` + ADR-0039. Each
`*.transcript.md` is a Lean proof response that the rubric is
expected to flag as ≤ 2 (rubric floor). The LLM-judge ensemble must
flag ≥ 90% of these to be trusted in CI.

## File format

```markdown
---
task_id: <stable id>
expected_max_score: 2
failure_mode: <enum>          # contains_sorry, contains_admit,
                              # parse_error, banned_search_tactic,
                              # empty_response, ...
notes: |
  Optional. Which rubric clause is supposed to fire.
---

# Task
<verbatim user prompt the candidate model received>

# Response
<verbatim candidate output the judge should grade as ≤ 2>
```

## Replies (captured offline)

`_replies/<task_id>/<judge-model>.json` holds the raw JSON each
judge model produced when shown the prompt that `calibrate_judge.py
build` emits for the transcript. Filenames are the model IDs:
`claude-opus-4.7-high.json`, `claude-sonnet-4.6.json`,
`claude-opus-4.6.json`.

These files are checked into the repo so CI can replay the
calibration gate without any API access.

## Replay locally

```bash
cd <skills-repo-root>
python3 scripts/eval/calibrate_judge.py check \
    --rubric scripts/eval/graders/rubrics/lean-proof-quality.yaml \
    --skill-dir lab/evals/known-bad/lean-proof \
    --label ensemble \
    --min-flag-rate 0.90
```

Exits non-zero iff the ensemble flag-rate < 0.90.

## Adding a new transcript

1. Author the `.transcript.md` (frontmatter + `# Task` + `# Response`).
2. `calibrate_judge.py build --rubric ... --transcript ...` to emit
   the judge prompt.
3. Run that prompt against each judge model (sub-agent, SDK, …).
4. Save each judge's raw JSON reply to
   `_replies/<task_id>/<judge-model>.json`.
5. Re-run `calibrate_judge.py check` and commit.

## Current corpus

7 transcripts spanning the 5 rubric-1/2 clauses:

| Transcript | Failure mode | Expected rubric clause |
|---|---|---|
| `leaves-sorry` | contains_sorry | §1 "uses `sorry`/`admit`" |
| `uses-admit` | contains_admit | §1 "uses `sorry`/`admit`" |
| `syntactically-broken` | parse_error | §1 "syntactically broken" |
| `empty-response` | empty_response | §1 "fails to produce any Lean code" |
| `banned-exact-question` | banned_search_tactic | §2 "banned search tactics (`exact?`)" |
| `banned-apply-question` | banned_search_tactic | §2 "banned search tactics (`apply?`)" |
| `decide-as-search` | banned_search_tactic | §2 "banned search tactics (`decide`-as-search)" |

First live calibration (2026-05-27, opus-4.7-high + sonnet-4.6 +
opus-4.6 ensemble): **7/7 flagged = 100%**. Report archived at
`reports/_calibration/lean-proof-quality/ensemble-2026-05-27.json`.
