---
name: ai-commonsense-reasoning
description: Commonsense reasoning for AI systems — world knowledge, naive physics, folk psychology, temporal/spatial reasoning, default reasoning, and their formalization. Use for reasoning about everyday knowledge that humans take for granted but AI systems need explicitly, including the project tacit knowledge externalization pipeline's commonsense aspects.
---

# Commonsense Reasoning

Formalizing the vast body of everyday knowledge that underlies human reasoning and is critical for AI systems operating in real-world contexts.

---

## Part 1 — Commonsense Knowledge Domains

### 1.1 Core Commonsense Categories

| Category | Examples | Formalization Approach |
|---|---|---|
| **Naive physics** | Objects fall, water flows downhill, containers hold things | Qualitative physics (Forbus), constraint systems |
| **Folk psychology** | People have beliefs/desires/intentions, deception is possible | BDI logic, theory of mind models |
| **Temporal reasoning** | Events have duration, causes precede effects, habits form | Allen's interval algebra, temporal logic (LTL/CTL) |
| **Spatial reasoning** | Objects have extent, containment, proximity, orientation | Region Connection Calculus (RCC-8), qualitative spatial reasoning |
| **Social reasoning** | Norms, roles, obligations, reputational effects | Deontic logic (see ai-causal-deontic), social choice theory |
| **Teleological reasoning** | Artifacts have purposes, actions serve goals | Functional reasoning, means-end analysis |
| **Taxonomic knowledge** | Dogs are animals, animals breathe, inheritance defaults | Description logic, default logic, typicality operators |

### 1.2 Project Relevance Map

| Project Concept | Commonsense Aspect | Why It Matters |
|---|---|---|
| Tacit knowledge externalization | Folk psychology: knowing WHAT you know tacitly | Identifying what needs capturing |
| Quality gates | Teleological: gates SERVE a purpose | Understanding gate function vs. structure |
| Phase classification | Temporal: phases progress, don't regress arbitrarily | Temporal common sense constrains phase transitions |
| Pipeline adaptation | Causal: interventions have expected effects | Commonsense causal reasoning guides adaptation |
| Trust dynamics | Social: trust is earned incrementally, lost quickly | Asymmetric trust is a commonsense phenomenon |
| Knowledge graphs | Taxonomic: IS-A, PART-OF, HAS-PURPOSE hierarchies | Commonsense ontology structures KGs |
| Provenance chains | Temporal + social: who did what when and why | Provenance requires folk psychology + temporal reasoning |

---

## Part 2 — Formal Commonsense Frameworks

### 2.1 Non-Monotonic Reasoning

Classical logic is monotonic (adding premises never retracts conclusions). Commonsense reasoning is non-monotonic:

```
Default: Birds fly.
Exception: Penguins don't fly.
Exception to exception: Penguins in a catapult fly (briefly).
```

**Formalisms:**

| Framework | Key Idea | Lean Approach |
|---|---|---|
| **Default logic** (Reiter) | Default rules with justifications | Structure with prerequisite, justification, consequent |
| **Circumscription** (McCarthy) | Minimize abnormality predicates | Second-order axiom, approximate with finite models |
| **Answer set programming** | Stable models of logic programs | Encode as Prop-valued functions, check stability |
| **Typicality operators** | "Typical birds fly" | Conditional assertions with defeat conditions |

### 2.2 Lean 4 Encoding Patterns

```lean
-- Default rule structure
structure DefaultRule (α : Type) where
  prerequisite : α → Prop  -- Must hold
  justification : α → Prop -- Must be consistent (not known false)
  consequent : α → Prop    -- Conclude this

-- Commonsense world model
structure WorldModel where
  objects : Type
  properties : objects → Set String
  relations : objects → objects → Set String
  defaults : List (DefaultRule objects)
  exceptions : List (DefaultRule objects → Prop) -- When to block defaults
```

### 2.3 Scripts and Frames (Schank/Minsky)

| Concept | Definition | Formalization |
|---|---|---|
| **Frame** | Stereotypical situation with default slot fillers | Structure with optional fields + defaults |
| **Script** | Stereotypical event sequence | Finite state machine with labeled transitions |
| **Plan** | Goal-directed action sequence | Partially ordered set of actions with preconditions |

---

## Part 3 — Qualitative Reasoning

### 3.1 Qualitative Process Theory (Forbus)

Instead of exact quantities, reason about signs and directions of change:

| Quantity Space | Values | Operations |
|---|---|---|
| **Sign** | {−, 0, +} | Addition, multiplication tables |
| **Ordinal** | {low, medium, high} | Comparison, bounded transitions |
| **Interval** | Named intervals + landmarks | Contains, overlaps, transitions |

**Project application:** Quality scores don't need exact values for commonsense reasoning about system behavior — "high quality + low risk = good outcome" is qualitative.

### 3.2 Qualitative Simulation

```
Given: quantity Q is increasing
Given: Q has landmark value L at which behavior changes
Infer: Q will eventually reach L (unless other factor intervenes)
Infer: After L, behavior regime changes
```

This directly maps to the project's phase transitions: quality metrics cross thresholds → phase changes.

---

## Part 4 — Theory of Mind & BDI

### 4.1 Belief-Desire-Intention (BDI) Architecture

| Component | Description | Formal Type |
|---|---|---|
| **Beliefs** | Agent's model of the world | `Agent → World → Prop` (epistemic) |
| **Desires** | Preferred world states | `Agent → World → Prop` (motivational) |
| **Intentions** | Committed-to plans | `Agent → Plan → Prop` (volitional) |

### 4.2 Epistemic Logic for Multi-Agent Commonsense

```
K_i(φ)     = Agent i knows φ
B_i(φ)     = Agent i believes φ
C(φ)       = φ is common knowledge
E(φ)       = everyone knows φ (but not necessarily commonly)
```

**Key axioms:**
- Knowledge implies truth: `K_i(φ) → φ`
- Positive introspection: `K_i(φ) → K_i(K_i(φ))`
- Belief doesn't imply truth: `B_i(φ) ↛ φ` (agents can be wrong)
- Common knowledge is closed under logical consequence

### 4.3 Project Multi-Agent Trust Connection

The trust dynamics in `AgenticSafety.lean` formalize a simplified version of BDI:
- Trust = belief about agent reliability
- Safety envelope = constraint on intentions
- Consensus distance = convergence of beliefs across agents

---

## Part 5 — Temporal Commonsense

### 5.1 Allen's Interval Algebra

13 relations between temporal intervals:

| Relation | Notation | Inverse |
|---|---|---|
| Before | A < B | After |
| Meets | A m B | Met-by |
| Overlaps | A o B | Overlapped-by |
| Starts | A s B | Started-by |
| During | A d B | Contains |
| Finishes | A f B | Finished-by |
| Equals | A = B | Equals |

**Project Pipeline:** Pipeline stages have temporal interval structure — stages don't overlap arbitrarily; there's a dependency ordering.

### 5.2 Temporal Reasoning Patterns

| Pattern | Commonsense Rule | Formal |
|---|---|---|
| Inertia | Things stay the same unless changed | Default persistence axiom |
| Ramification | Actions have indirect effects | Frame axiom + causal closure |
| Qualification | External factors can block actions | Exception handling in plan execution |
| Narrative | Events told in order happened | Temporal ordering = narrative ordering (default) |

---

## Part 6 — Commonsense Physics & Spatial Reasoning

### 6.1 Region Connection Calculus (RCC-8)

8 topological relations for spatial regions:

```
DC (disconnected), EC (externally connected), PO (partial overlap),
EQ (equal), TPP (tangential proper part), NTPP (non-tangential proper part),
TPPi (inverse TPP), NTPPi (inverse NTPP)
```

### 6.2 Naive Physics for Project

| Physics Concept | Commonsense | Project Analog |
|---|---|---|
| Containment | A container holds things | Phases contain quality states |
| Flow | Liquids flow from high to low | Information flows through pipeline |
| Momentum | Moving objects resist stopping | Quality improvement has momentum |
| Friction | Movement generates resistance | Process overhead slows pipeline |
| Equilibrium | Systems tend toward balance | CCV balanced state |

---

## Part 7 — Integration with Lean Formalization

### 7.1 What CAN Be Formalized

| Aspect | Formalizability | Approach |
|---|---|---|
| Taxonomic hierarchies | High | Lean typeclasses and instances |
| Temporal constraints | High | Lean structures + ordering proofs |
| Qualitative inequality | High | Nat-scaled ×100 approximation |
| Default reasoning | Medium | Explicit exception lists |
| Theory of mind | Medium | BDI structures with decidable belief |
| Naive physics | Low-Medium | Qualitative constraint satisfaction |
| Open-world commonsense | Low | Cannot formalize the open world |

### 7.2 Bridge to Project Modules

| Module | Commonsense Concept Used | Formalizability |
|---|---|---|
| QualityGates | Threshold commonsense (above/below) | High — already done |
| PhaseClassification | Taxonomic (3 regimes) | High — already done |
| PipelineAdaptive | Teleological (pipeline serves a purpose) | Medium |
| ProvenanceChain | Temporal + social (who did what when) | High — partially done |
| AgenticSafety | BDI + social (trust, intention) | Medium — partially done |
| StochasticCCV | Qualitative convergence (trending toward balance) | Medium |

---

## Part 8 — Research Directions

### 8.1 Open Problems

1. **Commonsense benchmark gap**: No standard for commonsense in formal verification
2. **Scalability**: Non-monotonic reasoning is computationally expensive
3. **Acquisition bottleneck**: Extracting commonsense knowledge from text/experience
4. **Contextual defaults**: When to apply which default in which context
5. **Cross-cultural commonsense**: Different cultures have different "obvious" knowledge

### 8.2 Key References

| Area | Key Work | Relevance |
|---|---|---|
| CYC project | Lenat (1995) | Largest commonsense KB, millions of assertions |
| ConceptNet | Speer & Havasi (2012) | Open commonsense knowledge graph |
| ATOMIC | Sap et al. (2019) | If-then commonsense about events |
| Commonsense Transformers | Bosselut et al. (2019) | Neural commonsense generation |
| Qualitative Process Theory | Forbus (1984) | Foundation of qualitative reasoning |
| Circumscription | McCarthy (1980) | Formal approach to defaults |

---

## Part 9 — Skill Cross-References

| If working on... | Also consult... |
|---|---|
| Default reasoning | `ai-causal-deontic` (deontic defaults) |
| Spatial reasoning | `math-topology-analysis` (topological foundations) |
| Temporal reasoning | `math-time-series` (time-series formalization) |
| Knowledge representation | `ai-symbolic-neuro` (KRR frameworks) |
| Agent beliefs | `ai-agentic-evolving` (BDI architectures) |
| Trust as commonsense | `lean-ai-formalization` (trust formalization) |
| Qualitative physics | `math-nonlinear-dynamics` (dynamical systems) |
| Commonsense for legal | `applied-legal-reasoning` (legal commonsense) |
