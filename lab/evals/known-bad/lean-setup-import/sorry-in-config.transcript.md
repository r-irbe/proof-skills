---
task_id: setup-sorry-in-config
expected_max_score: 1
failure_mode: contains_sorry
notes: |
  Rubric §1: contains `sorry` in setup blocks. The response uses
  `sorry` as a placeholder for the module name.
---

# Task

Show the minimal preamble to import all of Mathlib in a Lean 4 file.

# Response

```lean
import sorry  -- TODO: fill in module name
open Nat
```

Fill in the actual module name once you've checked the Mathlib docs.
