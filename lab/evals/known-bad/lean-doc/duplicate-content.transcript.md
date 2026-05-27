---
task_id: duplicate-content
expected_max_score: 2
failure_mode: duplicate_content
notes: |
  Rubric §2 fires: same Acceptance Criteria section appears twice with conflicting bullets.
---

# Task

Write a `lean-specification` document for a new `Mathlib.Order.WellFounded` helper lemma. Include the standard sections: Goals, Non-Goals, Invariants, Acceptance Criteria, Test Conditions.

# Response

## Goals
Prove `WellFounded.fix_eq` simplifies under a custom well-founded relation.

## Non-Goals
We do not address `Quot.lift` interactions.

## Invariants
The chosen relation must be transitive.

## Acceptance Criteria
- The lemma must type-check at the current Mathlib pin.
- All `decide` calls must terminate in < 100ms.
- Documentation must include a worked example.

## Test Conditions
Include three regression tests covering: empty relation, singleton, list-of-3.

## Acceptance Criteria
- Lemma type-checks against Mathlib master.
- `omega` discharges arithmetic side-goals.
- A counter-example file demonstrates failure under a non-WF relation.

## Closing
Document is ready for review.
