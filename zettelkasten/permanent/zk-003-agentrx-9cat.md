---
id: zk-003
title: AgentRx 9-category failure taxonomy
created: 2026-05-27
updated: 2026-11-15
type: permanent
tags: [agent-fleet, taxonomy, evals]
refs:
  - zk-006
  - zk-007
  - zk-009
status: validated
confidence: high
---

# AgentRx 9-category failure taxonomy

**Claim.** AgentRx fixes a nine-label space for agent failures so that eval fixtures, post-mortems, and judge prompts speak one shared vocabulary: (1) instruction/plan adherence, (2) invention/hallucination, (3) invalid tool invocation, (4) misinterpretation of tool output, (5) intent-plan misalignment, (6) under-specified user intent, (7) intent not supported, (8) guardrails false-positive, and (9) system/infra failure.

**Evidence.** Grounded in the AgentRx failure classification standard and `GUARDRAILS.md`. For Lean skills specifically, categories **2** (invented lemmas / hallucinated Mathlib names) and **4** (mis-reading `lake build` or `lean_diagnostics` output) dominate observed failure modes and require dedicated eval fixtures in `scripts/eval/cases/`.

**Implication.** Three downstream uses lock in. The eval-target matrix in [[zk-006]] uses these labels as the failure-mode signature channel; the Glicko-2 / ELO ranking scheme in [[zk-007]] requires a stable label space to compute per-category win-rates; and the consolidation rubric [[zk-009]] treats two skills that address the same AgentRx category as merge candidates.

See also: [[zk-006]], [[zk-007]], [[zk-009]].
