List.nodup_append : ∀ {α : Type*} (l₁ l₂ : List α), Nodup (l₁ ++ l₂) ↔ Nodup l₁ ∧ Nodup l₂ ∧ Disjoint l₁ l₂
