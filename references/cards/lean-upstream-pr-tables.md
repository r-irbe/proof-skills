---
name: "lean-upstream-pr-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-upstream-pr-handbook.md."
generated_from: "references/handbooks/lean-upstream-pr-handbook.md"
skill_ref: "skills/lean-upstream-pr/SKILL.md"
---

# `lean-upstream-pr` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-upstream-pr-handbook.md`](../handbooks/lean-upstream-pr-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Reusable general lemma inside domain repo | Generalize + Mathlib4 style pass | Strip project wrappers, minimize typeclasses, verify `#lint` |
| Multi-file upstream contribution | Stacked PR split (`<= 300 LOC` per PR) | Track dependencies via `- [ ] depends on: #NNN` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Check if lemma already exists in Mathlib | `lean_search(source: "loogle" | "code")` |
| Prepare Mathlib4 PR description & labels | `feat(Topic): summary` + AI disclosure | Require explicit human approval before `gh pr create` |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| `#lint` fails on `docBlame` or `unusedArguments` | Missing `/-- ... -/` docstring or extra typeclass | Add Mathlib docstring and prune unused `[Fintype ]` hypotheses |
| Upstream CI rejects `autoImplicit` reliance | Implicit free variables in signature | Bind all universe and type parameters explicitly |
