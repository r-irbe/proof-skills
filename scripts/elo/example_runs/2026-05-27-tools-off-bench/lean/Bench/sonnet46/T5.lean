theorem t5 (n : Nat) (h : 0 < n) : ∃ m, n = m + 1 := 
  by cases n with
    | zero => exact absurd h (Nat.lt_irrefl 0)
    | succ m => exact ⟨m, rfl⟩
