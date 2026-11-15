---
id: zk-007
title: Glicko-2 and ELO ranking for stochastic agents
created: 2026-05-27
updated: 2026-11-15
type: permanent
tags: [evals, elo, ranking]
refs:
  - zk-006
  - zk-010
  - zk-003
status: validated
confidence: high
---

# Glicko-2 and ELO ranking for stochastic agents

**Claim.** Pairwise rating systems accurately rank stochastic theorem-proving agents when each eval case is treated as a multi-game match (`n >= 5` runs per side), rating deviation (`RD`) and volatility are tracked explicitly, and `(model, reasoning_effort)` tuples are scored as distinct entrants.

**Evidence.** Implemented in `scripts/elo/glicko2.py` (superseding vanilla fixed-K ELO), consuming pairwise head-to-head outcomes across shared `scripts/eval/cases/` benchmarks and emitting 95% confidence intervals alongside rating volatility.

**Implication.** Two design constraints hold. (1) Case mixes must be stratified by difficulty, and per-target channels from [[zk-006]] must be reported separately so high-variance entrants cannot mask trajectory failures behind easy instruction wins. (2) Cost-aware selection on the Pareto frontier in [[zk-010]] pairs Glicko-2 rating with `$/case`, while failure-mode breakdowns use the [[zk-003]] taxonomy.

See also: [[zk-003]], [[zk-006]], [[zk-010]].
