---
id: zk-006
title: Four orthogonal skill evaluation targets
created: 2026-05-27
updated: 2026-11-15
type: permanent
tags: [evals, methodology]
refs:
  - zk-003
  - zk-005
  - zk-007
status: validated
confidence: high
---

# Four orthogonal skill evaluation targets

**Claim.** Skill evaluation decomposes into four orthogonal targets, each with its own metric and failure signature: **Instructions** (adherence to declared G-rules), **Skills** (dispatch routing + L0/L1/L2 contract fidelity), **Coding outputs** (generated Lean 4 compiles cleanly with zero `sorry` and clean axiom closure), and **Trajectories** (multi-step workflows reproduce deterministically). Conflating them loses ~25 percentage points of diagnostic signal.

**Evidence.** Enforced across `scripts/eval/cases/*.yaml`, `scripts/eval/run_eval.py`, and `tests/test_cross_language_fidelity_parity.py`, separating routing assertions from kernel compilation checks.

**Implication.** Three rules follow. (1) Every eval case in `scripts/eval/cases/` declares its target explicitly. (2) Aggregation stays per-skill and per-target rather than collapsing disparate axes into one opaque average. (3) Glicko-2 ranking in [[zk-007]] tracks rating channels per target, TDAD in [[zk-005]] authors fixtures per target, and failure tags follow AgentRx in [[zk-003]].

See also: [[zk-003]], [[zk-005]], [[zk-007]].
