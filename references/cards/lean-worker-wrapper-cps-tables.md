---
name: "lean-worker-wrapper-cps-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-worker-wrapper-cps-handbook.md."
generated_from: "references/handbooks/lean-worker-wrapper-cps-handbook.md"
skill_ref: "skills/lean-proof-refactor/SKILL.md"
---

# `lean-worker-wrapper-cps` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-worker-wrapper-cps-handbook.md`](../handbooks/lean-worker-wrapper-cps-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Typeclass dictionaries in tight recursor | `Worker/Wrapper Monomorphization` | `def worker (x : Nat) : Nat; @[inline] def wrapper [C] (x) := worker x` |
| Merge branch subterms duplicating AST | `Join Point Abstraction` | `let joinPt := fun acc => ...; if c then joinPt a else joinPt b` |
| Inductive constructor match in loop body | `SpecConstr Specialization` | `def workerA ...; def workerB ...; match c with | .A => workerA | .B => workerB` |
| Higher-order continuation closure `(a -> b) -> b` | `Defunctionalized Inductive Cont` | `inductive Cont | halt | step (k : Cont); def applyCont : Cont -> a -> b` |
| Non-tail-recursive tuple re-boxing | `Tail-Call Scalar Accumulator` | `@Nat.rec (fun _ => Nat -> Nat -> Nat) (fun a b => a) (fun _ loop a b => loop (a+1) b)` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Apply Worker/Wrapper split | `Unpack structure at entry` | Keeps inner loop free of projections, dictionaries, and boxing |
| Establish Join Point in recursor | `let joinPt := fun ...` | Retains single shared subterm node in kernel pointer cache |
| Specialize call pattern (SpecConstr) | `Split into monomorphic workers` | Eliminates inner pattern matching and branching overhead |
| Defunctionalize closure continuation | `First-order inductive dispatch` | Replaces lambda closures with token constructor matching |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Excessive `instantiate_rev` overhead in kernel | Lambda abstractions with open bound variables in loop | Lift to top-level auxiliary definition or defunctionalize into first-order inductive type |
| Heap allocation inside recursor step | Constructor boxing `(a, b)` on each step | Unbox into separate scalar accumulator arguments in `@Nat.rec` |
| Typeclass projection cannot be reduced | Opaque dictionary in kernel | Supply explicit monomorphic instance or use Worker/Wrapper to eliminate typeclass before loop |
| Stack overflow on deep CPS reduction | Non-tail-recursive continuation chain | Convert continuation evaluator to tail-recursive accumulator loop |
