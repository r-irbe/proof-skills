---
id: zk-007
title: ELO for non-deterministic agents
created: 2026-05-27
updated: 2026-05-29
type: permanent
tags: [evals, elo, ranking]
refs:
  - zk-006
  - zk-010
  - zk-003
status: superseded-by-glicko2
confidence: high
---

# ELO for non-deterministic agents

**Claim.** Pairwise ELO can rate stochastic agents if each eval case
is treated as a *multi-game match* (n ≥ 5 runs per side), variance is
folded into the K-factor (high-variance pairs get smaller K), and
near-ties inside a score-noise band *decay* rating instead of leaving
it flat. A `(model, reasoning_effort)` tuple is one player; rating is
recomputed monthly, not per-PR, to keep the leaderboard interpretable.

**Evidence.** The original vanilla-ELO prototype has been superseded by
`scripts/elo/glicko2.py`, which consumes the same pairwise rows but
adds RD/volatility and 95% confidence intervals. Inputs are pairwise
outcomes produced by the multi-model runner designed in
`lab/design/03-multi-model-runner.md` §1 ("ELO needs head-to-head
outcomes from shared cases"). Player identity is still
`model@effort`, so effort variants remain separate entrants.

**Implication.** Two design constraints fall out. (1) A high-variance
agent can ELO-grind by exploiting easy cases; the case mix must be
stratified by difficulty, and per-target ratings from [[zk-006]] must
be reported separately so a flaky agent cannot launder one strong
channel into an overall rank. (2) Cost-aware ranking — the
multi-model Pareto frontier in [[zk-010]] — needs rating *and*
$/case; rating alone understates the price axis. Failure-mode
breakdown still uses the [[zk-003]] label space.

See also: [[zk-003]], [[zk-006]], [[zk-010]].
