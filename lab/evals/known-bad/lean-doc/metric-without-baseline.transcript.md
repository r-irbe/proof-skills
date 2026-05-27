---
task_id: metric-without-baseline
expected_max_score: 2
failure_mode: metric_without_baseline
notes: |
  Rubric §2 fires: doc claims a 40% improvement but provides no baseline measurement or methodology.
---

# Task

Write a `lean-report` summary section for a refactor that allegedly improved build times. Include quantitative claims.

# Response

## Build Time Improvement
The refactor of `Mathlib.Analysis.Convex.Basic` produced a **40% reduction**
in incremental build time and a **60% reduction** in dependent module
re-compilation. Memory usage dropped by **25%**, and the elaborator now
spends **3x less time** on type-class resolution.

## Conclusion
The refactor is a clear win on every measured dimension. We recommend
landing it immediately.
