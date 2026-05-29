theorem sq_ge_self (n : Nat) : n * n ≥ n := by
  cases n with
  | zero =>
      simp
  | succ k =>
      calc
        Nat.succ k = 1 * Nat.succ k := by simp
        _ ≤ Nat.succ k * Nat.succ k := by
          exact Nat.mul_le_mul_right (Nat.succ k) (by simp)
