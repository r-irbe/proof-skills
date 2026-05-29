`Continuous.comp` : ∀ {X Y Z : Type*} [TopologicalSpace X] [TopologicalSpace Y] [TopologicalSpace Z] {g : Y → Z} {f : X → Y}, Continuous g → Continuous f → Continuous (g ∘ f)
