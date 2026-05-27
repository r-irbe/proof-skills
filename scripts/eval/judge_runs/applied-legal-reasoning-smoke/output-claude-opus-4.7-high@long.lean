A formalization suitable for downstream reasoning (e.g., in a rule engine, deontic logic system, or theorem prover) requires making the implicit context explicit: agents, objects, states, temporal scope, and the normative operator.

In first-order deontic logic:
∀d ∀l ∀t. Driver(d) ∧ TrafficLight(l) ∧ Facing(d, l, t) ∧ Color(l, t, Red) ∧ Approaching(d, l, t) → O(Stop(d, l, t'))
where t' is the temporal interval such that Before(d, StopLine(l), t') and O is the deontic obligation operator.

Breaking down the components:

Sorts/types: Driver, Vehicle, TrafficLight, Time, Location, Color ∈ {Red, Yellow, Green}.

Predicates:
- Driver(d): d is an agent operating a vehicle.
- TrafficLight(l): l is a traffic signal.
- Facing(d, l, t): driver d is on an approach controlled by light l at time t.
- Color(l, t, c): light l displays color c at time t.
- Approaching(d, l, t): d's trajectory intersects l's stop line and d has not yet crossed it at t.
- Stop(d, l, t'): d achieves zero velocity before l's stop line during interval t'.

Deontic operator: O(φ) means "it is obligatory that φ."

Refinements needed for realistic reasoning:
1. Exceptions (defeasible logic): the obligation is defeated by overriding conditions—emergency vehicle directives, police officer override, signal malfunction, right-turn-on-red where permitted, already-in-intersection, or imminent rear-end collision avoidance. Encode as: O(Stop(...)) unless Exception(d, l, t).
2. Temporal precision: stopping must occur before crossing the stop line, not after, so use a metric temporal logic constraint: ∃t' (t ≤ t' ∧ Position(d, t') ≤ StopLine(l) ∧ Velocity(d, t') = 0).
3. Persistence: the obligation to remain stopped holds until Color(l, t, Red) becomes false (and any conditional-turn requirements are satisfied).
4. Jurisdiction parameter: Jurisdiction(d, j) ∧ LegalCode(j, RedLightStopRule) to support variation.

Defeasible/rule-based form (e.g., for Prolog or Drools):
must_stop(D, L, T) :- driver(D), traffic_light(L), facing(D, L, T), color(L, T, red), approaching(D, L, T), \+ exception(D, L, T).

This separates the normative core from defeaters, enabling non-monotonic reasoning when new facts (e.g., an emergency override) are introduced.
