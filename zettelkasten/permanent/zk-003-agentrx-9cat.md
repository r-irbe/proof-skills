---
id: zk-003
title: AgentRx 9-category failure taxonomy
created: 2026-05-27
updated: 2026-05-27
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

**Claim.** AgentRx (ADR-0039 §"AgentRx") fixes a nine-label space for
agent failures so that eval fixtures, post-mortems, and judge prompts
all speak the same vocabulary. The categories are: (1)
instruction/plan adherence, (2) invention/hallucination, (3) invalid
tool invocation, (4) misinterpretation of tool output, (5) intent–plan
misalignment, (6) under-specified user intent, (7) intent not
supported, (8) guardrails false-positive, (9) system/infra failure.

**Evidence.** Lifted from `lab/filab-survey/01-adrs.md` §5.2 and
mirrored in `02-conventions.md` §3.2. For Lean skills specifically,
the survey predicts categories **2** (invented lemmas / hallucinated
Mathlib names) and **4** (mis-reading `lake build` output) as the
high-frequency classes — worth pre-budgeting fixtures for. Authority:
ADR-0039 (Accepted) under `filab-doc-experiment/adrs/`.

**Implication.** Three downstream uses lock in. The eval-target
matrix in [[zk-006]] uses these labels as the "failure-mode signature"
channel; the non-deterministic ELO scheme in [[zk-007]] needs a
stable label space to compute per-category win-rates; the
consolidation rubric [[zk-009]] treats two skills that address the
same AgentRx category as merge candidates. Any failure report in
`lab/` should tag findings with exactly one of these nine labels — no
free-form alternates.

See also: [[zk-006]], [[zk-007]], [[zk-009]].
