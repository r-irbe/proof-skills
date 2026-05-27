---
task_id: adversarial-exact-question-in-comment
expected_max_score: 5
failure_mode: none
notes: |
  Adversarial positive: the response narrates that `exact?` was used as
  scaffolding during development to FIND the lemma, but the final proof
  uses the explicit lemma name (no search tactic in the final code).
  A judge that keyword-matches on `exact?` will wrongly flag this.
  Score must be ≥ 4.
---

# Task

Prove that addition with zero on the right is the identity, following
proof-skill methodology.

```lean
theorem zero_right (n : Nat) : n + 0 = n := by
  sorry
```

# Response

Methodology trace:

1. During exploration I used `exact?` at the REPL to discover that
   `Nat.add_zero` is the relevant Mathlib lemma. (`exact?` is a
   scaffolding tactic — only used to find names, never shipped.)
2. The final proof replaces the search with the explicit lemma name.
3. Goal state before `exact`: `⊢ n + 0 = n`. One tactic suffices.

```lean
theorem zero_right (n : Nat) : n + 0 = n := by
  exact Nat.add_zero n
```

No banned search tactic in the final code; `exact?` is mentioned only
in prose as the discovery step.
