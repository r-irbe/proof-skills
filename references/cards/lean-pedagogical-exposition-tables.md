---
name: "lean-pedagogical-exposition-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-pedagogical-exposition-handbook.md."
generated_from: "references/handbooks/lean-pedagogical-exposition-handbook.md"
skill_ref: "skills/lean-pedagogical-exposition/SKILL.md"
---

# `lean-pedagogical-exposition` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-pedagogical-exposition-handbook.md`](../handbooks/lean-pedagogical-exposition-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Verified Lean 4 proof with inscrutable tactic script | Structured Mathematical Proof Narrative | Map `have`/`calc`/`induction` landmarks to human mathematical intuition |
| Type-theoretic encoding (`Fin n -> `, `Subtype`) | Standard mathematical notation translation | Render clean LaTeX (`x \in \mathbb{R}^n`) with side-by-side Lean anchor |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Turn a formal Lean module into a textbook chapter | `editor.md` + `math-pedagogy-author` overlay | Include motivation, geometric intuition, proof architecture diagram, and Lean table |
| Explain *why* a precondition is needed | Counterexample-driven exposition | Show concrete failure witness when hypothesis `h` is dropped |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Prose reads like line-by-line tactic transliteration ('First we `rw`...') | Tactic-level noise leaked into exposition | Summarize algebraic rewrites as conceptual equations (`calc` chain) |
| Exposition omits key technical hypothesis present in Lean | Silent simplification drift | List every Lean hypothesis explicitly in the theorem statement box |
