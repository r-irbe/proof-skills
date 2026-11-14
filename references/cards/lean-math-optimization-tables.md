---
name: "lean-math-optimization-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-math-optimization-handbook.md."
generated_from: "references/handbooks/lean-math-optimization-handbook.md"
skill_ref: "skills/lean-math-optimization/SKILL.md"
---

# `lean-math-optimization` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-math-optimization-handbook.md`](../handbooks/lean-math-optimization-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| `ConvexOn  s f` | `ConvexOn` combinators | `apply ConvexOn.add hf hg` |
| `T v - T w <=  * v - w` (Bellman contraction) | `ContractingWith` | `refine h, fun v w => ?_` |
| `u (a*, b) >= u (a, b)` (Nash equilibrium) | Best-response inequality | `unfold isNash; linarith` (or `omega` for finite payoff matrices) |
| Weak duality `primal_val <= dual_val` | Lagrangian saddle inequality | `calc primal <= L x y := ... _ <= dual := ...` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Prove convex combination inequality `t * x + (1 - t) * y` | `nlinarith [ht0, ht1]` | Pair `0 <= t` and `t <= 1` with `nlinarith` |
| Invoke Banach fixed-point theorem for Bellman operator | `ContractingWith.fixedPoint_unique` | Requires `[CompleteSpace E]` and `[Nonempty E]` |
| Verify finite-game dominance or minimax bound | `omega` / `decide` | Use scaled-integer payoffs when working in core-only or discrete lanes |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| `iInf` / `sSup` inequality fails on `Real` | `Real` is only `ConditionallyCompleteLinearOrder` | Supply `BddBelow s` / `BddAbove s` and `s.Nonempty` proofs |
| Discount factor `` division error in `1 / (1 - )` | `1 -  != 0` not in context | Derive `have : 0 < 1 -  := by linarith` then `positivity` + `field_simp` |
