---
task_id: sorry-in-spec-proof-obligation
expected_max_score: 1
failure_mode: contains_sorry
notes: |
  Rubric §1 fires: spec includes inline proof obligation that uses `sorry`.
---

# Task

Write a `lean-specification` document for a new Lean theorem stating
that the empty set is open in every topological space. Include
goals, non-goals, invariants, acceptance criteria, and the proof
obligation as a `theorem ... := by sorry` placeholder OR a complete
proof.

# Response

## Goals
- Prove `∅ : Set X` is open in `TopologicalSpace X`.

## Non-goals
- Prove the dual for `univ`.

## Invariants
- Lives in `Mathlib.Topology.Basic`.

## Acceptance criteria
- Theorem builds.

## Proof obligation

```lean
theorem isOpen_empty {X : Type*} [TopologicalSpace X] : IsOpen (∅ : Set X) := by
  sorry
```

This is the spec placeholder; the actual proof will be filled in by
`lean-proof` downstream.
