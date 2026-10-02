---
name: "lean-bigraph-modeling"
description: |
  USE FOR: Robin Milner Bigraphical Reactive Systems (BRS), orthogonal Place Graph (containment forest) and Link Graph (relational hyperedges), tensor product, categorical composition, interface faces, and structural well-formedness proofs in Lean 4.
  DO NOT USE FOR: standard simple graphs without containment hierarchy (use @lean-math-discrete); abstract monoidal category theory without bigraphs (use @lean-math-foundations).
  TRIGGERS: bigraph, place graph, link graph, hyperedge, containment forest, milner, tensor product, categorical composition, port rewiring.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-math-discrete", "skill:lean-proof"]
  successors: ["skill:lean-proof", "skill:lean-proof-review", "skill:lean-math-discrete"]
metadata:
  version: "0.1.0"
  source_spec: "skills/lean-bigraph-modeling/SKILL.md (this file)"
  last_reviewed: "2026-10-02"
---

# Lean 4 Milner Bigraphical Reactive Systems Modeling

Guide to formalizing Milner Bigraphs (Place Graphs + Link Graphs), interface faces, tensor products, and categorical composition in Lean 4.

## Routing

- **USE FOR:** Robin Milner Bigraphical Reactive Systems (BRS), orthogonal Place Graph (containment forest) and Link Graph (relational hyperedges), tensor product, categorical composition, interface faces, and structural well-formedness proofs in Lean 4.
- **DO NOT USE FOR:** standard simple graphs without containment hierarchy (delegate to `@lean-math-discrete`); abstract monoidal category theory without bigraphs (delegate to `@lean-math-foundations`).
- **TRIGGERS:** bigraph, place graph, link graph, hyperedge, containment forest, milner, tensor product, categorical composition, port rewiring.

## Workflow

1. Model the Place Graph as a parent pointer function `parent : NodeId -> Option NodeId` with explicit acyclicity invariants.
2. Model the Link Graph as hyperedges connecting sets of ports `linkMap : Port -> Option EdgeId` with typed relation kinds.
3. Formulate interface boundaries as faces `<width, names>`, where width represents sites/regions and names represent inner/outer link endpoints.
4. Prove orthogonality: demonstrate that rewiring link hyperedges leaves parent containment invariant (`rfl`).
5. Prove composition properties: prove tensor product commutativity (`place_tensor_count_comm`) and depth monotonicity under categorical grafting.
6. Verify against `templates/Template_Bigraph.md`.

## Recovery & STOP

- STOP if estimated belief that the bigraph representation satisfies structural acyclicity is below 0.90 -- ask user via HITL channel.
- STOP if custom axioms are proposed -- all bigraph theorems must resolve solely on `propext` and `Quot.sound`.
- STOP if link rewiring leaks into place containment -- verify orthogonality by definitional reflexivity.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-math-discrete` (graph definitions), `skill:lean-proof` (tactics).
- **Successors:** `skill:lean-proof` (theorem discharge), `skill:lean-proof-review` (axiom and invariant audit).
