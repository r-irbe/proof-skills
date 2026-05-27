---
task_id: broken-cross-ref
expected_max_score: 2
failure_mode: broken_cross_reference
notes: |
  Rubric §3 fires: cites cross-references to handbooks and modules
  that do not exist (`lean-zen-mode-handbook.md`,
  `Mathlib.Tactic.GhostFunction`). Looks authoritative, isn't.
---

# Task

Write doc-requirements (per `lean-doc-requirements`) for
`Mathlib.Analysis.Calculus.MeanValue`. Include "see also" cross-
references to relevant Mathlib modules and skill handbooks.

# Response

# Doc Requirements: Mathlib.Analysis.Calculus.MeanValue

Audience: 2nd-year graduate students in analysis. Required vocabulary:
mean-value theorem, Rolle's theorem, derivative-on-an-interval.

## See also

- `lean-zen-mode-handbook.md` — for the meditative single-step
  proof methodology covered in §3.
- `Mathlib.Analysis.Calculus.RolleAxiomatised` — the axiomatised
  variant of Rolle's theorem that this module builds on.
- `Mathlib.Tactic.GhostFunction` — the tactic for closing
  derivative-symbol-elimination goals.
- `references/lean-mvt-deep-dive.md` — chapter 12 on MVT-style
  arguments in the analysis cluster.
