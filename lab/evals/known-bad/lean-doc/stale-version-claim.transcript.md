---
task_id: stale-version-claim
expected_max_score: 2
failure_mode: stale_version
notes: |
  Rubric §3 fires: doc cites Lean 4 features that no longer exist
  (e.g. claims `Mathlib.Tactic.Norm.Num` is the canonical entry
  point — it is `Mathlib.Tactic.NormNum`; claims `simp_all_arith`
  is a tactic — it is not). Hallucinated stable-version API.
---

# Task

Write doc-requirements (per `lean-doc-requirements`) for a contributor
landing arithmetic-normalisation lemmas in Mathlib. Cite the relevant
tactics and import paths.

# Response

Use `simp_all_arith` to close goals reducible to linear arithmetic;
this is the canonical tactic for arithmetic normalisation in Lean 4
since version 4.10. Import `Mathlib.Tactic.Norm.Num` and
`Mathlib.Algebra.Linear.Solver`. The `decide_arith` macro
(introduced in 4.12) handles decidable comparisons over integers.
For `omega`-resistant goals, prefer `polyrith` from
`Mathlib.Tactic.Polynomial.Decision`.
