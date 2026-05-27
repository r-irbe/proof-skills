---
name: ai-symbolic-neuro
description: |
  USE FOR: Symbolic AI, neuro-symbolic integration, knowledge representation and reasoning (KRR), ontology engineering, description logics, and hybrid symbolic-neural architectures. Use for reasoning about formal knowledge structures, rule-based systems, logic programming, semantic web technologies, and their integration with neural approaches relevant to the project's knowledge graph and structuring phases.
  DO NOT USE FOR: formalising the ontology in Lean (use @lean-knowledge-formalization); commonsense reasoning (use @ai-commonsense-reasoning); agentic AI (use @ai-agentic-evolving).
  TRIGGERS: symbolic AI, neuro-symbolic, knowledge representation, KRR, ontology engineering, description logic, hybrid AI.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-knowledge-formalization', 'skill:ai-commonsense-reasoning', 'skill:math-graph-knowledge']
metadata:
  version: "0.2.0"
  source_spec: "skills/ai-symbolic-neuro/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Symbolic AI & Neuro-Symbolic Integration

Formal knowledge representation, symbolic reasoning, and their integration with neural methods for the project's knowledge structuring and consolidation phases.


## Routing

- **USE FOR:** Symbolic AI, neuro-symbolic integration, knowledge representation and reasoning (KRR), ontology engineering, description logics, and hybrid symbolic-neural architectures. Use for reasoning about formal knowledge structures, rule-based systems, logic programming, semantic web technologies, and their integration with neural approaches relevant to the project's knowledge graph and structuring phases.
- **DO NOT USE FOR:** formalising the ontology in Lean (use @lean-knowledge-formalization); commonsense reasoning (use @ai-commonsense-reasoning); agentic AI (use @ai-agentic-evolving).
- **TRIGGERS:** symbolic AI, neuro-symbolic, knowledge representation, KRR, ontology engineering, description logic, hybrid AI.

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
- **Successors:** `skill:lean-knowledge-formalization`, `skill:ai-commonsense-reasoning`, `skill:math-graph-knowledge`.

---

## Part 1 — Knowledge Representation Foundations

### 1.1 Representation Languages

| Language | Expressiveness | Decidability | Project Relevance |
|---|---|---|---|
| Propositional logic | Low | P (SAT: NP-complete) | Gate predicates |
| First-order logic (FOL) | High | Semi-decidable | Theorem formalization |
| Description logic (ALC) | Medium | ExpTime | Ontology TBoxes |
| OWL-DL | Medium-high | 2NExpTime | Semantic web ontologies |
| Datalog | Limited FOL | P (data complexity) | Recursive queries on KG |
| Answer Set Programming | Nonmonotonic | ΣP2-complete | Default reasoning |
| Modal logic | FOL + modalities | Varies | Epistemic/deontic reasoning |

### 1.2 Ontology Engineering

**Foundational ontologies:**
- DOLCE (Descriptive Ontology for Linguistic and Cognitive Engineering)
- BFO (Basic Formal Ontology) — ISO 21838
- SUMO (Suggested Upper Merged Ontology)

**Design patterns:**
- Parthood and mereology
- Temporal entities (endurants vs perdurants)
- Roles and role-playing
- Quality and quality spaces

**project application:** Knowledge Graph quality gates validate ontological consistency:
- TBox coherence (no unsatisfiable concepts)
- ABox consistency (instances satisfy TBox constraints)
- Schema-instance alignment

### 1.3 Formal Reasoning Systems

| System | Approach | Completeness | Use |
|---|---|---|---|
| Tableaux | Model construction attempt | Complete for DL | Ontology reasoning |
| Resolution | Refutation | Complete for FOL | Theorem proving |
| Sequent calculus | Structural proof | Complete for FOL | Proof theory |
| Natural deduction | Introduction/elimination | Complete for FOL | Human-like proofs |
| Type theory | Curry-Howard | ??? (depends on system) | Lean 4 foundation |

---

## Part 2 — Neuro-Symbolic Integration

### 2.1 Integration Spectrum (Kautz 2020)

| Level | Description | Example | Project Phase |
|---|---|---|---|
| 1 | Symbolic ← Neural | Neural generates symbolic output | Experience → symbols |
| 2 | Symbolic → Neural | Symbolic knowledge guides neural | Structuring → embedding |
| 3 | Hybrid pipeline | Neural + symbolic sequential | Full Project pipeline |
| 4 | Tightly coupled | Neural and symbolic share representation | Graph of Thoughts |
| 5 | Unified | Single system with both capabilities | Target architecture |

### 2.2 Key Architectures

- **Neural theorem proving**: Neural guide for tactic selection (GPT-f, AlphaProof)
- **Knowledge graph embeddings**: TransE, RotatE, CompGCN — vector representations of KG
- **Graph neural networks**: Message passing on knowledge structures
- **Neurosymbolic concept learner**: Learn visual concepts as logical programs
- **Logic tensor networks**: Differentiable first-order logic

### 2.3 the project's Neuro-Symbolic Position

Project operates at Level 3-4:
- **Experience phase**: Neural (LLM perception, embedding)
- **Articulation**: Neural→Symbolic (natural language → structured claims)
- **Structuring**: Symbolic (knowledge graph construction, validation)
- **Consolidation**: Hybrid (formal verification + neural synthesis)
- **Innovation**: Symbolic→Neural (validated knowledge → novel applications)

---

## Part 3 — Commonsense Reasoning

### 3.1 Commonsense Knowledge Types

| Type | Description | Formalization Challenge |
|---|---|---|
| Physical | Objects fall, liquids flow | Qualitative physics, spatial reasoning |
| Social | People have intentions, emotions | Theory of mind, folk psychology |
| Temporal | Events have duration, causation | Allen's interval algebra |
| Taxonomic | Dogs are animals | Inheritance hierarchies |
| Default | Birds fly (unless penguin) | Nonmonotonic logic |
| Causal | Pushing causes movement | Causal models (Pearl) |

### 3.2 Formal Approaches

- **Circumscription** (McCarthy): Minimize abnormality
- **Default logic** (Reiter): Default rules with exceptions
- **Answer set programming**: Stable models with negation-as-failure
- **Probabilistic logic**: Weight rules by confidence
- **Large language models**: Implicit commonsense from training data

### 3.3 Project Integration

Commonsense reasoning enters Project in:
- **Articulation**: Interpreting tacit knowledge requires commonsense context
- **Structuring**: Default rules for knowledge graph completion
- **Quality gates**: Commonsense consistency checks on extracted knowledge
- **Trust dynamics**: Social commonsense for multi-agent coordination

---

## Part 4 — Knowledge Graph Reasoning

### 4.1 Reasoning Tasks

| Task | Input | Output | Method |
|---|---|---|---|
| Link prediction | $(h, r, ?)$ | Missing tail entity | Embedding + scoring |
| Type inference | Entity features | Entity type | Classification |
| Rule mining | KG triples | Horn rules | AMIE, AnyBURL |
| Query answering | Complex query | Answer entities | Query embedding |
| KG completion | Partial KG | Complete KG | Combination methods |
| Consistency checking | KG + constraints | Violations | DL reasoning |

### 4.2 Formal Quality Metrics

| Metric | Formula | Interpretation |
|---|---|---|
| Precision | TP / (TP + FP) | Fraction of predicted links that are correct |
| Recall | TP / (TP + FN) | Fraction of true links predicted |
| MRR | $\frac{1}{|Q|}\sum_{q \in Q} \frac{1}{\text{rank}_q}$ | Mean reciprocal rank of correct answers |
| Hits@K | Fraction of correct in top-K | Retrieval quality |
| Semantic validity | Ontology-consistency rate | Structural soundness |

### 4.3 Project Knowledge Graph Architecture

```
Experience → Raw triples (LLM extraction)
  → Articulation → Candidate assertions with confidence
    → Structuring → Validated KG with ontological constraints
      → Consolidation → Proven properties (Lean formalization)
        → Innovation → Novel inferences from verified base
```

Quality gates at each transition enforce:
- Confidence thresholds (configurable per domain)
- Ontological consistency (TBox reasoning)
- Provenance tracking (W3C PROV-O)
- Temporal validity (assertions expire)

---

## Part 5 — Connection to Project Lean Modules

| Module | Symbolic AI Aspect | Key Structures |
|---|---|---|
| ProvenanceChain.lean | DAG well-formedness, trust composition | `ProvenanceStage`, `WellFormed` |
| Tactics.lean (§38-39) | CausalDAG, KnowledgeGraph formalization | `CausalLink`, `KGEdge` |
| QualityGates.lean | Predicate logic on quality measures | `Gate`, `GateMonotone` |
| PhaseClassification.lean | Decision procedures for regime classification | `RegimeType`, decidability |
| lean-causal-reasoning (SK-33) | Causal DAGs and counterfactual reasoning | Full causality skill |

---

## Part 6 — Research Connections

### 6.1 Epistemic Mapping Targets

| KK (Known) | KU (Gap) | UU (To Discover) |
|---|---|---|
| DAG formalization | Full DL reasoning in Lean | OWL-to-Lean translation |
| Propositional gates | Nonmonotonic formalization | Commonsense integration |
| Trust composition | Neuro-symbolic verification | LLM-generated proof verification |
| Provenance chains | Temporal knowledge evolution | Ontology evolution formalization |

### 6.2 Key References

- Brachman & Levesque (2004) — Knowledge Representation and Reasoning
- Hitzler et al. (2020) — Neuro-Symbolic AI: state of the art
- Marcus & Davis (2019) — Rebooting AI (commonsense perspective)
- Hogan et al. (2021) — Knowledge Graphs (comprehensive survey)
- Davis (2015) — Commonsense reasoning: an event calculus perspective
