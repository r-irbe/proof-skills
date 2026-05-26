---
name: applied-strategy-analysis
description: Strategy creation, analysis, and evaluation — game-theoretic foundations, competitive analysis, decision frameworks, SWOT/PESTLE, wargaming, and their mathematical underpinnings. Use for strategic reasoning about complex multi-agent scenarios, organizational strategy, research strategy, and the mathematical planning aspects of the project's governance and optimization layers.
---

# Strategy Creation & Analysis

Mathematical and systematic frameworks for creating, evaluating, and executing strategies in competitive and cooperative environments.

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

- `math-optimization-game` covers the formal mathematical details
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
| Game theory formalization | `math-optimization-game` |
| Decision under uncertainty | `math-measure-probability` |
| Bifurcation/catastrophe strategy | `math-nonlinear-dynamics` |
| Red team methodology | `lean-review-council` (adversarial) |
| Brainstorming techniques | `math-strategy-studio` |
| Research strategy | `research-council`, `epistemic-mapping` |
| Proof strategy | `lean-research-types` (Type M, Type T) |
| Network strategy | `math-graph-knowledge` |
| Temporal strategy | `math-time-series` |
