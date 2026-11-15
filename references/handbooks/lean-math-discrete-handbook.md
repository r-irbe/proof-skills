---
name: lean-math-discrete-handbook
description: Unified reference handbook for @lean-math-discrete (Lean 4 formalization
  + domain mathematical theory).
extracted_from: skills/lean-math-discrete/SKILL.md
---

# Discrete Mathematics Encyclopaedia (Lean 4)

> **Layering note.** This file holds the deep encyclopaedia content
> previously embedded in [`skills/lean-math-discrete/SKILL.md`](../../skills/lean-math-discrete/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow / Recovery /
> Handoffs) and the high-frequency pitfalls / recipes; this file holds the
> full reference content. Zero fidelity loss vs the pre-layering revision.

## Part 1 -- Graph Theory in Lean

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

## Part 2 -- DAG Algorithms

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

## Part 3 -- Lattice Theory

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

## Part 4 -- Combinatorics

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

## Part 5 -- Knowledge Graph Formalization

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

## Part 6 -- Finite State Machines

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

## Part 7 -- Order Theory Extensions

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

---

## Inline Pitfalls & Recovery Recipes (from `skills/lean-math-discrete/SKILL.md`)

# Lean 4 Discrete Mathematics & Graph Theory

Guide to formalizing graphs, lattices, combinatorics, and discrete structures in Lean 4.

## Routing

- **USE FOR:** graph theory, applied lattice theory, combinatorics, DAGs, posets, provenance chains, dependency orders, lattice operations (severity /
  quality-gate / trust-vector / information-flow lattices), combinatorial bounds, and finite structures in Lean 4. Owns all applied lattice instances.
- **DO NOT USE FOR:** the abstract algebraic typeclass tower (delegate to `@lean-math-foundations`); continuous structures (delegate to
  `@lean-math-analysis`); writing one specific proof (delegate to `@lean-proof`).
- **TRIGGERS:** graph, DAG, lattice, poset, combinatorics, provenance, dependency graph, severity lattice, knowledge graph, finite set bound.

## Workflow

1. Identify the discrete structure (graph, lattice, poset, finite set, combinatorial relation).
2. Map to the matching `Mathlib.Combinatorics.*` / `Mathlib.Order.*` API and read the relevant Part below.
3. Apply the pattern; handoff to `@lean-proof` for the concrete proof and to `@lean-math-foundations` if a `DecidableEq` / `Fintype` instance is missing.

## Recovery & STOP

- STOP if cardinality blows up or a `Fintype` instance cannot be synthesised -- handoff to `@lean-math-foundations` for the instance plumbing.
- STOP if the lattice instance you need does not exist at the current Mathlib pin -- escalate to `@lean-research`, then author the instance under `@lean-proof`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-proof` (mid-proof graph or lattice goal), `skill:lean-research` (combinatorial result survey).
- **Successors:** `skill:lean-proof` (apply the discrete pattern), `skill:lean-proof-review` (audit the instance), `skill:lean-math-foundations` (typeclass
  / decidability plumbing).

## Detailed reference

Full encyclopaedia content (Parts 1 through 7) lives in
[`references/lean4-math-discrete.md`](lean-math-discrete-handbook.md). Load that file
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

## Part 8 -- Research Council Integration

Consolidated into the single canonical routing matrix:
[`references/research-council-skill-map.md`](../protocols/research-council-skill-map.md)
(see the "Discrete" section).  When dispatching a question to a
council member, cite that table rather than restating the rows here.

---

## Part 9 -- Common Pitfalls & Quick Tactics

| Pitfall | Symptom | Recovery |
|---|---|---|
| Missing `DecidableEq` on vertex type | `decide` / `fin_cases` fail with `failed to synthesize` | `derive DecidableEq` on the type; or `instance : DecidableEq V := ...`; for adhoc structures use `instance : DecidableEq V := by intro a b; cases a <;> cases b <;> simp` |
| Confusing `Finset` vs `Set` | `Finset.mem` doesn't fire on a `Set` goal | Use `Set.toFinset` (needs `[Fintype]`) or rewrite the goal in `Finset` terms; the two APIs do not mix lemma-by-lemma |
| `omega` fails on a "should be obvious" `Finset.card` bound | `omega` has no `card` lemmas | Unfold `Finset.card` via `Finset.card_insert_of_not_mem` / `Finset.card_image_of_injective` first, then `omega` |
| Lattice instance overlap with foundations | Diamond / "multiple instances" warning | Locally `attribute [-instance] foo` or move the instance to the right cluster (applied → here, abstract → foundations) |
| Infinite graph snuck in | `Decidable` synthesis explodes; build hangs | Add `[Fintype V]` and re-check the existential / for-all is bounded over a `Finset`, not a `Set` |
| `SimpleGraph` vs `Graph` (multi-edge) confusion | Theorem statement uses the wrong vertex pair type | `SimpleGraph` = irreflexive symmetric `V → V → Prop`; multi-edge graphs need `Quiver` or hand-rolled types |

### Quick reference -- top-5 discrete tactics

1. **`decide`** -- for *closed* finite goals (no free variables, small cardinality); the workhorse for `Decidable` props on `Fin n`.
2. **`omega`** -- linear arithmetic over `Nat` / `Int`; works on `Finset.card` *only* after unfolding the cardinality recurrence.
3. **`fin_cases h`** -- case-split on `Fin n`, `Finset`, or `Finset.range`; the canonical way to enumerate.
4. **`simp [Finset.mem_*]`** -- Finset membership rewrites are the staple; pair with `mem_filter`, `mem_image`, `mem_insert`.
5. **`aesop`** -- try last; often closes graph-and-lattice mixed goals with `aesop (add safe simp [Finset.subset_iff])`.

---

## Part 10 -- Mathlib Cross-Reference Index

Concrete entry-points for the most common discrete-math goals:

| Goal | Mathlib lemma / namespace |
|---|---|
| Connectivity in a `SimpleGraph` | `SimpleGraph.Connected`, `Reachable` |
| DAG / topological sort | `Quiver.Path`, no canonical topological-sort tactic -- author one |
| Lattice `sup`/`inf` interaction | `Mathlib.Order.Lattice` -- `sup_inf_distrib_left` family |
| Galois connection between concrete and abstract | `GaloisConnection`, `GaloisInsertion` in `Mathlib.Order.GaloisConnection` |
| Finset cardinality bound | `Finset.card_le_card`, `Finset.card_image_le`, `Finset.card_filter_le` |
| `Fintype` instance on a structure | `deriving Fintype, DecidableEq` (works on most product / sum types) |
| Combinatorial identity | `Finset.sum_range_succ`, `Finset.sum_choose_succ_*` (Pascal-rule family) |

---

## See also

- [`../../references/lean4-math-discrete.md`](lean-math-discrete-handbook.md) -- Discrete Mathematics Encyclopaedia (full encyclopaedia, extracted
  from this skill)
- [`../../templates/Template_Arithmetic.md`](../../templates/packs/domain-starters/Template_Arithmetic.md) -- Template: Nat/Int arithmetic and simplex constraints
- [`../../templates/Template_Foundation.md`](../../templates/packs/domain-starters/Template_Foundation.md) -- Template: Decidable predicates and case analysis

---

## Merged Domain Companion: `lean-math-discrete` (Unified into `@lean-math-discrete`)

# Graph Theory & Knowledge Graph Mathematics

Graph-theoretic and knowledge representation foundations for provenance chains, trust networks, knowledge lifecycles, and causal reasoning structures.

---

## Routing

- **USE FOR:** Graph theory, knowledge graphs, ontology engineering, provenance structures, network analysis, and formal knowledge representation. Use for
  mathematical reasoning about DAGs, KGs, trust networks, provenance chains, and any graph-structured knowledge. Covers both pure graph theory and applied
  knowledge graph methodology.
- **DO NOT USE FOR:** KRR / symbolic AI (use @lean-knowledge-formalization); causal DAGs (use @lean-causal-reasoning); discrete math (use @lean-math-discrete).
- **TRIGGERS:** graph theory, knowledge graph, ontology, provenance, network analysis, formal knowledge representation.

## Workflow

1. Classify the graph object: directed / undirected / weighted / hypergraph / knowledge-graph / ontology-graph.
2. Pick the matching section (graph algorithms, KR semantics, provenance, network metrics).
3. Produce the answer; reference the relevant Mathlib `SimpleGraph` / `Graph` / `Quiver` namespaces.
4. Hand off: to `@lean-math-discrete` for Lean proof, to `@lean-knowledge-formalization` for ontology encoding, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if KRR/symbolic AI methodology dominates -- delegate to `@lean-knowledge-formalization`.
- STOP if causal-DAG semantics dominate -- delegate to `@lean-causal-reasoning`.
- STOP if a pin-verified Mathlib construction is required -- escalate to `@lean-research`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-math-discrete`, `skill:lean-knowledge-formalization`, `skill:lean-zettelkasten`.

---

## Detailed reference

Full content for `lean-math-discrete` lives in
[`references/lean-math-discrete-handbook.md`](lean-math-discrete-handbook.md).
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

- [`../../references/lean-math-discrete-handbook.md`](lean-math-discrete-handbook.md) -- Full handbook (extracted from this skill)
- [`../lean-math-discrete/SKILL.md`](../../skills/lean-math-discrete/SKILL.md) -- Successor
- [`../lean-knowledge-formalization/SKILL.md`](../../skills/lean-knowledge-formalization/SKILL.md) -- Successor
- [`../lean-zettelkasten/SKILL.md`](../../skills/lean-retro-methodology/SKILL.md) -- Successor

# Math Graph Knowledge Handbook

> **Layering note.** This file holds the deep content previously
> embedded in [`skills/lean-math-discrete/SKILL.md`](../../skills/lean-math-discrete/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow /
> Recovery / Handoffs) + a parts index. This file holds the full
> encyclopaedia. Zero fidelity loss vs the pre-layering revision.

---

## Part 1 -- Graph Theory Foundations

### 1.1 Graph Types in the project

| Graph Type | Definition | Project usage |
|---|---|---|
| DAG (Directed Acyclic) | Directed, no cycles | Provenance chains, causal reasoning |
| Weighted directed | Edges carry weights | Trust networks, confidence scores |
| Bipartite | Two disjoint vertex sets | Claim↔Evidence mapping |
| Hypergraph | Edges connect >2 vertices | Multi-party trust relationships |
| Labeled graph | Vertices/edges have labels | Knowledge graph (entity-relation-entity) |
| Dynamic graph | Evolves over time | Evolving knowledge state |

### 1.2 Key Graph Properties

| Property | Definition | Project Relevance |
|---|---|---|
| Topological sort | Linear ordering respecting edge direction | Provenance chain ordering |
| Reachability | Path exists from u to v | Dependency tracing |
| Strongly connected components | Maximal subgraphs with mutual reachability | Feedback loop detection |
| Diameter | Maximum shortest path length | Provenance chain depth |
| Centrality (degree, betweenness, PageRank) | Node importance measures | Critical knowledge nodes |
| Clustering coefficient | Triangle density | Knowledge cohesion |

### 1.3 DAG-Specific Theory

```
Theorem: Every finite DAG has at least one source (no incoming edges)
         and at least one sink (no outgoing edges).

For Project provenance: 
  Sources = raw observations (Experience stage)
  Sinks = final knowledge artifacts (Innovation stage)
  
Theorem: The longest path in a DAG with n nodes has length ≤ n-1.
  → Bounds the depth of any provenance chain.

Theorem: DAG isomorphism is GI-complete.
  → Comparing provenance structures is computationally hard in general.
```

---

## Part 2 -- Knowledge Graph Theory

### 2.1 KG Formalism

```
KG = (E, R, T) where:
  E = set of entities
  R = set of relation types
  T ⊆ E × R × E = set of triples (head, relation, tail)

Extended KG with attributes:
  KG+ = (E, R, A, T, F) where:
  A = set of attribute types
  F : E × A → V = attribute value function
```

### 2.2 KG Quality Dimensions

| Dimension | Definition | Project Quality Gate |
|---|---|---|
| Completeness | What fraction of true triples are in the KG? | Coverage matrix |
| Accuracy | What fraction of KG triples are true? | Review council verification |
| Freshness | How current is the information? | Staleness detection |
| Consistency | Are there contradictions? | Ω integration check |
| Trustworthiness | How reliable are the sources? | Trust simplex scoring |

### 2.3 KG Reasoning Tasks

| Task | Description | Mathematical Foundation |
|---|---|---|
| Link prediction | Predict missing edges | Graph neural networks, tensor factorization |
| Entity resolution | Identify duplicate entities | Similarity metrics, blocking |
| Rule mining | Discover logical rules from data | Inductive logic programming |
| Ontology alignment | Match concepts across KGs | Category-theoretic functors |
| Consistency checking | Find contradictions | Description logic reasoning |
| Provenance tracking | Trace information origin | DAG path analysis |

---

## Part 3 -- Provenance Mathematics

### 3.1 PROV-O Data Model

Project uses W3C PROV-O for provenance:
```
Entity  -- a thing (data, document, knowledge artifact)
Activity -- a process that transforms entities
Agent    -- a responsible actor (human, AI, system)

Relations:
  wasGeneratedBy(entity, activity)
  used(activity, entity)
  wasAttributedTo(entity, agent)
  wasDerivedFrom(entity₁, entity₂)
  wasAssociatedWith(activity, agent)
  actedOnBehalfOf(agent₁, agent₂)
```

### 3.2 Provenance Graph Properties

| Property | Mathematical Formulation | Project Guarantee |
|---|---|---|
| Acyclicity | No directed cycles in provenance DAG | Well-foundedness of derivation |
| Completeness | Every artifact reachable from a source | Full traceability |
| Non-repudiation | Agent attribution cannot be removed | Audit trail integrity |
| Monotonicity | Provenance only grows, never shrinks | Append-only log |
| Compositionality | Local provenance composes to global | Modular provenance tracking |

### 3.3 Trust Composition in Provenance

```
Trust propagation along provenance paths:
  t(path) = Π_{e ∈ path} t(e)   (multiplicative)
  or
  t(path) = min_{e ∈ path} t(e)  (weakest-link)
  
Project uses: simplex-based trust with composition via convex combination
  t_composed = α·t₁ + (1-α)·t₂  where α reflects source reliability
```

---

## Part 4 -- Network Analysis for Knowledge Structures

### 4.1 Centrality Measures

| Measure | Formula | Project Interpretation |
|---|---|---|
| Degree centrality | d(v)/n | Knowledge connectivity |
| Betweenness | # shortest paths through v | Information bottleneck |
| Closeness | 1/Σ d(v,u) | Information accessibility |
| PageRank | π(v) = α·Σ π(u)/d(u) + (1-α)/n | Knowledge influence |
| Eigenvector | Ax = λx | Structural importance |

### 4.2 Community Detection

```
Knowledge communities = densely connected subgraphs within the KG

Methods:
  - Louvain algorithm (modularity optimization)
  - Spectral clustering (eigenvalues of graph Laplacian)
  - Label propagation
  - Stochastic block model

Project use: identify knowledge domain clusters,
  detect bridge nodes connecting different Project stages
```

### 4.3 Graph Dynamics

```
Evolving knowledge graph:
  KG(t) = (E(t), R, T(t))
  
Events:
  - Entity addition: E(t+1) = E(t) ∪ {e_new}
  - Triple addition: T(t+1) = T(t) ∪ {(h, r, t)}
  - Entity retirement: mark as historical, don't delete
  - Triple revision: add new triple + provenance link to old

Graph metrics over time:
  - Growth rate: |T(t+1)| / |T(t)|
  - Density: |T(t)| / (|E(t)|² × |R|)
  - Diameter evolution: max shortest path over time
```

---

## Part 5 -- Ontology Engineering

### 5.1 Ontology Layers

```
Upper ontology → Domain ontology → Application ontology → Instance data
  (general)        (KM domain)      (project-specific)     (actual KG)

Upper: BFO, DOLCE, SUMO
Domain: PROV-O, SKOS, Dublin Core
Application: Project ontology (stages, gates, regimes, artifacts)
```

### 5.2 Description Logic

Knowledge representation using description logic (DL):
```
Concepts: C, D (classes)
Roles: R (binary relations)
Constructors:
  C ⊓ D (intersection)
  C ⊔ D (union)
  ¬C (complement)
  ∀R.C (universal restriction)
  ∃R.C (existential restriction)
  ≥nR.C (qualified number restriction)

Project example:
  MasteryState ≡ KnowledgeState ⊓ ∃hasClarity.High ⊓ ∃hasVolatility.Low
  SafeTransition ≡ Transition ⊓ ∀usesGate.PassedGate
```

### 5.3 Formal Ontology Properties

| Property | DL Test | Project Relevance |
|---|---|---|
| Concept satisfiability | C ≠ ⊥ in all models | Gate definitions are non-vacuous |
| Subsumption | C ⊑ D | Phase hierarchy |
| Consistency | Ontology has a model | Knowledge structure is coherent |
| Classification | Compute concept hierarchy | Automatic phase taxonomy |

---

## Part 6 -- Causal Graph Theory

### 6.1 Structural Causal Models (SCM)

```
M = (U, V, F, P(U)) where:
  U = exogenous variables (external causes)
  V = endogenous variables (observed)
  F = structural equations (V_i = f_i(pa_i, U_i))
  P(U) = distribution over exogenous variables

Causal DAG: G = (V, E) where V_i → V_j iff V_i ∈ pa_j in F
```

### 6.2 Causal Reasoning Tasks

| Task | Method | Project application |
|---|---|---|
| Causal discovery | PC algorithm, FCI, GES | Discover knowledge flow paths |
| Intervention | do-calculus, P(Y|do(X)) | Governance policy effects |
| Counterfactual | Abduction → Intervention → Prediction | "What if gate wasn't applied?" |
| Mediation | Direct/indirect effects | Which Project stage mediates quality? |
| Transportability | Transfer across domains | Reuse Project in new domains |

### 6.3 Causal Hierarchy (Pearl's Ladder)

```
Level 1: Association -- P(Y|X)      -- "Seeing"
Level 2: Intervention -- P(Y|do(X))  -- "Doing" 
Level 3: Counterfactual -- P(Y_x|X',Y') -- "Imagining"

Project governance operates at all three levels:
  L1: Observe quality gate scores
  L2: Intervene with governance actions
  L3: Counterfactual analysis of alternative strategies
```

---

## Part 7 -- Formalization Entry Points

### 7.1 What's in the project Codebase Now

| Concept | Module | Status |
|---|---|---|
| DAG well-formedness | ProvenanceChain | ✅ Proven |
| Trust composition | ProvenanceChain | ✅ Proven |
| Depth bounds | ProvenanceChain | ✅ Proven |
| CausalLink/CausalDAG | Tactics | ✅ Defined |
| KGEdge/KnowledgeGraph | Tactics | ✅ Defined |
| kg_min_confidence_bound | Tactics | ✅ Proven |
| 5-stage pipeline | ProvenanceChain | ✅ Proven |

### 7.2 Formalization Frontiers

- Ontology consistency checking in Lean (description logic fragment)
- Causal inference correctness (do-calculus soundness)
- KG completion bounds (how much is missing?)
- Provenance integrity under composition
- Graph homomorphism and isomorphism certificates

---
## Goal-Shape Templates (templates)

| Goal Shape | Target Typeclass / Lemma | Proof Template |
| :--- | :--- | :--- |
| `∑ x ∈ s, f x = ∑ x ∈ s, g x` | `Finset.sum_congr` | `refine Finset.sum_congr rfl (fun x hx => ?_)` |
| `∑ x ∈ s, f x = ∑ y ∈ t, g y` | `Finset.sum_bij` | `refine Finset.sum_bij (fun x hx => i x) ?_ ?_ ?_ ?_` |
| `(s : Finset α) = t` | `Finset.ext` | `ext x; simp only [Finset.mem_...]` |
| `G.Adj u v → G.Adj v u` | `SimpleGraph.adj_symm` | `exact G.symm h` |
| DAG / poset transitivity `a ≤ c` | `le_trans` | `exact le_trans hab hbc` |

## Intent-to-Tactic Phrasebook (phrasebook)

| Mathematical Intent | Lean 4 / Mathlib Tactic | Notes |
| :--- | :--- | :--- |
| Split a finite sum at one element `a ∈ s` | `rw [← Finset.add_sum_erase _ _ ha]` | Isolates `f a` from `s.erase a` |
| Swap nested finite sums `∑ i, ∑ j` | `rw [Finset.sum_comm]` | Works on any `Finset` product |
| Prove finite cardinality identity | `simp only [Finset.card_...]; omega` | Combine `Finset.card` lemmas with `omega` |
| Decide finite graph/combinatorial property | `by decide` | Works when vertices have `[Fintype V] [DecidableEq V]` |

## Error-to-Fix Table (errors)

| Error / Symptom | Root Cause | Fix |
| :--- | :--- | :--- |
| Off-by-one in `Finset.range n` | `Finset.range n` is `[0, n)`, not `[1, n]` | Use `Finset.Icc 1 n` for closed `1..n` intervals |
| `Finset.sum_union` unsolved goal | Missing `Disjoint s t` proof | Discharge `Disjoint s t` via `Finset.disjoint_left.mpr` |
| `SimpleGraph` self-loop error | `SimpleGraph` is irreflexive (`loopless`) | Add `h : u ≠ v` before constructing adjacency |

---

## Annex: Legacy Quick-Reference Supplement (Discrete & Combinatorics)

# Discrete Mathematics Encyclopaedia (Lean 4)

> **Layering note.** This file holds the deep encyclopaedia content
> previously embedded in [`skills/lean-math-discrete/SKILL.md`](../../skills/lean-math-discrete/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow / Recovery /
> Handoffs) and the high-frequency pitfalls / recipes; this file holds the
> full reference content. Zero fidelity loss vs the pre-layering revision.

## Part 1 -- Graph Theory in Lean

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

## Part 2 -- DAG Algorithms

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

## Part 3 -- Lattice Theory

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

## Part 4 -- Combinatorics

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

## Part 5 -- Knowledge Graph Formalization

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

## Part 6 -- Finite State Machines

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

## Part 7 -- Order Theory Extensions

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

---

## Annex: Bigraphical Reactive Systems (Place & Link Graphs)

# Lean 4 Milner Bigraphical Reactive Systems Modeling

Guide to formalizing Milner Bigraphs (Place Graphs + Link Graphs), interface faces, tensor products, and categorical composition in Lean 4.

## Routing

- **USE FOR:** Robin Milner Bigraphical Reactive Systems (BRS), orthogonal Place Graph (containment forest) and Link Graph (relational hyperedges), tensor
  product, categorical composition, interface faces, and structural well-formedness proofs in Lean 4.
- **DO NOT USE FOR:** standard simple graphs without containment hierarchy (delegate to `@lean-math-discrete`); abstract monoidal category theory without
  bigraphs (delegate to `@lean-math-foundations`).
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

---

## Annex: Competition Mathematics & Certified Numeric Evaluation

# lean-competitive-math (euler-prover)

> **MANDATORY** (hot-tier): the answer-check gate (G-2), the axiom audit (G-4),
> and the no-sorry gate (G-5) are hard gates. A `native_decide` answer-check is
> allowed ONLY as a Bronze rung that ships WITH a structural-proof follow-up
> filed (G-6) -- otherwise it is an ordinary one-tactic `decide` and
> `@lean-proof-review` L3 flags it. Skipping Persist = incomplete.

Formalize a Project-Euler / competition-math problem as a Lean 4 theorem that
pins the concrete numeric answer, prove it, VERIFY the answer computes, then
IMPROVE the proof up the trust ladder. This skill owns the move that trips the
generic review gate -- closing `theorem eulerN : answer = <KNOWN> := by
native_decide` -- and gives it a governed home with an explicit carve-out.

---

## Routing

- **USE FOR:** formalizing a Project-Euler / competition-math problem as a Lean 4
  theorem asserting a concrete numeric answer; getting a first green proof
  (typically Bronze `native_decide`); verifying the answer computes (`#eval` +
  the theorem closes); auditing the compiler-trust axiom via `#print axioms`;
  and driving the improvement pass up the ladder Bronze (`native_decide`) ->
  Silver (`decide` / `norm_num`) -> Gold (characterising property / closed form).
- **DO NOT USE FOR:** authoring the theorem statement alone (use `@lean-specification`);
  writing tactics one step at a time or triaging tactic errors (use `@lean-proof`);
  generic single-proof audit outside the carve-out (use `@lean-proof-review`);
  Mathlib API / lemma discovery (use `@lean-research`); project-wide quality
  scoring (use `@lean-quality-engine`); open problems with no known numeric
  answer (this skill requires a known target).
- **TRIGGERS:** Project Euler, competition math, euler-prover, numeric answer
  theorem, answer = N, native_decide answer-check, computed constant, closed-form
  proof.

## Behavioural rules (G-*)

- **G-1** (MUST): The theorem MUST pin the expected numeric answer as the
  right-hand side (`theorem eulerN : answer = <KNOWN>`), never an existential,
  an opaque bound, or a `True`-shaped restatement. [Trace: AC-EM-01]
- **G-2** (MUST): Before claiming done, the skill MUST verify the answer computes
  -- `#eval answer` MUST print `<KNOWN>` AND the theorem MUST close (via
  `native_decide` or `decide`). A statement that type-checks but does not
  evaluate to the target is NOT done. [Trace: AC-EM-02]
- **G-3** (SHOULD): The skill SHOULD run the improvement pass -- replace
  `native_decide` with a kernel-checked or structural proof along the ladder
  Bronze (`native_decide`) -> Silver (`decide` / `norm_num`) -> Gold
  (characterising property / closed form). In `@lean-core-only` packages
  (no Mathlib; see [`../../references/lean4-core-only-profile.md`](../protocols/lean4-core-only-profile.md)),
  `norm_num` is unavailable and `native_decide` introduces `Lean.ofReduceBool`
  (`Lean.trustCompiler`), so Silver MUST use kernel-checked `decide`, `omega`,
  or `rfl`. [Trace: AC-EM-03]
- **G-4** (MUST): When a `native_decide` answer-check ships, the skill MUST record
  its justification -- the compiler-trust axiom (in current Lean a generated
  `<thm>._native.native_decide.ax_*`, underpinned by `Lean.ofReduceBool` /
  `Lean.trustCompiler`) -- and MUST audit it with `#print axioms eulerN`.
  [Trace: AC-EM-04]
- **G-5** (MUST NOT): The skill MUST NOT close with `sorry` or `admit`; a
  placeholder answer-check is not a proof and MUST NOT be persisted as one.
  [Trace: AC-EM-05]
- **G-6** (MUST): L3 carve-out -- a one-tactic `native_decide` (or `decide`)
  close on the answer theorem is legitimate at `@lean-proof-review` L3
  (non-triviality) IFF a structural-proof follow-up task is filed. Absent that
  follow-up it MUST be flagged exactly like any other one-tactic `decide`
  (mirrors `@lean-proof-review` G-5). [Trace: AC-EM-06]
- **G-7** (MUST): On any guard failure the skill MUST escalate per Recovery &
  STOP; it MUST NOT silently downgrade a gate or ship a Bronze proof past a
  fired trigger. [Trace: AC-EM-07]

## Workflow

Discover -> Plan -> Execute -> Validate -> Persist.

1. **Discover** [discover] -- read the problem; extract the KNOWN numeric answer
   from its source; locate or request the Lean/Mathlib encoding of `answer`;
   confirm `lake env lean` (or `lean`) resolves. If the theorem statement is not
   yet written, pull it from `@lean-specification`.
2. **Plan** [discover] -- choose the encoding of `answer` (Finset / List
   enumeration vs closed form) and the ladder rung to aim for. If the encoding
   or a needed Mathlib primitive is uncertain, hand to `@lean-research`. STOP if
   the answer is unknown / the problem is open (this skill needs a known target).
3. **Execute** [execute] -- state `theorem eulerN : answer = <KNOWN>` (G-1);
   get a first GREEN proof, typically Bronze `native_decide`; delegate
   tactic-level work and error triage to `@lean-proof`. Keep `#eval answer` as a
   live sanity check next to the theorem.
4. **Validate** [validate] -- confirm `#eval answer` prints `<KNOWN>` and the
   theorem closes (G-2); run `#print axioms eulerN` and record the compiler-trust
   axiom whenever `native_decide` shipped (G-4); confirm no `sorry` / `admit`
   (G-5); run the improvement pass as far up the ladder as feasible (G-3); route
   the file to `@lean-proof-review` under the L3 carve-out (G-6).
5. **Persist** [persist] *(MANDATORY)* -- commit the Lean file plus the
   `#print axioms` result; whenever a `native_decide` answer-check remains, FILE
   the structural-proof follow-up task the carve-out requires (G-6); update the
   state tracker / tick `tasks.md`; emit a fleeting note via `@lean-zettelkasten`
   if a reusable Euler pattern surfaced. **Skipping Persist = incomplete.**

## Recovery & STOP

- **Novelty** -- answer unknown or the problem is open: STOP. This skill requires
  a known numeric target; ask for the target or decline.
- **Confidence** -- `native_decide` is the only feasible close and no
  structural follow-up can be scoped: STOP at belief < 0.90 and ask before
  shipping a permanent Bronze proof.
- Both `decide` and `native_decide` fail (recursion depth, timeout): STOP; hand
  the encoding to `@lean-research` for a closed-form / structural reduction
  before retrying (kernel `decide` blows `maxRecDepth` on large enumerations).
- **Conflict** -- the encoded `answer` does not match the problem's intended
  quantity: STOP; re-anchor the statement via `@lean-specification` before
  proving.
- **Governance / Irreversible** -- removing `native_decide` would change the
  theorem's trust surface in a way the owner has not accepted: STOP; do NOT
  silently swap axioms; ask.
- Same proof strategy fails 3 times: STOP; escalate to a human or hand to
  `@lean-proof` to isolate the failure.

## Handoffs

- **Predecessors:** `@lean-gateway` routes the task; `@lean-specification`
  supplies the theorem statement; `@lean-research` supplies the encoding and the
  Mathlib primitives.
- **Successors:** `@lean-proof` (tactic-level proving), `@lean-proof-review`
  (audits under the L3 carve-out), `@lean-quality-engine` (project QA).
- **Source spec:** this file (self-specified); every G-rule's `AC-EM-NN` is the
  correspondingly-numbered guarantee in this card.
- **Reference:** [`references/lean4-number-theory.md`](lean-math-discrete-handbook.md)
  -- Mathlib number-theory facilities, the Bronze/Silver/Gold tactic ladder, and
  the `native_decide` trust note. Template:
  [`Template_Euler.md`](lean-math-discrete-handbook.md) -- per-problem Lean file template with
  a verified Euler-1 example.

## Common failure modes

> AI agents commonly: state an existential or a bound instead of the exact
> numeric answer; declare done on a green `native_decide` without ever running
> `#print axioms`; leave a Bronze `native_decide` answer-check permanent with no
> structural follow-up filed (defeating the L3 carve-out); reach for kernel
> `decide` at a scale that blows `maxRecDepth` and then give up; paper a gap with
> `sorry`. Full registry: `GUARDRAILS.md` (Agent failure taxonomy).

## See also

- [`references/lean4-number-theory.md`](lean-math-discrete-handbook.md) -- Mathlib number-theory facilities + Bronze/Silver/Gold ladder + axiom-audit
  trust note (this skill's handbook).
- [`Template_Euler.md`](lean-math-discrete-handbook.md) -- per-problem Lean file template with a verified Euler-1 example.
- [`../lean-specification/SKILL.md`](../../skills/lean-specification/SKILL.md) -- Predecessor (theorem statement).
- [`../lean-research/SKILL.md`](../../skills/lean-research/SKILL.md) -- Predecessor (Mathlib encoding).
- [`../lean-proof/SKILL.md`](../../skills/lean-proof/SKILL.md) -- Successor (tactic-level proving).
- [`../lean-proof-review/SKILL.md`](../../skills/lean-proof-review/SKILL.md) -- Successor (audit under the L3 carve-out).
- [`../lean-quality-engine/SKILL.md`](../../skills/lean-corpus-audit/SKILL.md) -- Successor (project QA).
- [`../lean-gateway/SKILL.md`](../../skills/lean-gateway/SKILL.md) -- Predecessor / router.
- [`../../references/lean4-tactic-hierarchy.md`](../protocols/lean4-tactic-hierarchy.md) -- tactic priority table (`decide` vs `native_decide`).
- [`../../references/lean4-proof-strategy.md`](../protocols/lean4-proof-strategy.md) -- one-step-at-a-time proof strategy.

---

## Number Theory & Decidable Computation Reference

# Lean 4 Number Theory -- Euler / Competition Handbook

> Concise map of the Mathlib facilities most useful for Project-Euler and
> competition-math formalization, plus the Bronze/Silver/Gold tactic ladder and
> the `native_decide` trust note. Project-agnostic. Handbook for the
> `lean-competitive-math` (euler-prover) skill; pair with
> [`../../../references/lean4-tactic-hierarchy.md`](../protocols/lean4-tactic-hierarchy.md)
> and [`../../../references/lean4-proof-strategy.md`](../protocols/lean4-proof-strategy.md).

All Lean identifiers below are written in ASCII function-application form. Where
Mathlib also ships a Unicode notation (big-operator sum, the divides bar, the
`phi` / `sigma` letters, the factorial bang), the notation is named in words and
the ASCII identifier is given so the material stays ASCII-clean. Verify every
symbol exists at your Mathlib pin before relying on it -- names drift between
releases (see `@lean-research`).

---

## 1. Core facilities

| Facility | ASCII form / signature | What it gives you | Key lemmas (spot-check at your pin) |
|---|---|---|---|
| Primality | `Nat.Prime p : Prop` | Decidable primality of a `Nat`. `Nat.decidablePrime` makes `decide`/`native_decide` work; `Nat.minFac` finds the least factor. | `Nat.Prime.two_le`, `Nat.prime_def_lt`, `Nat.Prime.eq_one_or_self_of_dvd`, `Nat.exists_infinite_primes` |
| GCD / LCM | `Nat.gcd a b`, `Nat.lcm a b` | Greatest common divisor / least common multiple (both computable). | `Nat.gcd_dvd_left`, `Nat.gcd_comm`, `Nat.gcd_mul_lcm`, `Nat.Coprime` (defined as `Nat.gcd a b = 1`) |
| Coprimality | `Nat.Coprime a b : Prop` | `gcd a b = 1`; the workhorse for CRT / multiplicative arguments. | `Nat.Coprime.eq_one_of_dvd`, `Nat.Coprime.mul`, `Nat.Coprime.pow` |
| Divisors | `Nat.divisors n : Finset Nat` | The finite set of positive divisors of `n` (empty for `n = 0`). `Nat.properDivisors n` excludes `n`. | `Nat.mem_divisors`, `Nat.sum_divisors_eq_sum_properDivisors_add_self`, `Nat.divisors_prime_pow` |
| Divisor sums | `Nat.ArithmeticFunction.sigma k n` | The divisor-power sum (capital-sigma). `sigma 0 n` = number of divisors; `sigma 1 n` = sum of divisors. Perfect / abundant / deficient tests live here. | `Nat.ArithmeticFunction.sigma_apply`, `Nat.ArithmeticFunction.sigma_one_apply`, `Nat.ArithmeticFunction.isMultiplicative_sigma` |
| Totient | `Nat.totient n` | Euler `phi`: the count of `k < n` coprime to `n`. | `Nat.totient_prime`, `Nat.totient_mul` (coprime args), `Nat.totient_eq_card_coprime`, `Nat.sum_totient` |
| Fibonacci | `Nat.fib n` | The Fibonacci sequence (`fib 0 = 0`, `fib 1 = 1`). | `Nat.fib_add_two`, `Nat.fib_pos`, `Nat.fib_coprime_fib_succ`, `Nat.fib_add_two_strictMono` |
| Factorial | `Nat.factorial n` | `n!` (Unicode bang notation `n !`). | `Nat.factorial_pos`, `Nat.factorial_dvd_factorial`, `Nat.factorial_lt`, `Nat.succ_mul_factorial` |
| Binomials | `Nat.choose n k` (`n.choose k`) | Binomial coefficient. | `Nat.choose_symm`, `Nat.succ_mul_choose_eq`, `Nat.sum_range_choose`, `Nat.choose_mul_factorial_le` |

### Divisibility

Divisibility is `Dvd.dvd a b` (Mathlib infix is the divides bar, `a | b` in
source). It is decidable on `Nat`, so finite divisibility questions fall to
`decide` / `native_decide`. Useful: `Nat.dvd_sub'`, `Nat.dvd_gcd`,
`Nat.Prime.dvd_mul`, `Nat.dvd_factorial`.

---

## 2. Finite enumeration (the Euler bread-and-butter)

Most Euler answers are a sum or a count over a bounded range with a predicate.

| Facility | ASCII form | Notes |
|---|---|---|
| Range | `Finset.range n` | `{0, 1, ..., n-1}` as a `Finset Nat`. |
| Filter | `Finset.filter p s` | Keep elements of `s` satisfying decidable `p`. |
| Sum | `Finset.sum s f` | Big-operator sum notation (capital sigma over `i` in `s`). Function form shown here for ASCII. |
| Product | `Finset.prod s f` | Big-operator product. |
| Card | `Finset.card s` | Count of elements. |
| Interval | `Finset.Icc a b`, `Finset.Ico a b` | Closed / half-open integer intervals (need the `LocallyFiniteOrder` instance). |

Canonical "sum over a filtered range" (ASCII, Mathlib):

```lean
-- Sum of i*i for even i in 0..99 (idiomatic Finset form; needs Mathlib).
def s : Nat := Finset.sum (Finset.filter (fun i => i % 2 == 0) (Finset.range 100))
                          (fun i => i * i)
```

The same thing with a core `List` (no Mathlib -- handy for a self-contained
sanity check or a template that must compile with just `lean`):

```lean
def s : Nat :=
  ((List.range 100).filter (fun i => i % 2 == 0)).foldl (fun acc i => acc + i * i) 0
```

Key rewriting lemmas when you leave enumeration for structure:
`Finset.sum_range_succ`, `Finset.sum_filter`, `Finset.sum_range_id`
(`sum of 0..n-1 = n*(n-1)/2`), `Gauss`-style `Finset.sum_range_id_mul_two`.

---

## 3. The Bronze / Silver / Gold tactic ladder

The defining Euler move is closing `theorem eulerN : answer = <KNOWN>`. There are
three rungs of increasing trust. Climb as far as is feasible (skill rule G-3).

| Rung | Tactic(s) | Trust surface | When it applies |
|---|---|---|---|
| **Bronze** | `native_decide` | Compiler-trusted: adds a `native_decide` axiom (see Section 4). Fast; evaluates the compiled decision procedure. | First green proof; large enumerations where the kernel cannot reduce in time. |
| **Silver** | `decide`, `rfl`, `norm_num` | Kernel-checked: NO extra axioms. `decide` reduces the `Decidable` instance in the kernel; `rfl` uses definitional equality; `norm_num` for closed numeric goals. | Small enumerations, or once you have a cheap closed form. Kernel `decide` blows `maxRecDepth` on large ranges. |
| **Gold** | structural proof of a characterising property or closed form | Kernel-checked and general: the theorem no longer depends on brute evaluation. | The improvement target -- prove `answer = <closed form>` or a `..._spec` property, then discharge the numeral with `decide` / `norm_num`. |

Ladder guidance:

- Start Bronze to get GREEN, then improve. A permanent Bronze proof is only
  acceptable under the L3 carve-out (skill rule G-6): file a structural-proof
  follow-up, else `@lean-proof-review` L3 flags the one-tactic close.
- Silver often fails on raw Euler enumerations: kernel `decide` on a
  1000-element filtered range raises `maximum recursion depth has been reached`.
  Do NOT just crank `maxRecDepth` -- prefer a closed form.
- Gold is the honest endpoint: replace enumeration with a formula
  (inclusion-exclusion, triangular numbers, a multiplicative-function identity),
  prove the equivalence structurally, and the numeral falls to `decide` /
  `norm_num` with an empty axiom set.

See [`../../../references/lean4-tactic-hierarchy.md`](../protocols/lean4-tactic-hierarchy.md)
for the full tactic priority table (`decide` / `native_decide` sit at the
concrete-evaluation tier: "Prefer `decide` over `native_decide` for
kernel-checkability").

---

## 4. Trust note: what `native_decide` costs, and how to audit it

`native_decide` compiles and runs the decision procedure in native code, then
asserts the result as an axiom -- it does NOT re-check the computation in the
trusted kernel. That is why it is fast and why it is a strictly larger trust
surface than `decide`.

- The primitive is `Lean.ofReduceBool : forall (a b : Bool), Lean.reduceBool a = b -> a = b`,
  which itself depends on `[Lean.ofReduceBool, Lean.trustCompiler]`. In older
  Lean, `#print axioms` surfaced `Lean.trustCompiler` directly.
- In current Lean (verified on 4.30.0), `native_decide` instead emits a
  per-theorem generated axiom of the shape
  `<thm>._native.native_decide.ax_1_1 : decide (<prop>) = true`, which
  encapsulates that same compiler trust. (`Lean.reduceBool`, the old in-kernel
  path, is now deprecated with the message "assert native evaluations with
  axioms instead".)

**Always audit.** After the proof closes, run:

```lean
#print axioms eulerN
```

Interpretation:

- Bronze `native_decide` prints a `native_decide` axiom, e.g.
  `'eulerN' depends on axioms: [eulerN._native.native_decide.ax_1_1]`.
  Record this string in the file / review note (skill rule G-4).
- Silver / Gold prints either `does not depend on any axioms` or only the three
  standard axioms `[propext, Classical.choice, Quot.sound]`.
- Any `sorry` shows as `sorryAx` -- an automatic reject (skill rule G-5).

`@lean-enforcement`'s `axiom_audit.py` scans for exactly these markers; the
`@lean-proof-review` REFERENCE flags the compiler-trust axiom as a non-triviality
signal. The `lean-competitive-math` L3 carve-out (G-6) is the one place a
`native_decide` answer-check is allowed to pass review -- and only when a
structural follow-up is on file.

---

## 5. Verified micro-examples (Lean 4.30.0, core-only, ASCII)

Euler 1 -- sum of multiples of 3 or 5 below 1000; known answer `233168`.

```lean
-- Bronze: fast, compiler-trusted.
def answer : Nat :=
  ((List.range 1000).filter (fun n => n % 3 == 0 || n % 5 == 0)).foldl
    (fun acc n => acc + n) 0

#eval answer                                   -- 233168
theorem euler1 : answer = 233168 := by native_decide
#print axioms euler1
-- 'euler1' depends on axioms: [euler1._native.native_decide.ax_1_1]
```

```lean
-- Silver at this scale FAILS: kernel `decide` on 1000 elements ->
--   "maximum recursion depth has been reached".
-- Lesson: do not brute-force large enumerations in the kernel; go Gold.
```

```lean
-- Gold: inclusion-exclusion + triangular numbers T(k) = k*(k+1)/2.
--   multiples of 3 below 1000: 3*T(333); of 5: 5*T(199); of 15: 15*T(66).
def answer' : Nat := 3 * (333 * 334 / 2) + 5 * (199 * 200 / 2) - 15 * (66 * 67 / 2)

#eval answer'                                  -- 233168
theorem euler1_closed : answer' = 233168 := by decide
#print axioms euler1_closed
-- 'euler1_closed' does not depend on any axioms
```

The honest Gold endpoint additionally proves `answer = answer'` structurally
(reasoning about the filtered enumeration), which retires the `native_decide`
axiom from `euler1` entirely. Until that bridge lands, keep the Bronze `euler1`
AND file the follow-up (G-6).

---

## See also

- [`../../../references/lean4-tactic-hierarchy.md`](../protocols/lean4-tactic-hierarchy.md) -- full tactic priority table.
- [`../../../references/lean4-proof-strategy.md`](../protocols/lean4-proof-strategy.md) -- one-step-at-a-time proof strategy.
- [`../SKILL.md`](../../skills/lean-math-discrete/SKILL.md) -- the `lean-competitive-math` (euler-prover) contract.
- [`../Template_Euler.md`](lean-math-discrete-handbook.md) -- per-problem Lean file template.

