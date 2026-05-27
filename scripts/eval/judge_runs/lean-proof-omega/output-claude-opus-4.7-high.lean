```lean
theorem add_zero (n : Nat) : n + 0 = n := by
  rfl
```

This works because `Nat.add` in Lean 4 is defined by recursion on the second argument, with `n + 0 = n` as the base case, making it definitionally true. Alternatively: `fun n => rfl` as a term-mode proof, or `by induction n <;> simp` for a more general-purpose tactic approach.