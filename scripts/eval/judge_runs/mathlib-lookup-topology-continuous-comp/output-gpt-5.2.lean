Continuous.comp : ∀ {X Y Z : Type _} [TopologicalSpace X] [TopologicalSpace Y] [TopologicalSpace Z]
  {f : X → Y} {g : Y → Z}, Continuous g → Continuous f → Continuous (g ∘ f)
