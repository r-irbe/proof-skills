---
task_id: lookup-fabricated-lemma
expected_max_score: 1
failure_mode: fabricated_name
notes: |
  Rubric §1: names a fabricated lemma (no such declaration exists in
  Mathlib). `Finset.card_disjoint_union_le` is not a real Mathlib lemma —
  the closest real lemma is `Finset.card_union_le` (which is what the
  task asks for).
---

# Task

Name a Mathlib lemma bounding `(s ∪ t).card` by `s.card + t.card`
and show its type signature.

# Response

The relevant lemma is:

```lean
theorem Finset.card_disjoint_union_le (s t : Finset α) :
    (s ∪ t).card ≤ s.card + t.card := by
  apply Finset.card_disjoint_union
```

It's in the `Mathlib.Data.Finset.Lattice` file. The proof goes
through because disjoint union is the worst case.
