theorem nat_mul_self_ge (n : Nat) : n * n ≥ n := by
  cases n with
  | zero => simp
  | succ k =>
    calc (k + 1) * (k + 1)
        = (k + 1) * k + (k + 1) := Nat.mul_succ (k + 1) k
      _ ≥ 0 + (k + 1)           := Nat.add_le_add_right (Nat.zero_le _) _
      _ = k + 1                 := Nat.zero_add _
