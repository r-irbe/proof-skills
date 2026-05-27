---
task_id: uses-banned-search-tactic
expected_max_score: 2
failure_mode: banned_search_tactic
notes: |
  Rubric §2 fires: production-grade proof submits with `exact?` / `apply?` discovery tactic in place.
---

# Task

Provide a polished proof for `theorem foo : 2 + 2 = 4`. Production code only — no discovery tactics in the final form.

# Response

theorem foo : 2 + 2 = 4 := by
  exact?  -- found by suggestion

