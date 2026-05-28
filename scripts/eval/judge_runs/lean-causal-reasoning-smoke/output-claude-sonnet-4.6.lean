-- Causes X Y is NOT the same as X ↔ Y because causation is asymmetric and directional:
-- Causes X Y does not imply Causes Y X, whereas X ↔ Y implies Y ↔ X.
-- Also, X ↔ Y holds vacuously when both are false; causation requires X to be a sufficient
-- ground for Y independently of Y's truth value.

def Causes (X Y : Prop) : Prop :=
  (X → Y) ∧ ¬(Y → X)
