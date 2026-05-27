import Mathlib

theorem my_add_comm (m n : Nat) : m + n = n + m := by
  exact Nat.add_comm m n
