---
name: "lean-dependency-management-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-dependency-management-handbook.md."
generated_from: "references/handbooks/lean-dependency-management-handbook.md"
skill_ref: "skills/lean-dependency-management/SKILL.md"
---

# `lean-dependency-management` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-dependency-management-handbook.md`](../handbooks/lean-dependency-management-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| External package candidate on Reservoir | `lean_search(source: "reservoir")` | Check `lean-toolchain` match, license, and `0 sorry` status |
| Small external theorem slice on incompatible pin | Isolated `Vendor/<Pkg>/` vendoring | Preserve SPDX header, upstream URL + SHA, and run `lean_axiom_closure` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Bump `lean-toolchain` and Mathlib pin safely | `lake update` + `@lean-proof-repair` | Never hand-edit `lake-manifest.json` SHA hashes |
| Verify vendored code introduces no extra axioms | `@lean-verification-gate` | Audit transitive axioms of all vendored declarations |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| `lake update` version solver conflict | Transitive packages pin incompatible `lean-toolchain` | Align `lean-toolchain` to target Mathlib release tag first |
| Missing SPDX license on candidate repo | Unlicensed upstream code cannot be vendored | Halt vendoring and re-prove from mathematical literature |
