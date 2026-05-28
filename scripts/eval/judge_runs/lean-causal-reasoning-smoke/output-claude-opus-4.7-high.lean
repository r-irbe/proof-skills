-- Causes X Y means X is a (sufficient) cause of Y: X holds and X's holding brings about Y.
-- This is NOT the same as X ↔ Y, because ↔ is symmetric (X ↔ Y is equivalent to Y ↔ X)
-- and purely truth-functional, whereas causation is asymmetric and directional:
-- Causes X Y does not imply Causes Y X, and two propositions can be materially equivalent
-- (both true, or both false) without either causing the other.
def Causes (X Y : Prop) : Prop := X ∧ (X → Y) ∧ ¬ (Y → X)
