---
name: "lean-knowledge-formalization"
description: |
  USE FOR: Knowledge representation, ontology engineering, symbolic AI, commonsense reasoning, causal reasoning.
  DO NOT USE FOR: KRR methodology not in Lean (@lean-knowledge-formalization).
  TRIGGERS: knowledge formalisation, ontology in Lean, symbolic AI Lean.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-research"]
  successors: ["skill:lean-proof-review", "skill:lean-causal-reasoning", "skill:lean-zettelkasten"]
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-knowledge-formalization/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Lean 4 Knowledge Systems & Reasoning Formalization
Guide to formalizing knowledge representation, reasoning systems, and domain-specific logic in Lean 4.
---
## Routing
- **USE FOR:** Knowledge representation, ontology engineering, symbolic AI, commonsense reasoning, causal
  reasoning, legal
  reasoning, and
  abductive
  inference in Lean 4. Use when formalizing knowledge structures, reasoning systems, argumentation frameworks,
  deontic logic,
  defeasible
reasoning, or any
  domain where structured knowledge and inference must be formally verified. Core skill for
  knowledge-lifecycle and provenance
architectures.
- **DO NOT USE FOR:** KRR methodology not in Lean (use @lean-knowledge-formalization); commonsense reasoning
  methodology (use
  @lean-knowledge-formalization);
  causal/deontic methodology (use @lean-causal-reasoning).
- **TRIGGERS:** knowledge formalisation, ontology in Lean, symbolic AI Lean, abductive inference Lean, legal
  reasoning Lean.
## Workflow
1. Classify the knowledge object: ontology, taxonomy, causal model, deontic norm, or abductive rule.
2. Pick the matching encoding pattern from the body (description-logic encoding, SCM encoding, etc.).
3. Produce the Lean encoding; check Mathlib primitives at the current pin.
4. Hand off: to `@lean-causal-reasoning` if causal-DAG-specific, to `@lean-proof-review` for review, to
  `@lean-zettelkasten`.
## Recovery & STOP
- STOP if the question is methodological (not Lean) — delegate to `@lean-knowledge-formalization` /
  `@lean-knowledge-formalization` /
  `@lean-causal-reasoning`.
- STOP if Mathlib lacks the needed structure — escalate to `@lean-research`.
- STOP if the encoding requires graph-theoretic foundations not in the body — delegate to
  `@lean-math-discrete` or
  `@lean-math-discrete`.
## Handoffs
- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-proof-review`, `skill:lean-causal-reasoning`, `skill:lean-zettelkasten`.
---
## Detailed reference
Full content for `lean-knowledge-formalization` lives in
[`references/lean-knowledge-formalization-handbook.md`](../../references/lean-knowledge-formalization-handbook.md)
.
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.
| Section | Topic |
|---|---|
| Part 1 | Knowledge Representation |
| Part 2 | Reasoning Systems |
| Part 3 | Legal Reasoning |
| Part 4 | Symbolic AI |
| Part 5 | Intelligence Analysis Reasoning |
| Part 6 | Research Council Integration |
---
## See also
- [`../../references/lean-knowledge-formalization-handbook.md`](../../references/lean-knowledge-formalization-handbook.md)
  — Full
  handbook (extracted from
  this skill)
- [`../lean-proof-review/SKILL.md`](../lean-proof-review/SKILL.md) — Successor
- [`../lean-causal-reasoning/SKILL.md`](../lean-causal-reasoning/SKILL.md) — Successor
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor
