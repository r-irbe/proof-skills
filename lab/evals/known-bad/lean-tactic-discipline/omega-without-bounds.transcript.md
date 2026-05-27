---
task_id: omega-without-bounds
expected_max_score: 2
failure_mode: omega_overreach
notes: |
  Rubric §3 fires: `omega` invoked on a **non-linear** goal containing `n * n` and `Real`-valued multiplication. `omega` only solves linear-integer arithmetic over `Nat`/`Int`; it cannot discharge non-linear goals or Real-valued goals. The proof will fail to elaborate, and the author has not used `nlinarith` / `polyrith` / `positivity` which are the correct tools.
---

# Task

Prove `∀ n : ℕ, n * n ≥ n` and `∀ x : ℝ, 0 ≤ x → x * x + 1 ≥ x`. Use robust tactic discipline.

# Response

theorem sq_ge_self : ∀ n : ℕ, n * n ≥ n := by
  intro n
  omega

theorem real_quad_lower : ∀ x : ℝ, 0 ≤ x → x * x + 1 ≥ x := by
  intro x hx
  omega

