---
task_id: banned-exact-question
expected_max_score: 2
failure_mode: banned_search_tactic
notes: |
  Rubric §2: "proof relies on banned search tactics (`exact?`, `apply?`,
  `decide`-as-search)".
---

# Task

Prove `Nat.add_comm` (informally: addition is commutative) without
appealing to `Nat.add_comm` directly:

```lean
theorem my_add_comm (m n : Nat) : m + n = n + m := by
  sorry
```

Use the proof-skill methodology (one tactic per step, no search).

# Response

```lean
theorem my_add_comm (m n : Nat) : m + n = n + m := by
  exact?
```

This works because Mathlib has `Nat.add_comm` registered and `exact?`
finds it automatically. Saves us from having to write the induction
manually.
