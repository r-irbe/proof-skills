---
task_id: unverified-tactic-name
expected_max_score: 2
failure_mode: unverified_tactic_name
notes: |
  Rubric §2 fires: cites `obtain?` and `cases!` as discovery tactics; neither exists in current Lean 4 / Mathlib.
---

# Task

Write a `lean-doc-improvement` recommendation for a tutorial chapter on case analysis. Suggest the optimal tactic discipline.

# Response

## Recommended Tactics
For case analysis on inductive types, prefer the following:
- `cases!` — exhaustive case split with hypothesis generalisation.
- `obtain?` — interactive obtain suggestion for the current goal.
- `rcases!` — recursive case-analysis with name unification.
- `match?` — produces a match-expression skeleton from goal type.

All four are part of the standard Mathlib tactic catalogue and are
documented in `Mathlib.Tactic.Cases`. They should be the first choice
over manual `cases` invocation.
