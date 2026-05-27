---
name: "lean-math-discrete"
description: |
  USE FOR: graph theory, applied lattice theory, combinatorics, DAGs, posets, provenance chains, dependency orders, lattice operations (severity / quality-gate / trust-vector / information-flow lattices), combinatorial bounds, and finite structures in Lean 4. Owns all applied lattice instances.
  DO NOT USE FOR: the abstract algebraic typeclass tower (use @lean-math-foundations); continuous structures (use @lean-math-analysis); writing one specific proof (use @lean-proof).
  TRIGGERS: graph, DAG, lattice, poset, combinatorics, provenance, dependency graph, severity lattice, knowledge graph, finite set bound.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
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

- **USE FOR:** graph theory, applied lattice theory, combinatorics, DAGs, posets, provenance chains, dependency orders, lattice operations (severity / quality-gate / trust-vector / information-flow lattices), combinatorial bounds, and finite structures in Lean 4. Owns all applied lattice instances.
- **DO NOT USE FOR:** the abstract algebraic typeclass tower (delegate to `@lean-math-foundations`); continuous structures (delegate to `@lean-math-analysis`); writing one specific proof (delegate to `@lean-proof`).
- **TRIGGERS:** graph, DAG, lattice, poset, combinatorics, provenance, dependency graph, severity lattice, knowledge graph, finite set bound.

## Workflow

1. Identify the discrete structure (graph, lattice, poset, finite set, combinatorial relation).
2. Map to the matching `Mathlib.Combinatorics.*` / `Mathlib.Order.*` API and read the relevant Part below.
3. Apply the pattern; handoff to `@lean-proof` for the concrete proof and to `@lean-math-foundations` if a `DecidableEq` / `Fintype` instance is missing.

## Recovery & STOP

- STOP if cardinality blows up or a `Fintype` instance cannot be synthesised — handoff to `@lean-math-foundations` for the instance plumbing.
- STOP if the lattice instance you need does not exist at the current Mathlib pin — escalate to `@lean-research`, then author the instance under `@lean-proof`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-proof` (mid-proof graph or lattice goal), `skill:lean-research` (combinatorial result survey).
- **Successors:** `skill:lean-proof` (apply the discrete pattern), `skill:lean-proof-review` (audit the instance), `skill:lean-math-foundations` (typeclass / decidability plumbing).

## Detailed reference

Full encyclopaedia content (Parts 1 through 7) lives in
[`references/lean4-math-discrete.md`](../../references/lean4-math-discrete.md). Load that file
when authoring; the SKILL.md only carries the dispatch contract and
the high-frequency pitfalls / recipes (kept inline below).

| Part | Topic | Covers |
|---|---|---|
| Part 1 | Graph Theory in Lean | SimpleGraph, Reachable, Connected, Walk / Path |
| Part 2 | DAG Algorithms | Quiver.Path, topological-sort idioms (no canonical Mathlib tactic) |
| Part 3 | Lattice Theory | Lattice, CompleteLattice, sup_inf distributivity, BoundedOrder |
| Part 4 | Combinatorics | Finset, Multiset, combinatorial identities, choose-sum lemmas |
| Part 5 | Knowledge Graph Formalization | project knowledge-graph + provenance-chain idioms |
| Part 6 | Finite State Machines | Inductive State types, transition relations, reachability |
| Part 7 | Order Theory Extensions | Galois insertions, abstract interpretation patterns |

## Part 8 — Research Council Integration

Consolidated into the single canonical routing matrix:
[`references/research-council-skill-map.md`](../../references/research-council-skill-map.md)
(see the "Discrete" section).  When dispatching a question to a
council member, cite that table rather than restating the rows here.

---

## Part 9 — Common Pitfalls & Quick Tactics

| Pitfall | Symptom | Recovery |
|---|---|---|
| Missing `DecidableEq` on vertex type | `decide` / `fin_cases` fail with `failed to synthesize` | `derive DecidableEq` on the type; or `instance : DecidableEq V := …`; for adhoc structures use `instance : DecidableEq V := by intro a b; cases a <;> cases b <;> simp` |
| Confusing `Finset` vs `Set` | `Finset.mem` doesn't fire on a `Set` goal | Use `Set.toFinset` (needs `[Fintype]`) or rewrite the goal in `Finset` terms; the two APIs do not mix lemma-by-lemma |
| `omega` fails on a "should be obvious" `Finset.card` bound | `omega` has no `card` lemmas | Unfold `Finset.card` via `Finset.card_insert_of_not_mem` / `Finset.card_image_of_injective` first, then `omega` |
| Lattice instance overlap with foundations | Diamond / "multiple instances" warning | Locally `attribute [-instance] foo` or move the instance to the right cluster (applied → here, abstract → foundations) |
| Infinite graph snuck in | `Decidable` synthesis explodes; build hangs | Add `[Fintype V]` and re-check the existential / for-all is bounded over a `Finset`, not a `Set` |
| `SimpleGraph` vs `Graph` (multi-edge) confusion | Theorem statement uses the wrong vertex pair type | `SimpleGraph` = irreflexive symmetric `V → V → Prop`; multi-edge graphs need `Quiver` or hand-rolled types |

### Quick reference — top-5 discrete tactics

1. **`decide`** — for *closed* finite goals (no free variables, small cardinality); the workhorse for `Decidable` props on `Fin n`.
2. **`omega`** — linear arithmetic over `Nat` / `Int`; works on `Finset.card` *only* after unfolding the cardinality recurrence.
3. **`fin_cases h`** — case-split on `Fin n`, `Finset`, or `Finset.range`; the canonical way to enumerate.
4. **`simp [Finset.mem_*]`** — Finset membership rewrites are the staple; pair with `mem_filter`, `mem_image`, `mem_insert`.
5. **`aesop`** — try last; often closes graph-and-lattice mixed goals with `aesop (add safe simp [Finset.subset_iff])`.

---

## Part 10 — Mathlib Cross-Reference Index

Concrete entry-points for the most common discrete-math goals:

| Goal | Mathlib lemma / namespace |
|---|---|
| Connectivity in a `SimpleGraph` | `SimpleGraph.Connected`, `Reachable` |
| DAG / topological sort | `Quiver.Path`, no canonical topological-sort tactic — author one |
| Lattice `sup`/`inf` interaction | `Mathlib.Order.Lattice` — `sup_inf_distrib_left` family |
| Galois connection between concrete and abstract | `GaloisConnection`, `GaloisInsertion` in `Mathlib.Order.GaloisConnection` |
| Finset cardinality bound | `Finset.card_le_card`, `Finset.card_image_le`, `Finset.card_filter_le` |
| `Fintype` instance on a structure | `deriving Fintype, DecidableEq` (works on most product / sum types) |
| Combinatorial identity | `Finset.sum_range_succ`, `Finset.sum_choose_succ_*` (Pascal-rule family) |

---

## See also

- [`../../references/lean4-math-discrete.md`](../../references/lean4-math-discrete.md) — Discrete Mathematics Encyclopaedia (full encyclopaedia, extracted from this skill)
- [`../../templates/Template_Arithmetic.md`](../../templates/Template_Arithmetic.md) — Template: Nat/Int arithmetic and simplex constraints
- [`../../templates/Template_Foundation.md`](../../templates/Template_Foundation.md) — Template: Decidable predicates and case analysis
