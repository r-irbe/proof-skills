O(consent(a, p) → ¬act(a, p) U consent(a, p))

More cleanly, using SDL with action and consent predicates over agent a and proposition/action p:

∀a ∀p: O( act(a, p) → P_granted(consent(a, p)) )

Equivalently, as a strict obligation/prohibition pair:
F( act(a, p) ∧ ¬consent(a, p) )  ≡  O( ¬act(a, p) ∨ consent(a, p) )

Where O = obligatory, F = forbidden, P = permitted, and consent(a, p) must temporally precede act(a, p): ◻( act(a, p) → ⧫ consent(a, p) ).
