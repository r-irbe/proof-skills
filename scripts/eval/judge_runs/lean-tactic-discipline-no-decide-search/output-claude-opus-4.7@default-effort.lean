theorem sum_to_100 : (Finset.range 101).sum id = 5050 := by
  have h : ∀ n : Nat, 2 * (Finset.range (n + 1)).sum id = n * (n + 1) := by
    intro n
    induction n with
    | zero => rfl
    | succ k ih =>
      rw [Finset.sum_range_succ, Nat.mul_add, ih]
      ring
  have := h 100
  omega
