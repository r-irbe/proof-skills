---
title: "Math Nonlinear Dynamics Handbook"
status: "reference"
extracted_from: "skills/math-nonlinear-dynamics/SKILL.md"
extracted_on: "2026-05-27"
scope: "Part 1 — Core Mathematical Framework; Part 2 — Bifurcation Analysis Methodology; Part 3 — Lyapunov Function Construction; Part 4 — Phase Portrait Analysis; Part 5 — Control-Theoretic Perspective; Part 6 — Connections to Other Mathematical Disciplines; Part 7 — Research Entry Points"
loader_hint: "Load when @math-nonlinear-dynamics routes here for details; not needed for the dispatch decision."
---

# Math Nonlinear Dynamics Handbook

> **Layering note.** This file holds the deep content previously
> embedded in [`skills/math-nonlinear-dynamics/SKILL.md`](../skills/math-nonlinear-dynamics/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow /
> Recovery / Handoffs) + a parts index. This file holds the full
> encyclopaedia. Zero fidelity loss vs the pre-layering revision.

---

## Part 1 — Core Mathematical Framework

### 1.1 Dynamical Systems Taxonomy

| System Type | State Space | Evolution | Project Module |
|---|---|---|---|
| Continuous autonomous | ẋ = f(x) | ODE flow | PhasePortrait, LyapunovStability |
| Continuous non-autonomous | ẋ = f(x,t) | Time-varying ODE | Multi-timescale architecture |
| Discrete deterministic | x_{n+1} = T(x_n) | Iteration map | QualityGates, PipelineAdaptive |
| Discrete stochastic | x_{n+1} ~ P(·|x_n) | Markov chain | StochasticCCV |
| Hybrid | Mix of continuous + discrete | Switched systems | Project governance transitions |

### 1.2 Stability Theory Hierarchy

```
Lyapunov stability (trajectories stay close)
  ⊂ Asymptotic stability (convergence to equilibrium)
    ⊂ Exponential stability (convergence at rate e^{-αt})
      ⊂ Global exponential stability (convergence from any initial condition)

Project formalization: contraction mapping with rate (1-α) per step
  → exponential stability with rate α per iteration
```

### 1.3 Key Theorems Used in the project

| Theorem | Statement (informal) | Project usage |
|---|---|---|
| Lyapunov's Direct Method | V(x) ≥ 0, V̇(x) ≤ -αV(x) ⟹ exponential stability | Core of LyapunovStability module |
| LaSalle's Invariance Principle | V̇ ≤ 0, largest invariant set in {V̇ = 0} is the equilibrium | Governance convergence, trust dynamics |
| Contraction Mapping Theorem | T is contractive ⟹ unique fixed point, geometric convergence | Quality gates, Bellman iteration |
| Center Manifold Theorem | Near bifurcation, dynamics reduce to center manifold | Cusp catastrophe interpretation |
| Catastrophe Classification | Codimension-2 catastrophes are folds and cusps | CuspCatastrophe module |
| Hartman-Grobman | Near hyperbolic equilibrium, flow ≈ linearized flow | Phase portrait classification |

---

## Part 2 — Bifurcation Analysis Methodology

### 2.1 Bifurcation Detection Protocol

```
1. IDENTIFY control parameters (a, b in cusp V(x;a,b) = x⁴/4 + ax²/2 + bx)
2. COMPUTE equilibria: ∂V/∂x = 0 → x³ + ax + b = 0
3. CLASSIFY stability: ∂²V/∂x² at each equilibrium
4. FIND bifurcation set: discriminant Δ = 4a³ + 27b² = 0
5. MAP regimes: Δ > 0 (fold), Δ < 0 (cusp interior), Δ = 0 (bifurcation)
6. ANALYZE transitions: which equilibria appear/disappear at bifurcation
```

### 2.2 Catastrophe Types Relevant to Project

| Catastrophe | Codimension | Normal Form | Project Interpretation |
|---|---|---|---|
| Fold | 1 | V = x³/3 + ax | Binary regime transition |
| Cusp | 2 | V = x⁴/4 + ax²/2 + bx | Tacit knowledge singularity (TKS) |
| Swallowtail | 3 | V = x⁵/5 + ax³/3 + bx²/2 + cx | Multi-modal knowledge states |
| Butterfly | 4 | V = x⁶/6 + ... | (Future extension) |

### 2.3 Early Warning Signals

Critical slowing down before bifurcation:
- **Variance increase** — fluctuations grow as stability margin shrinks
- **Autocorrelation increase** — recovery from perturbation slows
- **Skewness** — distribution becomes asymmetric near fold
- **Flickering** — system alternates between two quasi-stable states

In Project: these are the EWS (Early Warning Signals) in PipelineAdaptive.

---

## Part 3 — Lyapunov Function Construction

### 3.1 Construction Techniques

| Technique | When to use | Project example |
|---|---|---|
| Quadratic V(x) = xᵀPx | Linear/quasi-linear systems | Basic governance stability |
| Sum-of-squares (SOS) | Polynomial systems | Cusp potential analysis |
| Control-Lyapunov | Systems with control input | Adaptive pipeline governance |
| Multiple Lyapunov | Switched systems | Phase-dependent governance |
| Composite Lyapunov | Interconnected subsystems | Multi-scale Project |
| LaSalle extension | V̇ ≤ 0 (not strictly negative) | Trust convergence |

### 3.2 Multi-Scale Lyapunov (Project-specific)

Project has 4 timescales:
```
τ_experience  ≪  τ_articulation  ≪  τ_structuring  ≪  τ_innovation

V_total = w₁V₁(x₁) + w₂V₂(x₂) + w₃V₃(x₃) + w₄V₄(x₄)

Where:
  V_total decreasing  ⟸  each level contracts AND timescale separation holds
  Timescale separation: τ_{i+1}/τ_i → ∞ means fast level equilibrates before slow level moves
```

### 3.3 Computational Checks

Before attempting formal proof:
1. **Sanity check**: Evaluate V at known stable and unstable points
2. **Derivative check**: Compute V̇ symbolically, verify sign
3. **Basin estimation**: Where is V̇ ≤ 0? Is the sublevel set contained?
4. **Robustness**: How sensitive is V to parameter changes?

---

## Part 4 — Phase Portrait Analysis

### 4.1 Phase Space Reconstruction

For the project's knowledge phase portrait:
```
State: x = (C, V, R, D, M) — Clarity, Volatility, Richness, Dependency, Momentum
Phase space: ℝ⁵ (or Nat-scaled: ℕ⁵ with ×100 resolution)

Derived quantities:
  - Phase velocity: ẋ (rate of knowledge state change)
  - Phase acceleration: ẍ (rate of velocity change)
  - TKS distance: d(x, x_cusp) (distance to tacit knowledge singularity)
  - Regime: classify(C, V, R, D) → {Exploration, Transition, Mastery, Crisis}
```

### 4.2 Attractor Classification

| Attractor | Dimension | Behavior | Project Interpretation |
|---|---|---|---|
| Fixed point | 0 | Steady state | Stable knowledge state |
| Limit cycle | 1 | Periodic | Oscillating knowledge (e.g., Exploration↔Transition) |
| Torus | 2 | Quasi-periodic | Multi-frequency knowledge dynamics |
| Strange attractor | Fractal | Chaotic | Unpredictable knowledge evolution (crisis regime) |

### 4.3 Basin of Attraction

The basin of attraction for each regime determines which initial knowledge states converge to which stable pattern. Project governance should:
- Maximize basin of "Mastery" attractor
- Minimize basin of "Crisis" attractor
- Ensure "Transition" basin funnels toward "Mastery"

---

## Part 5 — Control-Theoretic Perspective

### 5.1 Project as Control System

```
Plant: Knowledge state dynamics ẋ = f(x) + g(x)u
Controller: Governance function u = π(x)
Observation: Quality gates y = h(x)
Objective: Drive x to Mastery regime while maintaining safety envelope

Control design:
  1. Lyapunov-based control: choose u to make V̇ < 0
  2. Barrier certificates: ensure safety constraints satisfied
  3. Model predictive control: optimize over horizon
```

### 5.2 Feedback Linearization

Near a cusp bifurcation, the nonlinear dynamics can be approximately linearized:
```
ẋ = f(x) ≈ Ax + Bu  near equilibrium
Controllability: rank [B, AB, A²B, ...] = n
```

### 5.3 Robust Control

the project's governance must be robust to:
- Parameter uncertainty (unknown α, β in dynamics)
- Measurement noise (imperfect quality gate readings)
- Model mismatch (real knowledge dynamics ≠ mathematical model)

---

## Part 6 — Connections to Other Mathematical Disciplines

| Discipline | Connection to Nonlinear Dynamics | Project Bridge |
|---|---|---|
| Probability/Stochastic | Stochastic stability, noise-induced transitions | StochasticCCV + LyapunovStability |
| Optimization | Gradient dynamics as optimization flow | ReinforcementLearning + quality gate optimization |
| Graph theory | Network dynamics, coupled oscillators | ProvenanceChain + multi-agent trust |
| Measure theory | Invariant measures, ergodic theory | Ergodic convergence of OKD dynamics |
| Algebraic geometry | Singularity theory (catastrophes) | CuspCatastrophe formal classification |
| Topology | Topological invariants of flows, Morse theory | Phase portrait structure |
| Information theory | Entropy production, information geometry | Knowledge compression in the project stages |

---

## Part 7 — Research Entry Points

### 7.1 Key References for Project-Relevant Dynamics

| Topic | Standard References |
|---|---|
| Lyapunov stability | Khalil "Nonlinear Systems"; Vidyasagar "Nonlinear Systems Analysis" |
| Catastrophe theory | Arnol'd "Catastrophe Theory"; Poston & Stewart |
| Bifurcation | Kuznetsov "Elements of Applied Bifurcation Theory" |
| Control-Lyapunov | Sontag "Mathematical Control Theory" |
| Stochastic stability | Khasminskii "Stochastic Stability of Differential Equations" |
| Multi-scale dynamics | Pavliotis & Stuart "Multiscale Methods" |
| Phase portraits | Strogatz "Nonlinear Dynamics and Chaos" |

### 7.2 Open Research Frontiers

- **Hybrid catastrophe theory**: Combining cusp catastrophe with stochastic perturbation
- **Multi-agent Lyapunov**: Compositional Lyapunov for multi-agent trust dynamics
- **Data-driven stability**: Learning Lyapunov functions from trajectory data
- **Topological data analysis**: Using persistent homology for phase portrait classification
