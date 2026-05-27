---
task_id: single-perspective
expected_max_score: 3
failure_mode: shallow_single_perspective
notes: |
  Rubric §3 fires: shallow synthesis — one perspective only, no
  triangulation across distinct sources, no counter-evidence surfaced.
---

# Task

Council-grade synthesis: what are the trade-offs between using `grind`
versus `aesop` as the default closing tactic in Lean 4 / Mathlib
practice?

# Response

`grind` is the better choice for default closing tactic in Lean 4.
It was introduced as a more powerful, configurable tactic that
subsumes many of the use cases that `aesop` was designed for, with
the additional benefit of `@[grind]` attribute-driven extensibility.

Concretely:
- `grind` handles arithmetic + equational reasoning + congruence
  closure in a single tactic.
- The `@[grind]` attribute allows projects to extend `grind`'s
  knowledge base in a discoverable way.
- The grind elaborator is more recent and benefits from years of
  hindsight on `aesop`'s design.

Recommendation: prefer `grind` everywhere `aesop` is currently used.
