---
name: "lean-ai-formalization"
description: |
  USE FOR: Formal verification of AI systems — agentic AI safety, alignment, high-stakes AI, evolving agents, neural network properties, and AI governance constraints. Use when formalizing safety envelopes, trust dynamics, multi-agent composition, AI act compliance, reward specifications, alignment properties, or any AI system property that must be formally verified.
  DO NOT USE FOR: AI methodology itself (use @ai-high-stakes-verifiable or @ai-agentic-evolving); security-specific formalisation (use @lean-security-formalization); knowledge formalisation (use @lean-knowledge-formalization).
  TRIGGERS: AI formalization, agentic safety, alignment proof, high-stakes AI, neural network property, AI governance.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-proof-review', 'skill:lean-enforcement', 'skill:lean-zettelkasten', 'skill:lean-doc-feedback']
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-ai-formalization/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# Lean 4 AI Systems Formalization

Guide to formally verifying properties of AI systems, from safety envelopes to alignment guarantees.

---

## Routing

- **USE FOR:** Formal verification of AI systems — agentic AI safety, alignment, high-stakes AI, evolving agents, neural network properties, and AI governance constraints. Use when formalizing safety envelopes, trust dynamics, multi-agent composition, AI act compliance, reward specifications, alignment properties, or any AI system property that must be formally verified.
- **DO NOT USE FOR:** AI methodology itself (use @ai-high-stakes-verifiable or @ai-agentic-evolving); security-specific formalisation (use @lean-security-formalization); knowledge formalisation (use @lean-knowledge-formalization).
- **TRIGGERS:** AI formalization, agentic safety, alignment proof, high-stakes AI, neural network property, AI governance.

## Workflow

1. Identify the AI property to formalise: safety, alignment, agentic invariant, or neural-network property.
2. Pick the matching section of the body (verification framework, formal-property catalog, alignment-axiom set).
3. Produce the Lean statement + proof skeleton; verify against the current Mathlib pin before delegating to `@lean-proof`.
4. Hand off: to `@lean-proof-review` once the proof compiles, to `@lean-enforcement` for the CI gate, to `@lean-zettelkasten` for the pattern.

## Recovery & STOP

- STOP if the property has not been formally stated — delegate to `@lean-specification` first.
- STOP if Mathlib does not yet have the needed primitives — escalate to `@lean-research`.
- STOP if the AI system is agentic/emergent — delegate dynamics modelling to `@ai-agentic-evolving` first.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-proof-review`, `skill:lean-enforcement`, `skill:lean-zettelkasten`, `skill:lean-doc-feedback`.

---

## Detailed reference

Full content for `lean-ai-formalization` lives in
[`references/lean-ai-formalization-handbook.md`](../../references/lean-ai-formalization-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

| Section | Topic |
|---|---|
| Part 1 | AI Safety Properties |
| Part 2 | Agentic AI |
| Part 4 | High-Stakes AI Verification |
| Part 5 | Neural Network Properties |
| Part 6 | Multi-Agent Composition |
| Part 7 | Commonsense and Causal Reasoning |
| Part 8 | Research Council Integration |

---

## See also

- [`../../references/lean-ai-formalization-handbook.md`](../../references/lean-ai-formalization-handbook.md) — Full handbook (extracted from this skill)
- [`../lean-proof-review/SKILL.md`](../lean-proof-review/SKILL.md) — Successor
- [`../lean-enforcement/SKILL.md`](../lean-enforcement/SKILL.md) — Successor
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor
- [`../lean-doc-feedback/SKILL.md`](../lean-doc-feedback/SKILL.md) — Successor
