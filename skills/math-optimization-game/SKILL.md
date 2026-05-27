---
name: math-optimization-game
description: |
  USE FOR: Mathematical optimization, game theory, decision theory, mechanism design, multi-objective optimization, convex optimization, and reinforcement learning theory. Use for reasoning about Bellman equations, Nash equilibria, Pareto optimality, gradient methods, linear/convex/integer programming, and any optimization-related mathematics in the project. Covers both pure theory and computational methodology.
  DO NOT USE FOR: Lean optimization proofs (use @lean-math-optimization); strategy methodology (use @applied-strategy-analysis); general nonlinear dynamics (use @math-nonlinear-dynamics).
  TRIGGERS: optimization, game theory, decision theory, mechanism design, convex optimization, reinforcement learning.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-math-optimization', 'skill:lean-research', 'skill:lean-zettelkasten']
metadata:
  version: "0.2.0"
  source_spec: "skills/math-optimization-game/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Math Optimization & Game Theory

Mathematical optimization and strategic interaction theory, applied to the project's reinforcement learning, governance convergence, and multi-agent coordination.


## Routing

- **USE FOR:** Mathematical optimization, game theory, decision theory, mechanism design, multi-objective optimization, convex optimization, and reinforcement learning theory. Use for reasoning about Bellman equations, Nash equilibria, Pareto optimality, gradient methods, linear/convex/integer programming, and any optimization-related mathematics in the project. Covers both pure theory and computational methodology.
- **DO NOT USE FOR:** Lean optimization proofs (use @lean-math-optimization); strategy methodology (use @applied-strategy-analysis); general nonlinear dynamics (use @math-nonlinear-dynamics).
- **TRIGGERS:** optimization, game theory, decision theory, mechanism design, convex optimization, reinforcement learning.

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
- **Successors:** `skill:lean-math-optimization`, `skill:lean-research`, `skill:lean-zettelkasten`.

---

## Part 1 — Optimization Theory Foundations

### 1.1 Convex Optimization

| Concept | Definition | Project Relevance |
|---|---|---|
| Convex set | $S$ where $\forall x,y \in S, \lambda x + (1-\lambda)y \in S$ for $\lambda \in [0,1]$ | Quality gates, OKD simplex |
| Convex function | $f(\lambda x + (1-\lambda)y) \le \lambda f(x) + (1-\lambda)f(y)$ | Lyapunov candidates |
| Strong convexity | $f(y) \ge f(x) + \nabla f(x)^T(y-x) + \frac{\mu}{2}\|y-x\|^2$ | Convergence rate bounds |
| KKT conditions | Stationarity + primal/dual feasibility + complementarity | Constrained governance |
| Duality | $\min_x \max_\lambda L(x,\lambda)$ | Trust-safety trade-offs |

### 1.2 Linear & Integer Programming

- **Simplex method**: Pivoting through basic feasible solutions
- **Interior point**: Barrier methods for LP
- **Branch & bound**: Integer programming via LP relaxation
- **Network flows**: Min-cost flow, max-flow/min-cut
- **project application**: Pipeline composition as flow optimization

### 1.3 Nonlinear Optimization

| Method | Convergence | Best For |
|---|---|---|
| Gradient descent | $O(1/k)$ | General smooth |
| Accelerated GD (Nesterov) | $O(1/k^2)$ | Smooth convex |
| Newton's method | Quadratic | Strongly convex, Hessian available |
| BFGS/L-BFGS | Super-linear | Large-scale smooth |
| Proximal gradient | $O(1/k)$ | Composite (smooth + nonsmooth) |
| Mirror descent | $O(1/\sqrt{k})$ | Simplex constraints (OKD) |

---

## Part 2 — Game Theory

### 2.1 Solution Concepts

| Concept | Definition | Multi-Agent Relevance |
|---|---|---|
| Nash equilibrium | No player can improve by unilateral deviation | Trust equilibrium in multi-agent |
| Pareto optimality | No player can improve without harming another | Governance trade-offs |
| Correlated equilibrium | Players follow a joint signal device | Coordinated policy |
| Stackelberg equilibrium | Leader commits, followers optimize | Hierarchical governance |
| Evolutionary stable strategy | Resists invasion by mutant strategies | Long-term trust stability |

### 2.2 Game Classes

- **Zero-sum**: $\sum_i u_i = 0$ — adversarial safety scenarios
- **Potential games**: $\exists \Phi$ s.t. $\Delta u_i = \Delta \Phi$ — alignment incentives  
- **Stochastic games**: State evolves with actions — MDP foundation
- **Mechanism design**: Design rules to achieve desired outcomes — governance design
- **Cooperative games**: Coalition formation, Shapley value — trust allocation

### 2.3 Nash Existence & Computation

**Existence (Nash 1950):** Every finite game has at least one mixed-strategy NE.

**Computation complexity:** Finding NE is PPAD-complete (Daskalakis et al. 2009).

**Algorithms:**
- Support enumeration (small games)
- Lemke-Howson (bimatrix)
- Homotopy methods
- Learning dynamics (fictitious play, multiplicative weights)

**Project formalization:** Trust dynamics as learning dynamics converging to NE-like fixed points.

---

## Part 3 — Decision Theory

### 3.1 Expected Utility Theory

- Von Neumann-Morgenstern axioms → utility function
- Risk aversion: concave utility ($u'' < 0$)
- Project: Quality gate thresholds as risk-adjusted decisions

### 3.2 Multi-Criteria Decision Making

| Method | Type | Project Use |
|---|---|---|
| Weighted sum | Scalarization | CCV → single quality score |
| Pareto front | Geometric | Trade-off visualization |
| TOPSIS | Distance-based | Phase classification boundaries |
| AHP | Hierarchical | Nested learning level priorities |
| ELECTRE/PROMETHEE | Outranking | Governance action ranking |

### 3.3 Decision Under Uncertainty

- **Maximin**: Worst-case optimization — safety-critical governance
- **Minimax regret**: Minimize maximum regret — robust decisions
- **Bayesian**: Maximize expected utility with priors — adaptive trust
- **Info-gap**: Robustness to severe uncertainty — unknown-unknown resilience

---

## Part 4 — Reinforcement Learning Theory

### 4.1 MDP Foundations

| Component | Formal | Project Module |
|---|---|---|
| State space $\mathcal{S}$ | Finite or compact | Regime classification |
| Action space $\mathcal{A}$ | Finite or compact | Governance actions |
| Transition $P(s'|s,a)$ | Stochastic kernel | Pipeline dynamics |
| Reward $R(s,a)$ | Bounded real | Quality improvement |
| Discount $\gamma$ | $\in [0,1)$ | Convergence rate |

### 4.2 Key Theorems

- **Bellman optimality**: $V^*(s) = \max_a [R(s,a) + \gamma \sum_{s'} P(s'|s,a) V^*(s')]$
- **Contraction mapping**: $\|TV - TV'\|_\infty \le \gamma \|V - V'\|_\infty$
- **Policy improvement**: $\pi_{k+1}$ greedy w.r.t. $V^{\pi_k}$ ⟹ $V^{\pi_{k+1}} \ge V^{\pi_k}$
- **Regret bounds**: Policy gradient regret $\tilde{O}(\sqrt{T})$

### 4.3 Safe RL

- **Constrained MDP**: $\max_\pi V^\pi$ s.t. $C^\pi \le d$
- **Lyapunov-based**: Safety via Lyapunov barrier functions
- **Shielding**: Pre/post-safety filters on actions
- **Project**: Trust dynamics as safe RL with Lyapunov certification

---

## Part 5 — Multi-Objective Optimization

### 5.1 Pareto Theory

- **Pareto dominance**: $x \prec y$ iff $f_i(x) \le f_i(y)$ for all $i$, strict for some
- **Pareto front**: Set of non-dominated solutions
- **Scalarization**: $\min_x \sum_i w_i f_i(x)$ recovers Pareto points (for convex)
- **$\epsilon$-constraint**: $\min f_1$ s.t. $f_j \le \epsilon_j$ for $j \ge 2$

### 5.2 Project Multi-Objective Formulation

The Project governance problem is inherently multi-objective:
- Maximize quality (CCV scores)
- Minimize risk (safety envelope violations)
- Maximize learning rate (nested learning convergence)
- Minimize computational cost (pipeline efficiency)

---

## Part 6 — Connection to Project Lean Modules

| Project Module | Mathematical Foundation | Key Concepts |
|---|---|---|
| ReinforcementLearning.lean | MDP, Bellman, contraction | `ValueFunction`, `bellmanContraction`, `greedyValue` |
| AgenticSafety.lean | Constrained optimization, game theory | `MultiAgentTrust`, `SafetyEnvelope` |
| LyapunovStability.lean | Lyapunov optimization, safe RL | `governanceLyapunov`, `multiScaleLyapunov` |
| Tactics.lean | General contraction theory | `AlignedReward`, `ProjectHierarchy` |
| StochasticCCV.lean | Stochastic optimization, simplex | `okdStep`, `balancedStart` |

---

## Part 7 — Research Methodology for Optimization

### 7.1 When to Apply This Skill

- Designing governance objective functions
- Analyzing convergence rates of iterative schemes
- Proving optimality of policy choices
- Designing multi-agent coordination mechanisms
- Analyzing trade-offs in safety vs performance

### 7.2 Key References

- Boyd & Vandenberghe (2004) — Convex optimization Bible
- Osborne & Rubinstein (1994) — Game theory foundations
- Puterman (2014) — MDP theory and algorithms  
- Szepesvári (2010) — RL theory algorithms
- Miettinen (1999) — Nonlinear multi-objective optimization

### 7.3 Epistemic Mapping Targets

| KK | KU | UK/UU to discover |
|---|---|---|
| Bellman contraction | Tighter regret bounds | Novel game formulations for trust |
| Convex CCV structure | Multi-objective Pareto for Project | Mechanism design for governance |
| Simplex projection | Mirror descent for OKD | Stackelberg formulation of hierarchy |
