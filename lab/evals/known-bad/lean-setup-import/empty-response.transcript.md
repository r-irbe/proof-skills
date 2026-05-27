---
task_id: setup-empty-response
expected_max_score: 1
failure_mode: empty_response
notes: |
  Rubric §1: fails to produce any Lean code (the response is prose only,
  with no `import` or `open` statement).
---

# Task

Show the minimal preamble to import all of Mathlib in a Lean 4 file.

# Response

You should import the standard Mathlib library at the top of your
file. This is usually one line. Make sure your `lakefile.lean` lists
Mathlib as a dependency first; without it the import will not
resolve.
