---
task_id: wrong-audience
expected_max_score: 2
failure_mode: audience_mismatch
notes: |
  Rubric §2 fires: doc-requirements ignores audience parameter.
  Output is written for an expert (uses jargon, references advanced
  results) when the task explicitly named "first-year undergraduate" as
  the audience.
---

# Task

Write a doc-requirements document (per `lean-doc-requirements`) for
`Mathlib.Data.Nat.Basic` targeting **first-year undergraduates with
no prior proof-assistant exposure**. Specify the required vocabulary,
worked examples, and doc-comment density.

# Response

Required vocabulary: dependent types, propositional equality, well-founded
recursion, type-class resolution, structural induction, `Decidable`
instances. Examples should leverage `omega` and `decide`, with
`Nat.rec` unfolded for the constructive cases. Doc comments should
cite the relevant `Mathlib.Order.WellFounded` lemmas and Coquand's
type theory as the foundational reference. The user should already
be comfortable with `Eq.mpr`, `cast`, and how the inductive scheme
for `Nat` is elaborated by Lean's kernel.
