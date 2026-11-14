---
name: "lean-retro-methodology-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-retro-methodology-handbook.md."
generated_from: "references/handbooks/lean-retro-methodology-handbook.md"
skill_ref: "skills/lean-retro-methodology/SKILL.md"
---

# `lean-retro-methodology` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-retro-methodology-handbook.md`](../handbooks/lean-retro-methodology-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Completed proof wave or refactor campaign | RETRO 5-step loop (`Refactor-Extract-Test-Refine-Optimize`) | Mine recurring tactic bottlenecks into reusable lemmas/rules |
| Reusable insight discovered during proving/review | Luhmann Zettelkasten note (`fleeting -> literature -> permanent`) | Link bidirectionally with `ZK-` IDs and declaration anchors |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Prevent repeating the same 20-step proof struggle next wave | Extract tactic phrasebook row + static lint rule | Update handbook table and regenerate `handbook-tables.v1.json` |
| Curate permanent knowledge notes without confidential leaks | `gardener.md` + `lean-retro-facilitator` | Keep public `proof-skills` notes strictly project-agnostic |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Retrospective produces vague process wishes | Findings not bound to measured incidents | Bind every new rule/template change to a concrete failure or speedup metric |
| Orphan Zettelkasten notes with zero inbound/outbound links | Skipped index integration | Run Zettelkasten link check before closing `gardener` turn |
