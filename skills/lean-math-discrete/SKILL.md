---
name: "lean-math-discrete"
description: |
  USE FOR: graph theory, applied lattice theory, combinatorics, DAGs, posets, provenance chains, dependency orders.
  DO NOT USE FOR: the abstract algebraic typeclass tower (@lean-math-foundations).
  TRIGGERS: graph, DAG, lattice, poset, combinatorics, provenance.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-proof", "skill:lean-research"]
  successors: ["skill:lean-proof", "skill:lean-proof-review", "skill:lean-math-foundations"]
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-math-discrete/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Lean 4 Discrete Mathematics & Graph Theory
Guide to formalizing graphs, lattices, combinatorics, and discrete structures in Lean 4.
## Routing
- **USE FOR:** graph theory, applied lattice theory, combinatorics, DAGs, posets, provenance chains,
  dependency orders, lattice
  operations
  (severity /
  quality-gate / trust-vector / information-flow lattices), combinatorial bounds, and finite structures in
  Lean 4. Owns all
  applied lattice
instances.
- **DO NOT USE FOR:** the abstract algebraic typeclass tower (delegate to `@lean-math-foundations`);
  continuous structures
  (delegate to
  `@lean-math-analysis`); writing one specific proof (delegate to `@lean-proof`).
## Workflow
1. Identify the discrete structure (graph, lattice, poset, finite set, combinatorial relation).
2. Map to the matching `Mathlib.Combinatorics.*` / `Mathlib.Order.*` API and read the relevant Part below.
3. Apply the pattern; handoff to `@lean-proof` for the concrete proof and to `@lean-math-foundations` if a
  `DecidableEq` /
  `Fintype`
   instance is missing.
## Recovery & STOP
- STOP if cardinality blows up or a `Fintype` instance cannot be synthesised — handoff to
  `@lean-math-foundations` for the
  instance
  plumbing.
- STOP if the lattice instance you need does not exist at the current Mathlib pin — escalate to
  `@lean-research`, then author the
  instance
  under `@lean-proof`.
## Handoffs
- **Predecessors:** `agent:gateway`, `skill:lean-proof` (mid-proof graph or lattice goal),
  `skill:lean-research` (combinatorial
  result
  survey).
- **Successors:** `skill:lean-proof` (apply the discrete pattern), `skill:lean-proof-review` (audit the
  instance),
  `skill:lean-math-foundations` (typeclass
  / decidability plumbing).
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-math-discrete-handbook.md`](../../references/lean-math-discrete-handbook.md) .
## See also
- [`../../references/lean-math-discrete-handbook.md`](../../references/lean-math-discrete-handbook.md) --
  Complete
  `lean-math-discrete` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
