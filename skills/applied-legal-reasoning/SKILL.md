---
name: "applied-legal-reasoning"
description: |
  USE FOR: Legal reasoning formalization — statutory interpretation, case-based reasoning, argumentation frameworks, defeasible rules, deontic norms, regulatory compliance, and their connection to provenance chains, governance structures, and formal verification for legal-adjacent AI systems.
  DO NOT USE FOR: formalising those legal models in Lean (use @lean-applied-reasoning); deontic reasoning specifically (use @ai-causal-deontic); security policy (use @applied-data-information-security).
  TRIGGERS: statutory interpretation, case-based reasoning, argumentation framework, defeasible rule, deontic norm, legal reasoning, regulatory.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-applied-reasoning', 'skill:ai-causal-deontic', 'skill:lean-knowledge-formalization']
metadata:
  version: "0.2.0"
  source_spec: "skills/applied-legal-reasoning/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# Legal Reasoning

Formal frameworks for legal analysis, argumentation, normative reasoning, and their intersection with formal verification and AI governance.

---

## Routing

- **USE FOR:** Legal reasoning formalization — statutory interpretation, case-based reasoning, argumentation frameworks, defeasible rules, deontic norms, regulatory compliance, and their connection to provenance chains, governance structures, and formal verification for legal-adjacent AI systems.
- **DO NOT USE FOR:** formalising those legal models in Lean (use @lean-applied-reasoning); deontic reasoning specifically (use @ai-causal-deontic); security policy (use @applied-data-information-security).
- **TRIGGERS:** statutory interpretation, case-based reasoning, argumentation framework, defeasible rule, deontic norm, legal reasoning, regulatory.

## Workflow

1. Classify the legal task: statutory interpretation, case-based reasoning, argumentation, or deontic-norm modelling.
2. Pick the matching framework (ASPIC+, Carneades, defeasible-logic, deontic-action) from the body.
3. Apply the framework; document the argument structure + defeaters.
4. Hand off: to `@ai-causal-deontic` for deontic-logic encoding, to `@lean-applied-reasoning` for Lean formalisation, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the question is about pure deontic logic — delegate to `@ai-causal-deontic`.
- STOP if the legal regime is jurisdiction-specific and not in the body — escalate to `@research-council`.
- STOP if security/privacy policy dominates — delegate to `@applied-data-information-security`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-applied-reasoning`, `skill:ai-causal-deontic`, `skill:lean-knowledge-formalization`.

---

## Detailed reference

Full content for `applied-legal-reasoning` lives in
[`references/applied-legal-reasoning-handbook.md`](../../references/applied-legal-reasoning-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

| Section | Topic |
|---|---|
| Part 1 | Legal Reasoning Paradigms |
| Part 2 | Argumentation Frameworks |
| Part 3 | Defeasible Legal Rules |
| Part 4 | Statutory Interpretation |
| Part 5 | Case-Based Reasoning (CBR) |
| Part 6 | Regulatory Compliance Formalization |
| Part 7 | AI & Legal Reasoning |
| Part 8 | Cross-References |

---

## See also

- [`../../references/applied-legal-reasoning-handbook.md`](../../references/applied-legal-reasoning-handbook.md) — Full handbook (extracted from this skill)
- [`../lean-applied-reasoning/SKILL.md`](../lean-applied-reasoning/SKILL.md) — Successor
- [`../ai-causal-deontic/SKILL.md`](../ai-causal-deontic/SKILL.md) — Successor
- [`../lean-knowledge-formalization/SKILL.md`](../lean-knowledge-formalization/SKILL.md) — Successor
