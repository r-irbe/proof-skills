# references/ -- Background Knowledge, Proof Guides and Handbooks

This directory contains 58 reference documents, tactic guides, and domain handbooks
supporting the proof-skills repository.

Strict 7-bit ASCII only.

---

## Master Index

See **[INDEX.md](INDEX.md)** for the complete, searchable directory organized by
Agent Role (Specifier, Prover, Auditor, Gardener) and Domain Facet (Core, Math,
AI, Governance).

---

## Quick Navigation for AI Provers

If you are an autonomous coding agent working on Lean 4 theorem proving:

1. **Before writing a proof**: Read [lean4-lsp-guide.md](lean4-lsp-guide.md) to query
   proof state and expected term types via LSP, and harvest Try this suggestions.
2. **Interactive Proof Rules**: Follow [lean4-lsp-proof-protocol.md](lean4-lsp-proof-protocol.md)
   (zero trace_state file pollution; query plainGoal directly).
3. **Tactic Hierarchy**: Follow [lean4-tactic-hierarchy.md](lean4-tactic-hierarchy.md)
   (rfl -> omega / linarith -> simp only -> aesop -> exact?).
4. **Subgoal Decomposition**: Use [lean4-proof-strategy.md](lean4-proof-strategy.md)
   for have / suffices structuring.
5. **Module DAG Hygiene**: Consult [lean4-module-dependency-guide.md](lean4-module-dependency-guide.md)
   to respect Layer 0-4 module boundaries.
6. **Declaration Search**: Consult [theorem-search.md](theorem-search.md) for Loogle
   and Mathlib lookup patterns.
