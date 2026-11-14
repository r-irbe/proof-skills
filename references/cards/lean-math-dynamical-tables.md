---
name: "lean-math-dynamical-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-math-dynamical-handbook.md."
generated_from: "references/handbooks/lean-math-dynamical-handbook.md"
skill_ref: "skills/lean-math-dynamical/SKILL.md"
---

# `lean-math-dynamical` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-math-dynamical-handbook.md`](../handbooks/lean-math-dynamical-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| `V (step s) <= V s` (Discrete Lyapunov) | `linarith` / `nlinarith` / `omega` | `unfold V step; nlinarith [sq_nonneg ...]` |
| `forall  n, Inv (step^[n] s)` | `Nat.rec` / `Function.Iterate.rec` | `induction n with | zero => exact h0 | succ n ih => exact h_step _ ih` |
| `V (step^[n] s) <= V s` | Monotone trajectory induction | `induction n with | zero => rfl | succ n ih => exact le_trans (h_dec _) ih` |
| Cusp catastrophe equilibrium `4 x + 2 a x + b = 0` | Polynomial discriminant / `ring` | `nlinarith` / `ring` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Prove non-negativity of quadratic Lyapunov energy | `positivity` | Handles sums of squares `x^2 + y^2 >= 0` |
| Prove single-step Lyapunov decrease `V(f(x)) - V(x) <= 0` | `nlinarith [sq_nonneg (x - x_eq)]` | Pass explicit square witnesses to `nlinarith` |
| Unfold `n`-step iterate `f^[n + 1] x` | `rw [Function.iterate_succ_apply']` | Rewrites `f^[n+1] x` to `f (f^[n] x)` for inductive step |
| Discharge discrete scaled-integer barrier certificate | `omega` | Ensure all `Nat.sub` terms have `b <= a` guards |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| `Function.iterate_succ_apply`Associativity mismatch | `f^[n+1] x = f^[n] (f x)` vs `f (f^[n] x)` | Use `Function.iterate_succ_apply'` (primed) to put `f` on the outside |
| `nlinarith` fails on cubic/quartic potential | `nlinarith` only multiplies two existing inequalities | Factor into squares via `have : ... = (x^2 - a)^2 := by ring` + `positivity` |
| Vacuous stability from `Nat.sub` truncation | `V : S -> Nat` truncates `V(s') - V(s)` at `0` | Write decrease as `V (step s) +  <= V s` instead of `V s - V (step s) >= ` |
