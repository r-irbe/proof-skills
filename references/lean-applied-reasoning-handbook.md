---
title: "Lean Applied Reasoning Handbook"
status: "reference"
extracted_from: "skills/lean-applied-reasoning/SKILL.md"
extracted_on: "2026-05-27"
scope: "Part 1 — Intelligence Analysis Formalization; Part 2 — Strategy Formalization; Part 3 — Brainstorming Methodology; Part 4 — Investigative Reasoning (Project Core Domain); Part 5 — Decision Under Uncertainty; Part 6 — Project & Product Management for Mathematics; Part 7 — Research Council Integration"
loader_hint: "Load when @lean-applied-reasoning routes here for details; not needed for the dispatch decision."
---

# Lean Applied Reasoning Handbook

> **Layering note.** This file holds the deep content previously
> embedded in [`skills/lean-applied-reasoning/SKILL.md`](../skills/lean-applied-reasoning/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow /
> Recovery / Handoffs) + a parts index. This file holds the full
> encyclopaedia. Zero fidelity loss vs the pre-layering revision.

---

## Part 1 — Intelligence Analysis Formalization

### 1.1 Analytic Process Models

```lean
-- Intelligence cycle: Direction → Collection → Processing → Analysis → Dissemination
-- Each stage is a function with inputs and outputs
-- Formalize as a pipeline (like the project's 5 stages)

structure IntelCycle where
  direction : Requirements → CollectionPlan
  collection : CollectionPlan → RawData
  processing : RawData → ProcessedInfo
  analysis : ProcessedInfo → Assessment
  dissemination : Assessment → Product

-- Completeness: every requirement addressed
-- Timeliness: product delivered within deadline
-- Accuracy: assessment matches ground truth (when verifiable)
```

### 1.2 Structured Analytic Techniques

| Technique | Purpose | Formalization |
|---|---|---|
| **ACH** (Analysis of Competing Hypotheses) | Evaluate multiple hypotheses against evidence | Matrix analysis, consistency scoring |
| **Key Assumptions Check** | Surface and test hidden assumptions | Assumption inventory + vulnerability map |
| **Red Team Analysis** | Challenge from adversary perspective | Alternative model + max-min reasoning |
| **Indicators & Warnings** | Detect emerging threats/opportunities | Bayesian update on indicator observations |
| **Scenario Planning** | Explore multiple futures | Decision tree with probabilistic branches |
| **Structured Brainstorming** | Generate hypotheses | Divergent-convergent process model |

### 1.3 Evidence Reasoning

```lean
-- Evidential reasoning framework:
structure Evidence where
  source : String
  reliability : ℕ  -- 1-6 (A-F in intelligence grading)
  credibility : ℕ  -- 1-6
  content : Proposition
  timestamp : Nat

-- Composite assessment:
-- Multiple pieces of evidence → weighted conclusion
-- Formalize: weighted voting with reliability/credibility weights

def evidenceWeight (e : Evidence) : ℝ := 
  (7 - e.reliability) * (7 - e.credibility)  -- higher weight for better evidence

-- Project parallel: quality scores are evidence weights for knowledge artifacts
```

---

## Part 2 — Strategy Formalization

### 2.1 Strategic Frameworks as Formal Structures

```lean
-- SWOT analysis:
structure SWOT where
  strengths : List Factor
  weaknesses : List Factor
  opportunities : List Factor
  threats : List Factor

-- Strategy: a mapping from situation to actions
-- Formalize: state-dependent policy (like RL policy)
def Strategy (State Action : Type) := State → Action

-- Strategic dominance: strategy S₁ dominates S₂ if
-- S₁ yields better outcome in every state
def Dominates (u : State → Action → ℝ) (s₁ s₂ : Strategy State Action) : Prop :=
  ∀ state, u state (s₁ state) ≥ u state (s₂ state)
```

### 2.2 Decision Trees

```lean
-- Decision tree: alternating decision and chance nodes
inductive DecTree (Action Outcome : Type)
  | leaf : ℝ → DecTree Action Outcome           -- terminal payoff
  | decision : List (Action × DecTree Action Outcome) → DecTree Action Outcome
  | chance : List (ℝ × DecTree Action Outcome) → DecTree Action Outcome
  -- chance nodes: probabilities must sum to 1

-- Expected value:
noncomputable def expectedValue : DecTree Action Outcome → ℝ
  | .leaf v => v
  | .decision branches => branches.map (fun (_, t) => expectedValue t) |>.maximum' (by sorry)
  | .chance branches => branches.map (fun (p, t) => p * expectedValue t) |>.sum

-- Project: the knowledge pipeline as a decision tree
-- Each stage choice affects downstream quality
```

### 2.3 Adversarial Strategy

```lean
-- Minimax: optimal strategy against rational adversary
-- max_x min_y payoff(x, y)

-- project application: adversarial robustness
-- What's the worst-case quality when:
-- - Users game the quality gates?
-- - AI generates plausible but incorrect outputs?
-- - Reviewers are inattentive?
-- Formal: prove minimum quality bound under adversarial behavior
```

---

## Part 3 — Brainstorming Methodology

### 3.1 Divergent-Convergent Process

```lean
-- Formal model of brainstorming:
-- Phase 1 (Divergent): generate hypotheses without evaluation
-- Phase 2 (Convergent): evaluate, rank, and select

-- Divergent: maximize number of distinct hypotheses
-- Convergent: multi-criteria ranking (see optimization skill)

-- Quality of brainstorming:
-- Coverage: fraction of known hypothesis space covered
-- Novelty: number of hypotheses not in standard libraries
-- Diversity: pairwise distance between hypotheses
```

### 3.2 Morphological Analysis

```lean
-- Zwicky's morphological box:
-- Define dimensions (parameters) and values for each dimension
-- Generate combinations (cross-product)
-- Filter inconsistent combinations

structure MorphologicalBox where
  dimensions : List String
  values : String → List String
  constraints : List (List String → Prop)  -- cross-consistency

-- Total possibilities: ∏ |values(d)| for d in dimensions
-- After filtering: count feasible combinations
-- Project: exploring phase classification configurations
```

### 3.3 Lateral Thinking Formalization

```lean
-- Random entry: pick random concept, find connection to problem
-- Reversal: negate assumptions and explore consequences
-- Analogy: map problem to different domain

-- In formal terms: these are transformations on hypothesis space
-- Random entry: random walk on concept graph
-- Reversal: negation in proposition space
-- Analogy: functor between domain categories
```

---

## Part 4 — Investigative Reasoning (Project Core Domain)

### 4.1 Investigative Workflow

```lean
-- Investigation as hypothesis refinement:
-- Initial report → hypotheses → evidence collection → analysis → conclusion

-- Project maps naturally:
-- E: initial report + context capture
-- A: practitioner articulates hypotheses
-- S: structure evidence + identify counter-hypotheses (abduction)
-- C: peer review of analysis
-- I: case knowledge versioned and available for future cases
```

### 4.2 Evidentiary Standards

```lean
-- Legal standards of proof (ordered):
inductive ProofStandard
  | scintilla              -- any evidence at all
  | preponderance          -- more likely than not (> 50%)
  | clearAndConvincing     -- substantially more likely
  | beyondReasonableDoubt  -- near certainty

-- Evidence sufficiency: does accumulated evidence meet the standard?
-- Formalize: P(H | E₁, ..., Eₙ) ≥ threshold(standard)
-- Using Bayesian update or evidential weight summation
```

### 4.3 Chain of Custody

```lean
-- Chain of custody = provenance chain for physical/digital evidence
-- Properties: completeness (no gaps), integrity (no tampering), 
--             authentication (each handler identified)

-- Project PROV-O provides exactly this:
-- Every artifact has creator, timestamp, derivation history
-- Every transition has a quality gate check
```

---

## Part 5 — Decision Under Uncertainty

### 5.1 Bayesian Decision Theory

```lean
-- Prior: P(H) — initial belief
-- Likelihood: P(E | H) — how likely is evidence given hypothesis
-- Posterior: P(H | E) ∝ P(E | H) * P(H)
-- Decision: choose action maximizing expected utility under posterior

-- Formalization:
def bayesianUpdate (prior : Hyp → ℝ) (likelihood : Hyp → Ev → ℝ) (e : Ev) : Hyp → ℝ :=
  fun h => prior h * likelihood h e / (∑ h', prior h' * likelihood h' e)
```

### 5.2 Robust Decision Making

```lean
-- Deep uncertainty: probabilities themselves are uncertain
-- Approaches:
-- Minimax regret: minimize worst-case deviation from optimal
-- Info-gap: maximize robustness radius around nominal

-- Project: design the knowledge pipeline to be robust
-- under uncertainty about user behavior, AI reliability, reviewer quality
```

### 5.3 Sequential Decision Making

```lean
-- Decisions made over time, each revealing information
-- → Reinforcement learning / dynamic programming framework
-- Project: each pipeline run updates parameters for the next run
-- → Learning pipeline that improves with use
```

---

## Part 6 — Project & Product Management for Mathematics

### 6.1 Formal Dependency Management

```lean
-- Theorem dependency graph = DAG
-- Critical path: longest chain of dependent theorems
-- Parallelism: independent theorems can be proven simultaneously

-- Project scheduling: topological sort of dependency graph
-- with estimated effort per theorem
-- → Critical path method (CPM)
```

### 6.2 Risk Management

```lean
-- Risk = probability × impact
-- For math projects: risk of a theorem being unprovable
-- Mitigation: alternative proof strategies, weaker statements

-- Risk register for formalization:
structure TheoremRisk where
  theorem_name : String
  difficulty : ℕ  -- 1-5
  alternatives : ℕ  -- number of known alternative approaches
  dependency_count : ℕ  -- how many downstream theorems depend on this
  risk_score : ℕ  -- difficulty * dependency_count / (alternatives + 1)
```

### 6.3 Progress Metrics

| Metric | Formula | Target |
|---|---|---|
| Coverage | theorems_proved / total_claims | 100% |
| Velocity | theorems_proved / time | Increasing |
| Quality | theorems_without_sorry / total | 100% |
| Depth | max_proof_dependency_chain | N/A (minimize) |
| Complexity | avg_proof_lines | Decreasing (refactoring) |
| Health | enforcement_script_pass_rate | 100% |

---

## Part 7 — Research Council Integration

| Applied Reasoning Topic | Research Council Member |
|---|---|
| Intelligence analysis methods | Ε (Applications Bridge) |
| Strategic framework selection | Ε (Applications Bridge) |
| Brainstorming facilitation | Γ (Methods Scholar) |
| Investigative reasoning | Ε (Applications Bridge) + domain expert |
| Bayesian decision modeling | Γ (Methods Scholar) + Δ (Bounds Analyst) |
| Project risk assessment | Δ (Bounds Analyst) |
| Legal reasoning formalization | Ε (Applications Bridge) + Α (Foundations Architect) |
| Adversarial analysis | Δ (Bounds Analyst) + Γ (Methods Scholar) |

---

## Merged Domain Companion: `lean-applied-reasoning` (Unified into `@lean-applied-reasoning`)

# Intelligence Analysis

Structured analytic techniques and evidence-based reasoning frameworks for intelligence, investigative, and analytical contexts.

---

## Routing

- **USE FOR:** Intelligence analysis methodology — structured analytic techniques (SATs), evidence reasoning, hypothesis generation, cognitive bias
  mitigation, competitive intelligence, and their formalization. Use for analysis of competing hypotheses (ACH), link analysis, timeline reconstruction,
  source reliability assessment, and connections to quality gates, provenance, and multi-agent trust.
- **DO NOT USE FOR:** formalising intelligence reasoning in Lean (use @lean-applied-reasoning); strategy analysis (use @lean-applied-reasoning); legal
  reasoning (use @applied-legal-reasoning).
- **TRIGGERS:** structured analytic techniques, SATs, evidence reasoning, hypothesis generation, cognitive bias, intelligence analysis, competing hypotheses.

## Workflow

1. Classify the analytic task: hypothesis generation, evidence aggregation, competing-hypothesis evaluation, or bias mitigation.
2. Pick the matching SAT (ACH, key-assumptions check, devil's advocacy, red-team) from the body.
3. Apply the SAT to the concrete intelligence question; produce the structured output (hypothesis matrix, assumption ledger).
4. Hand off: to `@lean-applied-reasoning` for Lean encoding, to `@lean-applied-reasoning` for downstream strategy work, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the question is purely about strategy creation — delegate to `@lean-applied-reasoning`.
- STOP if evidence is missing for hypothesis evaluation — escalate to `@research-council`.
- STOP if the legal/regulatory dimension dominates — delegate to `@applied-legal-reasoning`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-applied-reasoning`, `skill:lean-applied-reasoning`, `skill:lean-knowledge-formalization`.

---

## Detailed reference

Full content for `lean-applied-reasoning` lives in
[`references/lean-applied-reasoning-handbook.md`](../../references/lean-applied-reasoning-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

| Section | Topic |
|---|---|
| Part 1 | Structured Analytic Techniques (SATs) |
| Part 2 | Analysis of Competing Hypotheses (ACH) |
| Part 3 | Evidence Reasoning |
| Part 4 | Cognitive Bias Mitigation |
| Part 5 | Link Analysis & Network Intelligence |
| Part 6 | Scenario Analysis & Forecasting |
| Part 7 | Source Handling & HUMINT Reasoning |
| Part 8 | Cross-References |

---

## See also

- [`../../references/lean-applied-reasoning-handbook.md`](../../references/lean-applied-reasoning-handbook.md) — Full handbook (extracted
  from this skill)
- [`../lean-applied-reasoning/SKILL.md`](../lean-applied-reasoning/SKILL.md) — Successor
- [`../lean-applied-reasoning/SKILL.md`](../lean-applied-reasoning/SKILL.md) — Successor
- [`../lean-knowledge-formalization/SKILL.md`](../lean-knowledge-formalization/SKILL.md) — Successor

# Applied Intelligence Analysis Handbook

> **Layering note.** This file holds the deep content previously
> embedded in [`skills/lean-applied-reasoning/SKILL.md`](../skills/lean-applied-reasoning/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow /
> Recovery / Handoffs) + a parts index. This file holds the full
> encyclopaedia. Zero fidelity loss vs the pre-layering revision.

---

## Part 1 — Structured Analytic Techniques (SATs)

### 1.1 Technique Taxonomy

| Category | Techniques | Purpose |
|---|---|---|
| **Decomposition** | Issue decomposition, chronologies, matrices | Break complex problems into parts |
| **Visualization** | Link charts, flow diagrams, geospatial | Reveal hidden patterns/relationships |
| **Idea generation** | Brainstorming, morphological analysis, red teaming | Expand hypothesis space |
| **Hypothesis testing** | ACH, diagnostic reasoning, key assumptions check | Rigorously evaluate explanations |
| **Assessment** | Structured debate, Delphi, prediction markets | Produce calibrated judgments |
| **Challenge** | Devil's advocacy, Team A/Team B, "What if?" | Combat groupthink and anchoring |

### 1.2 Project Mapping

| SAT Concept | Project Analog | Module |
|---|---|---|
| Source reliability (A-F scale) | Quality gate thresholds | QualityGates |
| Evidence chains | Provenance chain formalization | ProvenanceChain |
| Competing hypotheses | Phase classification boundaries | PhaseClassification |
| Multi-source fusion | CCV balanced state convergence | StochasticCCV |
| Analyst confidence | Trust composition scores | AgenticSafety |
| Red team challenge | Review council Σ/Φ adversarial checks | lean-review-council |

---

## Part 2 — Analysis of Competing Hypotheses (ACH)

### 2.1 The ACH Process

```
1. GENERATE hypotheses (at least 3, including contrarian)
2. LIST evidence items (all available data points)
3. BUILD consistency matrix:
   For each (hypothesis, evidence) pair:
     CC = Consistent and Confirmatory
     C  = Consistent (neutral)
     I  = Inconsistent
     N  = Not applicable
4. SCORE: Count I's per hypothesis (MORE inconsistencies = LESS likely)
5. ANALYZE: Focus on DISCONFIRMING evidence (not confirming)
6. SENSITIVITY: Which evidence items, if wrong, would change the conclusion?
7. REPORT: Ranked hypotheses with confidence and key uncertainties
```

### 2.2 Formalization

```lean
structure ACHMatrix where
  hypotheses : Finset String
  evidence : Finset String
  consistency : String → String → Consistency  -- (h, e) → rating
  
inductive Consistency where
  | confirmatory  -- CC: actively supports
  | consistent    -- C: doesn't contradict
  | inconsistent  -- I: contradicts
  | notApplicable -- N: irrelevant

def inconsistencyCount (m : ACHMatrix) (h : String) : Nat :=
  (m.evidence.filter (fun e => m.consistency h e = .inconsistent)).card

-- Key theorem: hypothesis with most inconsistencies is least likely
-- This is Popperian: we reject by falsification, not confirm by verification
```

### 2.3 Connection to Lean Review

The review council operates like ACH:
- Hypotheses = "this proof is correct" vs. "this proof has issues"
- Evidence = each council member's findings
- Inconsistencies = 🔴 findings that contradict correctness
- Decision = vote based on weight of evidence

---

## Part 3 — Evidence Reasoning

### 3.1 Evidence Quality Assessment

| Dimension | Scale | Project Quality Gate Analog |
|---|---|---|
| **Reliability** | A (very reliable) → F (unreliable) | Source trust score |
| **Credibility** | 1 (confirmed) → 6 (cannot be judged) | Verification status |
| **Relevance** | Direct → indirect → tangential | Theorem-claim mapping |
| **Timeliness** | Current → dated → historical | Staleness detection |
| **Corroboration** | Multiple independent sources → single | Cross-module verification |

### 3.2 Inferential Chains

```
Evidence → Inference₁ → Inference₂ → ... → Conclusion
   ↑            ↑             ↑
  Source    Assumption    Assumption
reliability  check         check
```

Each link in the chain is a potential failure point. Long chains are unreliable.

### 3.3 Lean Proof as Inferential Chain

A Lean proof IS a verified inferential chain:
- Each tactic step = one inference
- Each hypothesis = one assumption (stated explicitly)
- The kernel verifies every link
- No "gap in the chain" possible (unlike human analysis)

---

## Part 4 — Cognitive Bias Mitigation

### 4.1 Key Biases in Analysis

| Bias | Description | Mitigation | Project Analog |
|---|---|---|---|
| **Anchoring** | Over-reliance on first information | Consider alternatives first | Ν (Novelty Scout) checks |
| **Confirmation** | Seeking confirming evidence | ACH + disconfirmation focus | Σ (Soundness) adversarial |
| **Availability** | Overweight easily recalled info | Systematic evidence inventory | coverage_matrix.md |
| **Mirror imaging** | Assuming others think like us | Red teaming | Council diverse personas |
| **Groupthink** | Conformity pressure in teams | SDR (Structured Disagreement) | lean-review-council SDR |
| **Hindsight** | "I knew it all along" | Pre-mortem analysis | Retroactive audit baseline |

### 4.2 Debiasing in Formal Verification

Lean formalization is a powerful debiasing tool:
- **Anchoring**: The kernel doesn't care what you think the answer is
- **Confirmation**: If the proof is wrong, it fails — no amount of confidence helps
- **Groupthink**: The machine is the ultimate dissenter
- **Hindsight**: Git history + ZK notes preserve the actual sequence of discovery

---

## Part 5 — Link Analysis & Network Intelligence

### 5.1 Entity-Relationship Networks

```
Types of links:
- Communication (calls, messages, meetings)
- Financial (transactions, funding)
- Organizational (membership, employment)
- Geographic (co-location, travel)
- Technical (shared infrastructure)
```

### 5.2 Graph Metrics for Intelligence

| Metric | Intelligence Meaning | Math Foundation |
|---|---|---|
| Degree centrality | Number of direct contacts | `lean-math-discrete` |
| Betweenness centrality | Gatekeeping / brokerage role | Shortest path counting |
| Closeness centrality | Speed of information access | Inverse average path length |
| Clustering coefficient | Clique density | Directed graph analysis |
| Community detection | Organization/affiliation structure | Modularity optimization |

### 5.3 Project Knowledge Graph Connection

The knowledge graph in `Tactics.lean` (§38-§39) formalizes:
- `KGEdge`: labeled, weighted edges between entities
- `KnowledgeGraph`: set of edges with quality constraints
- `kg_min_confidence_bound`: minimum confidence thresholds
- This is directly applicable to intelligence link analysis

---

## Part 6 — Scenario Analysis & Forecasting

### 6.1 Scenario Construction

```
1. Identify driving forces (key factors)
2. Assess uncertainty levels for each
3. Construct scenario matrix (2×2 for 2 key uncertainties)
4. Develop narrative for each quadrant
5. Identify indicators/signposts for each scenario
6. Assess probability and impact
```

### 6.2 Project Scenario Connection

- Cusp catastrophe model: scenarios near bifurcation points
- Phase portraits: multiple equilibria = multiple scenarios
- Stochastic CCV: probability distributions over outcomes

---

## Part 7 — Source Handling & HUMINT Reasoning

### 7.1 Source Evaluation Framework

| Factor | Assessment | Data Type |
|---|---|---|
| Access | Does source have access to claimed info? | Structural |
| Reliability history | Track record of accuracy | Longitudinal |
| Motivation | Why is source sharing? (ideology, money, coercion) | Psychological |
| Corroboration | Do other sources confirm? | Cross-reference |
| Consistency | Does claim fit known facts? | Logical |

### 7.2 Analogy to Lean Axiom Audit

Source reliability assessment is analogous to axiom auditing:
- Each axiom is a "source" of truth
- `propext`, `Quot.sound`, `Classical.choice` = reliable sources (core logic)
- `sorryAx` = unreliable source (proof gap)
- Cross-module consistency = corroboration across sources

---

## Part 8 — Cross-References

| If working on... | Also consult... |
|---|---|
| Evidence chains | `lean-knowledge-formalization` (provenance) |
| Network analysis | `lean-math-discrete` (graph theory) |
| Hypothesis testing | `lean-causal-reasoning` (causal reasoning) |
| Cognitive biases | `lean-knowledge-formalization` (folk psychology) |
| Forecasting | `lean-math-stochastic` (temporal analysis) |
| Red teaming | `lean-review-council` (adversarial review) |
| Structured debate | `math-strategy-studio` (brainstorming) |
| Scenario modeling | `lean-math-dynamical` (bifurcation) |

---

## Merged Domain Companion: `lean-applied-reasoning` (Unified into `@lean-applied-reasoning`)

# Strategy Creation & Analysis

Mathematical and systematic frameworks for creating, evaluating, and executing strategies in competitive and cooperative environments.

---

## Routing

- **USE FOR:** Strategy creation, analysis, and evaluation — game-theoretic foundations, competitive analysis, decision frameworks, SWOT/PESTLE, wargaming,
  and their mathematical underpinnings. Use for strategic reasoning about complex multi-agent scenarios, organizational strategy, research strategy, and
  mathematical planning for governance and optimization layers.
- **DO NOT USE FOR:** formalising strategic models in Lean (use @lean-applied-reasoning); intelligence analysis (use @lean-applied-reasoning);
  game-theoretic optimization (use @lean-math-optimization).
- **TRIGGERS:** strategy, SWOT, PESTLE, wargaming, decision framework, competitive analysis, game-theoretic strategy.

## Workflow

1. Frame the strategic situation: competitors, payoffs, information structure, time horizon.
2. Pick the matching framework (SWOT, PESTLE, Porter, wargame, game-theoretic equilibrium) from the body.
3. Run the analysis; produce the strategic recommendation with explicit assumptions + sensitivities.
4. Hand off: to `@lean-applied-reasoning` if formalisation is needed, to `@lean-math-optimization` if game-theoretic structure dominates, to
   `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the question collapses to a pure optimization problem — delegate to `@lean-math-optimization`.
- STOP if intelligence-analysis methodology is what's needed — delegate to `@lean-applied-reasoning`.
- STOP if the legal/regulatory dimension dominates — delegate to `@applied-legal-reasoning`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-applied-reasoning`, `skill:lean-math-optimization`, `skill:lean-applied-reasoning`.

---

## Detailed reference

Full content for `lean-applied-reasoning` lives in
[`references/lean-applied-reasoning-handbook.md`](../../references/lean-applied-reasoning-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

| Section | Topic |
|---|---|
| Part 1 | Strategic Reasoning Foundations |
| Part 2 | Game-Theoretic Strategy |
| Part 3 | Decision Frameworks |
| Part 4 | Competitive Analysis Frameworks |
| Part 5 | Wargaming & Red Teaming |
| Part 6 | Proof Strategy Design |
| Part 7 | Research Strategy |
| Part 8 | Cross-References |

---

## See also

- [`../../references/lean-applied-reasoning-handbook.md`](../../references/lean-applied-reasoning-handbook.md) — Full handbook (extracted from this skill)
- [`../lean-applied-reasoning/SKILL.md`](../lean-applied-reasoning/SKILL.md) — Successor
- [`../lean-math-optimization/SKILL.md`](../lean-math-optimization/SKILL.md) — Successor
- [`../lean-applied-reasoning/SKILL.md`](../lean-applied-reasoning/SKILL.md) — Successor

# Applied Strategy Analysis Handbook

> **Layering note.** This file holds the deep content previously
> embedded in [`skills/lean-applied-reasoning/SKILL.md`](../skills/lean-applied-reasoning/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow /
> Recovery / Handoffs) + a parts index. This file holds the full
> encyclopaedia. Zero fidelity loss vs the pre-layering revision.

---

## Part 1 — Strategic Reasoning Foundations

### 1.1 Strategy Taxonomy

| Type | Focus | Mathematical Foundation |
|---|---|---|
| **Competitive** | Outperform adversaries | Game theory (Nash, minimax) |
| **Cooperative** | Maximize joint value | Bargaining theory, coalitions |
| **Adaptive** | Respond to changing environment | Control theory, RL |
| **Robust** | Perform well under uncertainty | Minimax regret, info-gap theory |
| **Creative** | Discover novel approaches | Combinatorial exploration, brainstorming |
| **Analytical** | Understand the strategic landscape | Decision analysis, scenario planning |

### 1.2 Project Strategic Mapping

| Strategy Aspect | Project Component | Module |
|---|---|---|
| Competitive dynamics | Multi-agent trust game | AgenticSafety |
| Adaptation under uncertainty | Stochastic dynamics on OKD simplex | StochasticCCV |
| Optimal policy selection | Bellman equation, RL convergence | ReinforcementLearning |
| Multi-objective tradeoffs | CCV quality components | CCVGating |
| Phase-aware strategy | Phase classification, regime switching | PhaseClassification |
| Catastrophic risks | Cusp bifurcation, regime collapse | CuspCatastrophe |

---

## Part 2 — Game-Theoretic Strategy

### 2.1 Strategic Form Games

```
G = (N, {Sᵢ}, {uᵢ})
- N = set of players
- Sᵢ = strategy set for player i
- uᵢ : S₁ × ... × Sₙ → ℝ = payoff function for player i
```

### 2.2 Solution Concepts

| Concept | Definition | When Applicable |
|---|---|---|
| **Nash equilibrium** | No player can unilaterally improve | Simultaneous moves, complete info |
| **Subgame perfect** | Nash in every subgame | Sequential moves |
| **Dominant strategy** | Best regardless of others' choices | When exists (rare) |
| **Minimax** | Minimize maximum loss | Zero-sum games |
| **Pareto optimal** | No one can improve without hurting another | Cooperative settings |
| **Correlated equilibrium** | Coordinated randomization | Communication possible |

### 2.3 Connection to Project Optimization

- `lean-math-optimization` covers the formal mathematical details
- Nash equilibrium ↔ stable regime in the project (no agent wants to deviate)
- Bellman optimality ↔ greedy policy improvement (ReinforcementLearning.lean §23)
- Multi-agent convergence ↔ trust consensus (AgenticSafety.lean §21)

---

## Part 3 — Decision Frameworks

### 3.1 Decision Under Uncertainty

| Framework | Assumption | Method |
|---|---|---|
| **Expected utility** | Known probabilities | Maximize E[u(x)] |
| **Maximin** | Worst-case focus | max_x min_s u(x,s) |
| **Minimax regret** | Minimize maximum regret | min_x max_s [max_y u(y,s) - u(x,s)] |
| **Info-gap** | Deep uncertainty (no probabilities) | Maximize robustness to uncertainty |
| **Real options** | Flexibility has value | Option pricing of strategic choices |
| **Satisficing** | "Good enough" threshold | First option exceeding threshold |

### 3.2 Multi-Criteria Decision Analysis (MCDA)

```
Score(option) = Σᵢ wᵢ × criterion_i(option)

Subject to:
  Σᵢ wᵢ = 1
  wᵢ ≥ 0
  criterion_i normalized to [0, 1]
```

the project's CCV balanced state is a multi-criteria framework:
- Competence, Value, Risk (or C, V, D) are weighted criteria
- The OKD simplex constrains weights to sum to 1
- Balanced state optimizes the multi-criteria objective

---

## Part 4 — Competitive Analysis Frameworks

### 4.1 Porter's Five Forces (Formalized)

| Force | Mathematical Model | Project Analog |
|---|---|---|
| Rivalry | Game theory: N-player competition | Multi-agent dynamics |
| New entrants | Barrier height estimation | Quality gate thresholds |
| Substitutes | Similarity metrics | Alternative phase paths |
| Buyer power | Bargaining solution | Trust negotiation |
| Supplier power | Supply constraint optimization | Pipeline bottleneck |

### 4.2 SWOT Analysis (Structured)

```
SWOT = {
  Strengths:     internal + positive → leverage
  Weaknesses:    internal + negative → mitigate
  Opportunities: external + positive → exploit
  Threats:       external + negative → defend
}

Strategic options = {
  SO: Use strengths to exploit opportunities
  WO: Overcome weaknesses using opportunities
  ST: Use strengths to counter threats
  WT: Minimize weaknesses and avoid threats
}
```

### 4.3 PESTLE Analysis

Political, Economic, Social, Technological, Legal, Environmental — structured environmental scanning.

---

## Part 5 — Wargaming & Red Teaming

### 5.1 Tabletop Wargaming Structure

```
1. SCENARIO: Define the strategic situation
2. SIDES: Assign teams to different actors
3. MOVES: Each team submits strategy simultaneously
4. ADJUDICATION: Evaluate outcomes based on rules/models
5. NEXT TURN: Update situation, repeat
6. DEBRIEF: Extract lessons, update assumptions
```

### 5.2 Red Team / Blue Team

| Team | Role | Project Analog |
|---|---|---|
| Blue | Defend current strategy | Implementer (proof writer) |
| Red | Attack / find vulnerabilities | Σ (Soundness Guardian) + Φ (Statement Oracle) |
| White | Referee / control | Ω (Integration Sentinel) |
| Green | Alternative perspectives | Ν (Novelty Scout) |

The review council IS a formalized wargaming structure.

---

## Part 6 — Proof Strategy Design

### 6.1 Mathematical Proof as Strategy

Every non-trivial proof requires strategic thinking:

| Strategic Decision | Options | Factors |
|---|---|---|
| Proof method | Direct, contradiction, induction, cases | Goal structure, hypothesis availability |
| Decomposition | Lemma chain, calc block, have/suffices | Complexity, reusability |
| Tactic selection | omega, simp, nlinarith, custom | Goal type, automation potential |
| Abstraction level | Concrete Nat, abstract ℝ, typeclass | Generality vs. provability |
| Dependency ordering | Prove A→B→C or C→A→B? | Hard-first strategy |

### 6.2 Proof Strategy Templates

| Pattern | When | Steps |
|---|---|---|
| **Divide and conquer** | Many cases | Split goal, solve each independently |
| **Strengthen and prove** | Goal too weak to attack | Prove stronger intermediate result |
| **Weaken and reduce** | Hypotheses too specific | Generalize, then instantiate |
| **Calculation pipeline** | Equational reasoning | calc block with chain of equalities |
| **Backwards from goal** | Goal structure dictates approach | apply, refine, constructor |

---

## Part 7 — Research Strategy

### 7.1 Strategic Research Planning

```
1. SURVEY the landscape (epistemic-mapping)
2. IDENTIFY key gaps (KU quadrant)
3. ASSESS difficulty × impact for each gap
4. PRIORITIZE: high-impact + tractable first
5. ALLOCATE resources (time, tools, depth)
6. EXECUTE with checkpoints
7. SYNTHESIZE and update epistemic map
```

### 7.2 Portfolio Strategy for Research

Don't put all research effort into one approach:
- **Core** (60%): Known methods applied to clear gaps
- **Adjacent** (30%): Extending methods to neighboring domains
- **Exploratory** (10%): High-risk, high-reward novel approaches

---

## Part 8 — Cross-References

| If working on... | Also consult... |
|---|---|
| Game theory formalization | `lean-math-optimization` |
| Decision under uncertainty | `lean-math-stochastic` |
| Bifurcation/catastrophe strategy | `lean-math-dynamical` |
| Red team methodology | `lean-review-council` (adversarial) |
| Brainstorming techniques | `math-strategy-studio` |
| Research strategy | `research-council`, `epistemic-mapping` |
| Proof strategy | `lean-research` (Type M, Type T) |
| Network strategy | `lean-math-discrete` |
| Temporal strategy | `lean-math-stochastic` |

---
## Goal-Shape Templates (templates)

| Goal Shape | Target Mechanism | Proof Template |
| :--- | :--- | :--- |
| ACH diagnosticity matrix score | Weighted sum over evidence rows | `unfold achScore; simp only [...]; omega` |
| Bayesian likelihood update (scaled integer) | Prior * likelihood normalization | `unfold updatePost; omega` |
| Game/wargame dominant strategy `payoff s* b ≥ payoff s b` | Finite case exhaustion + `omega` | `cases b <;> simp only [payoff] <;> omega` |

## Intent-to-Tactic Phrasebook (phrasebook)

| Applied Reasoning Intent | Lean 4 Tactic / Pattern | Notes |
| :--- | :--- | :--- |
| Prove Analysis of Competing Hypotheses (ACH) rank order | `decide` or `omega` on scaled diagnosticity weights | Keep weights in `Nat` or `Int` |
| Verify evidentiary chain-of-custody monotonicity | Lattice meet `min tier1 tier2` via `omega` | Weakest-link provenance bound |
| Prove minimax / saddle-point bound on finite strategy matrix | `decide` (concrete matrix) or `omega` (parametric) | Fast decidable verification |

## Error-to-Fix Table (errors)

| Error / Symptom | Root Cause | Fix |
| :--- | :--- | :--- |
| Division by zero in normalized posterior | Total evidence weight `∑ w = 0` not excluded | Add hypothesis `0 < totalWeight` or cross-multiply before comparing |
| Conflicting hypotheses sum to `> 100` | Unnormalized probability vector | Enforce simplex invariant `∑ p_i = 100` in state structure |
