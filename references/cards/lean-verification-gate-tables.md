---
name: "lean-verification-gate-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-verification-gate-handbook.md."
generated_from: "references/handbooks/lean-verification-gate-handbook.md"
skill_ref: "skills/lean-verification-gate/SKILL.md"
---

# `lean-verification-gate` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-verification-gate-handbook.md`](../handbooks/lean-verification-gate-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Exported theorem `theorem foo ...` before merge | `lean_axiom_closure` | Verify closure subset of `[propext, Classical.choice, Quot.sound]` |
| Module after `sorry` removal | `lake build <Module>` (cold replay) | Ensure `.olean` cache does not hide unchecked terms |
| File missing `set_option autoImplicit false` | Static enforcement lint | Add `set_option autoImplicit false` immediately after `import` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Lock down transitive axioms across corpus | `lean_axiom_closure` + `#print axioms` | Fail CI on `sorryAx`, custom `axiom`, or unapproved `Lean.ofReduceBool` |
| Verify proofs survive fresh kernel check | Cold replay (`lake clean` / targeted rebuild) | Quote scanned module & declaration counts in gate verdict |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| `depends on axiom sorryAx` | Unfinished subgoal or upstream `sorry` import | Locate culprit via `lean_axiom_closure` and route to `@lean-proof` |
| `depends on axiom Lean.ofReduceBool` | `native_decide` or `bv_decide` used in strict kernel lane | Replace with `kernel_decide` (`rfl |
