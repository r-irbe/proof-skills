theorem add_zero_right : ∀ n : ℕ, n + 0 = n := by
  intro n
  rfl

This works because in Lean 4's `Nat`, addition is defined by recursion on the second argument, so `n + 0` reduces definitionally to `n`, making `rfl` sufficient. Alternatively, `exact fun n => Nat.add_zero n` or `simp [Nat.add_zero]` also close the goal.