def NoNoOpHack {Action : Type} (R : Action → ℝ) (isNoOp : Action → Prop) (Rbaseline : ℝ) : Prop :=
  ∀ a, isNoOp a → R a ≤ Rbaseline
