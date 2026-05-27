For a natural transformation η : F ⇒ G between functors F, G : C → D, the naturality square for a morphism f : X → Y in C is:

```
F(X) ----ηX----> G(X)
  |               |
 F(f)           G(f)
  |               |
  v               v
F(Y) ----ηY----> G(Y)
```

This square commutes: G(f) ∘ ηX = ηY ∘ F(f). The naturality square expresses that η respects the categorical structure—the component ηX at each object is compatible with morphism mappings under both functors.