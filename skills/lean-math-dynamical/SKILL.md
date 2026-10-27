---
name: "lean-math-dynamical"
description: |
  USE FOR: nonlinear dynamical systems, Lyapunov stability, bifurcation theory, catastrophe theory, control theory.
  DO NOT USE FOR: stochastic dynamics (@lean-math-stochastic).
  TRIGGERS: Lyapunov, stability, bifurcation, cusp catastrophe, attractor.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-proof", "skill:lean-research"]
  successors: ["skill:lean-proof", "skill:lean-proof-review", "skill:lean-math-analysis"]
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-math-dynamical/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Lean 4 Nonlinear Dynamics & Stability
Guide to formalizing dynamical systems, stability theory, and bifurcation in Lean 4.
## Routing
- **USE FOR:** nonlinear dynamical systems, Lyapunov stability, bifurcation theory, catastrophe theory,
  control theory,
  phase-portrait
  analysis, attractor
  classification, and any deterministic system with state evolution over time in Lean 4.
- **DO NOT USE FOR:** stochastic dynamics (delegate to `@lean-math-stochastic`); pure analysis / topology
  (delegate to
  `@lean-math-analysis`);
  optimization-only control problems (delegate to `@lean-math-optimization`); writing one specific proof
  (delegate to
  `@lean-proof`).
## Workflow
1. Classify the system (Part 1) — discrete-time, continuous-time, gradient, conservative, controlled.
2. Pick the appropriate technique below (Lyapunov, contraction, bifurcation-normal-form,
  catastrophe-classification).
3. Handoff to `@lean-proof` for the concrete proof; if it bottoms out in a derivative / measure step, handoff
  to
  `@lean-math-analysis`.
## Recovery & STOP
- STOP if the proof depends on a manifold or smooth-structure API not in Mathlib at the current pin — escalate
  to
  `@lean-research`.
- STOP if a stochastic perturbation enters the model — re-route to `@lean-math-stochastic`; this skill covers
  only deterministic
  dynamics.
## Handoffs
- **Predecessors:** `agent:gateway`, `skill:lean-proof` (mid-proof stability goal), `skill:lean-research`
  (catastrophe-theory
  result
  survey).
- **Successors:** `skill:lean-proof` (apply the dynamical pattern), `skill:lean-proof-review` (audit Lyapunov
  candidate),
  `skill:lean-math-analysis`
  (continuous-derivative or contraction reduction).
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-math-dynamical-handbook.md`](../../references/lean-math-dynamical-handbook.md) .
## See also
- [`../../references/lean-math-dynamical-handbook.md`](../../references/lean-math-dynamical-handbook.md) --
  Complete
  `lean-math-dynamical` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
