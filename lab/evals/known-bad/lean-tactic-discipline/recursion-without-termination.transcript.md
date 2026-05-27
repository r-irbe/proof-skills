---
task_id: recursion-without-termination
expected_max_score: 2
failure_mode: missing_termination_proof
notes: |
  Rubric §2 fires: definition uses general recursion but provides no `termination_by` / `decreasing_by` clause; relies on Lean's auto-inference which is brittle.
---

# Task

Define a recursive function `collatz_steps : ℕ → ℕ` that counts steps to reach 1 under the Collatz iteration. Use sound recursion discipline.

# Response

def collatz_steps : Nat → Nat
  | 1 => 0
  | n => if n % 2 = 0 then 1 + collatz_steps (n / 2)
                       else 1 + collatz_steps (3 * n + 1)

