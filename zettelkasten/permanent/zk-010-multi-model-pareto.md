---
id: zk-010
title: Multi-model cost–quality Pareto across model × reasoning-effort
created: 2026-05-27
updated: 2026-05-29
type: permanent
tags: [evals, multi-model, cost, synthesis]
refs:
  - zk-006
  - zk-007
status: provisional
confidence: medium
---

# Multi-model cost–quality Pareto across model × reasoning-effort

**Claim.** Ranking agents by quality alone hides the dominant
operational variable: cost. The honest unit of comparison is a
two-dimensional frontier over `(model, reasoning_effort)` tuples,
with quality on one axis and `$/case` on the other. Below a
task-class-specific difficulty threshold, the cheap model dominates
and dispatching to the expensive one is pure waste; above it, the
relationship inverts. Prompt-cache hit rate further shifts the
frontier by an order of magnitude.

**Evidence.** Design rationale in
`lab/design/03-multi-model-runner.md` §1, which lists the seven
questions a single-model loop cannot answer — first among them
*"Cost–quality Pareto frontier per skill"*. The runner is the
producer of head-to-head outcomes (case × model × rep grid) consumed
by both the ELO calculator and the skill-eval reports. Player
identity in the current Glicko-2 pipeline remains `model@effort`,
confirming the tuple is the unit of analysis.

**Implication.** Three rules. (1) Every Pareto report must publish
**per-task-class** frontiers — there is no global Pareto. (2) ELO
([[zk-007]]) is necessary but not sufficient; ranking must include
`$/eval-point` and prompt-cache assumptions. (3) The four eval
targets in [[zk-006]] each have their own frontier; collapsing them
hides the regime where a cheap model dominates instructions but
loses trajectories.

See also: [[zk-006]], [[zk-007]].
