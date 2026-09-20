# Template_ClosedTermReversion.md: Context Reversion for Modular Proof Decoupling

> **Status:** Production template for cleanroom formalization and interface decoupling in `proof-skills`.
> **Audience:** Provers building large multi-module repositories or automated proof pipelines.
> **Pattern Source:** Extracted from the `P2M/Util.lean` and `Theorems/` infrastructure in the FLT Lean 4 repository.

---

## 1. When to Use This Template

Apply `Template_ClosedTermReversion` when:
- Separating **public theorem specifications** (e.g. `Theorems/Thm_*.lean`) from **private proof implementations** (e.g. `Sol/S_*.lean`).
- Re-exporting an autonomous proof term where the caller's local context contains variables, binders, or typeclass instances in a slightly different order or universe configuration.
- Standard `exact <term>` fails with:
  - *"unassigned metavariables remain"*
  - *"type mismatch: cannot unify local instance with synthesized instance"*
  - *"universe level parameter mismatch"*.
- Building multi-agent verification pipelines where one agent writes the theorem specification and another generates a self-contained proof term.

**Do NOT use for:**
- Small monolithic modules where proofs are inline and <= 50 lines.
- Pure definitions or inductive declarations.

---

## 2. The Architectural Principle

In large formalization projects, tying a theorem's public interface directly to its proof script creates high coupling:
1. Re-ordering a `variable` declaration breaks downstream proofs.
2. Inferred implicit binders drift between Lean versions.
3. Complex proof scripts pollute the environment namespace.

FLT solves this by **reverting the entire local context into a closed Pi-type** before assigning the autonomous solution:
```lean
/- Public Interface: -/
theorem MyTheorem {alpha : Type*} [Group alpha] (a b : alpha) : a * b = b * a := by
  p2m_exact_reverting @_root_.MySol.solution
```
The custom tactic reverts all local variables `alpha, [Group alpha], a, b`, transforming the open goal into `forall  {alpha} [Group alpha] (a b : alpha), a * b = b * a`. It then verifies that `@_root_.MySol.solution` matches this closed signature definitionally and assigns it in one shot.

---

## 3. Production Implementation & Template

### 3.1 The Reversion Tactic (`Util/Reversion.lean`)

```lean
import Lean

open Lean Elab Tactic Meta

/-- Reverts all user-visible local context variables into a closed Pi-type
    and assigns the provided term ensuring type confluence. -/
elab "exact_reverting " e:term : tactic => do
  let g <- getMainGoal
  let lctx := (<- g.getDecl).lctx
  /- Collect all free variables that are not implementation details -/
  let fvars := lctx.foldl (init := #[]) fun acc d =>
    if d.isImplementationDetail then acc else acc.push d.fvarId
  /- Revert all variables preserving declaration order and clearing aux decls -/
  let (_, g') <- g.revert fvars (preserveOrder := true) (clearAuxDeclsInsteadOfRevert := true)
  g'.withContext do
    let tgt <- g'.getType
    /- Elaborate the solution term ensuring it strictly matches the closed target -/
    let v <- Term.withSynthesize <| elabTermEnsuringType e tgt
    let v <- instantiateMVars v
    if v.hasExprMVar then
      throwError "exact_reverting: unassigned metavariables remain in {v}"
    g'.assign v
  replaceMainGoal []
```

### 3.2 The Autonomous Solution Module (`Proofs/Sol_Example.lean`)

```lean
/-
Copyright (c) <YEAR> <Project> Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
SPDX-License-Identifier: Apache-2.0
-/

import Mathlib.Algebra.Group.Basic

set_option autoImplicit false

namespace <Project>.Sol.Example

universe u

/-- Autonomous solution theorem. Completely self-contained closed term. -/
theorem solution {G : Type u} [CommGroup G] (x y : G) :
    x * y * (x * y)^-^1 = 1 := by
  have h_inv : (x * y)^-^1 = y^-^1 * x^-^1 := mul_inv_rev x y
  rw [h_inv, mul_assoc x y, <- mul_assoc y (y^-^1), mul_right_inv, one_mul, mul_right_inv]

#print axioms solution

end <Project>.Sol.Example
```

### 3.3 The Public Specification Module (`Theorems/Thm_Example.lean`)

```lean
/-
Copyright (c) <YEAR> <Project> Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
SPDX-License-Identifier: Apache-2.0
-/

import Mathlib.Algebra.Group.Basic
import <Project>.Util.Reversion
import <Project>.Proofs.Sol_Example

set_option autoImplicit false

namespace <Project>.Theorems

universe u

/-- **Public Interface Theorem** [<Reference>].
    Closed via context reversion to guarantee zero instance cache divergence. -/
theorem group_inv_mul_cancel {G : Type u} [CommGroup G] (x y : G) :
    x * y * (x * y)^-^1 = 1 := by
  exact_reverting @_root_.<Project>.Sol.Example.solution

end <Project>.Theorems
```

---

## 4. Anti-Patterns Checklist

| Anti-Pattern | Why It Fails | Correct Reversion Pattern |
| :--- | :--- | :--- |
| **`exact solution x y` in open context** | Re-elaborates typeclass search for `[CommGroup G]`, often choosing a diverging instance path. | Use `exact_reverting @_root_...solution` to match the closed Pi-type directly. |
| **Omission of `@_root_` prefix** | Relative namespace resolution may find a local declaration or fail in deep module hierarchies. | Always use fully qualified `@_root_.Namespace.solution`. |
| **Universe Under-Generalization** | Solution proved for `Type` while specification requires `Type u`. | Use `universe u` explicitly in both specification and solution files. |
| **Permuted Binder Order** | If the specification lists `(x y : G)` but solution lists `(y x : G)`, `revert` fails with type mismatch. | Ensure binder declaration order in the public header matches the solution signature. |
```

---

## 2.3 `Template_ConfluenceSimpOnly.md`

```markdown
