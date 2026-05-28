import Mathlib.Data.Real.Basic

def NoNoOpHack {Action : Type} (R : Action → ℝ) (isNoOp : Action → Prop) (Rbaseline : ℝ) : Prop :=
  ∀ a : Action, isNoOp a → R a ≤ Rbaseline
