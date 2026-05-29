---
name: "lean-security-formalization"
description: |
  USE FOR: Data security, information security, access control, cryptographic properties, and privacy in Lean 4. Use when formalizing information flow policies, access control models, confidentiality/integrity/availability properties, data protection compliance (GDPR/LED), or trust model properties.
  DO NOT USE FOR: security policy design not in Lean (use @applied-data-information-security); AI safety formalisation (use @lean-ai-formalization); general knowledge formalisation (use @lean-knowledge-formalization).
  TRIGGERS: security formalization, information flow Lean, access control proof, cryptographic Lean, privacy proof.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-proof-review', 'skill:lean-enforcement', 'skill:lean-zettelkasten']
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-security-formalization/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# Lean 4 Security & Privacy Formalization

Guide to formalizing security properties, access control, information flow, and privacy in Lean 4.

---

## Routing

- **USE FOR:** Data security, information security, access control, cryptographic properties, and privacy in Lean 4. Use when formalizing information flow policies, access control models, confidentiality/integrity/availability properties, data protection compliance (GDPR/LED), or trust model properties.
- **DO NOT USE FOR:** security policy design not in Lean (use @applied-data-information-security); AI safety formalisation (use @lean-ai-formalization); general knowledge formalisation (use @lean-knowledge-formalization).
- **TRIGGERS:** security formalization, information flow Lean, access control proof, cryptographic Lean, privacy proof.

## Workflow

1. Identify the security property class: information flow, access control, cryptographic, or privacy.
2. Pick the matching encoding from the body (non-interference, BLP-Lean, IND-CPA-Lean, k-anonymity-Lean).
3. Produce the Lean statement + proof skeleton; verify Mathlib primitives at the pin.
4. Hand off: to `@lean-proof-review` for review, to `@lean-enforcement` for CI, to `@applied-data-information-security` if the model is wrong.

## Recovery & STOP

- STOP if the question is about policy design — delegate to `@applied-data-information-security`.
- STOP if Mathlib lacks the cryptographic primitive — escalate to `@lean-research`.
- STOP if the property has not been formally stated — delegate to `@lean-specification`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-proof-review`, `skill:lean-enforcement`, `skill:lean-zettelkasten`.

---

## Detailed reference

Full content for `lean-security-formalization` lives in
[`references/lean-security-formalization-handbook.md`](../../references/lean-security-formalization-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

| Section | Topic |
|---|---|
| Part 1 | Security Properties |
| Part 2 | Access Control Models |
| Part 3 | Information Flow |
| Part 4 | Privacy and Data Protection |
| Part 5 | Cryptographic Properties |
| Part 6 | Trust Models |
| Part 7 | Research Council Integration |

---

## See also

- [`../../references/lean-security-formalization-handbook.md`](../../references/lean-security-formalization-handbook.md) — Full handbook (extracted from this skill)
- [`../lean-proof-review/SKILL.md`](../lean-proof-review/SKILL.md) — Successor
- [`../lean-enforcement/SKILL.md`](../lean-enforcement/SKILL.md) — Successor
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor
