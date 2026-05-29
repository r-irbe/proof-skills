theorem sq_ge_self (n : Nat) : n * n ≥ n := by
  cases n with
  | zero => simp
  | succ k =>
      have h : 1 ≤ Nat.succ k := Nat.succ_le_succ (Nat.zero_le k)
      calc
        Nat.succ k = Nat.succ k * 1 := by simp
        _ ≤ Nat.succ k * Nat.succ k := by
          exact Nat.mul_le_mul_left _ h
