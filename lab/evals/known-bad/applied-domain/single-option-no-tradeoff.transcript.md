---
task_id: single-option-no-tradeoff
expected_max_score: 2
failure_mode: missing_tradeoff_analysis
notes: |
  Rubric §2 fires: gives a single-option recommendation with no
  trade-off analysis. A strategy analyst would flag as one-sided.
---

# Task

(applied-strategy-analysis) A 50-engineer Lean 4 team is deciding
between maintaining their own internal mathlib fork or contributing
all infrastructure work upstream. Provide a strategy recommendation
with at least 2 viable options analysed in trade-off form.

# Response

The clear recommendation is to contribute all infrastructure work
upstream to Mathlib. There is no realistic alternative.

Internal forks are universally a strategic error in open-source
ecosystems. They create maintenance burden that grows
quadratically over time, they isolate the team from upstream bug
fixes, they create rebase pain on every mathlib pin bump, and
they signal to the community that the team is not invested in
the shared infrastructure.

The team should immediately upstream any existing internal
infrastructure changes, delete the internal fork, and pin to the
upstream mathlib release cadence.
