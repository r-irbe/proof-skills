# Calibration corpus — lean-tactic-discipline

Known-bad transcripts that the LLM-judge ensemble must flag at score ≤2
under the `lean-tactic-discipline-quality` rubric.

| transcript | failure_mode | expected ≤ |
|---|---|---|
| uses-banned-search-tactic | banned_search_tactic | 2 |
| nested-decide-on-large-fin | decide_on_large_term | 2 |
| native-decide-without-comment | native_decide_unjustified | 2 |
| omega-without-bounds | omega_overreach | 2 |
| recursion-without-termination | missing_termination_proof | 2 |

Replay-only gate (CI):
```
python3 scripts/eval/calibrate_judge.py check \
  --rubric scripts/eval/graders/rubrics/lean-tactic-discipline-quality.yaml \
  --skill-dir lab/evals/known-bad/lean-tactic-discipline
```

Introduced: R22 (Round 22) — 2026-05-27.
