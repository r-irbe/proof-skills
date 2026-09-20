# Template_ConfluenceSimpOnly.md: Defensive Simplification Avoiding Unbundling Traps and Cycles

> **Status:** Production template for safe, terminating equational simplification in `proof-skills`.
> **Audience:** Provers working with Mathlib bundled morphisms, topological structures, or algebra maps.
> **Pattern Source:** Extracted from the 10,426 `simp only` occurrences across FLT `P2M/Sol/`.

---

## 1. When to Use This Template

Apply `Template_ConfluenceSimpOnly` when:
- Normalizing expressions involving bundled structures (`RingHom`, `ContinuousMap`, `LinearMap`, `AlgHom`, `Submodule`).
- Bare `simp` causes **unbundling traps**: converting `f x` into `f.toFun x` or `Subtype.val`, breaking downstream algebraic typeclasses.
- Bare `simp` enters an infinite loop or exceeds maximum heartbeats.
- Simplifying across boundary morphisms (`map_add`, `map_mul`, `map_inv0`, `smul_eq_mul`).

**Do NOT use for:**
- Pure polynomial expansion -> use `ring` or `ring_nf`.
- Single definitional unfolding -> use `dsimp only [def_name]` or `change`.
- Arbitrary exploratory search in finished code -> harvest with `simp?` then enforce this template.

---

## 2. The 4-Phase Confluent Simplification Architecture

To guarantee termination, confluence, and structure preservation, simplification must follow four strict phases:

```text
+-----------------------------------------------------------------------------+
| Phase 1: Local Definition Unfolding                                         |
|          Unfold domain-specific wrappers (set, abbrev, local definitions)   |
|          `simp only [my_def, local_proj]`                                   |
+-----------------------------------------------------------------------------+
                                      v
+-----------------------------------------------------------------------------+
| Phase 2: Morphism Preservation (Push Morphisms Inside)                      |
|          Distribute bundled maps over operations WITHOUT unbundling toFun   |
|          `simp only [map_add, map_mul, map_pow, map_inv0]`                  |
+-----------------------------------------------------------------------------+
                                      v
+-----------------------------------------------------------------------------+
| Phase 3: Canonical Scalar / Action Reduction                                |
|          Standardize operations into canonical algebraic operators          |
|          `simp only [smul_eq_mul, mul_one, one_mul, add_zero, zero_add]`    |
+-----------------------------------------------------------------------------+
                                      v
+-----------------------------------------------------------------------------+
| Phase 4: Domain Terminal Closers                                            |
|          Close residual identities without cycling                          |
|          `exact`, `ring`, `omega`, or `linarith`                            |
+-----------------------------------------------------------------------------+
```

---

## 3. Full Production Template

```lean
/-
Copyright (c) <YEAR> <Project> Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
SPDX-License-Identifier: Apache-2.0
-/

import Mathlib.Algebra.Algebra.Hom
import Mathlib.Algebra.Ring.Hom.Basic

set_option autoImplicit false

namespace <Project>.<Module>

variable {R A B : Type*} [CommRing R] [CommRing A] [CommRing B]
variable [Algebra R A] [Algebra R B]

/-- **Morphism Image Normalization** [<Reference>].
    Demonstrates confluent, anti-unbundling `simp only` workflow. -/
theorem algHom_eval_normalForm (phi : A ->_a[R] B) (x y : A) (n : Nat) :
    phi (x * y + algebraMap R A 1) ^ n = (phi x * phi y + 1) ^ n := by
  /- Phase 1 & 2: Push algebraic homomorphism across operators -/
  /- DO NOT include phi.toRingHom or toFun: keeps phi bundled! -/
  have h_inner : phi (x * y + algebraMap R A 1) = phi x * phi y + 1 := by
    calc phi (x * y + algebraMap R A 1)
        = phi (x * y) + phi (algebraMap R A 1) := by
          /- Strict preservation of homomorphism -/
          simp only [map_add]
      _ = phi x * phi y + phi (algebraMap R A 1) := by
          simp only [map_mul]
      _ = phi x * phi y + 1 := by
          /- Commutes with base scalar ring map -/
          simp only [AlgHom.commutes, map_one]

  /- Phase 3 & 4: Substitute normalized base and close -/
  rw [h_inner]

end <Project>.<Module>
```

---

## 4. Anti-Patterns Checklist

| Anti-Pattern | Manifestation in Lean 4 | Preventive Discipline |
| :--- | :--- | :--- |
| **Bare `simp` on Bundled Maps** | `phi (x + y)` becomes `phi.toFun x + phi.toFun y` or `phi.toRingHom.toMonoidHom...`. Downstream `Algebra` lemmas fail. | NEVER use bare `simp`. Explicitly specify `simp only [map_add, map_mul]`. |
| **Cyclical Commutativity Pairs** | `simp only [mul_comm, mul_assoc]` produces an infinite rewriting loop or heartbeat timeout. | Never pair bidirectional symmetries. Use `ring` for AC-normalization. |
| **Wildcard Simplification `simp [*]`** | Hypotheses containing equations get rewritten into each other uncontrollably, erasing critical assumptions. | Isolate target hypotheses: `simp only [h1] at h2`. |
| **Mixing `coe` and `val` lemmas** | `simp only [Subtype.val, Subtype.coe_mk]` causes bouncing between coercions and raw projection. | Pick Mathlib's canonical form (`^x` via coercions) and stick to coercion lemmas (`Subtype.coe_inj`). |
```

---

