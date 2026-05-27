---
task_id: adversarial-legit-decide
expected_max_score: 5
failure_mode: none
notes: |
  Adversarial positive: `decide` is used here on a CONCRETE, FINITELY
  CHECKABLE proposition (`7 ∣ 21`) where the kernel can verify the
  Decidable instance directly. This is NOT "decide-as-search" — there
  is no unbounded search; the proposition reduces. The rubric's §2
  ban on `decide` targets the pattern `interval_cases ... <;> decide`
  used as a brute-force search after splitting infinite cases.
  Score must be ≥ 4.
---

# Task

Prove that 7 divides 21.

```lean
example : 7 ∣ 21 := by
  sorry
```

# Response

```lean
example : 7 ∣ 21 := by
  decide
```

Methodology narration:

1. Goal `⊢ 7 ∣ 21` is a concrete proposition between two `Nat`
   literals. `Nat.decEq` and divisibility on `Nat` are `Decidable` and
   reduce in the kernel; no search is involved.
2. `decide` here is a *one-step kernel evaluation*, not a search
   tactic. The rubric's ban on `decide` targets the
   `interval_cases <;> decide` pattern (decide-as-search over a
   case split), which is absent here.
3. Single tactic, single step, closes the goal.

Contrast with the banned pattern:

```lean
-- BAD (decide-as-search): brute-forces over an unbounded variable.
example (n : Nat) (h : n < 100) : n + 1 > n := by
  interval_cases n <;> decide
```

The good case has no case split, no unbounded variable, and exists
because the term itself reduces.
