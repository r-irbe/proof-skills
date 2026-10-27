---
name: "lean-math-dynamical-handbook"
description: "Unified reference handbook for @lean-math-dynamical (Lean 4 formalization + domain mathematical theory)."
extracted_from: "skills/lean-math-dynamical/SKILL.md"
---

# Nonlinear Dynamics Encyclopaedia (Lean 4)

> **Layering note.** This file holds the deep encyclopaedia content
> previously embedded in [`skills/lean-math-dynamical/SKILL.md`](../skills/lean-math-dynamical/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow / Recovery /
> Handoffs) and the high-frequency pitfalls / recipes; this file holds the
> full reference content. Zero fidelity loss vs the pre-layering revision.

## Part 1 — Dynamical Systems Taxonomy

### 1.1 System Types in the project

| System Type | Mathematical Form | Project Module | Lean Representation |
|---|---|---|---|
| Discrete-time, finite state | `x_{n+1} = f(x_n)` on `ℕ` or `Fin k` | QualityGates, PhaseClassification | `def iterate (n : ℕ) : State` |
| Discrete-time, real state | `x_{n+1} = f(x_n)` on `ℝⁿ` | ReinforcementLearning, StochasticCCV | `def step : ℝⁿ → ℝⁿ` |
| Continuous-time ODE | `ẋ = f(x)` | LyapunovStability (conceptual) | `HasDerivAt` + trajectory |
| Parametric family | `ẋ = f(x; a, b)` | CuspCatastrophe | `fun x a b => ...` |
| Stochastic | `x_{n+1} = f(x_n) + noise` | StochasticCCV | Measure-theoretic |

### 1.2 Formalization Strategy

Project uses **Nat-scaled discrete models** as the primary formalization, with **real-valued analysis** as the secondary layer for continuous concepts:

```
Nat model (primary)          Real model (secondary)
  - decidable                  - Lyapunov functions
  - kernel-checkable           - derivatives
  - finite case analysis       - contraction bounds
  - omega/decide proofs        - nlinarith/linarith proofs
       ↕ coercion bridges ↕
```

---

## Part 2 — Lyapunov Stability Theory

The Lyapunov direct method, the project Lyapunov-function inventory,
and the deprecation note for `proj_lyapunov` are consolidated into:
[`references/lean4-contraction-catalog.md`](../../references/lean4-contraction-catalog.md)
(§5 Lyapunov direct method, §6 Project Lyapunov-function inventory).
This section keeps only the dispatch-relevant *taxonomy* — actual
proof patterns live in the catalog.

| Module | Lyapunov function (one-liner) |
|---|---|
| LyapunovStability | Quadratic `V(q) = (q - q*)²` |
| LyapunovStability | Cusp energy `E(x;a,b)` |
| AgenticSafety | Trust distance `|t - t*|` |
| ReinforcementLearning | Bellman residual `‖V - V*‖` |
| StochasticCCV | L¹ distance to stationary |

---

## Part 3 — Bifurcation and Catastrophe Theory

### 3.1 The Cusp Catastrophe

the project's `CuspCatastrophe` module formalizes the cusp:

- **Module size:** 978 lines / 64 theorems
- **Key theorems:** `asymmetric_three_roots_ivt` (IVT sign-change for a=-3, b=1), `fold_curve_iff_discriminant_zero`
- **Lattice:** `FullRegime` obtains `LinearOrder` via `inferInstance`

```
Potential: V(x; a, b) = x⁴/4 + ax²/2 + bx
Equilibria: dV/dx = x³ + ax + b = 0
Discriminant: Δ = -4a³ - 27b²
  Δ > 0 → three real roots (bistable)
  Δ = 0 → degenerate (fold lines / bifurcation set)
  Δ < 0 → one real root (monostable)
```

### 3.2 Formalization Strategy

```lean
-- Cusp potential
noncomputable def cuspV (x a b : ℝ) : ℝ := x^4/4 + a*x^2/2 + b*x

-- Derivative (equilibrium condition)
theorem cusp_deriv : HasDerivAt (cuspV · a b) (x^3 + a*x + b) x := by
  -- decompose into polynomial derivative + ring

-- Discriminant classification
def cuspDiscriminant (a b : ℝ) : ℝ := -4*a^3 - 27*b^2

-- Regime theorem
theorem cusp_bistable (ha : a < 0) (hΔ : 0 < cuspDiscriminant a b) :
    ∃ x₁ x₂ x₃ : ℝ, x₁ < x₂ ∧ x₂ < x₃ ∧
      cuspV' x₁ a b = 0 ∧ cuspV' x₂ a b = 0 ∧ cuspV' x₃ a b = 0 := by
  -- cubic root analysis
  sorry -- research-level
```

### 3.3 Bifurcation Types

| Bifurcation | Normal form | Project relevance | Formalization status |
|---|---|---|---|
| Saddle-node | `ẋ = r + x²` | Phase transitions at thresholds | Routine (quadratic) |
| Transcritical | `ẋ = rx - x²` | Quality gate activation | Routine |
| Pitchfork | `ẋ = rx - x³` | Symmetry breaking | Moderate |
| **Cusp** | `V = x⁴/4 + ax²/2 + bx` | **CuspCatastrophe module** | Hard (cubic roots) |
| Hopf | `ż = (μ + i)z - z|z|²` | (Not in current Project) | Research-level |

### 3.4 Fold Curve

The fold curve is `{(a,b) : 4a³ + 27b² = 0}` — the boundary between mono- and bistable regimes.

```lean
-- In the project discrete model:
noncomputable def cuspDiscriminantR (a b : ℝ) : ℝ := -4 * a^3 - 27 * b^2

-- Fold curve = bifurcation set = discriminant zero set:
theorem fold_curve_iff_discriminant_zero (a b : ℝ) :
    classifyCuspRegime a b = .bifurcation ↔ cuspDiscriminantR a b = 0 := by
  simp [classifyCuspRegime, cuspDiscriminantR]

-- Bistable iff discriminant > 0:
-- classifyCuspRegime a b = .bistable ↔ cuspDiscriminantR a b > 0
```

---

## Part 4 — Phase Space Analysis

### 4.1 Phase Portrait Formalization

the project's `PhasePortrait` module represents state space trajectories:

```lean
-- State space as a product type
structure PhaseState where
  quality : ℕ      -- quality score (×100)
  phase : PhaseType  -- {stable, transition, chaotic, collapse}
  tks : ℕ          -- TKS score (×100)

-- Trajectory: sequence of states
def trajectory (f : PhaseState → PhaseState) (x₀ : PhaseState) : ℕ → PhaseState
  | 0 => x₀
  | n + 1 => f (trajectory f x₀ n)

-- Invariant set: a set S is invariant under f if f(S) ⊆ S
def Invariant (f : α → α) (S : Set α) : Prop := ∀ x ∈ S, f x ∈ S
```

### 4.2 Attractor Analysis

```lean
-- Attractor: invariant set that "attracts" nearby points
-- In Project: stable equilibria are point attractors
-- The trust simplex has an attractor at the target allocation

-- Omega-limit set: ω(x) = ∩_{n≥0} closure(orbit from n onward)
-- Formal definition uses Filter.atTop
```

### 4.3 Basins of Attraction

```lean
-- Basin of attraction for an equilibrium x*:
-- { x₀ | trajectory f x₀ n → x* as n → ∞ }

-- Project: each phase regime has a basin
-- Phase boundaries are separatrices between basins
-- Cusp catastrophe creates hysteresis in basin boundaries
```

---

## Part 5 — Control Theory Connections

### 5.1 Project as a Control System

| Control concept | Project interpretation | Module |
|---|---|---|
| Plant | Knowledge externalization pipeline | PipelineAdaptive |
| Controller | Quality gates + adaptive parameters | QualityGates |
| Feedback | CCV scores → parameter adjustment | CCVGating |
| Reference signal | Target quality thresholds | QualityGates |
| Disturbance | Cognitive load, stress, time pressure | PhasePortrait |
| Stability | Convergence to quality targets | LyapunovStability |

### 5.2 Controllability and Observability

```lean
-- Not explicitly formalized in the project, but conceptually:
-- Controllability: can we reach any quality state from any initial state?
-- Observability: can we infer the phase from quality gate outputs?
-- the project's design ensures both through its 5-stage pipeline.
```

---

## Part 6 — Nonlinear Methods Toolbox

### 6.1 Perturbation Methods

When exact solutions don't exist, use:
- **Linearization** around equilibria (Jacobian → eigenvalues)
- **Series expansion** (Taylor, asymptotic)
- **Averaging** (for oscillatory systems)

### 6.2 Comparison Principles

```lean
-- If V(f(x)) ≤ g(V(x)) and we know g's behavior, transfer to V:
-- Key: comparison_of_eventually_le (Mathlib filters)

-- Project pattern:
-- V(x_{n+1}) ≤ α * V(x_n) with α < 1
-- → V(x_n) ≤ α^n * V(x_0)
-- → V(x_n) → 0 as n → ∞
```

### 6.3 Energy Methods

```lean
-- Lyapunov function = "energy" that decreases along trajectories
-- Energy methods unify stability proofs across Project modules:
-- - Quadratic energy for linear contraction
-- - Polynomial energy for cusp
-- - Norm energy for RL value iteration
-- - Entropy/KL for stochastic convergence
```

---

---

## Inline Pitfalls & Recovery Recipes (from `skills/lean-math-dynamical/SKILL.md`)

# Lean 4 Nonlinear Dynamics & Stability

Guide to formalizing dynamical systems, stability theory, and bifurcation in Lean 4.

## Routing

- **USE FOR:** nonlinear dynamical systems, Lyapunov stability, bifurcation theory, catastrophe theory, control theory, phase-portrait analysis, attractor
  classification, and any deterministic system with state evolution over time in Lean 4.
- **DO NOT USE FOR:** stochastic dynamics (delegate to `@lean-math-stochastic`); pure analysis / topology (delegate to `@lean-math-analysis`);
  optimization-only control problems (delegate to `@lean-math-optimization`); writing one specific proof (delegate to `@lean-proof`).
- **TRIGGERS:** Lyapunov, stability, bifurcation, cusp catastrophe, attractor, phase portrait, dynamical system, control theory, equilibrium.

## Workflow

1. Classify the system (Part 1) — discrete-time, continuous-time, gradient, conservative, controlled.
2. Pick the appropriate technique below (Lyapunov, contraction, bifurcation-normal-form, catastrophe-classification).
3. Handoff to `@lean-proof` for the concrete proof; if it bottoms out in a derivative / measure step, handoff to `@lean-math-analysis`.

## Recovery & STOP

- STOP if the proof depends on a manifold or smooth-structure API not in Mathlib at the current pin — escalate to `@lean-research`.
- STOP if a stochastic perturbation enters the model — re-route to `@lean-math-stochastic`; this skill covers only deterministic dynamics.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-proof` (mid-proof stability goal), `skill:lean-research` (catastrophe-theory result survey).
- **Successors:** `skill:lean-proof` (apply the dynamical pattern), `skill:lean-proof-review` (audit Lyapunov candidate), `skill:lean-math-analysis`
  (continuous-derivative or contraction reduction).

## Detailed reference

Full encyclopaedia content (Parts 1 through 6) lives in
[`references/lean4-math-dynamical.md`](../../references/lean4-math-dynamical.md). Load that file
when authoring; the SKILL.md only carries the dispatch contract and
the high-frequency pitfalls / recipes (kept inline below).

| Part | Topic | Covers |
|---|---|---|
| Part 1 | Dynamical Systems Taxonomy | discrete-time, continuous-time, gradient, conservative, controlled |
| Part 2 | Lyapunov Stability Theory | candidate construction, positive-definiteness, LaSalle |
| Part 3 | Bifurcation and Catastrophe Theory | cusp / fold / pitchfork normal forms |
| Part 4 | Phase Space Analysis | phase portraits, equilibria classification |
| Part 5 | Control Theory Connections | Lyapunov-control, control-Lyapunov functions |
| Part 6 | Nonlinear Methods Toolbox | linearisation, normal-form reduction, numerical-continuation hints |

## Part 7 — Research Council Integration

Consolidated into the single canonical routing matrix:
[`references/research-council-skill-map.md`](../../references/research-council-skill-map.md)
(see the "Dynamical" section).  When dispatching a question to a
council member, cite that table rather than restating the rows here.

---

## Part 8 — IVT Sign-Change Pattern

Extracted to single canonical reference:
[`references/lean4-ivt-patterns.md`](../../references/lean4-ivt-patterns.md).
That file owns the canonical incantation, the
`asymmetric_three_roots_ivt` walk-through, and the polynomial-continuity
prerequisite.

---

## Part 9 — Common Pitfalls (Stability & Bifurcation)

| Pitfall | Symptom | Recovery |
|---|---|---|
| Lyapunov candidate not positive-definite | `V 0 = 0` proved, but `V x > 0` for `x ≠ 0` fails | Add a quadratic-form witness (`x^T Q x` with `Q` PSD); check `posDef_iff_eigenvalues_pos` family |
| Contraction map without `[CompleteSpace α]` | `ContractingWith.fixedPoint` won't apply | Add `[CompleteSpace α]` instance or restrict to a closed subset and use `IsCompact.completeSpace` |
| IVT sign-error in bifurcation diagram | Existential `∃ c, f c = 0` won't close | Re-check sign of `f a` and `f b`; see `references/lean4-ivt-patterns.md` for the canonical `asymmetric_three_roots_ivt` walk-through |
| Catastrophe normal form drifted from repository canon | `cusp` / `fold` polynomial signs don't match expectations | Compare against `Mathlib.Analysis.SpecialFunctions.Pow.Real`; there is *no* canonical catastrophe API in Mathlib — keep local definitions in the host repository's catastrophe namespace |
| Discrete- vs continuous-time confusion | `Tendsto` with the wrong filter | Discrete: `atTop` on `ℕ`; continuous: `atTop` on `ℝ` (often with a measure-preserving step) |
| Spurious equilibrium from `simp` overreach | `f x = x` "proved" by simplifying both sides to `0` | Disable `simp` for the candidate equilibrium proof; use `linear_combination` or explicit substitution |

### Cross-reference: repository stability tactics

- Host-repository Lyapunov modules — quadratic-form Lyapunov constructions for local cusp + phase-portrait models.
- Host-repository catastrophe modules — cusp-form polynomial bifurcation (the 3-real-roots case).
- [`references/lean4-ivt-patterns.md`](../../references/lean4-ivt-patterns.md) — `asymmetric_three_roots_ivt` walk-through (canonical entry-point for
  sign-change existence).
- [`references/lean4-contraction-catalog.md`](../../references/lean4-contraction-catalog.md) — catalog of contraction-mapping templates (uses
  `ContractingWith` / `LipschitzWith`).

---

## Part 10 — Banach Fixed-Point Recipe

The most common "I need a fixed point" pattern in this corpus:

```lean
-- Given a self-map f : α → α and a contraction constant K < 1:
example {α : Type*} [MetricSpace α] [CompleteSpace α]
    (f : α → α) {K : NNReal} (hK : K < 1)
    (hC : ContractingWith K f) :
    ∃! x, f x = x :=
  ⟨hC.fixedPoint, hC.fixedPoint_isFixedPt,
   fun y hy => hC.fixedPoint_unique hy⟩
```

Project-relevant adaptations:

- **Sub-Banach setting:** `IsCompact.completeSpace` lets you restrict to a closed ball when global completeness is unwieldy.
- **Iteration bounds:** `ContractingWith.aux_dist_le` gives `dist (f^[n] x) (fixedPoint) ≤ K^n * dist x (fixedPoint) / (1 - K)`.
- **Existence-only (no uniqueness):** Schauder fixed-point — *not* in Mathlib at the current pin; use `@lean-research` to confirm before authoring.

---

## See also

- [`../../references/lean4-math-dynamical.md`](../../references/lean4-math-dynamical.md) — Nonlinear Dynamics Encyclopaedia (full encyclopaedia, extracted
  from this skill)
- [`../../templates/Template_Dynamics.md`](../../templates/Template_Dynamics.md) — Template: Lyapunov / Markov / contraction mappings
- [`../../references/lean4-proof-strategy.md`](../../references/lean4-proof-strategy.md) — Proof strategy: real-valued contraction patterns

---

## Merged Domain Companion: `lean-math-dynamical` (Unified into `@lean-math-dynamical`)

# General Nonlinear Dynamics & Catastrophe Theory

Comprehensive mathematical methodology for nonlinear dynamics — the theoretical backbone of phase portraits, catastrophe models, Lyapunov stability, and
governance convergence modules.

---

## Routing

- **USE FOR:** General nonlinear dynamics, chaos theory, bifurcation analysis, catastrophe theory, attractor geometry, Lyapunov methods, phase portraits,
  and control-theoretic stability. Use for any mathematical reasoning about dynamical systems BEFORE or BEYOND Lean formalization. Covers theory,
  intuition, calculation techniques, and connections to phase portraits, catastrophe models, and governance dynamics.
- **DO NOT USE FOR:** Lean proofs in this domain (use @lean-math-dynamical); optimization theory (use @lean-math-optimization); topology methods (use
  @lean-math-analysis).
- **TRIGGERS:** nonlinear dynamics, chaos theory, bifurcation, catastrophe theory, attractor, Lyapunov, phase portrait.

## Workflow

1. Classify the system: ODE / PDE / map / SDE / hybrid; identify the phase-space and invariants.
2. Pick the matching section (Lyapunov / bifurcation / catastrophe / chaos / control).
3. Produce the answer with explicit assumptions + regularity; cite the Mathlib namespace if applicable.
4. Hand off: to `@lean-math-dynamical` for the Lean proof, to `@lean-math-optimization` if control becomes optimal-control, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the question is about optimisation (not dynamics) — delegate to `@lean-math-optimization`.
- STOP if topological tools dominate — delegate to `@lean-math-analysis`.
- STOP if Mathlib lacks the needed lemma — escalate to `@lean-research`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-math-dynamical`, `skill:lean-research`, `skill:lean-zettelkasten`.

---

## Detailed reference

Full content for `lean-math-dynamical` lives in
[`references/lean-math-dynamical-handbook.md`](../../references/lean-math-dynamical-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

| Section | Topic |
|---|---|
| Part 1 | Core Mathematical Framework |
| Part 2 | Bifurcation Analysis Methodology |
| Part 3 | Lyapunov Function Construction |
| Part 4 | Phase Portrait Analysis |
| Part 5 | Control-Theoretic Perspective |
| Part 6 | Connections to Other Mathematical Disciplines |
| Part 7 | Research Entry Points |

---

## See also

- [`../../references/lean-math-dynamical-handbook.md`](../../references/lean-math-dynamical-handbook.md) — Full handbook (extracted from this skill)
- [`../lean-math-dynamical/SKILL.md`](../lean-math-dynamical/SKILL.md) — Successor
- [`../lean-research/SKILL.md`](../lean-research/SKILL.md) — Successor
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor

# Math Nonlinear Dynamics Handbook

> **Layering note.** This file holds the deep content previously
> embedded in [`skills/lean-math-dynamical/SKILL.md`](../skills/lean-math-dynamical/SKILL.md).
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

---
## Goal-Shape Templates (templates)

| Goal Shape | Target Typeclass / Lemma | Proof Template |
| :--- | :--- | :--- |
| `V (step s) ≤ V s` (Discrete Lyapunov) | `linarith` / `nlinarith` / `omega` | `unfold V step; nlinarith [sq_nonneg ...]` |
| `∀ n, Inv (step^[n] s₀)` | `Nat.rec` / `Function.Iterate.rec` | `induction n with \| zero => exact h0 \| succ n ih => exact h_step _ ih` |
| `V (step^[n] s₀) ≤ V s₀` | Monotone trajectory induction | `induction n with \| zero => rfl \| succ n ih => exact le_trans (h_dec _) ih` |
| Cusp catastrophe equilibrium `4 x³ + 2 a x + b = 0` | Polynomial discriminant / `ring` | `nlinarith` / `ring` |

## Intent-to-Tactic Phrasebook (phrasebook)

| Mathematical Intent | Lean 4 / Mathlib Tactic | Notes |
| :--- | :--- | :--- |
| Prove non-negativity of quadratic Lyapunov energy | `positivity` | Handles sums of squares `x^2 + y^2 >= 0` |
| Prove single-step Lyapunov decrease `V(f(x)) - V(x) <= 0` | `nlinarith [sq_nonneg (x - x_eq)]` | Pass explicit square witnesses to `nlinarith` |
| Unfold `n`-step iterate `f^[n + 1] x` | `rw [Function.iterate_succ_apply']` | Rewrites `f^[n+1] x` to `f (f^[n] x)` for inductive step |
| Discharge discrete scaled-integer barrier certificate | `omega` | Ensure all `Nat.sub` terms have `b <= a` guards |

## Error-to-Fix Table (errors)

| Error / Symptom | Root Cause | Fix |
| :--- | :--- | :--- |
| `Function.iterate_succ_apply`Associativity mismatch | `f^[n+1] x = f^[n] (f x)` vs `f (f^[n] x)` | Use `Function.iterate_succ_apply'` (primed) to put `f` on the outside |
| `nlinarith` fails on cubic/quartic potential | `nlinarith` only multiplies two existing inequalities | Factor into squares via `have : ... = (x^2 - a)^2 := by ring` + `positivity` |
| Vacuous stability from `Nat.sub` truncation | `V : S → Nat` truncates `V(s') - V(s)` at `0` | Write decrease as `V (step s) + δ ≤ V s` instead of `V s - V (step s) ≥ δ` |
