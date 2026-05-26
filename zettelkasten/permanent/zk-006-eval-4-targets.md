---
id: zk-006
title: Four eval targets per ADR-0039
created: 2026-05-27
updated: 2026-05-27
type: permanent
tags: [evals, methodology]
refs:
  - zk-003
  - zk-005
  - zk-007
status: validated
confidence: high
---

# Four eval targets per ADR-0039

**Claim.** ADR-0039 splits "skill evaluation" into four orthogonal
targets, each with its own metric and failure mode: **Instructions**
(adherence to declared skill policy), **Skills** (dispatch reliability
+ output-quality delta with/without the skill), **Coding outputs**
(generated Lean compiles, passes ACs, no `sorry`), and
**Trajectories** (multi-step workflows reproduce, e.g. SK-61 → SK-39 →
SK-10). Conflating them costs roughly 25pp of eval signal (R32 F1,
cited in ADR-0076 §Evidence).

**Evidence.** Table in `lab/filab-survey/01-adrs.md` §5.1. The
mandatory rule: *"Every eval fixture under `lab/evals/` MUST declare
which of these four it targets"* (ADR-0039 §"Four evaluation
targets", line 42). The fork's harness layout under
`lab/evals/cases/` and `lab/evals/runners/` already separates fixture
files, so the declaration goes in frontmatter.

**Implication.** Three knock-ons. (1) Every eval case file in
`lab/evals/cases/` must declare its target; a single fixture cannot
mix them. (2) Aggregation is per-skill, *not* per-target — collapsing
across targets re-introduces the 25pp loss. (3) The non-deterministic
ELO method in [[zk-007]] computes one rating channel **per target**;
the TDAD loop in [[zk-005]] writes one fixture **per target**; failure
tags use the AgentRx labels in [[zk-003]].

See also: [[zk-003]], [[zk-005]], [[zk-007]].
