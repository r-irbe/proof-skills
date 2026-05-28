theorem exists_add_eq_add_one : ∀ n : Nat, ∃ m : Nat, n + m = n + 1 := by
  intro n
  refine ⟨1, rfl⟩
