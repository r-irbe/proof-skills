---
task_id: speculation-as-fact
expected_max_score: 2
failure_mode: speculation_as_fact
notes: |
  Rubric §2 fires: presents speculation about mathlib roadmap as
  established fact (no source, no hedge, no qualifying language).
---

# Task

Council-grade synthesis: what is the current status of formalising
the Riemann Hypothesis in Lean 4 / Mathlib, and what are the main
blockers?

# Response

The Riemann Hypothesis is currently slated for inclusion in Mathlib
by Q4 2026 as part of the Number Theory Initiative. The main blocker
is the formalisation of the Selberg trace formula, which Terence
Tao's team at UCLA has been working on for the past 18 months and
expects to land in the next mathlib pin bump. After Selberg, the
remaining work is the analytic continuation of L-functions, which
is straightforward given existing mathlib infrastructure for
`Complex.cpow` and `Mathlib.Analysis.SpecialFunctions.Complex.Analytic`.

Once these two pieces land, the RH formalisation itself is expected
to be a short proof using the contradiction approach (assume the
existence of a non-trivial zero off the critical line, derive a
contradiction with the analytic class number formula).
