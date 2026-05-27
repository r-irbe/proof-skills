---
name: applied-intelligence-analysis
description: |
  USE FOR: Intelligence analysis methodology — structured analytic techniques (SATs), evidence reasoning, hypothesis generation, cognitive bias mitigation, competitive intelligence, and their formalization. Use for analysis of competing hypotheses (ACH), link analysis, timeline reconstruction, source reliability assessment, and connections to the project's quality gates, provenance, and multi-agent trust.
  DO NOT USE FOR: formalising intelligence reasoning in Lean (use @lean-applied-reasoning); strategy analysis (use @applied-strategy-analysis); legal reasoning (use @applied-legal-reasoning).
  TRIGGERS: structured analytic techniques, SATs, evidence reasoning, hypothesis generation, cognitive bias, intelligence analysis, competing hypotheses.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-applied-reasoning', 'skill:applied-strategy-analysis', 'skill:lean-knowledge-formalization']
metadata:
  version: "0.2.0"
  source_spec: "skills/applied-intelligence-analysis/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Intelligence Analysis

Structured analytic techniques and evidence-based reasoning frameworks for intelligence, investigative, and analytical contexts.


## Routing

- **USE FOR:** Intelligence analysis methodology — structured analytic techniques (SATs), evidence reasoning, hypothesis generation, cognitive bias mitigation, competitive intelligence, and their formalization. Use for analysis of competing hypotheses (ACH), link analysis, timeline reconstruction, source reliability assessment, and connections to the project's quality gates, provenance, and multi-agent trust.
- **DO NOT USE FOR:** formalising intelligence reasoning in Lean (use @lean-applied-reasoning); strategy analysis (use @applied-strategy-analysis); legal reasoning (use @applied-legal-reasoning).
- **TRIGGERS:** structured analytic techniques, SATs, evidence reasoning, hypothesis generation, cognitive bias, intelligence analysis, competing hypotheses.

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
- **Successors:** `skill:lean-applied-reasoning`, `skill:applied-strategy-analysis`, `skill:lean-knowledge-formalization`.

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
| Degree centrality | Number of direct contacts | `math-graph-knowledge` |
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
| Network analysis | `math-graph-knowledge` (graph theory) |
| Hypothesis testing | `ai-causal-deontic` (causal reasoning) |
| Cognitive biases | `ai-commonsense-reasoning` (folk psychology) |
| Forecasting | `math-time-series` (temporal analysis) |
| Red teaming | `lean-review-council` (adversarial review) |
| Structured debate | `math-strategy-studio` (brainstorming) |
| Scenario modeling | `math-nonlinear-dynamics` (bifurcation) |
