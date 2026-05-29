theorem exists_add_eq_succ (n : Nat) : ∃ m : Nat, n + m = n + 1 := by
  refine ⟨1, ?_⟩
  simp
