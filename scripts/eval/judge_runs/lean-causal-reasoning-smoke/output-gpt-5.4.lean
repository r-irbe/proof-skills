-- Causes X Y is NOT the same as X ↔ Y because causation is taken as directional (X → Y), while ↔ also requires the reverse implication (Y → X).
def Causes (X Y : Prop) : Prop := X → Y
