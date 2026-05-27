---
task_id: lookup-coq-name
expected_max_score: 1
failure_mode: wrong_library
notes: |
  Rubric §1: cites a name from a different library (Coq/Lean3) without
  flagging the mismatch. `Finset.cardinal_union_le_addition` is not a
  Mathlib (Lean 4) name; the response treats it as if it were.
---

# Task

Name a Mathlib lemma bounding `(s ∪ t).card` by `s.card + t.card`
and show its type signature.

# Response

The standard lemma is:

```
Finset.cardinal_union_le_addition (s t : Finset α) :
    Cardinal.mk (s ∪ t : Set α) ≤ Cardinal.mk s + Cardinal.mk t
```

This is the classical inclusion-exclusion-style bound, available in
the `Finset` namespace.
