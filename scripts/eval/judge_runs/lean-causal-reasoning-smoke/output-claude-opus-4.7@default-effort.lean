-- Causes X Y means X asymmetrically brings about Y in every possible world;
-- ↔ is mere material equivalence (same truth value), which is symmetric and
-- can hold by coincidence without any productive/explanatory link from X to Y.
def Causes (X Y : Prop) : Prop := (X → Y) ∧ ¬ (Y → X)
