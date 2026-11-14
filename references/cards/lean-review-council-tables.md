---
name: "lean-review-council-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-review-council-handbook.md."
generated_from: "references/handbooks/lean-review-council-handbook.md"
skill_ref: "skills/lean-review-council/SKILL.md"
---

# `lean-review-council` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-review-council-handbook.md`](../handbooks/lean-review-council-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| High-stakes formalization batch or milestone merge | 5-Member Council (`, , , , `) + RALPH loop | Independent blind reviews aggregated by Chair `` |
| Disagreement between `` (Faithfulness) and `` (Tactics) | Structured Divergence Resolution (SDR) | `` (Soundness) & `` (Faithfulness) hold hard veto power over style |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Convene adversarial multi-agent proof review | Instantiate `auditor.md` with `council-{sigma,phi,nu,tau,omega}` overlays | Keep all 5 council seats strictly read-only |
| Verify novelty vs existing Mathlib lemmas | Seat `` (`council-nu-novelty`) `lean_search` audit | Flag re-proved standard lemmas for replacement |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Council approves theorem with unguarded `Nat` truncation | Seat `` skipped boundary witness check | Mandate `FIDELITY-01..08` deterministic precheck before council vote |
| RALPH loop exceeds 3 iterations without convergence | Specification ambiguity rather than tactic defect | Escalate specification dispute to human / `specifier` ADR |
