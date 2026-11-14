---
name: "lean-build-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-build-handbook.md."
generated_from: "references/handbooks/lean-build-handbook.md"
skill_ref: "skills/lean-build/SKILL.md"
---

# `lean-build` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-build-handbook.md`](../handbooks/lean-build-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Single edited module `Foo/Bar.lean` | `lake build Foo.Bar` or `lake env lean Foo/Bar.lean` | Compile narrowest target first before full `lake build` |
| Fresh clone of Mathlib-dependent project | `lake exe cache get` -> `lake build` | Never compile Mathlib from source on CI/workstations |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Inspect live errors without spawning duplicate `lake serve` | `lean_diagnostics` via `lean-serve-broker` | Attach to singleton broker (`CONV-LEAN-SERVE-SINGLETON`) |
| Recover from stale `.olean` hash mismatch | `lake build <Target>` (or `lake clean` as last resort) | Rebuild upstream `.Defs` module first |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| `object file ... of module ... does not exist` | Edited upstream dependency not yet rebuilt | Run `lake build <UpstreamModule>` |
| Multiple `lean --server` processes exhausting RAM | Direct `lake serve` spawned outside broker | Stop stray servers via `lean-serve-broker stop` |
