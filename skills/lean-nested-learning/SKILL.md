---
name: "lean-nested-learning"
description: |
  USE FOR: Formalize and extend nested learning theory in Lean 4.
  DO NOT USE FOR: proof tactics (@lean-proof); Lyapunov-only proofs (@lean-math-dynamical).
  TRIGGERS: nested learning, LaSalle invariance, learning hierarchy.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-research"]
  successors: ["skill:lean-proof", "skill:lean-proof-review", "skill:lean-zettelkasten"]
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-nested-learning/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# SK-32: Lean Nested Learning Formalization
---
## Routing
- **USE FOR:** Formalize and extend nested learning theory in Lean 4. Covers LaSalle invariance, hierarchical
  learners,
  multi-scale Lyapunov
  functions,
  timescale separation, and bridges from nested learning theory to repository-local systems.
- **DO NOT USE FOR:** proof tactics (use @lean-proof); Lyapunov-only proofs (use @lean-math-dynamical); review
  (use
  @lean-proof-review).
- **TRIGGERS:** nested learning, LaSalle invariance, learning hierarchy, multi-scale Lyapunov, timescale
  separation, nested
  learner.
## Workflow
1. Identify the learning object: LaSalle invariance set, hierarchy level, multi-scale Lyapunov function, or
  timescale-separated
  subsystem.
2. Pick the encoding from the body (nested-learning schema, hierarchy-level mapping, scale-separation
  argument).
3. Produce the Lean statement; verify Mathlib dynamics primitives at the pin.
4. Hand off: to `@lean-proof` for the proof, to `@lean-proof-review` for review, to `@lean-zettelkasten`.
## Recovery & STOP
- STOP if the question is general nonlinear dynamics — delegate to `@lean-math-dynamical`.
- STOP if the spec is informal — delegate to `@lean-specification`.
- STOP if Mathlib lacks the needed primitive — escalate to `@lean-research`.
## Handoffs
- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-proof`, `skill:lean-proof-review`, `skill:lean-zettelkasten`.
---
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-nested-learning-handbook.md`](../../references/lean-nested-learning-handbook.md) .
## See also
- [`../../references/lean-nested-learning-handbook.md`](../../references/lean-nested-learning-handbook.md) --
  Complete
  `lean-nested-learning` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
