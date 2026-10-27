---
name: "applied-data-information-security"
description: |
  USE FOR: Data security and information security formalization: CIA triad, access control models (BLP, RBAC, ABAC).
  DO NOT USE FOR: Lean formalisation of these policies (@lean-security-formalization).
  TRIGGERS: CIA triad, access control, BLP, RBAC, ABAC, information flow.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-research"]
  successors: ["skill:lean-security-formalization", "skill:applied-engineering-disciplines", "skill:lean-knowledge-formalization"]
metadata:
  version: "0.2.0"
  source_spec: "skills/applied-data-information-security/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Data & Information Security
Formal foundations of security properties, access control, information flow, privacy, and their verification
in formal frameworks.
---
## Routing
- **USE FOR:** Data security and information security formalization — CIA triad, access control models (BLP,
  RBAC, ABAC),
  information flow,
  cryptographic
  primitives, privacy (differential privacy, k-anonymity), threat modeling, and their formal verification in
  Lean 4. Use for
  security
properties of
  provenance chains, trust composition, and multi-agent systems.
- **DO NOT USE FOR:** Lean formalisation of these policies (use @lean-security-formalization); engineering
  disciplines more
  broadly (use
  @applied-engineering-disciplines); legal-policy reasoning (use @applied-legal-reasoning).
## Workflow
1. Classify the security goal in the CIA triad and pick the access-control model (BLP / RBAC / ABAC) or
  information-flow model
   (non-interference) from the body.
2. Apply the chosen model to the concrete asset or flow; surface assumptions and gaps.
3. Produce the security argument or policy ready for formal encoding.
4. Hand off: to `@lean-security-formalization` for the Lean encoding, to `@applied-engineering-disciplines` if
  reliability/safety
  overlap,
   to
   `@lean-zettelkasten`.
## Recovery & STOP
- STOP if the question demands a Lean proof — delegate to `@lean-security-formalization`.
- STOP if the question is about cryptographic-protocol design — escalate to `@research-council` if the body
  lacks the protocol.
- STOP if the question is about legal/regulatory compliance — delegate to `@applied-legal-reasoning`.
## Handoffs
- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-security-formalization`, `skill:applied-engineering-disciplines`,
  `skill:lean-knowledge-formalization`.
---
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/applied-data-information-security-handbook.md`](../../references/applied-data-information-security-handbook.md)
.
## See also
- [`../../references/applied-data-information-security-handbook.md`](../../references/applied-data-information-security-handbook.md)
  -- Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
