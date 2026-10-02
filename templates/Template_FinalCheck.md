# Template_FinalCheck -- Compile-Time Axiom Lockdown Gate Pattern

Use this template for **authoritative compilation gates**: verifying at compile time that all
formalized theorems in a package or release tranche depend exclusively on standard Lean 4 core axioms:
- `propext` (Propositional extensionality)
- `Quot.sound` (Quotient soundness)
or depend on zero axioms.

Rejects `sorryAx`, `Lean.ofReduceBool` (`native_decide`), or untracked custom axioms at compile time.
Modeled after Anthropic's Fermat's Last Theorem verification pattern.

## Main results
* `#guard_msgs in #print axioms <theorem>` compile-time failure if any unexpected axiom appears
* Certified audit trail for release verification and CI gates

## Implementation notes
- Place this gate in a separate test target (e.g. `Tests/FinalCheck.lean`).
- Import all exported modules and theorems to be certified.
- Guard each theorem with `#guard_msgs in #print axioms <declaration>`.
- Lean 4 compiler emits an error during `lake build Tests.FinalCheck` if the axioms printed do not match the docstring.

## References
* Kevin Buzzard et al., *Fermat's Last Theorem in Lean 4*, 2024-2026
* Leonardo de Moura and Sebastian Ullrich, *The Lean 4 Theorem Prover and Programming Language*, CADE 2021

## Tags
template, final-check, axiom-audit, guard-msgs, zero-sorry, compile-gate

```lean
import Rules.Theorems
import Rules.GPU
import Rules.Concurrency
import Rules.Distributed

set_option autoImplicit false

namespace Tests.FinalCheck

/-- info: 'Rules.evaluateMuleRule_disjoint' depends on axioms: [propext] -/
#guard_msgs in
#print axioms Rules.evaluateMuleRule_disjoint

/-- info: 'Rules.GPU.atomic_or_risk_flag_monotone' does not depend on any axioms -/
#guard_msgs in
#print axioms Rules.GPU.atomic_or_risk_flag_monotone

/-- info: 'Rules.Concurrency.cas_slot_uniqueness' depends on axioms: [propext, Quot.sound] -/
#guard_msgs in
#print axioms Rules.Concurrency.cas_slot_uniqueness

/-- info: 'Rules.Distributed.partition_mass_conservation' depends on axioms: [propext, Quot.sound] -/
#guard_msgs in
#print axioms Rules.Distributed.partition_mass_conservation

end Tests.FinalCheck
```
