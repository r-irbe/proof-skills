---
name: "lean-math-optimization-handbook"
description: "Unified reference handbook for @lean-math-optimization (Lean 4 formalization + domain mathematical theory)."
extracted_from: "skills/lean-math-optimization/SKILL.md"
---

# Optimization & Decision Theory Encyclopaedia (Lean 4)

> **Layering note.** This file holds the deep encyclopaedia content
> previously embedded in [`skills/lean-math-optimization/SKILL.md`](../skills/lean-math-optimization/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow / Recovery /
> Handoffs) and the high-frequency pitfalls / recipes; this file holds the
> full reference content. Zero fidelity loss vs the pre-layering revision.

## Part 1 — Optimization Fundamentals

### 1.1 Optimization Problem Structure

```lean
-- Minimization: find x* ∈ S such that f(x*) ≤ f(x) for all x ∈ S
-- Lean formalization:
def IsMinOn (f : α → ℝ) (S : Set α) (x : α) : Prop :=
  x ∈ S ∧ ∀ y ∈ S, f x ≤ f y

-- Mathlib: IsMinOn lives in Mathlib.Order.Filter.Basic
-- Also: IsLocalMin, IsLocalMinOn for local optima
```

### 1.2 Optimality Conditions

| Condition | Statement | Lean approach |
|---|---|---|
| First-order necessary | `∇f(x*) = 0` (unconstrained) | `HasDerivAt f 0 x` |
| Second-order sufficient | `∇²f(x*) > 0` | Positive definiteness of Hessian |
| KKT (constrained) | Lagrangian stationarity + complementarity | Structure with multipliers |
| Convex: global = local | `ConvexOn ℝ S f → IsLocalMinOn ⟹ IsMinOn` | `ConvexOn.isMinOn_of_isLocalMinOn` |

### 1.3 Project Optimization Problems

| Module | Optimization Problem | Type |
|---|---|---|
| QualityGates | Maximize quality subject to gate constraints | Constrained, discrete |
| PipelineAdaptive | Minimize cognitive load while maintaining quality | Multi-objective |
| CuspCatastrophe | Find equilibria (critical points of potential) | Unconstrained, polynomial |
| ReinforcementLearning | Maximize cumulative reward (Bellman) | Dynamic programming |
| AgenticSafety | Maximize utility subject to safety envelope | Constrained, dynamic |
| LyapunovStability | Find Lyapunov function (feasibility) | Satisfiability |

---

## Part 2 — Convex Optimization

### 2.1 Convex Functions in Mathlib

```lean
-- ConvexOn ℝ s f : f is convex on convex set s
-- ConcaveOn ℝ s f : -f is convex on s

-- Key properties:
-- ConvexOn.add : convex + convex = convex
-- ConvexOn.smul : nonneg scalar * convex = convex
-- ConvexOn.sup : max(convex, convex) is convex (pointwise sup)

-- Jensen's inequality:
-- f(∑ λᵢxᵢ) ≤ ∑ λᵢ f(xᵢ) when f is convex, λ on simplex
```

### 2.2 Proximal and Projection Operators

```lean
-- Projection onto convex set:
-- proj_S(x) = argmin_{y ∈ S} ‖x - y‖

-- In Project: projecting onto the trust simplex
-- After an update step, project back to maintain constraints

-- Mathlib: Metric.proj (inner product spaces)
-- EuclideanDomain for projection existence/uniqueness
```

### 2.3 Gradient Descent Convergence

```lean
-- For L-smooth, μ-strongly convex f:
-- x_{n+1} = x_n - η ∇f(x_n)
-- ‖x_n - x*‖² ≤ (1 - 2ηm/(m+L))^n ‖x₀ - x*‖²

-- This is a contraction → use `nlinarith [sq_nonneg ...]` directly (proj_contraction DEPRECATED — 0 uses)
-- Rate depends on condition number κ = L/μ
```

---

## Part 3 — Fixed-Point Iterations

### 3.1 Taxonomy

| Method | Update rule | Convergence condition | Project usage |
|---|---|---|---|
| Picard iteration | `x_{n+1} = f(x_n)` | `f` is contracting | Trust dynamics |
| Bellman iteration | `V_{n+1} = T[V_n]` | `T` is γ-contracting | Value iteration |
| Power iteration | `v_{n+1} = Av_n/‖Av_n‖` | Spectral gap | (Eigenvalue computation) |
| Projective | `x_{n+1} = proj_S(f(x_n))` | Nonexpansive + ... | Constrained optimization |

### 3.2 Banach Fixed Point Theorem in Lean

Consolidated into single canonical reference:
[`references/lean4-contraction-catalog.md`](../../references/lean4-contraction-catalog.md)
(§1 Mathlib API, §4 project contraction-theorem index — `BellmanOperator.contracting` row).

Project Bellman operator one-liner: the Bellman operator on bounded
value functions is a `γ`-contraction in the sup-norm; see the catalog
§4 index entry.  The deprecated `proj_bellman` tactic is gone — use
`unfold bellmanStep; omega` or the underlying `ContractingWith`
machinery directly.

---

## Part 4 — Game Theory

### 4.1 Game Formalization

```lean
-- Two-player game
structure Game (S₁ S₂ : Type) where
  payoff₁ : S₁ → S₂ → ℝ
  payoff₂ : S₁ → S₂ → ℝ

-- Nash equilibrium: no player can unilaterally improve
def IsNashEquilibrium (g : Game S₁ S₂) (s₁ : S₁) (s₂ : S₂) : Prop :=
  (∀ s₁', g.payoff₁ s₁ s₂ ≥ g.payoff₁ s₁' s₂) ∧
  (∀ s₂', g.payoff₂ s₁ s₂ ≥ g.payoff₂ s₁ s₂')

-- Zero-sum game: payoff₂ = -payoff₁
-- Minimax theorem (von Neumann): max_x min_y f(x,y) = min_y max_x f(x,y)
```

### 4.2 Project Game-Theoretic Aspects

| Project Mechanism | Game-Theoretic Model |
|---|---|
| Quality gate negotiation | Stackelberg game (system sets gates, user responds) |
| Multi-agent safety | Cooperative game with safety constraints |
| Trust allocation | Resource allocation game on simplex |
| Peer validation (Consolidation) | Signaling game (expertise signals credibility) |
| AI-human collaboration | Principal-agent with moral hazard |

### 4.3 Mechanism Design

```lean
-- Incentive compatibility: truth-telling is optimal
-- Individual rationality: participation is voluntary
-- the project's quality gates serve as mechanism design:
-- they incentivize thorough externalization (truth-telling about knowledge)
-- while maintaining individual rationality (reducing cognitive burden)
```

---

## Part 5 — Reinforcement Learning Theory

### 5.1 MDP Formalization

```lean
-- Markov Decision Process
structure MDP (State Action : Type) where
  transition : State → Action → State → ℝ  -- P(s'|s,a)
  reward : State → Action → ℝ              -- R(s,a)
  discount : ℝ                              -- γ ∈ [0,1)

-- Value function: V*(s) = max_π E[Σ γ^t R(s_t, a_t) | s₀ = s, π]
-- Bellman optimality: V*(s) = max_a [R(s,a) + γ Σ P(s'|s,a) V*(s')]
```

### 5.2 Convergence Theorems

| Algorithm | Convergence | Rate | Project formalization |
|---|---|---|---|
| Value iteration | `V_n → V*` | `‖V_n - V*‖ ≤ γ^n/(1-γ) ‖V₀ - V*‖` | Contraction mapping |
| Policy iteration | Finite convergence | ≤ \|S\|^{\|A\|} iterations | (Not formalized) |
| Q-learning | `Q_n → Q*` a.s. | Stochastic approximation | (Extended model) |

### 5.3 Project RL Module Patterns

```lean
-- The ReinforcementLearning module uses:
-- 1. Nat-scaled MDP (discrete states, Nat rewards)
-- 2. Bellman step defined as concrete computation
-- 3. Contraction proved via omega/nlinarith on Nat differences
-- 4. Bridge to real analysis for convergence rate

-- Key tactic: unfold bellmanStep; omega  (proj_bellman DEPRECATED — 0 uses)
-- Unfolds bellmanStep, reward, pipelineHealth then omega

-- Regret-as-Lyapunov: treating Bellman residual as Lyapunov function
-- V(x) = ‖V_n - V*‖ decreases by factor γ each iteration
```

---

## Part 6 — Multi-Objective Optimization

### 6.1 Pareto Optimality

```lean
-- Multi-objective: minimize (f₁(x), f₂(x), ..., f_k(x)) simultaneously
-- Pareto optimal: no other x improves all objectives

def IsParetoOptimal (fs : Fin k → α → ℝ) (S : Set α) (x : α) : Prop :=
  x ∈ S ∧ ¬∃ y ∈ S, (∀ i, fs i y ≤ fs i x) ∧ (∃ i, fs i y < fs i x)

-- Project: quality vs cognitive load vs speed
-- The pipeline navigates the Pareto frontier
```

### 6.2 Scalarization

```lean
-- Weighted sum: min Σ wᵢ fᵢ(x) (finds Pareto points on convex frontier)
-- ε-constraint: min f₁(x) s.t. fᵢ(x) ≤ εᵢ for i ≥ 2
-- Project quality gates use threshold ε-constraints
```

---

## Part 7 — Decision Theory

### 7.1 Expected Utility

```lean
-- Von Neumann-Morgenstern: preferences over lotteries
-- U(L) = Σ pᵢ u(xᵢ) for lottery L = Σ pᵢ δ_{xᵢ}
-- Axioms: completeness, transitivity, continuity, independence
```

### 7.2 Risk Measures

```lean
-- Value at Risk: VaR_α(X) = inf{x : P(X ≤ x) ≥ α}
-- Expected Shortfall: ES_α(X) = E[X | X ≤ VaR_α(X)]
-- Project: risk measures for quality score distributions
```

### 7.3 Bounded Rationality

```lean
-- Project explicitly models bounded rationality (cognitive load theory):
-- Agents don't optimize globally — they satisfice
-- Quality gates ensure minimum acceptable performance
-- This aligns with Simon's bounded rationality + Kahneman's dual process
```

---

---

## Inline Pitfalls & Recovery Recipes (from `skills/lean-math-optimization/SKILL.md`)

# Lean 4 Optimization & Decision Theory

Guide to formalizing optimization, game theory, RL theory, and decision-making in Lean 4.

## Routing

- **USE FOR:** optimization theory, convex optimization, game theory, reinforcement-learning theory (Bellman equations, value / policy iteration), Nash
  equilibria, minimax theorems, decision theory, and fixed-point iterations in Lean 4.
- **DO NOT USE FOR:** stochastic policies / Markov chains (delegate to `@lean-math-stochastic`); pure analysis (delegate to `@lean-math-analysis`);
  Lyapunov / control-stability proofs (delegate to `@lean-math-dynamical`); writing one specific proof (delegate to `@lean-proof`).
- **TRIGGERS:** optimization, convex, game theory, Bellman, value iteration, policy iteration, Nash, minimax, fixed point, KKT.

## Workflow

1. Identify the optimality structure (Part 1) — unconstrained, convex, equilibrium, dynamic-programming.
2. Pick the matching tool below (gradient / KKT, contraction / Banach fixed-point, Bellman backup, Nash-equilibrium argument).
3. Handoff to `@lean-proof`; if the contraction step requires a normed-space lemma, handoff to `@lean-math-analysis`.

## Recovery & STOP

- STOP if the proof requires a Banach-contraction instance not yet imported — handoff to `@lean-math-analysis`.
- STOP if a stochastic policy or expected-value argument appears — re-route to `@lean-math-stochastic`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-proof` (mid-proof optimization goal), `skill:lean-research` (Bellman / Nash-equilibrium API survey).
- **Successors:** `skill:lean-proof` (apply the optimization pattern), `skill:lean-proof-review` (audit fixed-point claim), `skill:lean-math-analysis`
  (contraction / normed-space reduction).

## Detailed reference

Full encyclopaedia content (Parts 1 through 7) lives in
[`references/lean4-math-optimization.md`](../../references/lean4-math-optimization.md). Load that file
when authoring; the SKILL.md only carries the dispatch contract and
the high-frequency pitfalls / recipes (kept inline below).

| Part | Topic | Covers |
|---|---|---|
| Part 1 | Optimization Fundamentals | objective / feasible-set / optimum vocabulary in Mathlib |
| Part 2 | Convex Optimization | ConvexOn, KKT (host-repository), Jensen, gradient conditions |
| Part 3 | Fixed-Point Iterations | Banach contraction; iteration-bound estimates |
| Part 4 | Game Theory | Nash equilibrium, zero-sum, minimax, saddle-point hypotheses |
| Part 5 | Reinforcement Learning Theory | Bellman backup, value/policy iteration, discount factor |
| Part 6 | Multi-Objective Optimization | Pareto frontier, lexicographic ordering |
| Part 7 | Decision Theory | bounded rationality + project alignment |

## Part 8 — Research Council Integration

Consolidated into the single canonical routing matrix:
[`references/research-council-skill-map.md`](../../references/research-council-skill-map.md)
(see the "Optimization" section).  When dispatching a question to a
council member, cite that table rather than restating the rows here.

---

## Part 9 — Common Pitfalls (Convex / RL / Game Theory)

| Pitfall | Symptom | Recovery |
|---|---|---|
| Bellman without `0 ≤ γ < 1` | Value-iteration convergence won't close | Add hypothesis `hγ : γ < 1`; the Bellman backup is a contraction in `‖·‖∞` *only* under this condition |
| Convex but not *strictly* convex | Uniqueness of optimum fails | Strengthen to `StrictConvexOn` instead of `ConvexOn`; pair with strict-monotonicity for the optimum step |
| Banach contraction missing `[CompleteSpace α]` | `ContractingWith.fixedPoint` won't apply | Add the instance, or restrict to a closed ball with induced completeness |
| Minimax order flipped | `inf sup ≤ sup inf` doesn't close | Saddle-point requires compact + convex + continuous on both sides; check Sion's-theorem hypotheses (no Sion in Mathlib at current pin — local construction or `@lean-research`) |
| Discount factor used as `ℝ` while state is `ℕ` | Coercion warnings; `^` won't elaborate | Use `(γ : ℝ) ^ n` and prove with `Real.rpow_lt_one` family (or `pow_lt_one_iff_of_nonneg`) |
| Non-empty / non-bounded feasible set assumed | `IsLeast` / `IsGLB` won't construct | Bound the feasible set explicitly; for unbounded LP, no Mathlib fixed-point applies — use `@lean-research` |

### RL-theory escape hatches

- **Finite horizon:** `Finset.sum_range_succ` unfolding usually beats induction on a `valueFn`.
- **Infinite horizon:** only meaningful with `0 ≤ γ < 1`; the geometric-series bound is `Real.geom_series_lt` / `tsum_geometric_lt_one` /
  `summable_geometric_of_lt_one`.
- **Value-iteration convergence:** prove the Bellman backup is a contraction in `‖·‖∞`, then apply the Banach fixed-point theorem (see
  `@lean-math-dynamical` Part 10 for the recipe).
- **Policy iteration:** equivalence to value iteration is *not* in Mathlib — author a local lemma in the host repository and cite it.

---

## Part 10 — Convex-Optimization Cross-Reference

| Goal | Mathlib lemma / tactic |
|---|---|
| Jensen's inequality | `ConvexOn.inner_le_iff`, `ConvexOn.smul_le_sum` |
| Strict convexity → unique minimum | `StrictConvexOn.eq_of_le_of_le` (host-repository lemma usually required) |
| Convex hull of a finite set | `Mathlib.Analysis.Convex.Hull` — `convexHull_eq` |
| Polytope vertices | `Mathlib.Analysis.Convex.Extrema` — extreme-point characterisation |
| KKT conditions | *No general KKT API in Mathlib*; author locally and cite |
| `stdSimplex.le_one` (single-coord ≤ 1) | `Mathlib/Analysis/Convex/StdSimplex.lean:304` — prefer over `(mem_Icc_of_mem_stdSimplex h x).2` for single-coordinate queries |

---

## See also

- [`../../references/lean4-math-optimization.md`](../../references/lean4-math-optimization.md) — Optimization & Decision Theory Encyclopaedia (full
  encyclopaedia, extracted from this skill)
- [`../../templates/Template_Dynamics.md`](../../templates/Template_Dynamics.md) — Template: Fixed-point and contraction iterations
- [`../../templates/Template_Arithmetic.md`](../../templates/Template_Arithmetic.md) — Template: Scaled-Nat thresholds and convex bounds
- [`../../references/lean4-tactic-hierarchy.md`](../../references/lean4-tactic-hierarchy.md) — Tactic priority for arithmetic goals

---

## Merged Domain Companion: `lean-math-optimization` (Unified into `@lean-math-optimization`)

# Math Optimization & Game Theory

Mathematical optimization and strategic interaction theory, applied to reinforcement learning, governance convergence, and multi-agent coordination.

---

## Routing

- **USE FOR:** Mathematical optimization, game theory, decision theory, mechanism design, multi-objective optimization, convex optimization, and
  reinforcement learning theory. Use for reasoning about Bellman equations, Nash equilibria, Pareto optimality, gradient methods, linear/convex/integer
  programming, and optimization-related mathematics. Covers both pure theory and computational methodology.
- **DO NOT USE FOR:** Lean optimization proofs (use @lean-math-optimization); strategy methodology (use @lean-applied-reasoning); general nonlinear
  dynamics (use @lean-math-dynamical).
- **TRIGGERS:** optimization, game theory, decision theory, mechanism design, convex optimization, reinforcement learning.

## Workflow

1. Classify the problem: convex / nonconvex / combinatorial / game-theoretic / mechanism-design / multi-objective / RL.
2. Pick the matching section of the body; identify Mathlib `Convex` / `Optimization` namespaces where applicable.
3. Produce the answer (algorithm, equilibrium, mechanism) with assumptions + complexity.
4. Hand off: to `@lean-math-optimization` for the Lean proof, to `@lean-math-dynamical` if dynamics dominate, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the question is strategy-analysis (not optimisation) — delegate to `@lean-applied-reasoning`.
- STOP if a Mathlib pin-verified lemma is required — escalate to `@lean-research`.
- STOP if the problem requires empirical RL experiments — escalate to `@research-council`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-math-optimization`, `skill:lean-research`, `skill:lean-zettelkasten`.

---

## Part 1 — Optimization Theory Foundations

### 1.1 Convex Optimization

| Concept | Definition | Common relevance |
|---|---|---|
| Convex set | $S$ where $\forall x,y \in S, \lambda x + (1-\lambda)y \in S$ for $\lambda \in [0,1]$ | Quality gates, stochastic simplexes |
| Convex function | $f(\lambda x + (1-\lambda)y) \le \lambda f(x) + (1-\lambda)f(y)$ | Lyapunov candidates |
| Strong convexity | $f(y) \ge f(x) + \nabla f(x)^T(y-x) + \frac{\mu}{2}\|y-x\|^2$ | Convergence rate bounds |
| KKT conditions | Stationarity + primal/dual feasibility + complementarity | Constrained governance |
| Duality | $\min_x \max_\lambda L(x,\lambda)$ | Trust-safety trade-offs |

### 1.2 Linear & Integer Programming

- **Simplex method**: Pivoting through basic feasible solutions
- **Interior point**: Barrier methods for LP
- **Branch & bound**: Integer programming via LP relaxation
- **Network flows**: Min-cost flow, max-flow/min-cut
- **Common application**: pipeline composition as flow optimization

### 1.3 Nonlinear Optimization

| Method | Convergence | Best For |
|---|---|---|
| Gradient descent | $O(1/k)$ | General smooth |
| Accelerated GD (Nesterov) | $O(1/k^2)$ | Smooth convex |
| Newton's method | Quadratic | Strongly convex, Hessian available |
| BFGS/L-BFGS | Super-linear | Large-scale smooth |
| Proximal gradient | $O(1/k)$ | Composite (smooth + nonsmooth) |
| Mirror descent | $O(1/\sqrt{k})$ | Simplex constraints |

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

**Common formalization:** trust dynamics as learning dynamics converging to NE-like fixed points.

---

## Part 3 — Decision Theory

### 3.1 Expected Utility Theory

- Von Neumann-Morgenstern axioms → utility function
- Risk aversion: concave utility ($u'' < 0$)
- Quality gate thresholds as risk-adjusted decisions

### 3.2 Multi-Criteria Decision Making

| Method | Type | Common use |
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
- **Common use**: trust dynamics as safe RL with Lyapunov certification

---

## Part 5 — Multi-Objective Optimization

### 5.1 Pareto Theory

- **Pareto dominance**: $x \prec y$ iff $f_i(x) \le f_i(y)$ for all $i$, strict for some
- **Pareto front**: Set of non-dominated solutions
- **Scalarization**: $\min_x \sum_i w_i f_i(x)$ recovers Pareto points (for convex)
- **$\epsilon$-constraint**: $\min f_1$ s.t. $f_j \le \epsilon_j$ for $j \ge 2$

### 5.2 Multi-Objective Formulation

Governance and safety problems are often inherently multi-objective:
- Maximize quality (CCV scores)
- Minimize risk (safety envelope violations)
- Maximize learning rate (nested learning convergence)
- Minimize computational cost (pipeline efficiency)

---

## Part 6 — Host-Repository Lean Extension Points

Do not assume repository-local Lean modules, tactics, or namespaces exist unless the host repository explicitly provides them. Map local modules by role:

| Local extension point | Mathematical foundation | Typical concepts |
|---|---|---|
| RL/value-function module | MDP, Bellman, contraction | value functions, Bellman contraction, greedy values |
| Safety/trust module | constrained optimization, game theory | multi-agent trust, safety envelopes |
| Lyapunov/stability module | Lyapunov optimization, safe RL | Lyapunov functions, multi-scale energy |
| Tactic-helper module | general contraction theory | aligned rewards, hierarchy bounds |
| Stochastic-dynamics module | stochastic optimization, simplex | transition steps, balanced starts |

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
| Convex quality structure | Multi-objective Pareto analysis | Mechanism design for governance |
| Simplex projection | Mirror descent on constrained probability states | Stackelberg formulation of hierarchy |

---
## Goal-Shape Templates (templates)

| Goal Shape | Target Typeclass / Lemma | Proof Template |
| :--- | :--- | :--- |
| `ConvexOn ℝ s f` | `ConvexOn` combinators | `apply ConvexOn.add hf hg` |
| `‖T v - T w‖ ≤ γ * ‖v - w‖` (Bellman contraction) | `ContractingWith` | `refine ⟨hγ, fun v w => ?_⟩` |
| `u (a*, b) ≥ u (a, b)` (Nash equilibrium) | Best-response inequality | `unfold isNash; linarith` (or `omega` for finite payoff matrices) |
| Weak duality `primal_val ≤ dual_val` | Lagrangian saddle inequality | `calc primal <= L x y := ... _ <= dual := ...` |

## Intent-to-Tactic Phrasebook (phrasebook)

| Mathematical Intent | Lean 4 / Mathlib Tactic | Notes |
| :--- | :--- | :--- |
| Prove convex combination inequality `t * x + (1 - t) * y` | `nlinarith [ht0, ht1]` | Pair `0 <= t` and `t <= 1` with `nlinarith` |
| Invoke Banach fixed-point theorem for Bellman operator | `ContractingWith.fixedPoint_unique` | Requires `[CompleteSpace E]` and `[Nonempty E]` |
| Verify finite-game dominance or minimax bound | `omega` / `decide` | Use scaled-integer payoffs when working in core-only or discrete lanes |

## Error-to-Fix Table (errors)

| Error / Symptom | Root Cause | Fix |
| :--- | :--- | :--- |
| `iInf` / `sSup` inequality fails on `Real` | `Real` is only `ConditionallyCompleteLinearOrder` | Supply `BddBelow s` / `BddAbove s` and `s.Nonempty` proofs |
| Discount factor `γ` division error in `1 / (1 - γ)` | `1 - γ ≠ 0` not in context | Derive `have : 0 < 1 - γ := by linarith` then `positivity` + `field_simp` |
