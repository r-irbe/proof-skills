---
name: "lean-egraph-cpsat-superopt-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-egraph-cpsat-superopt-handbook.md."
generated_from: "references/handbooks/lean-egraph-cpsat-superopt-handbook.md"
skill_ref: "skills/lean-specification/SKILL.md"
---

# `lean-egraph-cpsat-superopt` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-egraph-cpsat-superopt-handbook.md`](../handbooks/lean-egraph-cpsat-superopt-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Common subexpressions across e-graph | `CP-SAT Exact DAG Extraction` | `model := CpModel(); model.Minimize(sum(cost * x)); solver.Solve(model)` |
| Candidate rewrite rule `lhs -> rhs` | `Dual-Certified Rewriting` | `theorem sound : eval lhs = eval rhs; theorem cost : cost rhs <= cost lhs` |
| Bitwise logic simplification | `3-Gate Zhegalkin Normal Form` | `theorem maj_zhegalkin : (a &&& (b ^^^ c)) ^^^ (b &&& c) = (a &&& b) ^^^ (a &&& c) ^^^ (b &&& c)` |
| Fixed schedule constant folding | `E-Graph Equality Saturation` | `egg_saturate rules [const_fold, shift_fold]; extract_dag` |
| SWAR lane bit-budget allocation | `CP-SAT Knapsack Model` | `model.Add(sum(lane_widths) <= 62); solver.Solve(model)` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Extract sharing-optimal DAG from e-graph | `CP-SAT ILP solver` | Solves 0-1 integer model minimizing shared node cost with acyclicity levels |
| Prove semantic soundness of rewrite rule | `omega / bitwise lemmas` | Discharges algebraic equivalence without `bv_decide` or `native_decide` |
| Prove cost reduction under KernelModel | `by decide` | Verifies `whnfCost rhs <= whnfCost lhs` counting AST nodes and scalar limbs |
| Synthesize optimal schedule unrolling | `CP-SAT sequence formulation` | Finds optimal operation ordering minimizing peak register pressure |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Tree-greedy extractor increases instruction count | Greedy tree extraction duplicates shared subterms | Use CP-SAT sharing-aware DAG extractor with e-class activation variables |
| Cycle detected in extracted e-graph expression | E-graph rewrite cycles permitted circular dependency | Add topological level constraints `l_c >= l_child + 1` in CP-SAT model |
| `Nat` subtraction underflow in rewrite proof | Truncated subtraction hazard on `Nat` | Guard rewrite with hypothesis `b <= a` or use bitwise XOR masking |
| Solver timeout on massive e-graphs | Excessive e-class count without pruning | Apply e-graph class compaction and greedy domain tightening before CP-SAT |
