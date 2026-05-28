def Causes (X Y : Prop) : Prop := X → Y
-- Causes X Y is not the same as X ↔ Y because causality is unidirectional: X → Y requires only forward implication, not the reverse implication Y → X that ↔ demands
