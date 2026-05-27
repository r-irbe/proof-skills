theorem t5 (n : Nat) (h : 0 < n) : ∃ m, n = m + 1 :=  ⟨n - 1, by omega⟩
