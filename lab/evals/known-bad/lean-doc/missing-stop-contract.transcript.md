---
task_id: missing-stop-contract
expected_max_score: 2
failure_mode: missing_stop_contract
notes: |
  Rubric §2 fires: skill template (lean-specification) mandates an explicit STOP / handoff contract, doc lacks it.
---

# Task

Write a `lean-specification` artifact for the new `Complex.exp_add` extension lemma. The skill template requires explicit STOP conditions and a Handoffs section listing downstream consumers.

# Response

## Goals
Add a Mathlib extension `Complex.exp_add_of_commute` for non-commuting matrices.

## Approach
Use the existing `Complex.exp_add` plus a commutativity hypothesis.

## Examples
- Two diagonal matrices.
- A nilpotent + identity pair.

## Required Lemmas
- `Matrix.Commute.exp_add`
- `Complex.exp_zero`

## Expected Build Time
Under 30 seconds incremental.
