---
name: "lean-blueprint-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-blueprint-handbook.md."
generated_from: "references/handbooks/lean-blueprint-handbook.md"
skill_ref: "skills/lean-blueprint/SKILL.md"
---

# `lean-blueprint` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-blueprint-handbook.md`](../handbooks/lean-blueprint-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Declaration ready for dependency tracking | `@[blueprint "lem:foo" (statement := /-- ... -/)]` | Annotate lean declaration and link upstream lemma labels |
| Large multi-directory Lean codebase | 8-wave formalization breakdown + DAG census | Extract Layer 0..4 critical path via `lean_module_hierarchy` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Scaffold a LeanBlueprint / LeanArchitect tree | `lean_blueprint(action: "scaffold" | "skeleton")` |
| Launch interactive DAG / proof-walk visualizer | DAG export + marginalia mapping | Bind nodes to verified `.ilean` declarations |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Cyclic dependency between blueprint nodes | Forward lemma reference contradicts Lean import order | Run `lean_module_hierarchy` and split shared definitions into `.Defs` |
| Orphan `@[blueprint]` tag not appearing in graph | Label omitted from chapter `\lean{...}` / root import | Ensure module is imported by root `<Project>.lean` |
