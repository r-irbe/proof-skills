`List.nodup_append`:

```
theorem List.nodup_append {l₁ l₂ : List α} : (l₁ ++ l₂).Nodup ↔ l₁.Nodup ∧ l₂.Nodup ∧ l₁.Disjoint l₂
```
