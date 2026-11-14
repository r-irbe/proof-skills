---
name: "lean-setup-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-setup-handbook.md."
generated_from: "references/handbooks/lean-setup-handbook.md"
skill_ref: "skills/lean-setup/SKILL.md"
---

# `lean-setup` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-setup-handbook.md`](../handbooks/lean-setup-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| New Lean 4 repository bootstrap | `lean-skills init` / `elan` + `lean-toolchain` | Pin exact `leanprover/lean4:v4.x.y` and `autoImplicit = false` |
| Lakefile configuration (`lakefile.toml` / `lakefile.lean`) | `moreLeanArgs = #["-DautoImplicit=false"]` | Enforce `autoImplicit false` project-wide |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Configure `lean-lsp` MCP across IDE agents | `bin/lean-lsp-mcp.js` + `lean-serve-broker` | Auto-verify WASM SHA-256 pin via `scripts/check-engine-pin` |
| Align local toolchain with `lean-toolchain` file | `elan show` + `lake exe cache get` | Always read `lean-toolchain` directly rather than prose docs |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| `unknown package 'Mathlib'` on build | `lake-manifest.json` uninitialized or cache missing | Run `lake update` (or `lake exe cache get` on pinned manifest) |
| Silent typo turns into universally quantified variable | `autoImplicit` left enabled | Set `autoImplicit = false` in both `lakefile` and module headers |
