---
name: "lean-review-council"
description: |
  USE FOR: orchestrating a 5-member Lean 4 proof review council (Σ Kernel Guardian, Φ Statement Oracle, Ν Novelty Scout.
  DO NOT USE FOR: reviewing one Lean proof in isolation (@lean-proof-review).
  TRIGGERS: review council, RALPH loop, council vote, SDR, council topology.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-proof-review", "skill:lean-specification", "skill:lean-research"]
  successors:
    - "skill:lean-proof-review"
    - "skill:lean-enforcement"
    - "skill:lean-doc-feedback"
    - "skill:lean-zettelkasten"
    - "skill:research-council"
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-review-council/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Lean 4 Review Council
A formal review council of five voting AI agents that collectively execute the `lean-proof-review` skill with
99.99% reliability
and
resilience. Each
## Routing
- **USE FOR:** orchestrating a 5-member Lean 4 proof review council with RALPH loops at member / council /
  project / meta scales;
  structured
  voting with
  SDR; council topology selection; maximum-parallel agent dispatch with cascading completion handlers;
  specification lifecycle,
inter-council
  collaboration, Zettelkasten synthesis, calibration scoring, enforcement tactics.
- **DO NOT USE FOR:** reviewing one Lean proof in isolation (delegate to `@lean-proof-review`); writing a
  proof (delegate to
  `@lean-proof`);
  running CI
## Workflow
1. Identify the scope (theorem / file / module / project / meta-council cross-module).
2. Pick a topology (Part 4 of the handbook — Star for first pass, Pipeline for sequential dependencies,
  Hierarchical for project
  scale,
   Hub-Spoke for
   inter-council).
3. Run Part 12 — Execution Protocol (kept inline below) end-to-end.
4. On a blocking finding, enter SDR (handbook Part 3); on approval, dispatch Documenter + Synthesizer for the
  session report and
   Zettelkasten update.
5. Aggregate session reports at the module / project level; convene the Meta-Council for cross-module
  coherence when needed.
## Recovery & STOP
- STOP if more than two members report 🔴 votes on a single artifact — enter SDR (handbook Part 3) before any
  further dispatch.
- STOP if RALPH loop iteration count exceeds 3 without convergence — escalate to the Meta-Council (handbook
  Part 10) or handoff to
  `@lean-research` to
  widen evidence.
- STOP if the Documenter or Synthesizer fails to produce a session report — the council session is incomplete;
  do not advance to
  module-level aggregation.
## Handoffs
- **Predecessors:** `agent:gateway` (top-level invocation), `skill:lean-proof-review` (when a layer needs
  council-scale
  escalation),
  `skill:lean-specification` (specification lifecycle entry), `skill:lean-research` (when evidence widening is
  required
  mid-session).
- **Successors:** `skill:lean-proof-review` (layered re-review on a fix), `skill:lean-enforcement` (CI gates
  triggered by the
  council vote),
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-review-council-handbook.md`](../../references/lean-review-council-handbook.md) .
## See also
- [`../../references/lean-review-council-handbook.md`](../../references/lean-review-council-handbook.md) --
  Complete
  `lean-review-council` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
