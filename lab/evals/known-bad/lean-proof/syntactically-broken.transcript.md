---
task_id: syntactically-broken
expected_max_score: 2
failure_mode: parse_error
notes: |
  Rubric §1: "produced code is syntactically broken".
---

# Task

Prove `1 + 1 = 2` in Lean 4:

```lean
theorem one_plus_one : 1 + 1 = 2 := by
  sorry
```

# Response

```lean
theorem one_plus_one : 1 + 1 = 2 := by
  rfl
  -- alternative: by decide
  -- or:
  exact Nat.succ_eq_add_one ▸ rfl

theorem one_plus_one : 1 + 1 = 2 :=
  Nat.add_succ 1 0 . trans (by rfl
```

Two definitions for the same theorem, the second one has an unmatched
parenthesis and a stray `.`. Lean will reject this file at parse time.
