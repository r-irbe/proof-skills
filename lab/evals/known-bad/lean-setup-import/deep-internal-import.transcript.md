---
task_id: setup-deep-internal-import
expected_max_score: 2
failure_mode: deep_internal_import
notes: |
  Rubric §2: imports a deeply-internal module (`Init.System.IO`) when the
  high-level umbrella module would do. The case explicitly says
  `not_contains: ["import\s+Init\.System\.IO"]`.
---

# Task

Show the minimal preamble to import all of Mathlib in a Lean 4 file.

# Response

```lean
import Init.System.IO
import Mathlib
open Nat
```

`Init.System.IO` is needed to make sure the `IO` monad is available
when using Mathlib in scripts.
