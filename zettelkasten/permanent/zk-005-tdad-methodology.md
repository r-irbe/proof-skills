---
id: zk-005
title: TDAD -- Test-Driven Agent Definition (4-role loop)
created: 2026-05-27
updated: 2026-11-15
type: permanent
tags: [methodology, evals, agent-fleet]
refs:
  - zk-004
  - zk-006
  - zk-003
status: validated
confidence: high
---

# TDAD -- Test-Driven Agent Definition (4-role loop)

**Claim.** Test-Driven Agent Definition (TDAD) treats a `SKILL.md` as a compiled contract rather than unverified prose. Four roles cooperate in a red/green loop: **TestSmith** generates eval fixtures from each skill's G-rules; **PromptSmith** iterates `SKILL.md` until fixtures pass; **MutationSmith** weakens rules to verify fixture sensitivity; and the **Built Agent** is scored against the suite.

**Evidence.** Implemented across `scripts/eval/cases/*.yaml` and `scripts/eval/run_eval.py`, targeting >= 97% human pass rate, 86-100% mutation score, and >= 97% skill-under-rule adherence across all 38 core skills and 7 opt-in pack skills.

**Implication.** TDAD resolves the bootstrapping dilemma by requiring deterministic fixtures *before* prose expansion. The opening TestSmith phase uses BACM from [[zk-004]] to gather signal cheaply; the evaluation oracle maps onto the four targets in [[zk-006]]; and MutationSmith tags regressions with the nine AgentRx categories in [[zk-003]].

See also: [[zk-003]], [[zk-004]], [[zk-006]].
