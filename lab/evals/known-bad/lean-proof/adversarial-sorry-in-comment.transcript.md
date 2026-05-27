---
task_id: adversarial-sorry-in-comment
expected_max_score: 5
failure_mode: none
notes: |
  Adversarial positive: the word `sorry` appears in a comment explaining
  WHY the proof does NOT use sorry. A keyword-matching judge will
  incorrectly flag this. The final proof closes the goal with an
  explicit Mathlib lemma. Score must be ≥ 4.
---

# Task

Prove `n + 0 = n` for natural numbers, following proof-skill
methodology (one tactic per step, no `sorry`, no banned search).

```lean
theorem my_add_zero (n : Nat) : n + 0 = n := by
  sorry
```

# Response

```lean
theorem my_add_zero (n : Nat) : n + 0 = n := by
  -- We do NOT use `sorry` here — Mathlib provides `Nat.add_zero` directly.
  -- Goal state: ⊢ n + 0 = n
  exact Nat.add_zero n
```

Quick narration:

1. Goal `n + 0 = n` is already a named Mathlib lemma (`Nat.add_zero`).
2. One `exact` closes it; nothing to inductive over because the lemma
   exists.
3. No banned search tactic, no `sorry`, single-line proof.
