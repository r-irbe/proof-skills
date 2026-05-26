---
title: "Time-series patterns (Lean 4 / Mathlib4)"
status: reference
source: extracted from `lean-math-stochastic §Part 4`
owners: lean-math-stochastic, future EWS work
date: 2026-05-27
---

# Time-series patterns

Reference material for formalising **discrete-time series** in Lean 4 /
Mathlib4: stationarity, autocorrelation, ARMA-style recursions, trend
and change-point detection, and the project EWS (exponential warning
system) family.  Extracted from the slim of `lean-math-stochastic`.

## 1. Formalisation approaches

| Time-series concept | Mathematical framework | Lean formalisation |
|---|---|---|
| Stationarity | Shift-invariant distribution | `∀ k, dist(X_{n+k}) = dist(X_n)` |
| Autocorrelation | `R(k) = E[(X_n - μ)(X_{n+k} - μ)]` | Integral definition over the product measure |
| ARMA model | `X_t = Σ φᵢ X_{t-i} + Σ θⱼ ε_{t-j} + ε_t` | Recursive `def` on `ℕ → ℝ` |
| Trend detection | Monotone-component extraction | `Monotone (trend ∘ proj)` |
| Change point | Distribution shift at time τ | `∃ τ, ∀ n < τ, dist_1 ∧ ∀ n ≥ τ, dist_2` |
| Spectral density | Fourier transform of autocorrelation | Advanced — Mathlib partial coverage |

## 2. Project connections

| Project concept | Time-series aspect |
|---|---|
| Quality-score evolution | Discrete time series `{q_n}` |
| Phase transitions | Change-point detection on quality |
| CCV dynamics | Multivariate time series on the simplex |
| Alert severity | Ordinal time series with regime switches |
| Pipeline throughput | Count process with learning effects |
| Stress indicators | Bounded time series with Lyapunov decay |

## 3. Exponential smoothing (EWS canonical recurrence)

The project EWS uses single-exponential smoothing
`S_n = α · X_n + (1 - α) · S_{n-1}`:

```lean
def ewma (α : ℝ) (x : ℕ → ℝ) : ℕ → ℝ
  | 0     => x 0
  | n + 1 => α * x (n + 1) + (1 - α) * ewma α x n
```

### 3.1 Properties worth proving

1. **Convergence under convergent input.**
   If `x_n → L` then `ewma α x n → L` for `0 < α ≤ 1`.

2. **Contraction toward recent values.**
   Use the convex-combination contraction pattern from
   `references/lean4-contraction-catalog.md §3`.

3. **Lag-bias tradeoff.**
   Smaller `α` → more smoothing, larger lag.  Quantify via:
   `expected lag ≈ (1 - α) / α` (geometric-mean argument).

### 3.2 Proof sketch — convergence

```lean
-- Sketch: ewma is a convex combination, so
-- |ewma α x (n+1) - L| ≤ α · |x (n+1) - L| + (1 - α) · |ewma α x n - L|
-- The first term → 0 by hypothesis; the second is a contraction
-- with factor (1 - α) < 1 (for α > 0).
-- Apply geometric-decay + cesaro-like argument.
```

## 4. Beyond EWS — double/triple exponential smoothing

For completeness (not currently used in EASCI):

- **Holt's linear** : tracks level `S` + slope `B` separately;
  `S_n = α X_n + (1 - α)(S_{n-1} + B_{n-1})`.
- **Holt-Winters** : adds a periodic component `C_n`.

These are easy `def` extensions; convergence proofs become harder
because the slope iterate is no longer a single-factor contraction.

## 5. Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| `α = 0` makes EWS constant | `ewma 0 x n = x 0` always | Require `0 < α` in convergence lemmas |
| `α = 1` makes EWS noisy | `ewma 1 x n = x n` always | Same: bound `α` strictly below `1` |
| Off-by-one in time index | `x (n + 1)` vs `x n` mismatch | Stay with the `Nat.rec`-shaped def |
| ARMA recursion on `Int` | sign-flip / cast hassles | Stay on `ℕ` indices; cast values only |

## 6. See also

- `references/lean4-contraction-catalog.md` — the convex-combination
  contraction lemma reused by §3.1.
- `references/lean4-ergodic-theory.md` — the long-run-average twin of
  this file (ergodicity ↔ time-average = space-average).
- `Template_Probability.md` — broader probability-module starter.
