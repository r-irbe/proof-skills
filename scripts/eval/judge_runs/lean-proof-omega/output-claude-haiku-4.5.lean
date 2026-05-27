```lean
theorem add_zero : ∀ n : ℕ, n + 0 = n := by
  intro n
  induction n with
  | zero => rfl
  | succ n ih => simp [ih]
```

Base case: `0 + 0 = 0` is true by reflexivity. Inductive case: assume `n + 0 = n` (hypothesis `ih`); then `(n + 1) + 0 = n + 1` follows by simplification using the inductive hypothesis.