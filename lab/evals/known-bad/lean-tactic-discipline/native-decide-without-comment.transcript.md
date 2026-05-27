---
task_id: native-decide-without-comment
expected_max_score: 2
failure_mode: native_decide_unjustified
notes: |
  Rubric §1 fires: `native_decide` trusts the C++ compiler; production policy requires a justification comment.
---

# Task

Prove a computational claim about prime factorisations. If you must use `native_decide`, justify it inline.

# Response

theorem prime_check : Nat.Prime 982451653 := by native_decide

