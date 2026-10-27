---
name: "lean-causal-reasoning"
description: |
  USE FOR: Formalize causal DAGs, knowledge graph quality gates, counterfactual reasoning, and provenance bridges in Lean 4.
  DO NOT USE FOR: causal methodology not in Lean (@lean-causal-reasoning).
  TRIGGERS: causal DAG, counterfactual proof, provenance bridge, causal Lean.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-research"]
  successors: ["skill:lean-proof-review", "skill:lean-knowledge-formalization", "skill:lean-zettelkasten"]
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-causal-reasoning/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# SK-33: Lean Causal Reasoning Formalization
---
## Routing
- **USE FOR:** Formalize causal DAGs, knowledge graph quality gates, counterfactual reasoning, and provenance
  bridges in Lean 4.
  Use for
  causal reasoning
  structures and their integration with repository-local verification pipelines.
- **DO NOT USE FOR:** causal methodology not in Lean (use @lean-causal-reasoning); knowledge graph
  formalisation generally (use
  @lean-knowledge-formalization);
  general AI formalisation (use @lean-ai-formalization).
- **TRIGGERS:** causal DAG, counterfactual proof, provenance bridge, causal Lean, knowledge graph gate.
## Workflow
1. Identify the causal object: DAG, structural causal model, counterfactual query, provenance bridge, or
  knowledge-graph gate.
2. Pick the encoding pattern from the body; verify Mathlib primitives (graph, probability) at the pin.
3. Write the Lean encoding; surface identifiability + acyclicity proof obligations.
4. Hand off: to `@lean-proof-review` for review, to `@lean-knowledge-formalization` for KR integration, to
  `@lean-zettelkasten`.
## Recovery & STOP
- STOP if the question is causal-methodological (not Lean) — delegate to `@lean-causal-reasoning`.
- STOP if the question is about general KR (not causal) — delegate to `@lean-knowledge-formalization`.
- STOP if Mathlib primitives are missing — escalate to `@lean-research`.
## Handoffs
- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-proof-review`, `skill:lean-knowledge-formalization`, `skill:lean-zettelkasten`.
---
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-causal-reasoning-handbook.md`](../../references/lean-causal-reasoning-handbook.md) .
## See also
- [`../../references/lean-causal-reasoning-handbook.md`](../../references/lean-causal-reasoning-handbook.md)
  -- Complete
  `lean-causal-reasoning` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
