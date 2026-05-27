---
task_id: nested-decide-on-large-fin
expected_max_score: 2
failure_mode: decide_on_large_term
notes: |
  Rubric §2 fires: uses `decide` on `Fin 100000` which will OOM the kernel.
---

# Task

Prove that the 99999th element of `Fin 100000` is less than the cardinality.

# Response

theorem fin_lt : (⟨99999, by decide⟩ : Fin 100000).val < 100000 := by
  decide

