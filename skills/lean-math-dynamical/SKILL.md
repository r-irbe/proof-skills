---
name: lean-math-dynamical
description: Nonlinear dynamical systems, Lyapunov stability, bifurcation theory, catastrophe theory, and control theory in Lean 4. Use when formalizing stability proofs, Lyapunov functions, phase portraits, cusp catastrophes, attractor analysis, or any system with state evolution over time. Core skill for the project's Lyapunov, CuspCatastrophe, PhasePortrait, and stability-related modules.
---

# Lean 4 Nonlinear Dynamics & Stability

Guide to formalizing dynamical systems, stability theory, and bifurcation in Lean 4.

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

### 2.1 Lyapunov's Direct Method

For a system `x_{n+1} = f(x_n)` with equilibrium `x* = 0`:

1. **Find** a Lyapunov function `V : State → ℝ` such that:
   - `V(0) = 0`
   - `V(x) > 0` for `x ≠ 0`
   - `V(f(x)) - V(x) ≤ 0` (stability) or `< 0` (asymptotic stability)
   - `V(f(x)) ≤ c * V(x)` with `c < 1` (exponential stability)

2. **Formalize** in Lean:

```lean
-- Lyapunov function structure
structure LyapunovFn (State : Type) where
  V : State → ℝ
  V_nonneg : ∀ x, 0 ≤ V x
  V_zero : V equilibrium = 0
  V_pos : ∀ x, x ≠ equilibrium → 0 < V x
  V_decrease : ∀ x, V (f x) ≤ V x  -- stability
  -- or: V_contract : ∃ c < 1, ∀ x, V (f x) ≤ c * V x  -- exponential

-- Proving V_nonneg for quadratic V(x) = x²:
-- Use: sq_nonneg, mul_self_nonneg  (proj_lyapunov is DEPRECATED — 0 uses; use positivity + nlinarith directly)
```

### 2.2 Project Lyapunov Patterns

| Module | Lyapunov function | Key property | Proof technique |
|---|---|---|---|
| LyapunovStability | `V(q) = (q - q*)²` | Quadratic, `V ≥ 0` | `sq_nonneg` + `nlinarith` |
| LyapunovStability | Cusp energy `E(x;a,b)` | Critical point analysis | `HasDerivAt` + calculus |
| AgenticSafety | Trust distance `|t - t*|` | Contraction by `α` | `abs_mul` + geometric decay |
| ReinforcementLearning | Bellman residual `‖V - V*‖` | Contraction by `γ` | Banach fixed point |
| StochasticCCV | L¹ distance to stationary | Spectral gap decay | Matrix analysis |

### 2.3 The `proj_lyapunov` Tactic **(DEPRECATED — 0 cross-module uses)**

~~Custom Project tactic in `Tactics.lean` for non-negativity goals.~~
Use the underlying tactics directly instead:

```lean
-- Replace proj_lyapunov with:
-- 1. positivity           (for 0 ≤ e goals)
-- 2. nlinarith [sq_nonneg x, ...]   (for quadratic bounds)
-- 3. ring                (for algebraic identities)
-- 4. norm_num            (for numeric evaluations)

-- Use for: V(x) ≥ 0, V(f(x)) ≤ V(x), contraction factor bounds
```

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

| Dynamical Systems Topic | Research Council Member |
|---|---|
| Lyapunov function construction | Γ (Methods Scholar) + Δ (Bounds Analyst) |
| Bifurcation classification | Β (Structure Strategist) |
| Cusp catastrophe analysis | Γ (Methods Scholar) + literature search |
| Phase portrait topology | Β (Structure Strategist) |
| Contraction factor computation | Δ (Bounds Analyst) |
| Stability margin estimation | Δ (Bounds Analyst) |
| Nonlinear tactic selection | Γ (Methods Scholar) |
| Control-theoretic formulation | Ε (Applications Bridge) |

---

## Part 8 — IVT Sign-Change Pattern

### 8.1 Equilibrium Existence via IVT

For proving equilibria exist in Lean 4 / Mathlib:

```lean
-- Import: Mathlib.Topology.Order.IntermediateValue
-- Key theorem: IsPreconnected.intermediate_value₂ (for f vs g = const pattern)

-- For continuous f : ℝ → ℝ with f a ≤ 0 ≤ f b  (with hab : a ≤ b):
isPreconnected_Icc.intermediate_value₂
  (left_mem_Icc.mpr hab) (right_mem_Icc.mpr hab)
  hf.continuousOn continuous_const.continuousOn
  (le_of_lt ha) (le_of_lt hb)
-- → ∃ c ∈ Set.Icc a b, f c = 0

-- Alternative (gives Set inclusion form):
-- intermediate_value_Icc hab hf :
--   Set.Icc (f a) (f b) ⊆ f '' Set.Icc a b
```

### 8.2 Project application: `asymmetric_three_roots_ivt`

```lean
-- CuspCatastrophe: IVT sign-change for a = -3, b = 1
-- Proves three distinct real roots of x³ - 3x + 1 = 0
-- Sign analysis constructs the three intervals:
--   f(-2) = -8 + 6 + 1 = -1 < 0
--   f(-1) = -1 + 3 + 1 =  3 > 0  → root in (-2, -1)
--   f( 0) =           1 > 0
--   f( 1) = 1 - 3 + 1 = -1 < 0   → root in (0, 1)
--   f( 2) = 8 - 6 + 1 =  3 > 0   → root in (1, 2)
```

### 8.3 Polynomial Continuity

```lean
-- For polynomial f: Continuous by fun_prop after unfold
example (a b : ℝ) : Continuous (fun x : ℝ => x^3 + a*x + b) := by fun_prop

-- Or manually: continuous_pow + Continuous.mul + Continuous.add
```

---

## See also

- [`../../templates/Template_Dynamics.md`](../../templates/Template_Dynamics.md) — Template: Lyapunov / Markov / contraction mappings
- [`../../references/lean4-proof-strategy.md`](../../references/lean4-proof-strategy.md) — Proof strategy: real-valued contraction patterns
