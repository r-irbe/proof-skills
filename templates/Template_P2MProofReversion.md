# Template_P2MProofReversion.md - P2M Bipartite Statement/Proof Decoupling & Reversion Barrier

> **Status:** Standard production template for modular proof isolation and zero-invalidation compilation.  
> **Audience:** Formalization engineers, automated proof swarms, and subpackage maintainers.  
> **Origin:** Extracted from the 29,511-theorem Fermat's Last Theorem Lean 4 architecture (P2M/Util.lean).

---

## 1. When to Use This Template

Apply `Template_P2MProofReversion` when:
- Refactoring large, monolithic files (e.g., `EASCI/LyapunovStability.lean` > 1,000 LOC).
- Developing across multi-package boundaries (`packages/stochastic-ccv`, `packages/tacit-foundations`) where proof modifications must not invalidate downstream `.olean` caches.
- Operating multi-agent proof generation where an Architect agent issues formal specification cards and Worker agents prove them concurrently.
- Standard `exact` fails due to local context instance divergence, binder name drift, or subtle implicit parameter mismatches.
- Universe levels must be formally certified against undergeneralization (`P2M_UNDERGENERAL`).

**Do NOT use for:**
- Short leaf lemmas (< 30 lines) contained entirely within a single internal module.
- Inductive type definitions, structures, or purely computable functions.

---

## 2. Architectural Blueprint

Every theorem $X$ is split across two files:
1. **`Theorems/Thm_X.lean`** (Public Interface Card): Reverts local context and assigns the solution via `p2m_exact_reverting`.
2. **`Sol/S_X.lean`** (Isolated Solution Module): Contains the actual proof script inside a dedicated namespace.

```
                    +----------------------------+
                    |    Downstream Packages     |
                    +-------------+--------------+
                                  | imports ONLY
                                  v
                    +----------------------------+
                    |    Theorems/Thm_X.lean     |  <-- Stable Public Card
                    +-------------^--------------+
                                  | p2m_exact_reverting
                                  | (Closed Pi-type assignment)
                    +-------------+--------------+
                    |       Sol/S_X.lean         |  <-- Private Proof Sandbox
                    +----------------------------+
```

---

## 3. Implementation Files

### 3.1 The Solution Sandbox (`Sol/S_MyTheorem.lean`)

```lean
/-
Copyright (c) 2026 EASCI Project. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
-/

import Mathlib.Analysis.Calculus.Deriv.Basic
import EASCI.Util.P2MUtil

set_option autoImplicit false
set_option maxHeartbeats 400000

namespace EASCI.Sol.S_MyTheorem

universe u

/-! Private scratchpad helper: completely invisible to downstream modules -/
private lemma helper_bound (x : Real) (hx : 0 < x) : 0 <= x^2 := by
  positivity

/-- Autonomous solution theorem. Must be proved as a standalone declaration. -/
theorem solution {alpha : Type u} [NormedAddCommGroup alpha] [NormedSpace Real alpha]
    (f : Real -> alpha) (x : Real) (hf : DifferentiableAt Real f x) :
    ContinuousAt f x := by
  exact hf.continuousAt

#print axioms solution

end EASCI.Sol.S_MyTheorem
```

### 3.2 The Interface Card (`Theorems/Thm_MyTheorem.lean`)

```lean
/-
Copyright (c) 2026 EASCI Project. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
-/

import Mathlib.Analysis.Calculus.Deriv.Basic
import EASCI.Util.P2MUtil
import EASCI.Sol.S_MyTheorem

set_option autoImplicit false

namespace EASCI.Theorems

universe u

/-- **Public Interface Card**: Differentiability implies continuity.
    Closed via `p2m_exact_reverting` against the autonomous solution. -/
theorem MyTheorem {alpha : Type u} [NormedAddCommGroup alpha] [NormedSpace Real alpha]
    (f : Real -> alpha) (x : Real) (hf : DifferentiableAt Real f x) :
    ContinuousAt f x := by
  p2m_exact_reverting @_root_.EASCI.Sol.S_MyTheorem.solution

/-- Verification guard: confirms signature equality and prevents universe collapse -/
#p2m_type_eq MyTheorem EASCI.Sol.S_MyTheorem.solution

end EASCI.Theorems
```

---

## 4. Anti-Patterns & Verification Gates

| Defect / Anti-Pattern | Root Cause | P2M Prevention Mechanism |
| :--- | :--- | :--- |
| **Downstream importing `Sol/S_*.lean`** | Violates interface boundary; exposes private helpers. | Linter / CI check: flag any `import ...Sol` outside of `Theorems/`. |
| **Universe Undergeneralization** | Prover wrote `Type` instead of `Type u`, collapsing universe polymorphism. | `#p2m_type_eq` fails with `P2M_UNDERGENERAL`. |
| **Context Instance Divergence** | Open `exact` synthesizes alternative typeclass instance path. | `p2m_exact_reverting` closes context before unification. |
| **Unassigned Metavariable Leak** | Implicit argument left unspecified in solution term. | `v.hasExprMVar` triggers compile-time error in tactic. |
| **Tactic Search Explosion in Card** | Public card inherits bloated typeclass search space. | Apply `attribute [-instance]` blocks in the interface card. |
