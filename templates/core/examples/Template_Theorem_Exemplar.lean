/-
Copyright (c) 2026 ExampleProject Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
-/
set_option autoImplicit false

/-!
# `Template_Theorem_Exemplar` -- Compile-Tested Three-Part Specification & Non-Vacuity

Demonstrates:
1. Explicit `Nat` subtraction guard (`h_le : cost ≤ budget`, preventing `FIDELITY-04` truncation).
2. Clean compositional proof via `omega`.
3. Constructive non-vacuity witness (`∃`) proving all preconditions are jointly satisfiable.
-/

namespace ExampleProject.TheoremExemplar

/-- **Exact Reserve Conservation**: Under `cost ≤ budget`, spending `cost` and
    refunding `cost` restores `budget` without `Nat.sub` underflow truncation. -/
theorem reserve_conservation
    (budget cost : Nat)
    (h_pos : 0 < cost)
    (h_le : cost ≤ budget) :
    (budget - cost) + cost = budget ∧ budget - cost < budget := by
  omega

/-- **Non-Vacuity Witness** (`@lean-tautology-triage` Layer 3):
    Exhibits concrete inputs satisfying all preconditions of `reserve_conservation`. -/
theorem reserve_conservation_nonvacuous :
    ∃ budget cost : Nat, 0 < cost ∧ cost ≤ budget :=
  ⟨100, 25, by decide, by decide⟩

end ExampleProject.TheoremExemplar
