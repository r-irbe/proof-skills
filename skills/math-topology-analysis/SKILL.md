---
name: "math-topology-analysis"
description: |
  USE FOR: Point-set topology, functional analysis, real analysis, and topological methods for dynamical systems. Use for reasoning about continuity, compactness, fixed-point theorems, Banach spaces, metric spaces, convergence, and the topological foundations underlying Lyapunov stability, contraction mappings, and phase portrait analysis.
  DO NOT USE FOR: Lean analysis proofs (use @lean-math-analysis); algebraic structures (use @math-algebra-category); measure theory (use @math-measure-probability).
  TRIGGERS: point-set topology, functional analysis, real analysis, continuity, compactness, topological method.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-math-analysis', 'skill:math-algebra-category', 'skill:lean-zettelkasten']
metadata:
  version: "0.2.0"
  source_spec: "skills/math-topology-analysis/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# Math Topology & Real Analysis

Topological and analytic foundations for dynamical systems, convergence proofs, and contraction mappings.

---

## Routing

- **USE FOR:** Point-set topology, functional analysis, real analysis, and topological methods for dynamical systems. Use for reasoning about continuity, compactness, fixed-point theorems, Banach spaces, metric spaces, convergence, and the topological foundations underlying Lyapunov stability, contraction mappings, and phase portrait analysis.
- **DO NOT USE FOR:** Lean analysis proofs (use @lean-math-analysis); algebraic structures (use @math-algebra-category); measure theory (use @math-measure-probability).
- **TRIGGERS:** point-set topology, functional analysis, real analysis, continuity, compactness, topological method.

## Workflow

1. Classify the question: point-set topology, functional analysis, real analysis, or topological dynamics.
2. Pick the matching section of the body; identify the Mathlib `Topology` / `Analysis` namespace.
3. Produce the answer; cite the relevant Mathlib lemma and verify it at the current pin.
4. Hand off: to `@lean-math-analysis` for the Lean proof, to `@math-measure-probability` if measure-theoretic structure surfaces, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the question is algebraic-structural — delegate to `@math-algebra-category`.
- STOP if measure theory dominates — delegate to `@math-measure-probability`.
- STOP if a pin-verified Mathlib lemma is required — escalate to `@lean-research`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-math-analysis`, `skill:math-algebra-category`, `skill:lean-zettelkasten`.

---

## Part 1 — Metric Spaces & Topology

### 1.1 Metric Space Fundamentals

| Concept | Definition | Common use |
|---|---|---|
| Metric | $d(x,y) \ge 0$, $d(x,y) = 0 \iff x=y$, triangle inequality | Trust distance, L1 on simplex |
| Open ball | $B(x,r) = \{y : d(x,y) < r\}$ | Neighborhoods in phase space |
| Cauchy sequence | $\forall \epsilon > 0, \exists N, \forall m,n > N: d(x_m, x_n) < \epsilon$ | Convergence of governance |
| Completeness | Every Cauchy sequence converges | Banach fixed-point applicability |
| Compactness | Every open cover has finite subcover | Bounded phase space |
| Total boundedness | $\forall \epsilon, \exists$ finite $\epsilon$-net | Finite approximation of state space |

### 1.2 Key Fixed-Point Theorems

| Theorem | Statement | Common application |
|---|---|---|
| **Banach** | Contraction on complete metric space ⟹ unique fixed point | Bellman operator, governance Lyapunov |
| **Brouwer** | Continuous map $B^n → B^n$ has fixed point | Trust equilibrium existence |
| **Schauder** | Continuous map on compact convex ⟹ fixed point | Infinite-dimensional generalizations |
| **Kakutani** | Upper-hemicontinuous correspondence ⟹ fixed point | Nash equilibrium existence |
| **Tarski** | Monotone function on complete lattice ⟹ fixed point | Lattice-ordered quality gates |
| **Knaster-Tarski** | Monotone on CPO ⟹ least/greatest fixed points | Order-theoretic gate properties |

### 1.3 Contraction Mapping Theory

The central tool for contraction-based convergence:

**Banach Contraction Principle:**
If $T: X → X$ is a contraction ($d(Tx,Ty) \le \alpha d(x,y)$, $\alpha < 1$) on a complete metric space, then:
- Unique fixed point $x^* = Tx^*$
- Iteration converges: $d(T^n x, x^*) \le \frac{\alpha^n}{1-\alpha} d(x, Tx)$
- Rate: geometric $O(\alpha^n)$

**Common extensions:**
- Asymptotic regularity: weaker than contraction, still converges
- Non-expansive mappings + additional conditions
- Composition of contractions: product of rates
- Multiscale contractions: hierarchical convergence bounds

---

## Part 2 — Topological Dynamics

### 2.1 Dynamical Systems on Metric Spaces

For $\phi_t : X → X$ continuous:
- **Orbit**: $\mathcal{O}(x) = \{\phi_t(x) : t \ge 0\}$
- **$\omega$-limit set**: $\omega(x) = \bigcap_{T>0} \overline{\{\phi_t(x) : t \ge T\}}$
- **Invariant set**: $A$ where $\phi_t(A) = A$ for all $t$
- **Attracting set**: $\exists$ neighborhood $U$ with $\phi_t(U) \subseteq U$ and $\bigcap_t \phi_t(U) = A$

### 2.2 Compactness Arguments

Bounded phase spaces such as quality measures in $[0,1]^n$ are compact:
- **Bolzano-Weierstrass**: Every sequence has convergent subsequence
- **Arzela-Ascoli**: Equicontinuous + pointwise bounded ⟹ compact in $C(X)$
- **Prokhorov**: Tight probability measures ⟹ compact (for stochastic CCV)

### 2.3 Stability Topology

| Stability Type | Topological Characterization |
|---|---|
| Lyapunov stable | $\forall$ neighborhood $U$, $\exists V \subseteq U$ with $\phi_t(V) \subseteq U$ |
| Asymptotically stable | Lyapunov stable + $\omega(x) = \{x^*\}$ for nearby $x$ |
| Globally asymptotically stable | Asymptotically stable with basin $= X$ |
| Exponentially stable | $d(\phi_t(x), x^*) \le C e^{-\alpha t} d(x, x^*)$ |

---

## Part 3 — Functional Analysis Essentials

### 3.1 Banach Spaces

- **Norm**: $\|x\| \ge 0$, homogeneity, triangle inequality
- **Complete normed space** = Banach space
- **Commonly relevant**: $\ell^\infty$ (value functions), $\ell^1$ (simplex measures), $L^p$ (distributional properties)

### 3.2 Key Operators

| Operator | Type | Common use |
|---|---|---|
| Bellman operator $T$ | Contraction on $\ell^\infty$ | Value iteration |
| Stochastic transition $P$ | Linear on simplex | Stochastic dynamics |
| Lyapunov map $V \mapsto V \circ \phi$ | Nonlinear, monotone | Stability analysis |
| Gradient $\nabla f$ | Linear map $X → X^*$ | Optimization |

### 3.3 Spectral Theory

- **Spectrum**: $\sigma(A) = \{\lambda : (A - \lambda I) \text{ not invertible}\}$
- **Spectral radius**: $\rho(A) = \max |\sigma(A)|$
- **Spectral gap**: $1 - \rho_2$ where $\rho_2$ = second-largest eigenvalue modulus
- **Perron-Frobenius**: Non-negative matrix ⟹ dominant eigenvalue real, positive
- **Common use**: spectral gaps of stochastic transition matrices govern mixing time

---

## Part 4 — Convergence Theory

### 4.1 Types of Convergence

| Type | Definition | Strength | Common use |
|---|---|---|---|
| Pointwise | $f_n(x) → f(x)$ for each $x$ | Weakest | — |
| Uniform | $\sup_x |f_n(x) - f(x)| → 0$ | Stronger | Value iteration |
| $L^p$ | $\|f_n - f\|_p → 0$ | Intermediate | Distributional |
| Weak | $\langle f_n, g \rangle → \langle f, g \rangle$ for all $g$ | Weakest in Banach | — |
| In measure | $\mu(\{|f_n - f| > \epsilon\}) → 0$ | Probabilistic | Stochastic CCV |
| Almost sure | $f_n(\omega) → f(\omega)$ a.e. | Strong probabilistic | Ergodic limits |

### 4.2 Rate of Convergence

- **Linear**: $\|x_{n+1} - x^*\| \le c \|x_n - x^*\|$, $c < 1$
- **Superlinear**: $\|x_{n+1} - x^*\| / \|x_n - x^*\| → 0$
- **Quadratic**: $\|x_{n+1} - x^*\| \le C \|x_n - x^*\|^2$
- **Sublinear**: $\|x_n - x^*\| \le C/n^\alpha$ — common for SGD

---

## Part 5 — Filter Theory (Lean/Mathlib Perspective)

Mathlib uses filters for convergence:

### 5.1 Key Filters

| Filter | Lean Name | Captures |
|---|---|---|
| Neighborhood | `nhds a` | Convergence to point $a$ |
| At infinity | `Filter.atTop` | Limit as $n → ∞$ |
| Eventually | `Filter.Eventually` | "for sufficiently large $n$" |
| Frequently | `Filter.Frequently` | Infinitely often |
| Cofinite | `Filter.cofinite` | All but finitely many |

### 5.2 Tendsto

$f$ converges to $L$ along filter $F$:
```
Filter.Tendsto f F (nhds L) ↔ ∀ U ∈ nhds L, f⁻¹(U) ∈ F
```

### 5.3 Common Patterns

- `Filter.Tendsto f atTop (nhds L)`: sequence converges
- `Filter.Tendsto f atTop atTop`: diverges to infinity
- `Filter.Eventually (P ∘ f) atTop`: eventually holds

---

## Part 6 — Host-Repository Lean Extension Points

Do not assume any project-specific Lean modules, tactics, or namespaces exist unless the host repository explicitly provides them. Map local modules by mathematical role:

| Local extension point | Topological foundation | Typical structures |
|---|---|---|
| Lyapunov/stability module | metric stability, Banach contraction | Lyapunov functions, sublevel sets |
| RL/value-function module | $\ell^\infty$ contraction | Bellman contraction, value functions |
| Stochastic-dynamics module | L1 metric, spectral gap | transition step, spectral gap |
| Bifurcation/catastrophe module | bifurcation topology | discriminants, critical sets |
| Safety/trust module | product metric spaces | multi-agent trust distance |
| Tactic-helper module | contraction lemma library | iterate bounds, convexity bounds |

---

## Part 7 — Research Methodology

### 7.1 Topological Proof Strategies

1. **Contraction**: Verify metric and rate → apply Banach
2. **Compactness**: Establish bounded state space → extract convergent subsequence
3. **Monotone convergence**: Find ordering + bounded → limit exists
4. **Barrier/Lyapunov**: Construct sublevel set → show invariance + decrease
5. **Spectral**: Compute eigenvalues → bound convergence via spectral gap

### 7.2 Key References

- Munkres (2000) — Topology (point-set foundations)
- Rudin (1991) — Functional Analysis
- Granas & Dugundji (2003) — Fixed Point Theory
- Kreyszig (1989) — Introductory Functional Analysis
- Brezis (2011) — Functional Analysis, Sobolev Spaces
