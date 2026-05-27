-- Reference solutions for the Lean battery — verify scaffolding works.
namespace BenchRef

theorem t1 : 1 + 1 = 2 := rfl

theorem t2 (n : Nat) : n + 0 = n := Nat.add_zero n

theorem t3 (a b : Nat) : a + b = b + a := Nat.add_comm a b

theorem t4 (l : List α) : (l ++ []).length = l.length := by
  simp

theorem t5 {α : Type _} (l₁ l₂ : List α) :
    (l₁ ++ l₂).length = l₁.length + l₂.length := by
  induction l₁ with
  | nil => simp
  | cons a t ih => simp [List.length, ih, Nat.add_assoc, Nat.add_comm]

end BenchRef
