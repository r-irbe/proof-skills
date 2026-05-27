---
task_id: lookup-empty-response
expected_max_score: 1
failure_mode: empty_response
notes: |
  Rubric §1: response is empty (no lemma name, no signature). Mathlib
  lookup must produce a citable name.
---

# Task

Name a Mathlib lemma bounding `(s ∪ t).card` by `s.card + t.card`
and show its type signature.

# Response

There are many lemmas in Mathlib about cardinality of unions of
finite sets. The bound you want is standard and provable from
inclusion-exclusion.
