---
title: "Contraction & Banach fixed-point catalog (Lean 4 / Mathlib)"
status: reference
source: extracted from `lean-math-analysis §4.2 + §8.3`, `lean-math-dynamical §Part 2`, `lean-math-foundations §4.3`, `lean-math-optimization §3.2`, `lean-ai-formalization §2.3`
owners: lean-math-convergence (primary), lean-math-optimization, lean-ai-formalization
date: 2026-05-27
---

# Contraction & Banach fixed-point catalog

Single canonical reference for every place a Lean 4 + Mathlib4 project
reasons about **contraction maps**: the `ContractingWith` bundle, the
Banach fixed-point theorem, geometric decay from a contraction factor,
and the inventory of host-repository contraction theorems.  All consumer
skills (analysis, dynamical, optimization, AI safety) link here.

## 1. Mathlib API entry-points

```lean
import Mathlib.Topology.MetricSpace.Contracting

-- ContractingWith K f : Prop
-- where K : ℝ≥0, K < 1, dist (f x) (f y) ≤ K * dist x y

-- Fixed point existence + uniqueness:
-- ContractingWith.fixedPoint  (complete metric space required)
-- ContractingWith.tendsto_iterate_fixedPoint  → convergence to fixed point

-- For lattice-side (Knaster-Tarski):
import Mathlib.Order.FixedPoints
-- CompleteLattice.fixedPoint_lfp, CompleteLattice.fixedPoint_gfp
```

## 2. Geometric decay from a contraction factor

The bread-and-butter lemma: if a process satisfies
`‖x_{n+1} - x*‖ ≤ α · ‖x_n - x*‖` with `0 ≤ α < 1`, then
`‖x_n - x*‖ ≤ α^n · ‖x_0 - x*‖ → 0`.

```lean
theorem convergence_from_contraction (hα : α < 1) (hα0 : 0 ≤ α) :
    Filter.Tendsto (fun n => α^n * d₀) Filter.atTop (nhds 0) :=
  (tendsto_pow_atTop_nhds_zero_of_lt_one hα0 hα).const_mul d₀ |>.congr
    (fun n => (mul_comm _ _))
```

Key Mathlib lemma: `tendsto_pow_atTop_nhds_zero_of_lt_one`.
Adjacent: `tendsto_pow_atTop_nhds_zero_of_norm_lt_one` (normed case).

## 3. Project pattern — affine trust contraction

```lean
theorem trust_contraction (α : ℝ) (hα : 0 ≤ α) (hα1 : α < 1)
    (target : ℝ) (x : ℝ) :
    |α * x + (1 - α) * target - target| = α * |x - target| := by
  ring_nf
  rw [abs_mul, abs_of_nonneg hα]
```

This pattern recurs whenever an iteration is convex-combination of a
state and a fixed target.  The right-hand side is exactly the geometric
decay setup from §2.

## 4. Project contraction theorem index

| Theorem | Location | Description |
|---|---|---|
| `trust_L1_contraction` | `AgenticSafety.lean` | L¹ trust contraction bound |
| `trust_L1_exact` | `AgenticSafety.lean` (line 2075) | Exact L¹ trust equality |
| `okdStep_L1_contraction` | `StochasticCCV.lean` | L¹ contraction for OKD step |
| `ContractingWith.fixedPoint` | Mathlib | Banach fixed point (complete metric space) |
| `BellmanOperator.contracting` | `ReinforcementLearning.lean` | Bellman operator is `γ`-contraction |

## 5. Lyapunov direct method (the discrete-time bridge)

For `x_{n+1} = f(x_n)` with equilibrium `x* = 0`:

1. **Find** a Lyapunov function `V : State → ℝ` with:
   - `V(0) = 0`
   - `V(x) > 0` for `x ≠ 0`
   - `V(f(x)) - V(x) ≤ 0` (stability) or `< 0` (asymptotic stability)
   - `V(f(x)) ≤ c · V(x)` with `c < 1` (exponential stability)

2. **Formalize**:

```lean
structure LyapunovFn (State : Type) where
  V : State → ℝ
  V_nonneg : ∀ x, 0 ≤ V x
  V_zero : V equilibrium = 0
  V_pos : ∀ x, x ≠ equilibrium → 0 < V x
  V_decrease : ∀ x, V (f x) ≤ V x
  -- or: V_contract : ∃ c < 1, ∀ x, V (f x) ≤ c * V x
```

For `V(x) = x²` non-negativity, use `sq_nonneg`, `mul_self_nonneg`, or
`positivity`.  The deprecated `proj_lyapunov` tactic is gone — use the
underlying tactics (`positivity`, `nlinarith [sq_nonneg x, …]`, `ring`,
`norm_num`) directly.

## 6. Project Lyapunov-function inventory

| Module | Lyapunov function | Key property | Proof technique |
|---|---|---|---|
| LyapunovStability | `V(q) = (q - q*)²` | Quadratic, `V ≥ 0` | `sq_nonneg` + `nlinarith` |
| LyapunovStability | Cusp energy `E(x;a,b)` | Critical-point analysis | `HasDerivAt` + calculus |
| AgenticSafety | Trust distance `|t - t*|` | Contraction by `α` | `abs_mul` + geometric decay |
| ReinforcementLearning | Bellman residual `‖V - V*‖` | Contraction by `γ` | Banach fixed point |
| StochasticCCV | L¹ distance to stationary | Spectral-gap decay | Matrix analysis |

## 7. Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Missing `CompleteSpace` | `ContractingWith.fixedPoint` won't apply | Add hypothesis or use `instCompleteSpaceReal` |
| `ℝ` vs `ℝ≥0` confusion | type mismatch on the contraction factor | Use `.toReal` or `NNReal.coe_*` lemmas |
| Trying `apply ContractingWith.fixedPoint` cold | "could not synthesise instance" | Bundle the `ContractingWith` first, then `apply` |
| Geometric-decay forgotten | `Tendsto` proof loops | Use `tendsto_pow_atTop_nhds_zero_of_lt_one` directly |

## 8. Where the contraction block was duplicated before this extraction

| Location | Lines (pre-extraction) |
|---|---|
| `lean-math-foundations §4.3` | ~12 |
| `lean-math-analysis §4.2 + §8.3` | ~35 |
| `lean-math-dynamical §Part 2` | ~55 |
| `lean-math-optimization §3.2` | ~25 |
| `lean-ai-formalization §2.3` | ~10 |

All five now `See also`-link this file.
