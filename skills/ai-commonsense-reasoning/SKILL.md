---
name: "ai-commonsense-reasoning"
description: |
  USE FOR: Commonsense reasoning for AI systems — world knowledge, naive physics, folk psychology, temporal/spatial reasoning, default reasoning, and their formalization. Use for reasoning about everyday knowledge that humans take for granted but AI systems need explicitly, including the project tacit knowledge externalization pipeline's commonsense aspects.
  DO NOT USE FOR: formal KR/ontology engineering (use @ai-symbolic-neuro); causal/deontic reasoning (use @ai-causal-deontic); formalisation in Lean (use @lean-knowledge-formalization).
  TRIGGERS: commonsense, naive physics, folk psychology, temporal reasoning, spatial reasoning, default reasoning.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:ai-symbolic-neuro', 'skill:lean-knowledge-formalization', 'skill:lean-zettelkasten']
metadata:
  version: "0.2.0"
  source_spec: "skills/ai-commonsense-reasoning/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# Commonsense Reasoning

Formalizing the vast body of everyday knowledge that underlies human reasoning and is critical for AI systems operating in real-world contexts.

---

## Routing

- **USE FOR:** Commonsense reasoning for AI systems — world knowledge, naive physics, folk psychology, temporal/spatial reasoning, default reasoning, and their formalization. Use for reasoning about everyday knowledge that humans take for granted but AI systems need explicitly, including the project tacit knowledge externalization pipeline's commonsense aspects.
- **DO NOT USE FOR:** formal KR/ontology engineering (use @ai-symbolic-neuro); causal/deontic reasoning (use @ai-causal-deontic); formalisation in Lean (use @lean-knowledge-formalization).
- **TRIGGERS:** commonsense, naive physics, folk psychology, temporal reasoning, spatial reasoning, default reasoning.

## Workflow

1. Classify the commonsense gap: naive physics, folk psychology, temporal, spatial, or default reasoning.
2. Pick the matching paradigm from the body (qualitative reasoning, situation calculus, default logic, etc.) and the representative formalism.
3. Apply the formalism to the concrete scenario; document where it does or doesn't yield the human-intuitive answer.
4. Hand off: to `@ai-symbolic-neuro` for ontology grounding, to `@lean-knowledge-formalization` for a Lean encoding, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the question is purely about KR/ontology — delegate to `@ai-symbolic-neuro`.
- STOP if the answer would require world-model data not in the body — escalate to `@research-council`.
- STOP if the question is about causal/deontic norms — delegate to `@ai-causal-deontic`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:ai-symbolic-neuro`, `skill:lean-knowledge-formalization`, `skill:lean-zettelkasten`.

---

## Detailed reference

Full content for `ai-commonsense-reasoning` lives in
[`references/ai-commonsense-reasoning-handbook.md`](../../references/ai-commonsense-reasoning-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

| Section | Topic |
|---|---|
| Part 1 | Commonsense Knowledge Domains |
| Part 2 | Formal Commonsense Frameworks |
| Part 3 | Qualitative Reasoning |
| Part 4 | Theory of Mind & BDI |
| Part 5 | Temporal Commonsense |
| Part 6 | Commonsense Physics & Spatial Reasoning |
| Part 7 | Integration with Lean Formalization |
| Part 8 | Research Directions |
| Part 9 | Skill Cross-References |

---

## See also

- [`../../references/ai-commonsense-reasoning-handbook.md`](../../references/ai-commonsense-reasoning-handbook.md) — Full handbook (extracted from this skill)
- [`../ai-symbolic-neuro/SKILL.md`](../ai-symbolic-neuro/SKILL.md) — Successor
- [`../lean-knowledge-formalization/SKILL.md`](../lean-knowledge-formalization/SKILL.md) — Successor
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor

