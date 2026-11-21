# Lean to Mathematical Exposition Patterns: Pedagogical Translation Guide

<!-- Scoped Unicode policy (INV-001; typographic-free by default). Invariant per AGENTS.md (INV-001).
     Status: Authoritative Engineering Reference
     Authority: Systems Architecture Council / Mathematical Exposition Lead
     Target Skills: lean-pedagogical-exposition, lean-blueprint, lean-doc-improvement -->

## 1. Pedagogical Objective

Formal Lean 4 code is optimized for type-checking correctness, elaboration stability,
and compiler performance. Human mathematical understanding, conversely, requires
intuitive motivation, structural clarity, and geometric or algebraic analogies.

This guide provides concrete translation patterns for converting Lean 4 idioms,
types, and tactic structures into beautiful, clear, textbook-quality mathematical prose.

---

## 2. Type and Structure Translation Dictionary

| Lean 4 Construct | Formal Representation | Standard Mathematical Prose |
| :--- | :--- | :--- |
| **Sobolev Spaces** | `SmoothL2Field Space` | Smooth vector field $u \in C^\infty(\mathbb{R}^3) \cap L^2(\mathbb{R}^3)$ |
| **Frechet Derivative** | `fderiv R u x` | Total derivative or Jacobian matrix $\nabla u(x) \in \mathcal{L}(\mathbb{R}^3, \mathbb{R}^3)$ |
| **Vorticity / Curl** | `vectorCurl u x` | Vorticity vector field $\omega(x) = \nabla \times u(x)$ |
| **Incompressibility** | `divergence u x = 0` | Divergence-free condition $\text{div}(u) = \nabla \cdot u = 0$ |
| **Bilinear Form** | `ContinuousLinearMap.adjoint` | Adjoint operator $A^* \in \mathcal{L}(H, H)$ |
| **Matrix Congruence** | `F.transpose * A * F` | Quadratic/bilinear transformation under coordinate change $F^T A F$ |
| **Matrix Adjugate** | `F.adjugate` | Classical adjugate matrix $F^{\text{adj}} = \det(F) F^{-1}$ |
| **Filter Convergence** | `Tendsto f atTop (nhds L)` | Asymptotic limit $\lim_{t \to \infty} f(t) = L$ |
| **Endpoint Filter** | `nhdsWithin Tstar (Iio Tstar)` | Left-sided limit as $t \to T^{*-}$ |
| **Extended Real Integral**| `\int x in s, ENNReal.ofReal (f x)` | Extended Lebesgue integral $\int_s f(x) dx \in [0, \infty]$ |
| **Probability Simplex** | Integer scaled $\sum x_i = 100$ | Point on the standard probability simplex $\Delta^n$ with rational precision |

---

## 3. Proof Deconstruction Patterns

### 3.1 Translating `calc` Chains into Analytical Estimates
In Lean, equality and inequality chains are written as:
```lean
calc
  f x <= g x := by apply h1
  _   <= h x := by apply h2
```
In pedagogical prose, translate this by introducing the intermediate quantity and
explaining the underlying bound:
> Applying the Cauchy-Schwarz inequality bounds the cross-term by $g(x)$.
> Then, using the Sobolev embedding $H^2(\mathbb{R}^3) \hookrightarrow L^\infty(\mathbb{R}^3)$,
> this bounds $g(x)$ by $h(x)$, completing the estimate.

### 3.2 Translating `have` Milestone Towers
Large formal proofs rely on nested `have` declarations. In human exposition:
1. Identify the 2 to 4 pivotal `have` milestones that carry independent mathematical meaning.
2. Formulate each milestone as an explicitly named Lemma.
3. Show how the lemmas combine to yield the final theorem.

### 3.3 Translating Contradiction Arguments (`by_contra`)
Lean proofs of unboundedness or divergence often use `by_contra` followed by `push Not`:
```lean
by_contra hn
push Not at hn
apply L.no_endpoint
...
```
In pedagogical exposition, state the strategy directly:
> The proof proceeds by contradiction. If the total vorticity accumulated on $[0, T^*)$
> were bounded by some finite constant $G$, the Beale-Kato-Majda logarithmic inequality
> would guarantee that the velocity gradient remains integrable up to $T^*$.
> By the local continuation theorem, the solution could then be extended past $T^*$,
> which directly contradicts the maximality of $T^*$.

---

## 4. Architectural Rules for High-Quality Exposition

1. **Avoid Tactic Narratives**: Never narrate the mechanical tactics used to close the goal
   (avoiding mechanical sequences like 'then apply simp only and linarith'). Explain the mathematical reason the identity holds.
2. **State Universal Bounds Explicitly**: Highlight when constants depend only on dimension
   or domain geometry rather than hiding them in an opaque Lean constant name.
3. **Connect to Classical Literature**: Whenever formalizing a landmark result, cite the
   original mathematical literature (e.g., Beale, Kato, and Majda, 1984; Taylor, 1991;
   Wiles, 1995) to ground the formalization in the broader mathematical environment.
4. **Pure-Math Paper Presentation (Halmos & Knuth Ch. 18)**:
   - Keep running prose, theorem statements, and figure captions free of `.lean` filenames, dotted module namespaces, and `snake_case` code tokens; consolidate formal mapping into a dedicated verification table and a machine-checked `Concordance.lean` module.
   - Make every theorem environment self-contained: bind all symbols, index sets, and positivity/domain hypotheses internally, and reserve bracketed `[...]` theorem titles strictly for classical landmark theorems.
   - Follow Knuth TeXbook Chapter 18 micro-typography: write inline fractions with slash notation (`$a/b$`, reserving `\frac` for displayed equations), avoid comma-spliced formulas (`$x = 1$, $y = 2$` -> `$x = 1$ and $y = 2$`), avoid clause-initial math after punctuation, and avoid bare parenthesized math (`($x$)`).
5. **Skeptical Terminology & Three-Tier Proof Provenance**:
   - Verify every eponymous term against primary literature (never splice unrelated author pairs, apply `"Presburger"` to quadratic expressions, call partition measurability $K_i(B)=B$ `"awareness"`, or replace exact quota/cycle inequalities with slogans).
   - Explicitly partition formalization credit across three tiers: (i) upstream `Mathlib`/`Cslib` foundations, (ii) adapted third-party ports (preserving SPDX notices) and newly mechanized settled classical results, and (iii) novel domain models, sharpness counterexamples, and compositional synthesis theorems.
