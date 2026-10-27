---
name: "lean-math-foundations"
description: |
  USE FOR: foundational mathematics in Lean 4: Lean's type system (Prop / Type / universes).
  DO NOT USE FOR: applied lattice instances such as severity / quality-gate lattices.
  TRIGGERS: type universe, Prop vs Type, classical reasoning.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-proof", "skill:lean-research"]
  successors: ["skill:lean-proof", "skill:lean-proof-review", "skill:lean-enforcement"]
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-math-foundations/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Lean 4 Mathematical Foundations
Guide to formalizing foundational mathematics in Lean 4, covering the structures and patterns that underpin
all domain-specific
formalization work.
## Routing
- **USE FOR:** foundational mathematics in Lean 4 — Lean's type system (Prop / Type / universes), classical vs
  constructive
  choices,
  Mathlib's algebraic
  typeclass hierarchy (Group / Ring / Order / Lattice / Module / Algebra), category theory basics, and any
  proof that needs
  foundational
reasoning about
  types, propositions, or universes.
- **DO NOT USE FOR:** applied lattice instances such as severity / quality-gate lattices (delegate to
  `@lean-math-discrete`);
  analysis-flavoured algebra
  such as normed-space structure (delegate to `@lean-math-analysis`); writing a specific proof (delegate to
  `@lean-proof`);
  reviewing a
finished proof
## Workflow
1. Identify whether the question is about Lean's logical foundation (Part 1), Mathlib's typeclass hierarchy
  (Parts 2–5), or a
   category-theoretic
   construction (later parts).
2. Locate the relevant Part below and read the project-relevance callouts before applying any pattern.
3. If the answer is a specific proof, handoff to `@lean-proof`; if it is a soundness-affecting choice (e.g.,
  adding a new
  `Classical`
   import), handoff to
   `@lean-proof-review` and `@lean-enforcement`.
## Recovery & STOP
- STOP if a foundational choice silently introduces a new axiom — `#print axioms` must show only `propext`,
  `Classical.choice`,
  `Quot.sound`
  (and `funext`
  is a theorem, not an axiom). Escalate to `@lean-review-council` if uncertain.
- STOP and handoff to `@lean-research` if the question is about a result not present in Mathlib at the current
  pin (e.g., a new
  universe-polymorphism API).
## Handoffs
- **Predecessors:** `agent:gateway`, `skill:lean-proof` (mid-proof typeclass synthesis failure),
  `skill:lean-research` (when a
  survey turns
  up a
  foundational construct).
- **Successors:** `skill:lean-proof` (apply the foundational pattern in a concrete proof),
  `skill:lean-proof-review` (verify axiom
  impact),
  `skill:lean-enforcement` (run native-decide / `#print axioms` checks after the change).
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-math-foundations-handbook.md`](../../references/lean-math-foundations-handbook.md) .
## See also
- [`../../references/lean-math-foundations-handbook.md`](../../references/lean-math-foundations-handbook.md)
  -- Complete
  `lean-math-foundations` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
