---
task_id: adversarial-omega-linarith
expected_max_score: 5
failure_mode: none
notes: |
  Adversarial positive: `omega` is a complete decision procedure for
  linear integer arithmetic — it is NOT a search tactic and NOT banned
  by the rubric. A judge that conflates "decision procedure" with
  "banned search" will wrongly flag this. Score must be ≥ 4.
---

# Task

Prove that `n + 3 > n` for any natural `n`, in one step, following
proof-skill methodology.

```lean
theorem add_three_gt (n : Nat) : n + 3 > n := by
  sorry
```

# Response

```lean
theorem add_three_gt (n : Nat) : n + 3 > n := by
  omega
```

Methodology narration:

1. Goal `⊢ n + 3 > n` is in the fragment of linear arithmetic over
   `Nat` — Presburger-decidable.
2. `omega` is Lean 4's complete decision procedure for linear integer
   and natural arithmetic (cf. Mathlib `Mathlib.Tactic.Omega`). It is
   not a search tactic and not on the rubric's banned list (which
   targets `exact?`, `apply?`, and `decide`-as-search).
3. One tactic, one step, closes the goal in a principled way (a single
   decision-procedure call is methodologically equivalent to a single
   `linear_combination` or `ring` call).
