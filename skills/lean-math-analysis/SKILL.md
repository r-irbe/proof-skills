---
name: "lean-math-analysis"
description: |
  USE FOR: real analysis, functional analysis, topology, and measure theory in Lean 4 / Mathlib: continuous functions.
  DO NOT USE FOR: stochastic / probabilistic convergence (@lean-math-stochastic).
  TRIGGERS: continuous, derivative, integral, metric space, normed space.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-proof", "skill:lean-research"]
  successors: ["skill:lean-proof", "skill:lean-proof-review", "skill:lean-math-foundations"]
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-math-analysis/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Lean 4 Real Analysis & Topology
Guide to formalizing analysis and topology in Lean 4 using Mathlib's filter-based approach.
## Routing
- **USE FOR:** real analysis, functional analysis, topology, and measure theory in Lean 4 / Mathlib —
  continuous functions,
  derivatives,
  integrals, metric
  / normed spaces, filter-based convergence, contraction mappings, convex analysis, spectral theory, and the
  real-valued bridges
  from a
Nat-scaled model.
- **DO NOT USE FOR:** stochastic / probabilistic convergence (delegate to `@lean-math-stochastic`);
  deterministic dynamical-system
  stability
  proofs
  (delegate to `@lean-math-dynamical`); pure optimization (delegate to `@lean-math-optimization`);
  typeclass-tower reasoning
  (delegate to
## Workflow
1. Map the problem to Mathlib's filter-based architecture (Part 1) — most analysis goals can be phrased as
  `Tendsto … atTop` or
   `ContinuousAt`.
2. Locate the relevant Part below (continuity, derivatives, integrals, normed spaces, measure theory) and
  apply the pattern.
3. If the result is a concrete proof obligation, handoff to `@lean-proof`; if it depends on a foundational
  instance, handoff to
   `@lean-math-foundations`.
## Recovery & STOP
- STOP if the lemma you need is not in Mathlib at the current pin — escalate to `@lean-research` to verify,
  then `@lean-proof` to
  author a
  local helper.
- STOP if a classical-only result is invoked and the project has documented constructive constraints —
  escalate to
  `@lean-review-council`.
## Handoffs
- **Predecessors:** `agent:gateway`, `skill:lean-proof` (mid-proof convergence goal), `skill:lean-research`
  (when a survey turns
  up an
  analysis API).
- **Successors:** `skill:lean-proof` (apply the analysis pattern), `skill:lean-proof-review` (audit the
  resulting proof),
  `skill:lean-math-foundations`
  (when the goal collapses to a typeclass-tower issue).
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-math-analysis-handbook.md`](../../references/lean-math-analysis-handbook.md) .
## See also
- [`../../references/lean-math-analysis-handbook.md`](../../references/lean-math-analysis-handbook.md) --
  Complete
  `lean-math-analysis` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
