---
name: "lean-specification"
description: |
  USE FOR: Design theorem specifications for Lean 4 proofs.
  DO NOT USE FOR: actual proof writing (@lean-proof).
  TRIGGERS: specification, theorem spec, three-part spec, lemma plan.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-research"]
  successors: ["skill:lean-proof", "skill:lean-proof-review", "skill:lean-zettelkasten"]
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-specification/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Lean 4 Theorem Specification
Structured process for specifying theorems before implementation. Every theorem passes through Specify →
Design → Implement →
Review →
Merge, with each
stage tracked by document templates.
---
## Routing
- **USE FOR:** Design theorem specifications for Lean 4 proofs. Use when planning new theorems, lemmas,
  definitions, or tactics.
  Covers the
  three-part
  specification (requirements, design, documentation), lifecycle management, dependency analysis, and
  integration with the review
  council.
- **DO NOT USE FOR:** actual proof writing (use @lean-proof); requirement extraction (use
  @lean-doc-requirements); review (use
  @lean-proof-review).
- **TRIGGERS:** specification, theorem spec, three-part spec, lemma plan, tactic plan.
## Workflow
1. Identify the artifact: new theorem, new lemma, new definition, or new tactic.
2. Apply the three-part specification template from the body (signature, intent, traceability); verify Mathlib
  primitives exist at
  the pin.
3. Run mandatory specification fidelity checks before approving:
   - **Check 5 (Necessity & Sufficiency `↔` Pairing):** Every executable `Bool` checker `f ... : Bool` or
  decidable predicate MUST
  specify
     both soundness and completeness (`f x = true ↔ Spec x`), never a one-way `f x = true -> ...` implication
     alone
     (`ONE_WAY_BOOL_CHECKER`).
## Recovery & STOP
- STOP if the artifact is informal — extract requirements via `@lean-doc-requirements` first.
- STOP if the spec depends on Mathlib primitives missing at the pin — escalate to `@lean-research`.
- STOP if reviewer would reject on grounds the body covers (vacuous truth, missing hypothesis) — fix before
  publishing.
## Handoffs
- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-proof`, `skill:lean-proof-review`, `skill:lean-zettelkasten`.
---
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-specification-handbook.md`](../../references/lean-specification-handbook.md) .
## See also
- [`../../references/lean-specification-handbook.md`](../../references/lean-specification-handbook.md) --
  Complete
  `lean-specification` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
