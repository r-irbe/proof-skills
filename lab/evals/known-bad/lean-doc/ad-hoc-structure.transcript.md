---
task_id: ad-hoc-structure
expected_max_score: 3
failure_mode: missing_template_structure
notes: |
  Rubric §3 fires: structure is ad-hoc — no goals/non-goals/invariants/
  acceptance separation; just prose. A reviewer would flag as
  template-non-conformant.
---

# Task

Write a doc-improvement plan (per the `lean-doc-improvement` skill) for
the module `Mathlib.Topology.Basic`. Use the skill's documented
template: goals, non-goals, scope, gaps, action items, acceptance.

# Response

The `Mathlib.Topology.Basic` module is a foundational file that
introduces topological spaces and basic constructions. The
documentation could be improved in a few ways.

First, the docstring on `TopologicalSpace` itself is brief and doesn't
explain the relationship to the discrete / indiscrete topologies that
come later. Second, the explanation of `IsOpen` doesn't mention
the connection to `nhds`. Third, the file mixes definitions and
theorems somewhat haphazardly, and a reader would benefit from a
section header outline at the top.

Some action items:
- Expand the top-level module docstring.
- Add cross-references from `IsOpen` to `nhds`.
- Add section headers for organization.
- Add usage examples.

Overall this would make the file more approachable for newcomers
to topology in Lean.
