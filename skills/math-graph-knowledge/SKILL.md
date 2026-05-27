---
name: "math-graph-knowledge"
description: |
  USE FOR: Graph theory, knowledge graphs, ontology engineering, provenance structures, network analysis, and formal knowledge representation. Use for mathematical reasoning about DAGs, KGs, trust networks, provenance chains, and any graph-structured knowledge. Covers both pure graph theory and applied knowledge graph methodology relevant to Project.
  DO NOT USE FOR: KRR / symbolic AI (use @ai-symbolic-neuro); causal DAGs (use @ai-causal-deontic); discrete math (use @lean-math-discrete).
  TRIGGERS: graph theory, knowledge graph, ontology, provenance, network analysis, formal knowledge representation.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-math-discrete', 'skill:lean-knowledge-formalization', 'skill:lean-zettelkasten']
metadata:
  version: "0.2.0"
  source_spec: "skills/math-graph-knowledge/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# Graph Theory & Knowledge Graph Mathematics

Graph-theoretic and knowledge representation foundations for the project's provenance chains, trust networks, knowledge lifecycle, and causal reasoning structures.

---

## Routing

- **USE FOR:** Graph theory, knowledge graphs, ontology engineering, provenance structures, network analysis, and formal knowledge representation. Use for mathematical reasoning about DAGs, KGs, trust networks, provenance chains, and any graph-structured knowledge. Covers both pure graph theory and applied knowledge graph methodology relevant to Project.
- **DO NOT USE FOR:** KRR / symbolic AI (use @ai-symbolic-neuro); causal DAGs (use @ai-causal-deontic); discrete math (use @lean-math-discrete).
- **TRIGGERS:** graph theory, knowledge graph, ontology, provenance, network analysis, formal knowledge representation.

## Workflow

1. Classify the graph object: directed / undirected / weighted / hypergraph / knowledge-graph / ontology-graph.
2. Pick the matching section (graph algorithms, KR semantics, provenance, network metrics).
3. Produce the answer; reference the relevant Mathlib `SimpleGraph` / `Graph` / `Quiver` namespaces.
4. Hand off: to `@lean-math-discrete` for Lean proof, to `@lean-knowledge-formalization` for ontology encoding, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if KRR/symbolic AI methodology dominates — delegate to `@ai-symbolic-neuro`.
- STOP if causal-DAG semantics dominate — delegate to `@ai-causal-deontic`.
- STOP if a pin-verified Mathlib construction is required — escalate to `@lean-research`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-math-discrete`, `skill:lean-knowledge-formalization`, `skill:lean-zettelkasten`.

---

## Detailed reference

Full content for `math-graph-knowledge` lives in
[`references/math-graph-knowledge-handbook.md`](../../references/math-graph-knowledge-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

| Section | Topic |
|---|---|
| Part 1 | Graph Theory Foundations |
| Part 2 | Knowledge Graph Theory |
| Part 3 | Provenance Mathematics |
| Part 4 | Network Analysis for Knowledge Structures |
| Part 5 | Ontology Engineering |
| Part 6 | Causal Graph Theory |
| Part 7 | Formalization Entry Points |

---

## See also

- [`../../references/math-graph-knowledge-handbook.md`](../../references/math-graph-knowledge-handbook.md) — Full handbook (extracted from this skill)
- [`../lean-math-discrete/SKILL.md`](../lean-math-discrete/SKILL.md) — Successor
- [`../lean-knowledge-formalization/SKILL.md`](../lean-knowledge-formalization/SKILL.md) — Successor
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor

