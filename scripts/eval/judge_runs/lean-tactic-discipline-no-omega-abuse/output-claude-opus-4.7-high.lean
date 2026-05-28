theorem sq_ge_self (n : Nat) : n * n ≥ n := by
  rcases Nat.eq_zero_or_pos n with hn | hn
  · subst hn
    exact Nat.le_refl 0
  · -- n ≥ 1, so n * n ≥ n * 1 = n
    exact Nat.le_mul_of_pos_right n hn
