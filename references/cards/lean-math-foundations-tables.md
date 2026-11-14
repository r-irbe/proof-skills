---
name: "lean-math-foundations-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-math-foundations-handbook.md."
generated_from: "references/handbooks/lean-math-foundations-handbook.md"
skill_ref: "skills/lean-math-foundations/SKILL.md"
---

# `lean-math-foundations` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-math-foundations-handbook.md`](../handbooks/lean-math-foundations-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| `(a : ) = b` in `Subtype P` | `Subtype.ext` | `ext; simp only [...]` |
| `Quotient.mk s a = Quotient.mk s b` | `Quotient.sound` / `Quotient.eq` | `apply Quotient.sound; ...` |
| `(f :  -> ) = g` | `funext` | `funext x; ...` |
| `l (a : ) <= b <-> a <= u b` | `GaloisConnection l u` | `exact gc.le_iff_le` |
| Algebraic identity in `[CommRing R]` | `ring` | `by ring` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Prove two functions or sets equal | `ext x` | Chains `funext`, `Set.ext`, `Subtype.ext` |
| Lift function to quotient `Quotient s` | `Quotient.lift f (fun a b hab => ...)` | Requires congruence proof |
| Induct over quotient elements | `induction q using Quotient.inductionOn` | Reduces goal to representatives |
| Synthesize algebraic typeclass instance | `infer_instance` | Avoids manual constructor spelling |
| Use classical decidability locally | `classical` (tactic) | Scopes `Classical.propDecidable` to current goal |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| `failed to synthesize Decidable` | Predicate in `Prop` lacks computational decision procedure | Run `classical` tactic inside proof or add `[DecidablePred P]` |
| Typeclass diamond (`type mismatch` on instances) | Two non-defeq paths to same base carrier class | Use `extends` flat hierarchy or `convert h using 1` |
| `funext_iff` fails to rewrite | Function is dependent `(x : ) ->  x` | Use `Department.funext` (`funext x`) instead of `funext_iff` |
