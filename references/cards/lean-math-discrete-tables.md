---
name: "lean-math-discrete-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-math-discrete-handbook.md."
generated_from: "references/handbooks/lean-math-discrete-handbook.md"
skill_ref: "skills/lean-math-discrete/SKILL.md"
---

# `lean-math-discrete` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-math-discrete-handbook.md`](../handbooks/lean-math-discrete-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| `sum x in s, f x = sum x in s, g x` | `Finset.sum_congr` | `refine Finset.sum_congr rfl (fun x hx => ?_)` |
| `sum x in s, f x = sum y in t, g y` | `Finset.sum_bij` | `refine Finset.sum_bij (fun x hx => i x) ?_ ?_ ?_ ?_` |
| `(s : Finset ) = t` | `Finset.ext` | `ext x; simp only [Finset.mem_...]` |
| `G.Adj u v -> G.Adj v u` | `SimpleGraph.adj_symm` | `exact G.symm h` |
| DAG / poset transitivity `a <= c` | `le_trans` | `exact le_trans hab hbc` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Split a finite sum at one element `a in s` | `rw [<- Finset.add_sum_erase _ _ ha]` | Isolates `f a` from `s.erase a` |
| Swap nested finite sums `sum i, sum j` | `rw [Finset.sum_comm]` | Works on any `Finset` product |
| Prove finite cardinality identity | `simp only [Finset.card_...]; omega` | Combine `Finset.card` lemmas with `omega` |
| Decide finite graph/combinatorial property | `by decide` | Works when vertices have `[Fintype V] [DecidableEq V]` |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Off-by-one in `Finset.range n` | `Finset.range n` is `[0, n)`, not `[1, n]` | Use `Finset.Icc 1 n` for closed `1..n` intervals |
| `Finset.sum_union` unsolved goal | Missing `Disjoint s t` proof | Discharge `Disjoint s t` via `Finset.disjoint_left.mpr` |
| `SimpleGraph` self-loop error | `SimpleGraph` is irreflexive (`loopless`) | Add `h : u != v` before constructing adjacency |
