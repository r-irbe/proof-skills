---
name: math-graph-knowledge
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


## Routing

- **USE FOR:** Graph theory, knowledge graphs, ontology engineering, provenance structures, network analysis, and formal knowledge representation. Use for mathematical reasoning about DAGs, KGs, trust networks, provenance chains, and any graph-structured knowledge. Covers both pure graph theory and applied knowledge graph methodology relevant to Project.
- **DO NOT USE FOR:** KRR / symbolic AI (use @ai-symbolic-neuro); causal DAGs (use @ai-causal-deontic); discrete math (use @lean-math-discrete).
- **TRIGGERS:** graph theory, knowledge graph, ontology, provenance, network analysis, formal knowledge representation.

## Workflow

1. Confirm the question / task is in scope by checking the **USE FOR** clause above; if any of the **DO NOT USE FOR** redirects apply, hand off and stop.
2. Consult the body of this skill (the existing Parts below) for the domain content; pick the smallest relevant section.
3. Execute the section's procedure; emit an output suitable for the listed successor skill(s). Belief floor: 0.90 before publishing.
4. On handoff, attach: scope, key findings, recommended next-skill call. Leave a Zettel breadcrumb when permanent.

## Recovery & STOP

- STOP if the task hits a topic redirected by **DO NOT USE FOR** — hand off to that skill rather than expanding scope here.
- STOP if belief is below 0.90 on a key claim — request HITL or escalate to `@lean-research` for evidence widening.
- STOP if the domain content below is insufficient for the question — log the gap as a research request and hand off to `@research-council` (or `@lean-research` for a single question).

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-math-discrete`, `skill:lean-knowledge-formalization`, `skill:lean-zettelkasten`.

---

## Part 1 — Graph Theory Foundations

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

## Part 2 — Knowledge Graph Theory

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

## Part 3 — Provenance Mathematics

### 3.1 PROV-O Data Model

Project uses W3C PROV-O for provenance:
```
Entity  — a thing (data, document, knowledge artifact)
Activity — a process that transforms entities
Agent    — a responsible actor (human, AI, system)

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

## Part 4 — Network Analysis for Knowledge Structures

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

## Part 5 — Ontology Engineering

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

## Part 6 — Causal Graph Theory

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
Level 1: Association — P(Y|X)      — "Seeing"
Level 2: Intervention — P(Y|do(X))  — "Doing" 
Level 3: Counterfactual — P(Y_x|X',Y') — "Imagining"

Project governance operates at all three levels:
  L1: Observe quality gate scores
  L2: Intervene with governance actions
  L3: Counterfactual analysis of alternative strategies
```

---

## Part 7 — Formalization Entry Points

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
