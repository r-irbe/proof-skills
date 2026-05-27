import Mathlib

theorem my_add_comm (m n : Nat) : m + n = n + m := by
  -- goal: m + n = n + m
  exact Nat.add_comm m n
