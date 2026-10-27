---
name: "lean-math-optimization"
description: |
  USE FOR: optimization theory, convex optimization, game theory, reinforcement-learning theory (Bellman equations.
  DO NOT USE FOR: stochastic policies / Markov chains (@lean-math-stochastic).
  TRIGGERS: optimization, convex, game theory, Bellman, value iteration.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-proof", "skill:lean-research"]
  successors: ["skill:lean-proof", "skill:lean-proof-review", "skill:lean-math-analysis"]
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-math-optimization/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Lean 4 Optimization & Decision Theory
Guide to formalizing optimization, game theory, RL theory, and decision-making in Lean 4.
## Routing
- **USE FOR:** optimization theory, convex optimization, game theory, reinforcement-learning theory (Bellman
  equations, value /
  policy
  iteration), Nash
  equilibria, minimax theorems, decision theory, and fixed-point iterations in Lean 4.
- **DO NOT USE FOR:** stochastic policies / Markov chains (delegate to `@lean-math-stochastic`); pure analysis
  (delegate to
  `@lean-math-analysis`);
  Lyapunov / control-stability proofs (delegate to `@lean-math-dynamical`); writing one specific proof
  (delegate to
  `@lean-proof`).
- **TRIGGERS:** optimization, convex, game theory, Bellman, value iteration, policy iteration, Nash, minimax,
  fixed point, KKT.
## Workflow
1. Identify the optimality structure (Part 1) — unconstrained, convex, equilibrium, dynamic-programming.
2. Pick the matching tool below (gradient / KKT, contraction / Banach fixed-point, Bellman backup,
  Nash-equilibrium argument).
3. Handoff to `@lean-proof`; if the contraction step requires a normed-space lemma, handoff to
  `@lean-math-analysis`.
## Recovery & STOP
- STOP if the proof requires a Banach-contraction instance not yet imported — handoff to
  `@lean-math-analysis`.
- STOP if a stochastic policy or expected-value argument appears — re-route to `@lean-math-stochastic`.
## Handoffs
- **Predecessors:** `agent:gateway`, `skill:lean-proof` (mid-proof optimization goal), `skill:lean-research`
  (Bellman /
  Nash-equilibrium API
  survey).
- **Successors:** `skill:lean-proof` (apply the optimization pattern), `skill:lean-proof-review` (audit
  fixed-point claim),
  `skill:lean-math-analysis`
  (contraction / normed-space reduction).
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-math-optimization-handbook.md`](../../references/lean-math-optimization-handbook.md) .
## See also
- [`../../references/lean-math-optimization-handbook.md`](../../references/lean-math-optimization-handbook.md)
  -- Complete
  `lean-math-optimization` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
