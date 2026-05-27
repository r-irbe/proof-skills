---
task_id: contradictory-blueprint
expected_max_score: 2
failure_mode: self_contradiction
notes: |
  Rubric §2 fires: the doc contradicts itself across sections (claims
  the proof is one-step in §1 and induction-over-list in §3).
---

# Task

Write a `lean-blueprint`-style blueprint stub for the theorem
`List.length_append : (l₁ ++ l₂).length = l₁.length + l₂.length`.
Include: statement, dependencies, proof sketch, regeneration command.

# Response

## Statement
`List.length_append : (l₁ ++ l₂).length = l₁.length + l₂.length`

## Dependencies
- `List.length_cons`
- `List.append_nil`
- `Nat.add_succ`

## Proof sketch
Single tactic `simp` discharges the goal — the simp lemmas
`List.length_append`, `List.length_cons`, `Nat.add_succ` close it
in one step.

## Regeneration command
```
leanblueprint web
```

## Detailed proof
By induction on `l₁`:
- Base case `l₁ = []`: `([] ++ l₂).length = l₂.length`
  and `[].length + l₂.length = 0 + l₂.length = l₂.length` — close with
  `Nat.zero_add`.
- Inductive case `l₁ = a :: t`: rewrite with `List.cons_append`,
  `List.length_cons`, then apply the induction hypothesis. Use
  `Nat.succ_add` to align.
