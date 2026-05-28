theorem nat_sq_ge_self (n : Nat) : n * n ≥ n := by
  induction n with
  | zero => rfl
  | succ n ih =>
    rw [Nat.succ_mul, Nat.mul_succ]
    exact Nat.le_add_left (n + 1) (n * n + n)
