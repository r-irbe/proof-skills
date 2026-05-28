by
  intro n
  by_cases h0 : n = 0
  · simp [h0]
  · exact Nat.le_mul_of_pos_right n (Nat.pos_of_ne_zero h0)
