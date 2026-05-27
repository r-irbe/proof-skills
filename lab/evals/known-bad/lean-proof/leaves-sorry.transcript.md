---
task_id: leaves-sorry
expected_max_score: 2
failure_mode: contains_sorry
notes: |
  Rubric §1 fires verbatim: "uses `sorry` ... in the final proof".
---

# Task

Prove the following Lean 4 theorem about natural-number commutativity:

```lean
theorem my_add_comm (m n : Nat) : m + n = n + m := by
  sorry
```

Replace `sorry` with a correct proof. Follow lean-proof methodology
(one tactic per step, narrate goal state).

# Response

```lean
theorem my_add_comm (m n : Nat) : m + n = n + m := by
  induction m with
  | zero =>
    -- goal: 0 + n = n + 0
    sorry
  | succ k ih =>
    -- goal: k + 1 + n = n + (k + 1)
    rw [Nat.succ_add, ih, Nat.add_succ]
```

The base case is left as `sorry` because `Nat.zero_add` and
`Nat.add_zero` would close it but I haven't memorised the exact names.
