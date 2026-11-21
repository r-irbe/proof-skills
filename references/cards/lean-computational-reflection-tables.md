---
name: "lean-computational-reflection-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-computational-reflection-handbook.md."
generated_from: "references/handbooks/lean-computational-reflection-handbook.md"
skill_ref: "skills/lean-computational-reflection/SKILL.md"
---

# `lean-computational-reflection` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-computational-reflection-handbook.md`](../handbooks/lean-computational-reflection-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| `fastStep s = specStep s` on fixed schedule | `Computational Reflection` | `change denote env (compileFast s) = denote env (compileSpec s); rw [compile_sound]; rfl` |
| `impl n = spec n` over inductive domain | `Section 1/2/3 Induction Bridge` | `intro n; induction n with | zero => rfl | succ n ih => exact step_bridge n ih` |
| Monolithic 2,000-line tactic unfolding | `Reflective Normalization` | `have h : e = reify e' := rfl; rw [h, <- norm_sound]; rfl` |
| Equivalence of 64-round word circuits | `denote (compile c) = eval c` | `refine Circuit.soundness_reflection _ _ _ rfl` |
| Proof-cone isolation audit | `KERNEL-LAW-22 0-Prop Leakage` | `set_option pp.all true in #check impl -- verify 0 Prop dependencies` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Compress 3,000-line tactical proof into reflection | `rw [<- norm_sound]; rfl` | Replaces repetitive rewrite sequences with certified decision procedure |
| Enforce Section 1/2/3 Abstraction-Concrete Split | `#verso split directives` | Separates motives, concrete kernel implementation, and correctness proofs |
| Eliminate Prop leakage from computational core | `extract_pure_computation` | Audits runtime definitions to ensure zero equality witnesses or proof types |
| Verify reflection soundness via structural induction | `induction e with ... <;> (dsimp [simplify]; omega)` | Establishes `denote (norm e) = denote e` for all AST instances |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| `maximum recursion depth exceeded during rfl` | Reified AST contains unreduced non-constructor redexes | Ensure reified expressions use closed inductive constructors; avoid unfolding large lambdas |
| `Lean.ofReduceBool introduced in axiom check` | Usage of `native_decide` or `bv_decide` on proof path | Replace with computational reflection (`rfl`) or kernel-verified decision procedure |
| `motive is not type correct in Nat.rec` | Dependent motive in recursor carries `Prop` payload | Use monomorphic non-dependent motive; separate proof witness from computational accumulator |
| `kernel WHNF heartbeat timeout on step` | Complex branching step body inside recursor | Factor branch arms into top-level helper definitions (`stepAux`) or use branch-free ANF |
