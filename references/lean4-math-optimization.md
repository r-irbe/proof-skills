---
title: "Optimization & Decision Theory Encyclopaedia (Lean 4)"
status: "reference"
extracted_from: "skills/lean-math-optimization/SKILL.md"
extracted_on: "2026-05-27"
scope: "Parts 1-7 (optimization fundamentals, convex optimization, fixed-point iterations, game theory, RL theory, multi-objective optimization, decision theory)"
loader_hint: "Load when @lean-math-optimization routes here; not needed for dispatch decisions."
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

