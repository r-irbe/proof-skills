import Mathlib

theorem add_zero (n : Nat) : n + 0 = n := by
  -- goal: n + 0 = n, which simp resolves via Nat.add_zero
  simp
