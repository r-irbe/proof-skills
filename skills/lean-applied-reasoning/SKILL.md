---
name: lean-applied-reasoning
description: Applied reasoning for intelligence analysis, strategy creation and analysis, brainstorming methodologies, investigative reasoning, and domain-specific decision-making. Use when formalizing strategic frameworks, situational analysis, hypothesis generation workflows, decision-under-uncertainty models, or when connecting the project's theoretical formalization to practical operational contexts. Bridges mathematical formalization to real-world application domains.
---

# Lean 4 Applied Reasoning & Strategy

Guide to formalizing applied reasoning — from intelligence analysis to strategic decision-making — in Lean 4.

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
