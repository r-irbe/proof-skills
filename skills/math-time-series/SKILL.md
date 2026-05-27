---
name: math-time-series
description: |
  USE FOR: Time series analysis, signal processing, temporal pattern detection, and multi-scale temporal dynamics. Use for mathematical reasoning about time-varying data, smoothing, derivative estimation, spectral analysis, changepoint detection, and the temporal aspects of the project's knowledge trajectory computation. Covers both theory and computational methodology.
  DO NOT USE FOR: measure-theoretic / probabilistic basis (use @math-measure-probability); Lean proofs (use @lean-math-stochastic); nonlinear dynamics (use @math-nonlinear-dynamics).
  TRIGGERS: time series, signal processing, temporal pattern, multi-scale temporal, spectral analysis.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-math-stochastic', 'skill:math-measure-probability', 'skill:lean-zettelkasten']
metadata:
  version: "0.2.0"
  source_spec: "skills/math-time-series/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Time Series Analysis & Temporal Mathematics

Comprehensive methodology for temporal mathematics — the computational backbone of the project's phase trajectory computation, early warning signal detection, and multi-timescale architecture.


## Routing

- **USE FOR:** Time series analysis, signal processing, temporal pattern detection, and multi-scale temporal dynamics. Use for mathematical reasoning about time-varying data, smoothing, derivative estimation, spectral analysis, changepoint detection, and the temporal aspects of the project's knowledge trajectory computation. Covers both theory and computational methodology.
- **DO NOT USE FOR:** measure-theoretic / probabilistic basis (use @math-measure-probability); Lean proofs (use @lean-math-stochastic); nonlinear dynamics (use @math-nonlinear-dynamics).
- **TRIGGERS:** time series, signal processing, temporal pattern, multi-scale temporal, spectral analysis.

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
- **Successors:** `skill:lean-math-stochastic`, `skill:math-measure-probability`, `skill:lean-zettelkasten`.

---

## Part 1 — Project Temporal Context

the project's phase trajectory computation (paper §Phase Trajectory Computation) requires:

| Computation | Mathematical Foundation | Section |
|---|---|---|
| State vector construction | Sampling theory, measurement models | §Data Acquisition |
| Derivative estimation | Numerical differentiation, smoothing | §Derivative Estimation |
| Momentum computation | Moving averages, exponential smoothing | §Derived Quantities |
| EWS detection | Changepoint analysis, variance tracking | §Early Warning Signals |
| Phase classification | Time-series clustering, regime detection | §Phase Classification |
| Multi-timescale decomposition | Wavelet analysis, EMD | §Multi-Timescale |

---

## Part 2 — Smoothing and Derivative Estimation

### 2.1 Smoothing Methods

| Method | Formula | Properties | Project Use |
|---|---|---|---|
| Moving Average (MA) | ŷ_t = (1/k)Σy_{t-i} | Simple, lagging | Baseline trend |
| Exponential (EMA) | ŷ_t = αy_t + (1-α)ŷ_{t-1} | Weighted recency, tunable | Momentum M₃ |
| Savitzky-Golay | Polynomial least-squares on window | Preserves peaks, smooth derivatives | Derivative estimation |
| Kalman filter | State-space model with noise | Optimal for linear Gaussian | State estimation |
| Gaussian Process | Bayesian nonparametric | Uncertainty quantification | Confidence bands |

### 2.2 Numerical Differentiation

```
First derivative (central difference): ẋ_t ≈ (x_{t+h} - x_{t-h}) / 2h
Second derivative: ẍ_t ≈ (x_{t+h} - 2x_t + x_{t-h}) / h²

Better: Savitzky-Golay differentiation
  - Fit polynomial of degree p to window of width 2m+1
  - Differentiate polynomial analytically
  - Result: smooth derivative estimate with known error bounds
```

### 2.3 Multi-Scale Derivative Estimation

the project's multi-timescale architecture requires derivatives at different scales:
```
Fast (experience):   ẋ_fast  — computed on τ_fast  window (minutes/hours)
Medium (structure):  ẋ_mid   — computed on τ_mid   window (days/weeks)
Slow (innovation):   ẋ_slow  — computed on τ_slow  window (weeks/months)

Separation criterion: τ_{slow}/τ_{fast} > 10 for reliable decomposition
```

---

## Part 3 — Spectral Analysis

### 3.1 Fourier Methods

| Method | Input | Output | Project Use |
|---|---|---|---|
| DFT/FFT | Uniformly sampled time series | Frequency spectrum | Periodicity detection |
| Periodogram | Time series | Power spectral density | Dominant timescales |
| Welch's method | Long time series | Smoothed PSD | Robust spectral estimation |
| Lomb-Scargle | Irregularly sampled data | PSD for irregular data | Missing data handling |

### 3.2 Wavelet Analysis

```
Continuous wavelet transform (CWT):
  W(a,b) = ∫ x(t) ψ*((t-b)/a) dt/√a

  a = scale (inverse frequency), b = time location
  → Time-frequency decomposition (localized spectra)

Discrete wavelet transform (DWT):
  Multiresolution analysis: x = Σ_j D_j + A_J
  D_j = detail at scale 2^j (high frequency at scale j)
  A_J = approximation at coarsest scale (low frequency trend)
```

**project application**: Decompose knowledge trajectory into timescale components → validate multi-timescale architecture.

### 3.3 Empirical Mode Decomposition (EMD)

```
EMD: x(t) = Σ_k IMF_k(t) + residual(t)

IMFs (Intrinsic Mode Functions):
  - Each IMF captures an oscillatory component
  - Data-driven (no basis function choice needed)
  - Adaptive to nonlinear/nonstationary dynamics
```

Better for Project than Fourier (knowledge dynamics are nonstationary).

---

## Part 4 — Changepoint Detection

### 4.1 Methods for Regime Change Detection

| Method | Type | Detects | Speed |
|---|---|---|---|
| CUSUM | Parametric | Mean shift | Fast, online |
| PELT | Penalized likelihood | Mean/variance shifts | Fast offline |
| Bayesian Online | Bayesian | Any distributional change | Online, with uncertainty |
| Hidden Markov Model | Model-based | Regime switching | Needs model spec |
| Kernel-based (MMD) | Nonparametric | Distributional change | Flexible, slower |

### 4.2 Project Phase Transition Detection

```
Knowledge state: x(t) = [C(t), V(t), R(t), D(t), M(t)]

Phase transition ≡ changepoint in regime classification:
  1. Track classification: regime(t) = classify(x(t))
  2. Detect when regime(t) changes
  3. Validate: is this a true transition or noise?

Validation criteria:
  - Duration: new regime persists for ≥ minimum_dwell_time
  - Confidence: quality gate conditions clearly switch
  - Consistency: multiple indicators agree (C, V, R, D all support new regime)
```

### 4.3 Early Warning Signals (EWS)

Before a catastrophic transition (cusp bifurcation), detect:
```
1. Rising autocorrelation: lag-1 AC → 1 (critical slowing down)
2. Rising variance: Var(x_t) → ∞ (amplitude increases)
3. Rising skewness: skew(x_t) ≠ 0 (asymmetry develops)
4. Flickering: bimodal distribution (system samples both basins)

Project computation:
  - Window: rolling window of size W
  - Metric: Kendall τ trend test on each EWS indicator
  - Threshold: Kendall τ > 0.3 → "approaching transition"
```

---

## Part 5 — Stochastic Time Series Models

### 5.1 Classical Models

| Model | Equation | Properties | Project Relevance |
|---|---|---|---|
| AR(p) | x_t = Σ φ_i x_{t-i} + ε_t | Linear, stationary | Baseline comparison |
| MA(q) | x_t = ε_t + Σ θ_i ε_{t-i} | Finite memory | Moving average smoothing |
| ARMA(p,q) | Combines AR + MA | Parsimonious | General linear model |
| ARIMA(p,d,q) | ARMA on differenced series | Handles trends | Non-stationary data |
| GARCH(p,q) | Conditional variance model | Models volatility clusters | Volatility V(t) modeling |

### 5.2 Regime-Switching Models

```
Markov-switching AR:
  x_t = φ_{s_t} x_{t-1} + σ_{s_t} ε_t
  s_t ~ Markov(P)  (regime indicator)

  → Each regime has its own AR parameters
  → Transition probabilities capture phase switching
  → Project: regimes = {Exploration, Transition, Mastery, Crisis}
```

### 5.3 State-Space Models

```
State equation:   x_{t+1} = Ax_t + Bu_t + w_t   (hidden state evolution)
Observation:      y_t = Cx_t + v_t              (noisy measurement)

Kalman filter: optimal state estimation given observations
Kalman smoother: uses future as well as past observations

Project: x = [C, V, R, D, M], y = quality gate scores, u = governance inputs
```

---

## Part 6 — Multi-Scale Temporal Methods

### 6.1 Timescale Separation Analysis

```
Given: time series x(t) with multiple timescales

Method 1: Wavelet decomposition
  → Separate into scale bands corresponding to Project timescales
  → Verify that energy is concentrated at expected scales

Method 2: Singular Spectrum Analysis (SSA)
  → Embed time series in delay coordinates
  → SVD → extract principal components (oscillatory + trend)
  → Group components by timescale

Method 3: Multi-scale entropy
  → Coarse-grain at different scales
  → Compute SampEn at each scale
  → Complex systems show high entropy across scales
```

### 6.2 Project Multi-Timescale Validation

To validate the 4-timescale architecture from data:
```
1. Collect trajectory data from all Project stages
2. Decompose using wavelets or SSA
3. For each decomposed component:
   a. Estimate characteristic timescale (autocorrelation time or spectral peak)
   b. Assign to Project level (Experience/Articulation/Structuring/Innovation)
4. Verify separation: τ_{i+1}/τ_i > 10 for adjacent levels
5. Verify coupling: cross-correlation between levels exists but is weak
```

---

## Part 7 — Connections to Formalization

### 7.1 What Can Be Formalized in Lean

| Concept | Formalizability | Current Status |
|---|---|---|
| Convergence of smoothed estimates | ✅ (via Mathlib analysis) | Partially covered |
| EWS threshold crossing | ✅ (decidable Nat comparison) | In PipelineAdaptive |
| Phase classification | ✅ (decidable finite cases) | In PhaseClassification |
| Spectral gap bounds | ✅ (algebraic) | In StochasticCCV |
| ARIMA forecast bounds | 🟡 (requires probability theory) | Not yet |
| Wavelet decomposition properties | 🟡 (sparse Mathlib coverage) | Not yet |
| Changepoint detection guarantees | 🟡 (depends on statistical theory) | Not yet |

### 7.2 Research Frontiers for Formalization

- Formal verification of EWS detection algorithms
- Proven error bounds for numerical differentiation
- Certified changepoint detection (false positive rate bounds)
- Formal connection between time-series stability and Lyapunov stability
