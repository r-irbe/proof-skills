---
name: "epistemic-mapping"
description: |
  USE FOR: mapping a domain's concept lattice, identifying load-bearing assumptions, surfacing implicit ontologies.
  DO NOT USE FOR: producing formal proofs (@lean-proof).
  TRIGGERS: concept-map, ontology, terrain, epistemic-survey.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["skill:epistemic-discovery-engine"]
  successors: ["skill:lean-blueprint", "skill:research-synthesis-engine"]
metadata:
  version: "0.1.0"
  source_spec: "specs/epistemic/mapping/requirements.md"
  last_reviewed: "2026-05-26"
---

# epistemic-mapping
Operational dispatch contract for `@epistemic-mapping`.
## Routing
- **USE FOR:** mapping the concept lattice of an unfamiliar domain; identifying load-bearing assumptions;
  surfacing implicit
  ontologies;
  drafting an
  epistemic terrain map to seed downstream formalization.
- **DO NOT USE FOR:** producing formal proofs (use `@lean-proof`); gathering primary research data (use
  `@lean-applied-reasoning`).
- **TRIGGERS:** concept-map, ontology, terrain, epistemic-survey.
## Workflow
1. **Discover** [discover] — read brief, locate prior maps, list candidate concepts.
2. **Plan** [discover] — choose framing set; STOP if < 3 framings.
3. **Draft** [execute] — write the terrain map with provisional nodes flagged.
4. **Verify** [validate] — cross-check anchor citations; max 3 attempts then escalate.
5. **Persist** [persist] — commit map, update state tracker, tick `tasks.md`.
## Recovery & STOP
- Anchor citation missing ×3 → STOP, escalate.
- Single-framing collapse detected → immediate STOP, re-anchor.
- Confidence < 80 % on top-level structure → STOP, ask.
## Handoffs
- **Predecessors / successors**: see FM `handoffs` (grammar from ADR-0080).
- **Source spec**: `specs/epistemic/mapping/requirements.md`.
- **Related ADRs**: ADR-0076, ADR-0080.
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/epistemic-mapping-handbook.md`](../../references/epistemic-mapping-handbook.md) .
## See also
- [`../../references/epistemic-mapping-handbook.md`](../../references/epistemic-mapping-handbook.md) --
  Complete
  `epistemic-mapping` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
