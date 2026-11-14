---
name: "lean-mwe-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-mwe-handbook.md."
generated_from: "references/handbooks/lean-mwe-handbook.md"
skill_ref: "skills/lean-mwe/SKILL.md"
---

# `lean-mwe` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-mwe-handbook.md`](../handbooks/lean-mwe-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Elaborator error deep inside 1,500-LOC file | inline imports + axiomatize unrelated prereqs | Shrink to `<40 LOC` standalone Core-only `.lean` file |
| Expected compiler diagnostic regression test | `#guard_msgs in` | Pin exact error/info message text reproducibly |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Create upstream `leanprover/lean4` bug reproducer | Remove `import Mathlib` -> replace with minimal `structure`/`axiom` | Verify bug still reproduces under `lake env lean MWE.lean` |
| Isolate slow `simp` / typeclass loop | `set_option trace.Meta.synthInstance true in` in scratch MWE | Keep `trace.*` strictly in scratch MWE, never committed modules |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Replacing helper with `sorry` masks the bug | `sorry` synthesizes flexible universe/type | Use typed `opaque` or local hypothesis `(h : P)` instead of `sorry` in MWE |
| MWE still imports `Mathlib` umbrella | Transitive imports hide root cause | Inline only the 2-3 needed definitions until zero external imports remain |
