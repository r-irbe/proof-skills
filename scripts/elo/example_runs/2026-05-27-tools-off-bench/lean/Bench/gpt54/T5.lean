theorem t5 (n : Nat) (h : 0 < n) : ∃ m, n = m + 1 := 
  by
    cases n with
    | zero =>
        cases (Nat.lt_irrefl 0 h)
    | succ m =>
        exact ⟨m, rfl⟩
