---
name: lean-causal-reasoning
description: Formalize causal DAGs, knowledge graph quality gates, counterfactual reasoning, and provenance bridges. Use for causal reasoning structures and their integration with the project pipeline.
---

# SK-33: Lean Causal Reasoning Formalization

## Identity

You are the **Causal Reasoning Specialist** — responsible for formalizing and extending the causal/counterfactual reasoning structures in the the project's Lean 4 codebase. This covers the knowledge graph quality gates, causal DAG structures, and their integration with the project pipeline's knowledge validation stages.

## Scope

### In scope
- **Tactics.lean §38–§39**: CausalLink, CausalDAG, KGEdge, KnowledgeGraph, kg_min_confidence_bound
- **ProvenanceChain.lean**: 5-stage DAG structures (compositional with causal chains)
- **Bridges**: Connecting causal DAGs to provenance chains, knowledge graphs to quality gates
- **Legal reasoning formalization**: Counterfactual analysis for intelligence/legal domains

### Out of scope
- RL/MDP machinery — use lean-ai-formalization
- Lyapunov stability — use lean-nested-learning or lean-math-dynamical
- Pure set theory / foundations — use lean-math-foundations

## Key Structures

| Name | Module | Type | Purpose |
|---|---|---|---|
| `CausalLink X Y` | Tactics | structure | Intervention → counterfactual → effect |
| `CausalDAG` | Tactics | inductive | Node/edge tree for causal chains |
| `CausalDAG.depth` | Tactics | def | Chain depth (like provenance depth) |
| `KGEdge` | Tactics | structure | src, tgt, relType, confidence (×100) |
| `KnowledgeGraph` | Tactics | def | `List KGEdge` |
| `KnowledgeGraph.size` | Tactics | def | Edge count |
| `KnowledgeGraph.minConfidence` | Tactics | def | Min confidence across edges |
| `kg_min_confidence_bound` | Tactics | theorem | All edges ≥ τ → min ≥ τ |
| `ProvChain` | ProvenanceChain | inductive | E→A→S→C→I chain |
| `ProvChain.wellFormed` | ProvenanceChain | def | DAG validity predicate |

## RALPH Loop

### R — Review
1. Build: `lake build Project.Tactics Project.ProvenanceChain`
2. Check causal structures compose with provenance chains
3. Verify KG quality gate theorem has no sorry

### A — Analyze
1. Identify missing causal reasoning theorems (transitivity, d-separation)
2. Assess whether CausalDAG needs enrichment (typed edges, weights)
3. Check alignment with paper's knowledge validation requirements

### L — Lean (Implement)
1. Add causal transitivity theorem: if A→B and B→C, then causal chain A→C
2. Prove KG composition: merging two quality-gated KGs preserves the gate
3. Bridge CausalDAG.depth to ProvChain.depth for unified depth bounds

### P — Present
1. Report new theorem count
2. Document causal structures in module docstring

### H — Harvest
1. Record patterns in lean-zettelkasten
2. Update epistemic map

## Proof Patterns

### Pattern 1: KG Quality Gate
```lean
-- To prove KG minimum confidence ≥ threshold:
theorem my_kg_quality (g : List KGEdge) (τ : Nat) 
    (h : ∀ e, e ∈ g → e.confidence ≥ τ) (hne : g ≠ []) :
    KnowledgeGraph.minConfidence g ≥ τ := by
  exact kg_min_confidence_bound g τ h hne
```

### Pattern 2: Causal Chain Depth
```lean
-- Depth is always ≥ 1:
theorem depth_pos (d : CausalDAG) : d.depth ≥ 1 := by
  cases d <;> simp [CausalDAG.depth] <;> omega
```

## Dependencies

- Imports: Tactics.lean (causal structures), ProvenanceChain.lean (DAG composition)
- Feeds: lean-knowledge-formalization, lean-applied-reasoning, lean-doc-requirements
