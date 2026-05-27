---
task_id: lookup-wrong-signature
expected_max_score: 2
failure_mode: wrong_signature
notes: |
  Rubric §2: real lemma name in correct namespace, but wrong type
  signature. `Finset.card_union_le` does NOT take a disjointness
  hypothesis (that's `Finset.card_disjoint_union`, which gives equality);
  the LE version has no extra hypotheses.
---

# Task

Name a Mathlib lemma bounding `(s ∪ t).card` by `s.card + t.card`
and show its type signature.

# Response

The Mathlib lemma is:

```lean
theorem Finset.card_union_le (s t : Finset α) (h : Disjoint s t) :
    (s ∪ t).card ≤ s.card + t.card
```

The `Disjoint` hypothesis ensures the bound holds; without it the
union would double-count the intersection.
