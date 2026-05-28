theorem add_one_exists (n : Nat) : ∃ m : Nat, n + m = n + 1 := by
  refine ⟨1, by simp⟩
