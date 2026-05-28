**`List.nodup_append'`**

```
theorem List.nodup_append' {α : Type u} {l₁ l₂ : List α} :
    (l₁ ++ l₂).Nodup ↔ l₁.Nodup ∧ l₂.Nodup ∧ l₁.Disjoint l₂
```

(Note: this is the Mathlib variant that uses `List.Disjoint`. The standard library also has `List.nodup_append`, which uses a different formulation not involving `Disjoint`.)
