---
name: "lean-research-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-research-handbook.md."
generated_from: "references/handbooks/lean-research-handbook.md"
skill_ref: "skills/lean-research/SKILL.md"
---

# `lean-research` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-research-handbook.md`](../handbooks/lean-research-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Need exact Mathlib lemma for a subgoal type | `lean_search(source: "loogle" | "code")` |
| Unfamiliar mathematical domain ontology | Concept-lattice epistemic mapping | Map core carriers, morphisms, and load-bearing theorems before specifying |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Find theorem across Mathlib, Reservoir, and indexed books | Discovery ladder (`code -> loogle -> ontology -> book -> arxiv`) | Verify hit compiles via `lean_lookup_symbol` / `lean_exec` |
| Map cross-ITP equivalent of Coq/Isabelle theorem | `lean_search(source: "concordance")` | Hand off porting work to `@itp-cross-porting` |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Hallucinated Mathlib4 lemma name from Lean 3 era | Uncertified memory recall instead of live tool lookup | Always confirm symbol existence via `lean_lookup_symbol` |
| Broad text search returns 500+ noisy matches | Unconstrained keyword query | Use Loogle type-pattern query (`?a -> ?b`) or module-scoped search |
