---
task_id: lookup-wrong-namespace
expected_max_score: 2
failure_mode: wrong_namespace
notes: |
  Rubric §2: real Mathlib lemma name but in the wrong namespace.
  `Set.card_union_le` exists for `Set.ncard`, but the task is about
  `Finset.card` — the correct namespace is `Finset.card_union_le`.
---

# Task

Name a Mathlib lemma bounding `(s ∪ t).card` by `s.card + t.card`
and show its type signature.

# Response

The lemma is:

```lean
theorem Set.card_union_le (s t : Set α) :
    (s ∪ t).card ≤ s.card + t.card
```

This bounds the cardinality of a union by the sum of cardinalities.
