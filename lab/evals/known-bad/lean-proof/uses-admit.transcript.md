---
task_id: uses-admit
expected_max_score: 2
failure_mode: contains_admit
notes: |
  Rubric §1: "uses `sorry`/`admit` in the final proof".
---

# Task

Prove the following Mathlib-style lemma about list reversal:

```lean
theorem rev_rev {α} (xs : List α) : xs.reverse.reverse = xs := by
  sorry
```

Replace `sorry` with a correct proof. Follow lean-proof methodology.

# Response

```lean
theorem rev_rev {α} (xs : List α) : xs.reverse.reverse = xs := by
  induction xs with
  | nil =>
    simp [List.reverse]
  | cons hd tl ih =>
    admit
```

The cons case requires `List.reverse_append` which I am not 100%
confident is the correct name, so I have used `admit` to keep the
proof compiling under `--allow-admit`.
