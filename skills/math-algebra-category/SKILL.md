---
name: "math-algebra-category"
description: |
  USE FOR: Abstract algebra, category theory, lattice theory, universal algebra, and algebraic structures relevant to Project formalization. Use for reasoning about groups, rings, fields, modules, categories, functors, natural transformations, monads, adjunctions, lattices, and algebraic hierarchies. Covers both pure algebraic theory and categorical perspectives essential for type-theoretic formalization.
  DO NOT USE FOR: measure-theoretic reasoning (use @math-measure-probability); topology/analysis (use @math-topology-analysis); Lean proof (use @lean-math-foundations).
  TRIGGERS: abstract algebra, category theory, lattice theory, universal algebra, algebraic structure.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-math-foundations', 'skill:lean-research', 'skill:lean-zettelkasten']
metadata:
  version: "0.2.0"
  source_spec: "skills/math-algebra-category/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# Abstract Algebra & Category Theory

Algebraic and categorical foundations for the project's type-hierarchies, compositional structures, lattice-based orderings, and the deep connection between algebra and dependent type theory that makes Lean formalization possible.

---

## Routing

- **USE FOR:** Abstract algebra, category theory, lattice theory, universal algebra, and algebraic structures relevant to Project formalization. Use for reasoning about groups, rings, fields, modules, categories, functors, natural transformations, monads, adjunctions, lattices, and algebraic hierarchies. Covers both pure algebraic theory and categorical perspectives essential for type-theoretic formalization.
- **DO NOT USE FOR:** measure-theoretic reasoning (use @math-measure-probability); topology/analysis (use @math-topology-analysis); Lean proof (use @lean-math-foundations).
- **TRIGGERS:** abstract algebra, category theory, lattice theory, universal algebra, algebraic structure.

## Workflow

1. Classify the structure: group / ring / field / module / lattice / category / functor / monoidal.
2. Pick the matching section of the body for the structure + its standard constructions.
3. Produce the mathematical answer or the Mathlib pointer; surface any Mathlib namespacing convention.
4. Hand off: to `@lean-math-foundations` for the Lean encoding, to `@lean-research` if pin-verification is needed, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the question is measure-theoretic — delegate to `@math-measure-probability`.
- STOP if topology/analysis dominates — delegate to `@math-topology-analysis`.
- STOP if the answer requires a pin-verified Mathlib lemma — escalate to `@lean-research`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-math-foundations`, `skill:lean-research`, `skill:lean-zettelkasten`.

---

## Detailed reference

Full content for `math-algebra-category` lives in
[`references/math-algebra-category-handbook.md`](../../references/math-algebra-category-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

| Section | Topic |
|---|---|
| Part 1 | Algebraic Structures Hierarchy |
| Part 2 | Lattice Theory |
| Part 3 | Category Theory Foundations |
| Part 4 | Monads and Computational Effects |
| Part 5 | Topos Theory and Logic |
| Part 6 | Type Theory as Algebra |
| Part 7 | Homological Methods |
| Part 8 | Galois Theory Perspective |
| Part 9 | Formalization Connections |

---

## See also

- [`../../references/math-algebra-category-handbook.md`](../../references/math-algebra-category-handbook.md) — Full handbook (extracted from this skill)
- [`../lean-math-foundations/SKILL.md`](../lean-math-foundations/SKILL.md) — Successor
- [`../lean-research/SKILL.md`](../lean-research/SKILL.md) — Successor
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor

