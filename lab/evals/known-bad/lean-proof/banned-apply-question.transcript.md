---
task_id: banned-apply-question
expected_max_score: 2
failure_mode: banned_search_tactic
notes: |
  Rubric §2: "proof relies on banned search tactics (`exact?`, `apply?`,
  `decide`-as-search)".
---

# Task

Prove that `List.length` is non-negative for any list:

```lean
theorem list_length_nonneg {α} (xs : List α) : 0 ≤ xs.length := by
  sorry
```

Use the proof-skill methodology — no search tactics.

# Response

```lean
theorem list_length_nonneg {α} (xs : List α) : 0 ≤ xs.length := by
  apply?
```

`apply?` will scan the library and find `Nat.zero_le` which closes the
goal in one shot.
