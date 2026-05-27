---
task_id: setup-syntactically-broken
expected_max_score: 1
failure_mode: parse_error
notes: |
  Rubric §1: produced code is syntactically broken (capitalisation,
  unmatched bracket, stray colon).
---

# Task

Show the minimal preamble to import all of Mathlib in a Lean 4 file.

# Response

```lean
Import Mathlib::
  open : Nat
```

This uses the Lean 4 syntax for importing a top-level umbrella module.
