def Causes (X Y : Prop) : Prop := X ∧ (X → Y)

-- Causes X Y is NOT the same as X ↔ Y because it only asserts X and that X implies Y, not that Y implies X.
