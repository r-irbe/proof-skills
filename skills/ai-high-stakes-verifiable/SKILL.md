---
name: "ai-high-stakes-verifiable"
description: |
  USE FOR: Formally verifiable AI, high-stakes AI systems, safety-critical deployment, certification, and regulatory compliance. Use for reasoning about AI systems that must be provably correct, auditable, or certifiable — medical AI, autonomous vehicles, legal decision support, military/intelligence systems, and mathematically rigorous AI governance.
  DO NOT USE FOR: formal verification proofs in Lean (use @lean-ai-formalization); agentic AI dynamics (use @ai-agentic-evolving); causal/deontic reasoning (use @ai-causal-deontic).
  TRIGGERS: high stakes, verifiable AI, safety critical, certification, regulatory compliance, AI assurance.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-ai-formalization', 'skill:lean-security-formalization', 'skill:applied-data-information-security']
metadata:
  version: "0.2.0"
  source_spec: "skills/ai-high-stakes-verifiable/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# High-Stakes & Formally Verifiable AI

Mathematical frameworks for AI systems where correctness, safety, and auditability are non-negotiable.

---

## Routing

- **USE FOR:** Formally verifiable AI, high-stakes AI systems, safety-critical deployment, certification, and regulatory compliance. Use for reasoning about AI systems that must be provably correct, auditable, or certifiable — medical AI, autonomous vehicles, legal decision support, military/intelligence systems, and mathematically rigorous AI governance.
- **DO NOT USE FOR:** formal verification proofs in Lean (use @lean-ai-formalization); agentic AI dynamics (use @ai-agentic-evolving); causal/deontic reasoning (use @ai-causal-deontic).
- **TRIGGERS:** high stakes, verifiable AI, safety critical, certification, regulatory compliance, AI assurance.

## Workflow

1. Identify the verification class: certification (regulatory), assurance case (engineering), or formal property (mathematical).
2. Pick the matching framework from the body (ISO 21448, ASIL, formal-property catalog).
3. Produce the verification artifact appropriate for the class — assurance argument, requirement decomposition, or property statement ready for `@lean-ai-formalization`.
4. Hand off: to `@lean-ai-formalization` for the proof, to `@applied-data-information-security` for security-specific properties, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the property is informally argued but needs a Lean proof — hand directly to `@lean-ai-formalization`.
- STOP if the system is agentic/emergent — delegate dynamics modelling to `@ai-agentic-evolving` first.
- STOP if the certification target is jurisdiction-specific and not in the body — escalate to `@applied-legal-reasoning`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-ai-formalization`, `skill:lean-security-formalization`, `skill:applied-data-information-security`.

---

## Detailed reference

Full content for `ai-high-stakes-verifiable` lives in
[`references/ai-high-stakes-verifiable-handbook.md`](../../references/ai-high-stakes-verifiable-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

| Section | Topic |
|---|---|
| Part 1 | Verification Hierarchy |
| Part 2 | Safety Standards & Certification |
| Part 3 | Formal Safety Analysis |
| Part 4 | Provably Robust AI |
| Part 5 | Decision Support in High-Stakes Domains |
| Part 6 | Connection to Project Lean Modules |
| Part 7 | Research Directions |

---

## See also

- [`../../references/ai-high-stakes-verifiable-handbook.md`](../../references/ai-high-stakes-verifiable-handbook.md) — Full handbook (extracted from this skill)
- [`../lean-ai-formalization/SKILL.md`](../lean-ai-formalization/SKILL.md) — Successor
- [`../lean-security-formalization/SKILL.md`](../lean-security-formalization/SKILL.md) — Successor
- [`../applied-data-information-security/SKILL.md`](../applied-data-information-security/SKILL.md) — Successor
