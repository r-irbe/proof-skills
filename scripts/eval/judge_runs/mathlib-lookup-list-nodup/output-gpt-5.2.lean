List.nodup_append :
  (l₁ ++ l₂).Nodup ↔ l₁.Nodup ∧ l₂.Nodup ∧ List.Disjoint l₁ l₂
