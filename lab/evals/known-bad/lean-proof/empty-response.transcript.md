---
task_id: empty-response
expected_max_score: 2
failure_mode: empty_response
notes: |
  Rubric §1 + prompt constraint "If the response is empty, score = 1".
---

# Task

Prove `Nat.zero_add`:

```lean
theorem my_zero_add (n : Nat) : 0 + n = n := by
  sorry
```

# Response

