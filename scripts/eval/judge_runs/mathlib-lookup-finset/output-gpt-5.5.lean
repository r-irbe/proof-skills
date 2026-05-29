import Mathlib

-- Theorem: `Finset.card_union_le`
-- Type: `Finset.card_union_le (s t : Finset α) : (s ∪ t).card ≤ s.card + t.card`

variable {α : Type*} [DecidableEq α] (s t : Finset α)

#check Finset.card_union_le
#check (Finset.card_union_le s t : (s ∪ t).card ≤ s.card + t.card)
