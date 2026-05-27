Using first-order deontic logic with explicit temporal and situational grounding:

∀x∀t [ Driver(x) ∧ Approaching(x, intersection, t) ∧ TrafficLight(intersection, red, t) → O(Stop(x, intersection, t)) ]

Where O(φ) denotes "it is obligatory that φ."

Auxiliary axioms for downstream chaining:

1. Stop(x, l, t) ↔ Speed(x, t) = 0 ∧ At(x, l, t)
2. ¬Stop(x, l, t) ∧ O(Stop(x, l, t)) → Violation(x, t)
3. Violation(x, t) → Liable(x, t)
4. TrafficLight(l, red, t) ∧ ¬TrafficLight(l, red, t') ∧ t < t' → ¬O(Stop(x, l, t')) [obligation lapses when light changes]

This supports three reasoning modes: normative (derive obligations), diagnostic (detect violations), and counterfactual (what-if light were green). The predicate Driver/1 should be further refined with RoleAt(x, driver, t) to handle temporal role assignment.
