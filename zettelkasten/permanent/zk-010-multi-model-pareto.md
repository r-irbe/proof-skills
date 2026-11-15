---
id: zk-010
title: Multi-model cost-quality Pareto across model x reasoning-effort
created: 2026-05-27
updated: 2026-11-15
type: permanent
tags: [evals, multi-model, cost, synthesis]
refs:
  - zk-006
  - zk-007
status: validated
confidence: high
---

# Multi-model cost-quality Pareto across model x reasoning-effort

**Claim.** Ranking theorem-proving agents by solve rate alone hides operational cost. The faithful unit of comparison is the two-dimensional Pareto frontier over `(model, reasoning_effort)` tuples, plotting verified pass rate against `$/case` and wall-clock latency. Below a task-class difficulty threshold, compact fast models dominate; above it, deep-reasoning models invert the frontier.

**Evidence.** Tracked via `scripts/elo/glicko2.py` and `scripts/eval/run_eval.py`, where player identity is `model@effort` and progressive L0/L1/L2 disclosure keeps prompt-cache hit rates high across repeated proof attempts.

**Implication.** Three operational rules apply. (1) Publish Pareto frontiers per task class rather than a single global average. (2) Pair Glicko-2 ratings from [[zk-007]] with `$/eval-point` and token-budget metrics. (3) Keep the four evaluation targets in [[zk-006]] uncollapsed so instruction-following efficiency never masks multi-step proof trajectory regressions.

See also: [[zk-006]], [[zk-007]].
