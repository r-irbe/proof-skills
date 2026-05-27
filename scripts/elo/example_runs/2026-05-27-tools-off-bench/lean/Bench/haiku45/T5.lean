theorem t5 (n : Nat) (h : 0 < n) : ∃ m, n = m + 1 :=  match n with | 0 => absurd h (Nat.not_lt_zero 0) | k + 1 => ⟨k, rfl⟩
