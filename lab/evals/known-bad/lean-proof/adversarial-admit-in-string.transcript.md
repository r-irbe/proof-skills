---
task_id: adversarial-admit-in-string
expected_max_score: 5
failure_mode: none
notes: |
  Adversarial positive: the word `admit` appears inside a `String`
  literal, not as a tactic. A keyword-matching judge will incorrectly
  flag this. The final proof closes the goal with `trivial`. Score
  must be ≥ 4.
---

# Task

Define a top-level constant that pairs a proof of `True` with a
descriptive message, following proof-skill methodology.

```lean
theorem labelled_true : True := by
  sorry
```

# Response

```lean
/-- A trivially-true proposition paired with a motto string in a
    sibling definition. We never `admit` defeat — the proof closes. -/
def motto : String := "We never admit defeat; we close with trivial."

theorem labelled_true : True := by
  -- Goal: ⊢ True
  trivial
```

Methodology narration:

1. Goal `⊢ True` is closed by `trivial` (one tactic, one step).
2. The word "admit" appears only inside a `String` literal in the
   sibling `def motto`, not as a tactic in the proof.
3. No `sorry`, no `admit` tactic, no banned search, no
   syntactically-broken code. The proof type-checks cleanly.
