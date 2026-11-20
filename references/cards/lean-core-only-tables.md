---
name: "lean-core-only-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-core-only-handbook.md."
generated_from: "references/handbooks/lean-core-only-handbook.md"
skill_ref: "skills/lean-core-only/SKILL.md"
---

# `lean-core-only` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-core-only-handbook.md`](../handbooks/lean-core-only-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Linear arithmetic over `Nat` / `Int` without Mathlib | `omega` | Replaces Mathlib `linarith` in Core-only lanes |
| Congruence + E-matching + case-splitting without Mathlib | `grind` | Replaces `aesop` / `congr` chains in Lean v4.27+ Core |
| Decidable finite identity without `Lean.ofReduceBool` | `kernel_decide` (`rfl | decide +kernel |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Prove theorems with zero Mathlib dependency | `Std` + `Init` (`Nat`, `Int`, `List`, `Array`, `BitVec`) | Use `lean_search(source: "code")` scoped to `Init`/`Std` |
| Replace `ring` in Core-only polynomial identities | `Nat`/`Int` normalization lemmas or `grind` | Avoid importing `Mathlib.Tactic.Ring` in Core-only artifacts |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| `unknown module prefix 'Mathlib'` | Mathlib import pasted into Core-only package | Remove `Mathlib.*` import; use `Init`/`Std` lemmas + `omega`/`grind` |
| `unknown tactic 'linarith'` or `'ring'` | Mathlib tactic invoked in Core-only lane | Use `omega` (linear) or `grind` / explicit `Nat` algebra lemmas |
