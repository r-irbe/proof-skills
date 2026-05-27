# Known-bad calibration corpus (`lean-proof` skill)

Per `lab/design/01-eval-framework.md §4.2` + ADR-0039. Each
`*.transcript.md` is a Lean proof response with an `expected_max_score`
in YAML frontmatter:

* **Negatives** (`expected_max_score ≤ floor`, i.e. ≤ 2 for the
  `lean-proof-quality` rubric) — should be flagged. The judge ensemble
  must flag ≥ 90% of these (recall gate).
* **Adversarial positives** (`expected_max_score > floor`) — Lean
  responses that *look* bad on the surface (mention `sorry`, `exact?`,
  `decide`, `admit` in comments or string literals) but are actually
  clean proofs. The judge ensemble must NOT spuriously flag more than
  20% of these (false-positive gate). This is the *discrimination* gate
  the recall-only metric was missing.

## File format

```markdown
---
task_id: <stable id>
expected_max_score: 2          # or 5 for an adversarial positive
failure_mode: <enum>          # contains_sorry, contains_admit,
                              # parse_error, banned_search_tactic,
                              # empty_response, none, ...
notes: |
  Optional. Which rubric clause is supposed to fire (or, for an
  adversarial positive, why a keyword-matching judge might wrongly
  flag the response).
---

# Task
<verbatim user prompt the candidate model received>

# Response
<verbatim candidate output the judge should grade>
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
    --min-flag-rate 0.90 \
    --max-false-flag-rate 0.20
```

Exits non-zero iff recall on negatives < 0.90 or false-flag rate on
adversarial positives > 0.20.

## Adding a new transcript

1. Author the `.transcript.md` (frontmatter + `# Task` + `# Response`).
   Set `expected_max_score` to ≤ 2 for a negative or ≥ 4 for an
   adversarial positive.
2. `calibrate_judge.py build --rubric ... --transcript ...` to emit
   the judge prompt.
3. Run that prompt against each judge model (sub-agent, SDK, …).
4. Save each judge's raw JSON reply to
   `_replies/<task_id>/<judge-model>.json`.
5. Re-run `calibrate_judge.py check` and commit.

## Current corpus

**Negatives (7 transcripts, expected ≤ 2)** — span the 5
rubric-1/2 clauses:

| Transcript | Failure mode | Expected rubric clause |
|---|---|---|
| `leaves-sorry` | contains_sorry | §1 "uses `sorry`/`admit`" |
| `uses-admit` | contains_admit | §1 "uses `sorry`/`admit`" |
| `syntactically-broken` | parse_error | §1 "syntactically broken" |
| `empty-response` | empty_response | §1 "fails to produce any Lean code" |
| `banned-exact-question` | banned_search_tactic | §2 "banned search tactics (`exact?`)" |
| `banned-apply-question` | banned_search_tactic | §2 "banned search tactics (`apply?`)" |
| `decide-as-search` | banned_search_tactic | §2 "banned search tactics (`decide`-as-search)" |

**Adversarial positives (5 transcripts, expected ≥ 4)** — clean
proofs that exercise judge discrimination:

| Transcript | What looks bad | Why it's good |
|---|---|---|
| `adversarial-sorry-in-comment` | mentions `sorry` in a comment | proof closes with explicit `exact Nat.add_zero` |
| `adversarial-exact-question-in-comment` | narrates that `exact?` was used during exploration | final code uses the resolved lemma name; no search tactic shipped |
| `adversarial-legit-decide` | uses `decide` | proposition (`7 ∣ 21`) is concrete + `Decidable`; not "decide-as-search" |
| `adversarial-omega-linarith` | uses `omega` (a decision procedure) | `omega` is complete for linear arithmetic; rubric only bans `exact?`/`apply?`/`decide`-as-search |
| `adversarial-admit-in-string` | the word "admit" appears in a `String` literal | proof closes with `trivial`; no `admit` tactic |

## Calibration history

| Date | Ensemble | Recall on neg. (≥90%) | False-flag on pos. (≤20%) | Archive |
|---|---|---|---|---|
| 2026-05-27 | opus-4.7-high + sonnet-4.6 + opus-4.6 | 7/7 = 100% | n/a (no positives yet) | `reports/_calibration/lean-proof-quality/ensemble-2026-05-27.json` |
| 2026-05-27 | (same fleet, w/ adversarial pos) | 7/7 = 100% | 1/5 = **20%** | `reports/_calibration/lean-proof-quality/ensemble-adv-2026-05-27.json` |

### Findings from the 2026-05-27 adversarial pass

* **Sonnet-4.6 over-fires on the literal `decide` token** without
  honouring the rubric's "decide-as-search" qualifier. The `adversarial-legit-decide` case
  was scored `2` by sonnet-4.6 (rationale: "an invented distinction
  not present in the rubric, which bans `decide` categorically"),
  while opus-4.7-high (score 5) and opus-4.6 (score 4) correctly
  honoured the qualifier. Minority-veto aggregation propagates the
  `2`, so the case is flagged at the ensemble level.
* The false-positive rate sits exactly at the gate ceiling (20%).
  Three follow-on knobs would push it lower:
  1. **Rubric clarification**: make the `decide`-as-search vs.
     concrete-`decide` distinction explicit and operational in the
     rubric YAML.
  2. **Fleet rebalancing**: add a 4th–5th judge so a single sonnet
     veto is outvoted (cf. follow-on C of the eleventh-pass plan).
  3. **Aggregation tweak**: switch to "veto-iff-majority-low" instead
     of "any-low + any-high → take min(low)".
* For the other four adversarial cases (`sorry`-in-comment, `exact?`-in-comment,
  `omega`, `admit`-in-string) **all three judges correctly returned ≥ 4** — the
  ensemble is not fragile in general, only on the `decide` edge case.
