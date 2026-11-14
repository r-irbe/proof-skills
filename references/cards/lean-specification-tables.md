---
name: "lean-specification-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-specification-handbook.md."
generated_from: "references/handbooks/lean-specification-handbook.md"
skill_ref: "skills/lean-specification/SKILL.md"
---

# `lean-specification` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-specification-handbook.md`](../handbooks/lean-specification-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Informal claim `If X then Y` | 3-Part Spec (Preconditions, Postconditions, Witness) | Include explicit non-vacuity `example` / `exists ` witness |
| Arithmetic invariant over differences/ratios | Truncation-safe carrier selection | Guard `b <= a` on `Nat` or state over `Int` / `` / `` |
| Computable algorithm + algebraic theory | Abstraction-Concrete Duality spec | State `Prop` theorems on abstract `specFn`; link `fastFn` via `@[csimp]` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Design a theorem statement resistant to vacuity | `@lean-specification` + `@counterexample-first-proving` | Verify preconditions are jointly satisfiable before handing to `prover` |
| Avoid over-concrete fixed-arity signatures | Collection/index abstraction (`List `, `Fin n -> `) | Prevents `FIDELITY-08` (`a0 a1 a2 a3` anti-pattern) |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Theorem proved trivially because hypotheses contradict | Missing non-vacuity witness (`Part 3`) | Add constructive `example` instantiating all hypotheses simultaneously |
| Downstream callers cannot compose concrete bit-packed signature | Representation leaked into `Prop` spec | Factor abstract algebraic interface and push bit-packing behind `@[csimp]` |
