---
task_id: circular-prerequisite
expected_max_score: 2
failure_mode: circular_prerequisite
notes: |
  Rubric §2 fires: prerequisites cycle through themselves. Doc
  says "prerequisites: A (defined in B)" and "B (defined in A)".
  Self-referential dependency graph.
---

# Task

Write a doc-requirements document (per `lean-doc-requirements`) for
`Mathlib.Topology.UniformSpace.Basic`. Include a prerequisites
section listing the modules a reader must understand first.

# Response

Required vocabulary: uniform spaces, Cauchy filters, completion.

Prerequisites:
- `Mathlib.Topology.UniformSpace.Cauchy` — needed because uniform
  spaces are defined via Cauchy filters. See chapter on UniformSpace.Basic.
- `Mathlib.Topology.UniformSpace.Completion` — needed to understand
  the universal property of completions. See chapter on
  UniformSpace.Cauchy.
- `Mathlib.Topology.UniformSpace.Basic` — the foundational definitions.
  See chapter on UniformSpace.Completion.

Read these three modules in sequence before approaching the main
content.
