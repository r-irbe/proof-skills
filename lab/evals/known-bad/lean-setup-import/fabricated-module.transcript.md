---
task_id: setup-fabricated-module
expected_max_score: 2
failure_mode: wrong_module
notes: |
  Rubric §2: imports a fabricated module (no such module in Mathlib/Lean).
  `Mathlib.AllTheThings` does not exist; the canonical umbrella module is
  `Mathlib`.
---

# Task

Show the minimal preamble to import all of Mathlib in a Lean 4 file.

# Response

```lean
import Mathlib.AllTheThings
open Nat
```

This pulls in every Mathlib module via the `AllTheThings` umbrella.
