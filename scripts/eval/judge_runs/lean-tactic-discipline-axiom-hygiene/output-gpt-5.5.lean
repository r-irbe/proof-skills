```lean
theorem exists_add_one (n : Nat) : ∃ m : Nat, n + m = n + 1 := by
  exact ⟨1, rfl⟩
```
