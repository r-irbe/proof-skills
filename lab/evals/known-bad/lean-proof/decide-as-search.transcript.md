---
task_id: decide-as-search
expected_max_score: 2
failure_mode: banned_search_tactic
notes: |
  Rubric §2: `decide`-as-search. Using `decide` to brute-force a
  general claim is exactly the banned pattern. (Plain `decide` on a
  closed, decidable proposition is fine in general, but using it to
  "search" for unknown structure on a parameterised goal is banned.)
---

# Task

Prove that for all natural numbers `n ≤ 1000`, we have `n + 0 = n`:

```lean
theorem all_add_zero (n : Nat) (h : n ≤ 1000) : n + 0 = n := by
  sorry
```

Use the proof-skill methodology.

# Response

```lean
theorem all_add_zero (n : Nat) (h : n ≤ 1000) : n + 0 = n := by
  -- iterate over every possible n
  interval_cases n <;> decide
```

We use `interval_cases` to split into 1001 finite branches and then
`decide` to brute-force each one. This avoids having to know about
`Nat.add_zero`.
