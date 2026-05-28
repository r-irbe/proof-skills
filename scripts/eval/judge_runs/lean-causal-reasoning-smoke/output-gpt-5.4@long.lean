-- Causes X Y is not the same as X ↔ Y because causation is directional and does not require the reverse implication Y → X.
def Causes (X Y : Prop) : Prop := X → Y
