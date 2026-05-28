**List.nodup_append**

```lean
List.nodup_append : {l₁ l₂ : List α} → (l₁ ++ l₂).Nodup ↔ l₁.Nodup ∧ l₂.Nodup ∧ Disjoint l₁ l₂
```
