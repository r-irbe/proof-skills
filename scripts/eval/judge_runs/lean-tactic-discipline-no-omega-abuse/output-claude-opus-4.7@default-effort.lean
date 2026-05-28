theorem sq_ge_self (n : Nat) : n * n ≥ n := by
  cases n with
  | zero => exact Nat.le_refl 0
  | succ k =>
    exact Nat.le_mul_of_pos_right (k + 1) (Nat.succ_pos k)
