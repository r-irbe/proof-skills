# Template: Modular Subpackage Interface & Cross-Package Quotient Dispatch

## 1. Context & Architectural Rationale

In a multi-package Lean 4 ecosystem (e.g. `packages/tacit-foundations`, `packages/stochastic-ccv`, `packages/cusp-catastrophe`, `packages/reinforcement-learning`, `packages/provenance-chain`, `packages/agentic-safety`), multiple packages are developed in parallel as independent mini-projects.
Directly importing the monolithic legacy codebase (`EASCI.*`) or creating circular imports between peer packages violates DAG modularity and triggers Lake build failures.

This template formalizes the **Cross-Package Interface Pattern** inspired by Wiles' complete intersection criterion (#(eta_T) = #(m_R / m_R^2)) and Mazur's cuspidal quotienting in Fermat's Last Theorem:
- **Vertical Hierarchy**: Strict 4-tier DAG (Tier 0 -> Tier 1 -> Tier 2 -> Tier 3).
- **Horizontal Decoupling**: Peer packages within the same tier cannot import each other sideways.
- **Certified Valuation**: Continuous quantities crossing package boundaries are quantized via `Foundations.ScaledInt`.
- **Complete Intersection**: Interface mappings have trivial kernel (every required upstream symbol is faithfully resolved with matching signature hash).

---

## 2. Interface Module Blueprint

Every cross-package interface module must adhere to the following template:

```lean
import Mathlib.Data.Real.Basic
import Mathlib.Tactic
-- 1. Tier 0 Foundational Imports (never import EASCI.*)
import Foundations.DiscreteValuation

set_option autoImplicit false
set_option linter.unusedVariables false

namespace <PackageName>

/-!
# <Subpackage> — <ModuleName> Cross-Package Interface

Interface morphism connecting `<UpstreamPackage>` (Tier N) to `<DownstreamPackage>` (Tier M).
Architecture Invariant: M > N (strict DAG tier order).
-/

/-- Section-retraction embedding ensuring faithful interface translation without information loss. -/
structure InterfaceBridge (α β : Type*) where
  toDownstream : α → β
  toUpstream : β → α
  left_inv : ∀ a : α, toUpstream (toDownstream a) = a

/-- Certified integer-scaled parameter passing across package boundary. -/
def bridgeScaledParam (S : ℤ) (val : ℤ) (hS : 0 < S) : Foundations.ScaledInt S :=
  ⟨val, hS⟩

/-- Quotient conservation law: net flux across interface boundaries is zero. -/
theorem interface_conservation_exact (S : ℤ) (hS : 0 < S) (x y : Foundations.ScaledInt S) :
    x.val + y.val = (Foundations.ScaledInt.add x y).val := by
  rfl

end <PackageName>
```

---

## 3. Checklist for Subpackage Interface Authors

1. **Monolith Isolation**: Confirm `git grep "import EASCI" packages/<name>/` returns 0 hits.
2. **DAG Monotonicity**: Ensure your package only imports packages of strictly lower tier.
3. **Integer Scaling**: Ensure parameters crossing boundaries use `Foundations.ScaledInt` or explicit integer scales (x 100).
4. **Symbol Registry**: Register all new interface symbols in `docs/easci/lean/skills-overrides/subst_table.json`.
5. **Zero Sorry Hard Invariant**: 0 unproven goals committed.
