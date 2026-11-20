---
name: "lean-proof-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-proof-handbook.md."
generated_from: "references/handbooks/lean-proof-handbook.md"
skill_ref: "skills/lean-proof/SKILL.md"
---

# `lean-proof` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-proof-handbook.md`](../handbooks/lean-proof-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Definitional or closed finite equality `lhs = rhs` | `rfl` / `decide` / `norm_num` | `simp only [...]` |
| Linear `Nat` / `Int` inequality or equality | `omega` | `zify [h_le] at *; omega` |
| Polynomial identity over `[CommRing R]` | `ring` | `field_simp [hne]; ring` |
| Real / rational linear inequality | `linarith` | `nlinarith [sq_nonneg ...]` |
| Strict / weak sign bound `0 <= e` or `0 < e` | `positivity` | `linarith` |
| Quantified / inductive data structure goal | `induction x with ...` | `fun_induction f x` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Inspect live tactic state without `lake build` | `lean_goal(filePath, line, col, target: "tactic")` | Never insert `trace_state` into `.lean` files |
| Get ranked alternative proof candidates | `lean_goal(filePath, line, col, target: "altproof")` | Queries AltProof/kernel advisor |
| Unpack nested existential & conjunctive hypothesis `h` | `rcases h with x, hx1, hx2` | Or `obtain x, hx := h` |
| Chain multi-step equality and inequality calculation | `calc a = b := by ... _ <= c := by ...` | Isolates each step's heartbeat budget |
| Discharge routine propositional + simp subgoal | `aesop` or `grind` | Prefer explicit `simp only` when fast |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| `unknown identifier` | P1 | Check spelling/imports via `lean_search(source: "code")` |
| `type mismatch` | P2 | Inspect expected vs actual types via `lean_goal(target: "term")`; insert cast or `congrArg` |
| `failed to synthesize instance` | P3 | Check missing `[Fintype]` / `[DecidableEq]` binder or `open Classical in` |
| `motive is not type correct` | P4 | Generalize index expression `generalize hx : e = x` before `cases`/`induction` |
| `unsolved goals` | P5 | Inspect remaining subgoals via `lean_goal` and close each branch explicitly |
