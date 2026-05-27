---
name: "lean-math-dynamical"
description: |
  USE FOR: nonlinear dynamical systems, Lyapunov stability, bifurcation theory, catastrophe theory, control theory, phase-portrait analysis, attractor classification, and any deterministic system with state evolution over time in Lean 4.
  DO NOT USE FOR: stochastic dynamics (use @lean-math-stochastic); pure analysis / topology (use @lean-math-analysis); optimization-only control problems (use @lean-math-optimization); writing one specific proof (use @lean-proof).
  TRIGGERS: Lyapunov, stability, bifurcation, cusp catastrophe, attractor, phase portrait, dynamical system, control theory, equilibrium.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-proof", "skill:lean-research"]
  successors: ["skill:lean-proof", "skill:lean-proof-review", "skill:lean-math-analysis"]
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-math-dynamical/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Lean 4 Nonlinear Dynamics & Stability

Guide to formalizing dynamical systems, stability theory, and bifurcation in Lean 4.

## Routing

- **USE FOR:** nonlinear dynamical systems, Lyapunov stability, bifurcation theory, catastrophe theory, control theory, phase-portrait analysis, attractor classification, and any deterministic system with state evolution over time in Lean 4.
- **DO NOT USE FOR:** stochastic dynamics (delegate to `@lean-math-stochastic`); pure analysis / topology (delegate to `@lean-math-analysis`); optimization-only control problems (delegate to `@lean-math-optimization`); writing one specific proof (delegate to `@lean-proof`).
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
- **Successors:** `skill:lean-proof` (apply the dynamical pattern), `skill:lean-proof-review` (audit Lyapunov candidate), `skill:lean-math-analysis` (continuous-derivative or contraction reduction).

---

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
| Catastrophe normal form drifted from project canon | `cusp` / `fold` polynomial signs don't match expectations | Compare against `Mathlib.Analysis.SpecialFunctions.Pow.Real`; there is *no* canonical catastrophe API in Mathlib — keep local definitions in `EASCI.CuspCatastrophe.*` |
| Discrete- vs continuous-time confusion | `Tendsto` with the wrong filter | Discrete: `atTop` on `ℕ`; continuous: `atTop` on `ℝ` (often with a measure-preserving step) |
| Spurious equilibrium from `simp` overreach | `f x = x` "proved" by simplifying both sides to `0` | Disable `simp` for the candidate equilibrium proof; use `linear_combination` or explicit substitution |

### Cross-reference: EASCI stability tactics

- `EASCI.Lyapunov.*` — quadratic-form Lyapunov constructions for the project's cusp + phase-portrait models.
- `EASCI.CuspCatastrophe.*` — cusp-form polynomial bifurcation (the 3-real-roots case).
- [`references/lean4-ivt-patterns.md`](../../references/lean4-ivt-patterns.md) — `asymmetric_three_roots_ivt` walk-through (canonical entry-point for sign-change existence).
- [`references/lean4-contraction-catalog.md`](../../references/lean4-contraction-catalog.md) — catalog of contraction-mapping templates (uses `ContractingWith` / `LipschitzWith`).

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

- [`../../templates/Template_Dynamics.md`](../../templates/Template_Dynamics.md) — Template: Lyapunov / Markov / contraction mappings
- [`../../references/lean4-proof-strategy.md`](../../references/lean4-proof-strategy.md) — Proof strategy: real-valued contraction patterns
