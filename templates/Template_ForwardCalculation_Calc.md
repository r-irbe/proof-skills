# Template_ForwardCalculation_Calc.md: Step-by-Step Equational Calculation with Show Horizons

> **Status:** Production template for proof-heavy modules in `proof-skills`.
> **Audience:** AI provers and formalization engineers writing non-trivial equational chains.
> **Pattern Source:** Extracted from the 29,511-theorem Fermat's Last Theorem Lean 4 corpus (`P2M/Sol/`).

---

## 1. When to Use This Template

Apply `Template_ForwardCalculation_Calc` when:
- Proving an equality or inequality (`=`, `<=`, `<`, `subset`, `<->`) that requires more than two intermediate transformation steps.
- Working with complex algebraic structures (polynomials, differential operators, modular forms, tensor products) where `ring` or `simp` times out or fails to find a path.
- Encountering **elaborator divergence** or **unassigned metavariables** during rewrites.
- Establishing intermediate equalities inside `have` blocks where every step must be independently auditable.

**Do NOT use for:**
- Single-step definitional equalities -> use `rfl` or term mode.
- Pure linear arithmetic solvable in one shot -> use `omega` (Nat/Int) or `linarith` (Real/Rat).
- Pure logic / structural proofs -> use `Template_ProofStrategy.md` or `obtain`.

---

## 2. Structural Principles

### 2.1 The "Show Horizon" Invariant
When rewriting subterms in a large goal, Lean's higher-order unification can match unintended subexpressions or fail due to implicit coercions. An inline **show horizon** bounds the scope of elaboration:
```lean
rw [show <subterm_lhs> = <subterm_rhs> by <tactic>]
```
This forces Lean to elaborate `<subterm_lhs> = <subterm_rhs>` in isolation before attempting the outer rewrite, eliminating ambiguity.

### 2.2 Rigid `calc` Formatting
Every step in a `calc` block must explicitly declare its right-hand side and justification:
```lean
calc lhs = mid1 := by <justification1>
  _ = mid2 := by <justification2>
  _ = rhs := by <justification3>
```
Never leave intermediate expressions as wildcards (`_ = _ := ...`). Explicit intermediate types anchor the elaborator.

---

## 3. Full Production Template

```lean
/-
Copyright (c) <YEAR> <Project> Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: <Project> Contributors
SPDX-License-Identifier: Apache-2.0
-/

import Mathlib.Algebra.Ring.Basic
import Mathlib.Data.Polynomial.Basic
import Mathlib.Data.Polynomial.Derivative

set_option autoImplicit false

namespace <Project>.<Module>

open Polynomial

variable {R : Type*} [CommRing R]

/-- **Operator Commutation Identity** [<Reference>].
    Demonstrates rigid `calc` chaining with inline `show` horizons and explicit rewriting. -/
theorem derivative_pow_mul_comm (f : R[X]) (n : Nat) :
    derivative (f ^ (n + 1)) = (n + 1 : R[X]) * f ^ n * derivative f := by
  /- Section 1. Forward induction / base setup -/
  induction n with
  | zero =>
    /- Base case: n = 0 -/
    calc derivative (f ^ (0 + 1)) = derivative f := by rw [zero_add, pow_one]
      _ = 1 * 1 * derivative f := by rw [mul_one, one_mul]
      _ = (0 + 1 : R[X]) * f ^ 0 * derivative f := by
        rw [show (0 + 1 : R[X]) = 1 by ring, show f ^ 0 = 1 by exact pow_zero f]

  | succ k ih =>
    /- Inductive step: k + 1 -/
    /- Establish inductive hypothesis decomposition -/
    have h_split : f ^ (k + 1 + 1) = f ^ (k + 1) * f := by
      rw [pow_succ]

    /- Step-by-step equational calculation with explicit show horizons -/
    calc derivative (f ^ (k + 1 + 1))
        = derivative (f ^ (k + 1) * f) := by rw [h_split]
      _ = derivative (f ^ (k + 1)) * f + f ^ (k + 1) * derivative f := by
        exact derivative_mul (f ^ (k + 1)) f
      _ = ((k + 1 : R[X]) * f ^ k * derivative f) * f + f ^ (k + 1) * derivative f := by
        rw [ih]
      _ = (k + 1 : R[X]) * (f ^ k * f) * derivative f + f ^ (k + 1) * derivative f := by
        ring
      _ = (k + 1 : R[X]) * f ^ (k + 1) * derivative f + 1 * f ^ (k + 1) * derivative f := by
        rw [show f ^ k * f = f ^ (k + 1) by exact (pow_succ f k).symm]
        rw [show f ^ (k + 1) * derivative f = 1 * f ^ (k + 1) * derivative f by ring]
      _ = ((k + 1 : R[X]) + 1) * f ^ (k + 1) * derivative f := by
        ring
      _ = (k + 1 + 1 : R[X]) * f ^ (k + 1) * derivative f := by
        rw [show (k + 1 : R[X]) + 1 = (k + 1 + 1 : R[X]) by ring]

end <Project>.<Module>
```

---

## 4. Anti-Patterns Checklist

| Anti-Pattern | Why It Fails | Correct FLT Pattern |
| :--- | :--- | :--- |
| **Monolithic `calc ... := by simp; ring`** | `simp` drifts and unfolds non-target definitions; `ring` fails if terms are unbundled. | One equational transformation per line; explicit target term specified. |
| **Unanchored subterm rewrite `rw [h]`** | If `h` matches in multiple places, Lean picks the first syntactic match (often wrong). | Use `conv_lhs` or insert `show <old> = <new> by rw [h]` to target exactly one occurrence. |
| **Skipping intermediate types** | Leaving intermediate terms implicit forces higher-order unification across the whole chain. | Write out each intermediate line in full, letting Lean's type checker verify each step locally. |
| **Mixing `<` and `<=` without explicit transitivity** | Transitivity typeclasses for mixed orders frequently trigger elaborator timeouts. | Break into separate `have` bounds and close with `lt_of_lt_of_le` or `calc` using explicit relations. |
```

---

## 2.2 `Template_ClosedTermReversion.md`

```markdown
