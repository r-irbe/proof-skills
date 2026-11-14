---
name: "lean-doc-sync-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-doc-sync-handbook.md."
generated_from: "references/handbooks/lean-doc-sync-handbook.md"
skill_ref: "skills/lean-doc-sync/SKILL.md"
---

# `lean-doc-sync` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-doc-sync-handbook.md`](../handbooks/lean-doc-sync-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Informal paper theorem `\begin{theorem}` | `requirements` mode -> 3-part spec | Extract Preconditions, Postconditions, and Witness for `@lean-specification` |
| Completed `@[blueprint]` graph | `scripts/lean/blueprint_to_report.py` | Compile dependency-ordered LaTeX report sections |
| Paper appendix theorem/module table | `scripts/lean/metric_sync.py` | Re-derive exact counts from compiled `.olean` census |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Verify every Lean name cited in LaTeX exists | `scripts/lean/check_citations.py` | Check `file:line` and identifier parity against compiled tree |
| Review documentation draft for undefined terms | `feedback` mode readability pass | Flag forward references, missing assumptions, and scope overclaims |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Broken `file.lean:123` citation in docs | Line numbers shifted after refactoring | Prefer declaration-anchored references and re-run `check_citations.py` |
| Prose claims theorem proved while `sorry` remains | Premature paper sync before `@lean-verification-gate` | Downgrade prose claim or block release until `0 sorry` |
