---
name: "epistemic-mapping"
description: |
  USE FOR: mapping a domain's concept lattice, identifying load-bearing assumptions, surfacing implicit ontologies, drafting an epistemic terrain map.
  DO NOT USE FOR: producing formal proofs (use @lean-formalization), gathering primary research data (use @applied-intelligence-analysis).
  TRIGGERS: concept-map, ontology, terrain, epistemic-survey.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
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

## Routing

- **USE FOR:** mapping the concept lattice of an unfamiliar domain; identifying load-bearing assumptions; surfacing implicit ontologies; drafting an epistemic terrain map to seed downstream formalization.
- **DO NOT USE FOR:** producing formal proofs (use `@lean-formalization`); gathering primary research data (use `@applied-intelligence-analysis`).
- **TRIGGERS:** concept-map, ontology, terrain, epistemic-survey.

## Behavioural rules (G-*)

- **G-1** (MUST): The map MUST distinguish observed concepts from inferred ones. [Trace: AC-01]
- **G-2** (SHOULD): The map SHOULD enumerate at least three competing framings before settling. [Trace: AC-02]
- **G-3** (MUST NOT): The skill MUST NOT collapse contested distinctions into a single label without an explicit caveat. [Trace: AC-03]
- **G-4** (SHOULD): The skill SHOULD cite at least one anchor source per top-level node. [Trace: AC-04]
- **G-5** (MUST): On confidence < 80 % the skill MUST mark the node `provisional`. [Trace: AC-05]

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

## Common failure modes

> AI agents commonly: pick the first framing; merge contested terms; omit
> citations for "obvious" nodes. Full registry: GUARDRAILS.md.
