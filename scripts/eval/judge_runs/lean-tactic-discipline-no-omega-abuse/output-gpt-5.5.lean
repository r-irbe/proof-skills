```lean
theorem nat_square_ge (n : Nat) : n ≤ n * n := by
  cases n with
  | zero => simp
  | succ n =>
      exact Nat.le_mul_of_pos_right (Nat.succ_pos n)
```
