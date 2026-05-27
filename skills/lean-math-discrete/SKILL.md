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

---

## Part 1 — Graph Theory in Lean

### 1.1 Mathlib Graph Representations

```lean
-- Mathlib.Combinatorics.SimpleGraph
-- SimpleGraph V: symmetric, irreflexive relation on V
-- For directed graphs: use Quiver or direct relation

-- Directed graph (most common in the project):
structure DiGraph (V : Type) where
  edge : V → V → Prop

-- DAG: directed acyclic graph
structure DAG (V : Type) extends DiGraph V where
  acyclic : ∀ v, ¬ (TransGen edge v v)  -- no cycles via transitive closure
```

### 1.2 Project Graph Structures

| Structure | Type | Project Module | Properties |
|---|---|---|---|
| Provenance chain | DAG | ProvenanceChain | 5-stage, well-formed, depth-bounded |
| Module dependency | DAG | (Build system) | Topological order, import graph |
| Knowledge graph | Directed graph | (Conceptual) | May have cycles (revisions) |
| Phase transition | State machine | PhaseClassification | Finite states, deterministic |
| Pipeline flow | DAG | PipelineAdaptive | Sequential stages with feedback edges |

### 1.3 Provenance DAG Formalization

```lean
-- Project ProvenanceChain: 5-stage DAG
-- Stages: Experience → Articulation → Structuring → Consolidation → Innovation
inductive ProvStage | E | A | S | C | I

-- Chain: sequence of provenance nodes
structure ProvNode where
  stage : ProvStage
  author : String
  timestamp : Nat
  content_hash : Nat

-- Well-formedness: stages appear in order, no skips
def WellFormed (chain : List ProvNode) : Prop :=
  chain.Chain' (fun a b => a.stage.toNat < b.stage.toNat)

-- Depth bound: chain length ≤ 5 (one per stage)
theorem chain_depth_bound (h : WellFormed chain) : chain.length ≤ 5 := by
  omega  -- or induction on chain structure
```

---

## Part 2 — DAG Algorithms

### 2.1 Topological Sort

```lean
-- A topological sort of a DAG is a linear extension of the partial order
-- Existence: every finite DAG has a topological sort
-- Uniqueness: not unique in general

-- Project usage: module build order = topological sort of import graph
-- Audit waves = layers of the topological sort
```

### 2.2 Reachability

```lean
-- TransGen R x y: y is reachable from x via R (transitive closure)
-- ReflTransGen R x y: y is reachable from x via R, or x = y

-- Project: can we reach module B from module A via imports?
-- Provenance: is artifact B derived from artifact A?
```

### 2.3 Well-Founded Recursion on DAGs

```lean
-- DAGs have well-founded edge relations (no cycles)
-- This enables structural induction / well-founded recursion

-- Pattern: prove a property for all nodes by induction on DAG depth
theorem dag_induction (hdag : IsDAG G) (hbase : ∀ v, (∀ w, ¬G.edge w v) → P v)
    (hstep : ∀ v, (∀ w, G.edge w v → P w) → P v) :
    ∀ v, P v := by
  exact WellFounded.fix hdag.wf (fun v ih => hstep v (fun w hw => ih w hw))
```

---

## Part 3 — Lattice Theory

### 3.1 Lattice Hierarchy in Mathlib

```
Preorder → PartialOrder → SemilatticeSup → Lattice
                         → SemilatticeInf ↗
                                            → DistribLattice
                                            → CompleteLattice
                                            → BooleanAlgebra
```

### 3.2 Project Lattice Structures

| Project Concept | Lattice Structure | Operations |
|---|---|---|
| Quality gate outputs | BoundedOrder on `{pass, warn, fail}` | `⊔` = worst, `⊓` = best |
| Alert severity | LinearOrder on `{none, low, medium, high, critical}` | `max`, `min` |
| Phase severity | LinearOrder on `{stable, transition, chaotic, collapse}` | `max` |
| Trust components | PartialOrder on trust vectors | Componentwise `≤` |
| Information flow | Lattice of security levels | Join = LUB, Meet = GLB |

### 3.3 Fixed Points on Lattices

```lean
-- Knaster-Tarski: monotone f on complete lattice has a fixed point
-- lfp f = ⊓ {x | f x ≤ x}  -- least fixed point
-- gfp f = ⊔ {x | x ≤ f x}  -- greatest fixed point

-- Project: quality gate cascade reaches a fixed point
-- (processing gates in order converges to unique outcome)
```

---

## Part 4 — Combinatorics

### 4.1 Counting Arguments

```lean
-- Fintype: finite type with decidable equality
-- Finset.card: cardinality of a finite set
-- Fintype.card: cardinality of a finite type

-- Project: counting phase states, gate combinations, pipeline configurations
-- Example: exactly 4 phase types → 4^n configurations for n components

-- Pigeonhole principle: Finset.exists_lt_card_fiber_of_nMul_lt_card
```

### 4.2 Binomial Coefficients and Bounds

```lean
-- Nat.choose n k: binomial coefficient C(n,k)
-- Properties: Nat.choose_symm, Nat.choose_le_choose

-- Project: combinatorial explosion analysis
-- Number of possible provenance paths through 5 stages with branching
```

### 4.3 Inclusion-Exclusion

```lean
-- |A ∪ B| = |A| + |B| - |A ∩ B|
-- Finset.card_union_add_card_inter

-- Project: overlap analysis between quality gate domains
```

---

## Part 5 — Knowledge Graph Formalization

### 5.1 RDF-Like Structures

```lean
-- Triple: (subject, predicate, object)
structure Triple (Entity Relation : Type) where
  subject : Entity
  predicate : Relation
  object : Entity

-- Knowledge graph: set of triples
def KnowledgeGraph (E R : Type) := Set (Triple E R)

-- PROV-O provenance: specialization of knowledge graph
-- with specific relations: wasGeneratedBy, wasDerivedFrom, wasAttributedTo
```

### 5.2 Ontological Reasoning

```lean
-- Subsumption: A ⊑ B (every instance of A is an instance of B)
-- Transitivity: A ⊑ B ∧ B ⊑ C → A ⊑ C
-- This forms a preorder on concepts

-- Project: stage hierarchy, quality level hierarchy
-- Formalize as PartialOrder on concept types
```

### 5.3 Graph Metrics

```lean
-- Centrality measures (for knowledge graph analysis):
-- Degree centrality: number of edges
-- Betweenness: fraction of shortest paths through node
-- PageRank: eigenvector of modified adjacency matrix

-- Project: trust centrality in multi-agent provenance
-- Which artifacts/agents are most central to knowledge flow?
```

---

## Part 6 — Finite State Machines

### 6.1 Automata in Lean (CSLib)

```lean
-- CSLib provides automata foundations:
-- DFA, NFA, regular languages
-- Project imports CSLib for state machine reasoning

-- Project phase classification is a finite state machine:
-- States: {stable, transition, chaotic, collapse}
-- Transitions: governed by quality score thresholds
-- Deterministic: each quality score maps to exactly one phase
```

### 6.2 State Machine Properties

```lean
-- Reachability: is state s reachable from s₀?
-- Safety: bad states are unreachable
-- Liveness: good states are eventually reached
-- Fairness: all states visited infinitely often (under conditions)

-- Project: safety = collapse state unreachable under normal operation
-- Liveness = system eventually reaches stable state
```

---

## Part 7 — Order Theory Extensions

### 7.1 Well-Quasi-Orders

```lean
-- WQO: no infinite antichains, no infinite strictly decreasing sequences
-- Dickson's lemma: ℕⁿ with componentwise ≤ is a WQO
-- Relevant for termination arguments in the project pipeline
```

### 7.2 Galois Connections

```lean
-- GaloisConnection l u where l ⊣ u:
-- ∀ a b, l a ≤ b ↔ a ≤ u b

-- Project: abstraction/concretization framework
-- Abstract interpretation of quality scores
-- l: concrete → abstract (quality score → phase classification)
-- u: abstract → concrete set (phase → quality range)
```

---

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

- [`../../templates/Template_Arithmetic.md`](../../templates/Template_Arithmetic.md) — Template: Nat/Int arithmetic and simplex constraints
- [`../../templates/Template_Foundation.md`](../../templates/Template_Foundation.md) — Template: Decidable predicates and case analysis
