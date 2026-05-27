#check @Finset.card_union_le
theorem ex {α : Type*} [DecidableEq α] (s t : Finset α) :
    (s ∪ t).card ≤ s.card + t.card := Finset.card_union_le s t
