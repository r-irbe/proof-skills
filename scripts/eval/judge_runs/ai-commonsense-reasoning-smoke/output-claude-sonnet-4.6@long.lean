This is the Frame Problem, first identified by McCarthy and Hayes in 1969. An agent reasoning about actions must know not only what changes but what stays the same. Without an explicit mechanism, an agent might be unable to conclude that a table's position is unaffected by placing a cup on it, because the agent cannot enumerate all non-effects of every action.

The classical solution is the frame axiom: for every action and every fluent not mentioned in the action's effect list, assert that the fluent is unchanged. But this requires writing O(actions × fluents) axioms, which is intractable.

The successor-state axiom approach, used in the Situation Calculus, compresses this. For each fluent F, write a single axiom of the form: F holds after action A in situation S if and only if A caused F to hold, or F held before and A did not cause it to cease. The table's position fluent has no clause linking it to the PutOn action, so the axiom directly entails the position is preserved.

In the Event Calculus the analogous mechanism is the Clipped predicate. A fluent persists by default from the time it is initiated until it is explicitly clipped by a terminating event. Since PutCupOnTable does not appear in any Terminates axiom for the table's location, the agent infers persistence by default.

In STRIPS and its successors, the solution is the Closed World Assumption over effects: only fluents listed in the add-list or delete-list of an operator change. Everything else is implicitly preserved. The table's position is in neither list for PutOn, so it is held constant. This is simple but brittle; it assumes perfect domain specification.

Default logic and circumscription offer a logical account. Circumscription minimizes the extension of the Abnormal predicate. An instance is abnormal only if it must be. Placing a cup is not forced to be an abnormal event for the table's location, so by minimization it is normal, and normal events do not move things.

In probabilistic agent frameworks such as those using Dynamic Bayesian Networks, the solution is a persistence CPT: P(Location(table, t+1) | Location(table, t), Action=PutCupOn) is set to near 1 because the causal model has no mechanism linking that action to table movement. The agent updates beliefs via Bayesian inference and the posterior leaves the table's location essentially unchanged.

Physics-based simulation agents solve this differently. A rigid-body simulator applies forces and computes accelerations. The cup has negligible mass relative to the table and any floor friction constraint. The net force on the table from the cup is below the static friction threshold, so the table's acceleration is zero and its position does not change. The agent reads the simulator's output directly.

Ontology-based agents use a taxonomy of affordances. An object's affordance set lists what actions can affect it. The table's position is afforded by actions in the class MoveObject applied to the table itself, not by PlaceObjectOn applied to objects resting on it. The PlaceObjectOn action's range of effect is restricted by the ontology to the placed object and the surface state, not to the supporting object's location.

A constraint-based agent maintains a constraint network. The table is connected to a floor constraint fixing its position. The PutOn action adds a SupportedBy constraint between cup and table, and a ContactSurface constraint, but does not modify or remove the floor constraint. Constraint propagation leaves the table's position variable bound to its prior value.

Causal models formalize this via a directed acyclic graph. The table's position node has parents: floor friction, applied horizontal force, applied vertical force beyond structural limit. None of those parent variables are set by PutCupOnTable at the forces that would overcome static friction or the structural limit. An intervention on CupLocation via PutOn does not propagate upstream through the causal graph to TablePosition because there is no directed edge from cup placement to table position.

The non-monotonic reasoning agent uses a default rule: for any object O and action A, if A does not have O as its primary object and does not transmit force exceeding O's inertial threshold, then O's location is unchanged after A. PutOn's primary object is the cup. The table is not the primary object. The default fires and location is preserved.

In knowledge graphs, the agent queries for EffectsOf(PutCupOnTable) and finds {CupLocation: OnTable, TableSurface: HasCup}. TablePosition is not in the set. The agent concludes by closed-world assumption that TablePosition is not an effect.

A planning agent using Hierarchical Task Networks encodes PutOn as a primitive task with preconditions and effects at the subtask level. The effects are defined extensionally. TablePosition is absent from the effects list. HTN execution does not modify it.

For a learning agent, the conclusion comes from experience or training data. Across thousands of observed cup placements, the table's position shows no statistically significant change correlated with the action. The agent builds a model assigning zero or near-zero influence weight from PutCupOn to TablePosition.

For a neural agent, the same result emerges if trained on physics-consistent data: the attention or causal mechanism learns that cup placement and table position are independent given the floor constraint. The agent's internal representation reflects this conditional independence.

The core insight across all frameworks is the same: an agent must have a representation that distinguishes the primary object of an action from bystander objects, and a default or explicit rule that bystander objects are unaffected unless a causal pathway is specified. Without this, the agent faces the Frame Problem and cannot conclude anything about the table's position. With it, the conclusion is immediate.
