---
title: "Discrete Mathematics Encyclopaedia (Lean 4)"
status: "reference"
extracted_from: "skills/lean-math-discrete/SKILL.md"
extracted_on: "2026-05-27"
scope: "Parts 1-7 (graph theory, DAG algorithms, lattice theory, combinatorics, knowledge-graph formalization, finite state machines, order-theory extensions)"
loader_hint: "Load when @lean-math-discrete routes here; not needed for dispatch decisions."
---

# Discrete Mathematics Encyclopaedia (Lean 4)

> **Layering note.** This file holds the deep encyclopaedia content
> previously embedded in [`skills/lean-math-discrete/SKILL.md`](../skills/lean-math-discrete/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow / Recovery /
> Handoffs) and the high-frequency pitfalls / recipes; this file holds the
> full reference content. Zero fidelity loss vs the pre-layering revision.

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

