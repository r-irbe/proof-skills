---
title: "Math Measure Probability Handbook"
status: "reference"
extracted_from: "skills/math-measure-probability/SKILL.md"
extracted_on: "2026-05-27"
scope: "Part 1 — Measure Theory Foundations; Part 2 — Probability Theory; Part 3 — Concentration Inequalities; Part 4 — Stochastic Processes; Part 5 — Ergodic Theory; Part 6 — Bayesian Methods; Part 7 — Extreme Value Theory; Part 8 — Project-specific Probabilistic Models; Part 9 — Formalization Connections"
loader_hint: "Load when @math-measure-probability routes here for details; not needed for the dispatch decision."
---

# Math Measure Probability Handbook

> **Layering note.** This file holds the deep content previously
> embedded in [`skills/math-measure-probability/SKILL.md`](../skills/math-measure-probability/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow /
> Recovery / Handoffs) + a parts index. This file holds the full
> encyclopaedia. Zero fidelity loss vs the pre-layering revision.

---

## Part 1 — Measure Theory Foundations

### 1.1 Measure Space Hierarchy

```
Set → σ-algebra → Measure → Probability measure → Signed measure → Complex measure
  Ω      𝓕        μ: 𝓕→[0,∞]   P: 𝓕→[0,1]      ν: 𝓕→ℝ           μ: 𝓕→ℂ
```

### 1.2 Key Measure-Theoretic Constructs

| Construct | Definition | Project usage |
|---|---|---|
| σ-algebra 𝓕 | Closed under complement & countable union | Event space for knowledge states |
| Filtration (𝓕_t) | Increasing family of σ-algebras | Information available up to time t |
| Measurable function | f⁻¹(B) ∈ 𝓕 for Borel B | Knowledge metric as random variable |
| Radon-Nikodym derivative | dν/dμ — density of ν w.r.t. μ | Likelihood ratio for regime detection |
| Product measure | μ × ν on Ω₁ × Ω₂ | Independent subsystem coupling |
| Pushforward measure | f_*μ(B) = μ(f⁻¹(B)) | State transformation probability |

### 1.3 Convergence Modes

```
Almost sure (a.s.):  P(Xₙ → X) = 1
In probability:      ∀ε>0, P(|Xₙ - X| > ε) → 0
In Lᵖ (mean):       E[|Xₙ - X|ᵖ] → 0
In distribution:     Fₙ(x) → F(x) at continuity points

Implications:
  a.s. → in probability → in distribution
  Lᵖ → in probability → in distribution
  (but NOT: in probability → a.s.)
```

### 1.4 Key Theorems

| Theorem | Statement | Project application |
|---|---|---|
| Monotone Convergence | E[lim fₙ] = lim E[fₙ] for fₙ↑ | Quality metric convergence |
| Dominated Convergence | E[lim fₙ] = lim E[fₙ] under |fₙ|≤g | Bounded metric analysis |
| Fubini-Tonelli | Iterated integrals equal double integral | Multi-timescale decomposition |
| Lebesgue Decomposition | ν = ν_ac + ν_s | Continuous vs jump dynamics |
| Radon-Nikodym | Density exists iff absolute continuity | Change of measure for regimes |
| Egorov | a.e. convergence → near-uniform convergence | Uniform quality convergence |

---

## Part 2 — Probability Theory

### 2.1 Random Variables and Distributions

```
Discrete: P(X = x) given by mass function
  Important: Bernoulli, Binomial, Poisson, Geometric

Continuous: f_X(x) density, P(a ≤ X ≤ b) = ∫_a^b f_X
  Important: Normal, Exponential, Gamma, Beta, Uniform

project-relevant distributions:
  - Beta(α,β): trust scores, confidence parameters
  - Dirichlet(α₁,...,αₖ): simplex-valued (trust simplex)
  - Gamma(k,θ): waiting times between phase transitions
  - Wishart(V,n): covariance matrices for multi-dimensional states
```

### 2.2 Conditional Probability & Independence

```
Conditional probability: P(A|B) = P(A∩B)/P(B)
Bayes' theorem: P(H|E) = P(E|H)·P(H) / P(E)

Independence:
  P(A∩B) = P(A)·P(B)  (pairwise)
  P(∩ᵢAᵢ) = Πᵢ P(Aᵢ)  (mutual)

Conditional independence:
  X ⊥ Y | Z  iff  P(X,Y|Z) = P(X|Z)·P(Y|Z)

Project use: conditional independence in causal DAGs,
  Bayesian updating of knowledge state beliefs
```

### 2.3 Expectation, Variance, Moments

```
E[X] = ∫ x dP_X
Var(X) = E[(X - E[X])²] = E[X²] - (E[X])²
Cov(X,Y) = E[(X-μ_X)(Y-μ_Y)]

Moment generating function: M_X(t) = E[e^{tX}]
Characteristic function: φ_X(t) = E[e^{itX}]

For vectors: Covariance matrix Σ where Σᵢⱼ = Cov(Xᵢ, Xⱼ)
```

---

## Part 3 — Concentration Inequalities

### 3.1 Key Inequalities

| Inequality | Bound | Use Case |
|---|---|---|
| Markov | P(X ≥ a) ≤ E[X]/a | Crude bound on quality score |
| Chebyshev | P(|X-μ|≥kσ) ≤ 1/k² | Deviation bound |
| Chernoff | P(X ≥ a) ≤ min_t E[e^{t(X-a)}] | Exponential tail bound |
| Hoeffding | P(|S̄ₙ-μ|≥t) ≤ 2exp(-2n²t²/Σ(bᵢ-aᵢ)²) | Bounded average |
| Bernstein | Sharper than Hoeffding with variance info | Quality metric average |
| McDiarmid | Bounded differences → concentration | Stability of scored functions |
| Azuma-Hoeffding | For martingales with bounded increments | Sequential quality tracking |

### 3.2 Project Applications

```
Quality gate threshold: Use Hoeffding to bound
  P(quality_score deviates from true quality by > ε)
  ≤ 2·exp(-2nε²)
  
  So n = O(1/ε²) observations suffice for reliable gating.

Trust score stability: McDiarmid for trust composition
  Changing one evidence source changes trust by ≤ cᵢ
  P(|trust - E[trust]| > t) ≤ 2·exp(-2t²/Σcᵢ²)
```

---

## Part 4 — Stochastic Processes

### 4.1 Process Classification

| Process | Definition | Project model |
|---|---|---|
| Markov chain (discrete) | P(Xₙ₊₁|X₀,...,Xₙ) = P(Xₙ₊₁|Xₙ) | Knowledge regime transitions |
| Markov chain (continuous) | Generator matrix Q | Continuous-time phase dynamics |
| Brownian motion | Continuous Gaussian process with stationary increments | Stochastic perturbation model |
| Diffusion process | dXₜ = μ(Xₜ)dt + σ(Xₜ)dWₜ | Knowledge state SDE |
| Poisson process | Count process with exponential inter-arrivals | Phase transition events |
| Renewal process | Generalized Poisson with arbitrary inter-arrivals | Knowledge update arrivals |
| Martingale | E[Xₙ₊₁|𝓕ₙ] = Xₙ | Fair game / unbiased estimators |

### 4.2 Markov Chain Theory

```
Transition matrix: P where Pᵢⱼ = P(Xₙ₊₁=j | Xₙ=i)

Key properties:
  Irreducibility: any state reachable from any other
  Aperiodicity: gcd of return times = 1
  Positive recurrence: expected return time finite

Fundamental theorem: Irreducible + aperiodic + positive recurrent
  → unique stationary distribution π where πP = π

Convergence rate: ||P^n(x,·) - π||_TV ≤ C·ρⁿ  (geometric mixing)
  where ρ = 1 - spectral gap of P
```

### 4.3 Stochastic Differential Equations (SDEs)

```
Itô SDE: dXₜ = μ(Xₜ,t)dt + σ(Xₜ,t)dWₜ

Itô's Lemma: For f(Xₜ,t):
  df = (∂f/∂t + μ·∂f/∂x + ½σ²·∂²f/∂x²)dt + σ·∂f/∂x dWₜ

Project knowledge state SDE:
  dK = f(K)dt + g(K)dW   (deterministic drift + stochastic perturbation)
  
  Lyapunov for SDE: LV(x) = μ·∇V + ½ tr(σσᵀ·∇²V) ≤ -αV
  ensures stochastic stability in mean
```

---

## Part 5 — Ergodic Theory

### 5.1 Ergodic Theorems

```
Birkhoff (pointwise): (1/n)Σf(Tⁱx) → ∫f dμ  a.e.
  for measure-preserving T on (Ω, 𝓕, μ)

Von Neumann (mean): (1/n)Σf(Tⁱx) → ∫f dμ  in L²

project application:
  Time averages of knowledge metrics converge to
  spatial averages (ensemble averages) in ergodic regime.
  → Long-running Project cycle converges to steady-state quality.
```

### 5.2 Mixing and Spectral Gap

```
Mixing: The system "forgets" its initial condition.

Strong mixing: |P(A ∩ T⁻ⁿB) - P(A)P(B)| → 0

Spectral gap: λ₁ = 1 (trivial), λ₂ < 1
  Gap = 1 - λ₂ > 0  ⟹  exponential mixing

Mixing time: t_mix(ε) = min{t : max_x ||P^t(x,·) - π||_TV ≤ ε}
  t_mix ≤ O(1/gap · log(1/ε))

project implication:
  Spectral gap > 0 ⟹ knowledge process converges to equilibrium
  Larger gap ⟹ faster convergence to steady-state quality
```

### 5.3 Entropy and Information

```
Shannon entropy: H(X) = -Σ p(x) log p(x)
Kullback-Leibler divergence: D_KL(P||Q) = Σ p(x) log(p(x)/q(x))
Mutual information: I(X;Y) = H(X) + H(Y) - H(X,Y)
Conditional entropy: H(X|Y) = H(X,Y) - H(Y)

Entropy rate for stochastic processes:
  h = lim_{n→∞} H(Xₙ|X₁,...,Xₙ₋₁)

Project: entropy tracks knowledge uncertainty reduction across stages
  Innovation stage should minimize entropy of knowledge representation
```

---

## Part 6 — Bayesian Methods

### 6.1 Bayesian Framework

```
Prior: π(θ) — initial belief about parameters
Likelihood: L(θ|data) = P(data|θ)
Posterior: π(θ|data) ∝ L(θ|data)·π(θ)
Evidence: P(data) = ∫ L(θ|data)·π(θ) dθ

Conjugate priors:
  Normal likelihood + Normal prior → Normal posterior
  Bernoulli likelihood + Beta prior → Beta posterior
  Multinomial + Dirichlet → Dirichlet posterior (trust simplex!)
```

### 6.2 Project Bayesian Applications

```
Trust updating:
  Prior: Beta(α₀, β₀) on source reliability
  Each verification: success → α+=1, failure → β+=1
  Posterior: Beta(α₀+s, β₀+f)
  Mean trust: (α₀+s)/(α₀+β₀+s+f)

Knowledge regime belief:
  Prior: Dirichlet(α) over K regimes
  Observations update: α_k += observation count in regime k
  Regime probability: softmax of updated Dirichlet
```

### 6.3 Model Selection

```
Bayesian Information Criterion: BIC = -2·log L + k·log n
Akaike Information Criterion: AIC = -2·log L + 2k
Bayesian model averaging: P(Y|data) = Σ P(Y|M_i,data)·P(M_i|data)

Use for: selecting number of knowledge regimes,
  choosing complexity of quality gate models
```

---

## Part 7 — Extreme Value Theory

### 7.1 EVT Foundations

```
Three extreme value distributions (Fisher-Tippett-Gnedenko):
  Gumbel (Type I):   exp(-exp(-x))         — light tails
  Fréchet (Type II):  exp(-x^{-α})         — heavy tails
  Weibull (Type III): exp(-(-x)^c), x ≤ 0  — bounded support

Generalized Extreme Value:
  H_ξ(x) = exp(-(1+ξx)^{-1/ξ})
  ξ = 0: Gumbel, ξ > 0: Fréchet, ξ < 0: Weibull

Project use: model extreme knowledge quality events,
  tail risk in governance decision-making
```

### 7.2 Peaks Over Threshold

```
Generalized Pareto Distribution (GPD):
  P(X > u+y | X > u) ≈ (1 + ξ·y/σ)^{-1/ξ}

Use for: rare catastrophic events in knowledge lifecycle
  (sudden quality collapse, trust breach, critical phase transition)
```

---

## Part 8 — Project-specific Probabilistic Models

### 8.1 Knowledge Phase Portrait as Probability Space

```
State space: S = [0,1]^d (d-dimensional quality vector)
σ-algebra: Borel subsets of S
Probability: P_t = evolved measure under dynamics

Phase classification:
  P(regime = k | observation) via posterior inference
  Uses Bayesian updating with Dirichlet prior on regime probabilities
```

### 8.2 Quality Gate as Hypothesis Test

```
H₀: artifact quality meets threshold (q ≥ q_min)
H₁: artifact quality below threshold (q < q_min)

Type I error (α): reject good artifact
Type II error (β): accept bad artifact

Gate design: choose threshold to minimize β
  subject to α ≤ α_max (governance constraint)
  
Neyman-Pearson lemma: optimal test uses likelihood ratio
```

### 8.3 Multi-timescale Probability

```
Fast process: τ_fast ~ O(1)     — individual measurements
Medium process: τ_med ~ O(10)   — quality gate evaluations  
Slow process: τ_slow ~ O(100)   — regime transitions

Averaging principle:
  On slow timescale, fast variables are at quasi-equilibrium
  P_slow(x) = ∫ P(x, y_fast) dy_fast ≈ P(x | y_fast = ȳ(x))
```

---

## Part 9 — Formalization Connections

### 9.1 Current Lean Coverage

| Concept | Module | Status |
|---|---|---|
| Spectral gap bounds | StochasticCCV | ✅ Proven |
| Mixing time sufficiency | StochasticCCV | ✅ Proven |
| Ergodic average bounds | StochasticCCV | ✅ Proven |
| Noise stability region | StochasticCCV | ✅ Proven |
| TrustSimplex (Dirichlet structure) | ProvenanceChain | ✅ Proven |

### 9.2 Formalization Frontiers

- Stochastic Lyapunov theory (Itô calculus in Lean)
- Concentration inequality library (Hoeffding, McDiarmid)
- Ergodic theorem for Project Markov chains
- Bayesian posterior consistency for quality gates
- EVT for rare catastrophic transition events
