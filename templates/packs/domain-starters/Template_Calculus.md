
# Template_Calculus -- `HasDerivAt`, Chain Rule, Polynomial Derivatives

Use this template for **calculus modules** that work with
`HasDerivAt` / `deriv` / `HasFDerivAt` from Mathlib's analysis layer.
Covers chain rule via `.comp`, polynomial differentiation, derivatives
through user-defined arithmetic, and the standard `Differentiable ...`
bundle that Mathlib API consumers prefer.

This template is the "level up" from `Template_Analysis`: `Analysis`
covers `ContinuousOn`, `MonotoneOn`, `IsCompact`-style topology;
`Calculus` is specifically about derivatives and their algebra.

Examples of modules at this layer:
- `<Project>.CuspCatastrophe.Core`
- `<Project>.LyapunovStability.SmoothFunctional`
- `<Project>.RL.PolicyGradient`

## Main results
* `<yourFun>_hasDerivAt` -- `HasDerivAt f f' x` with a concrete `f'`
* `<yourFun>_deriv_eq` -- `deriv f x = ...` (the unfolded value)
* `<yourFun>_differentiable` -- `Differentiable ℝ f`

## Implementation notes
- Prefer `HasDerivAt` over `deriv`; the former records the derivative
  *value* in the statement, which is what downstream `.comp` needs.
- Chain rule: `HasDerivAt.comp x hf hg` requires the derivatives to be
  named.  Don't try `apply chain_rule`; it will not find the witnesses.
- Polynomial derivatives close themselves via the `Polynomial.derivative`
  algebra + `(p.derivative).eval`; do NOT re-derive `(x²)' = 2x` from
  scratch.

## References
* `Mathlib/Analysis/Calculus/Deriv/Basic.lean`
* `Mathlib/Analysis/Calculus/Deriv/Polynomial.lean`
* `Mathlib/Analysis/Calculus/FDeriv/Comp.lean`
* `Mathlib/Analysis/Calculus/MeanValue.lean`

## Tags
template, calculus, derivative, chain-rule, polynomial, hasDerivAt

```lean
import Mathlib.Analysis.Calculus.Deriv.Basic
import Mathlib.Analysis.Calculus.Deriv.Polynomial
import Mathlib.Analysis.Calculus.Deriv.Pow
import Mathlib.Analysis.Calculus.Deriv.Mul
import Mathlib.Analysis.Calculus.FDeriv.Comp

set_option autoImplicit false
```

 ### §1  Namespace and variables

```lean
namespace <Project>.<YourDomain>.<YourModule>

open scoped Topology
open Filter

variable {f g : ℝ → ℝ} {f' g' x : ℝ}
```

 ### §2  A `HasDerivAt` proof from scratch

```lean
/-- TEMPLATE: derive `f x = x^3 - 3 x` (cusp catastrophe potential)
    and its derivative `3 x^2 - 3`. -/
example : HasDerivAt (fun x : ℝ => x^3 - 3 * x) (3 * x^2 - 3) x := by
  have h₁ : HasDerivAt (fun x : ℝ => x^3) (3 * x^2) x := by
    simpa using (hasDerivAt_pow 3 x)
  have h₂ : HasDerivAt (fun x : ℝ => (3 : ℝ) * x) 3 x := by
    simpa using ((hasDerivAt_id x).const_mul 3)
  simpa using h₁.sub h₂
```

 ### §3  Chain rule via `.comp`

```lean
-- TEMPLATE: `(f ∘ g)'(x) = f'(g x) * g'(x)`.
example
    (hf : HasDerivAt f f' (g x))
    (hg : HasDerivAt g g' x) :
    HasDerivAt (f ∘ g) (f' * g') x :=
  hf.comp x hg

-- PITFALL: the outer derivative is evaluated at `g x`, not `x`.  The
-- statement above makes that explicit; do NOT use `HasDerivAt f f' x`
-- unless you really mean it.
```

 ### §4  Polynomial derivatives

```lean
open Polynomial

-- TEMPLATE: a concrete polynomial and its derivative-eval lemma.
example (x : ℝ) : (C 3 * X^2 + C 1).derivative.eval x = 6 * x := by
  -- `derivative_C_mul_X_pow` + `eval_*` simp set close this.
  simp [derivative_C_mul_X_pow]
  ring
```

 ### §5  `Differentiable` bundle

```lean
-- TEMPLATE: package `HasDerivAt` everywhere as `Differentiable ℝ`.
example (h : ∀ x, HasDerivAt f (f' x) x) : Differentiable ℝ f :=
  fun x => (h x).differentiableAt
```

 ### §6  Mean-value-type bound (optional)

```lean
-- TEMPLATE: if `|f'| ≤ K` on an interval, then `f` is `K`-Lipschitz on it.
example
    (K : ℝ) (h : ∀ x ∈ Set.Icc (0 : ℝ) 1, |f' x| ≤ K)
    (hf : ∀ x ∈ Set.Icc (0 : ℝ) 1, HasDerivAt f (f' x) x) :
    LipschitzOnWith ⟨K, by sorry⟩ f (Set.Icc 0 1) := by
  sorry  -- TEMPLATE: use Mathlib `Convex.lipschitzOnWith_of_nnnorm_deriv_le`
```

 ### §7  Common pitfalls

```lean
-- PITFALL #1: `deriv f x` returns `0` when `f` is not differentiable.
-- So `deriv f x = 0` is NOT evidence of a critical point -- convert to
-- `HasDerivAt f 0 x` + `Differentiable ...` first.
--
-- PITFALL #2: `(hf.add hg)` gives `HasDerivAt (f + g) (f' + g') x`.
-- The functions must be written as `f + g`, not `fun x => f x + g x`,
-- or `simp` will struggle to apply the lemma.
--
-- PITFALL #3: `hasDerivAt_pow n x : HasDerivAt (· ^ n) (n * x^(n-1)) x`.
-- For `n = 0` the derivative is `0`, NOT `0 * x⁻¹` -- Mathlib special-cases it.
```

 ### §8  See also

```lean
-- See Template_Analysis for `ContinuousOn`, `MonotoneOn`, topology side.
-- See Template_ProofStrategy when planning a multi-step derivative chain.
-- See Template_Performance if your derivative chain blows up heartbeats.
```

end <Project>.<YourDomain>.<YourModule>
