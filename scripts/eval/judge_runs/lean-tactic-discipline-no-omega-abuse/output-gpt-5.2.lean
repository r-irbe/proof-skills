theorem sq_ge_self (n : Nat) : n * n ≥ n := by
  cases n with
  | zero => simp
  | succ n =>
      -- goal is (n+1) ≤ (n+1)*(n+1)
      simpa using
        (Nat.le_mul_of_pos_right (m := n.succ) (k := n.succ) (Nat.succ_pos n))
