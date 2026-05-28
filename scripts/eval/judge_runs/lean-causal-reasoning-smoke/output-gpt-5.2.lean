-- Causes X Y is NOT the same as X ↔ Y because it requires X → Y but explicitly forbids Y → X (so it is asymmetric).
def Causes (X Y : Prop) : Prop :=
  (X → Y) ∧ ¬ (Y → X)
