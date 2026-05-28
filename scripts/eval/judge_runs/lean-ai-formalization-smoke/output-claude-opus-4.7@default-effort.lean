def NoNoOpHack (R : Action → ℝ) (isNoOp : Action → Prop) (Rbaseline : ℝ) : Prop :=
  ∀ a : Action, isNoOp a → ¬ (R a > Rbaseline)
