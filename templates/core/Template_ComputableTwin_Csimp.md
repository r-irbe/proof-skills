# `Template_ComputableTwin_Csimp.md` -- Abstraction-Concrete Duality & `@[csimp]` Bridge (v3)

> **Status**: v3 canonical template (`@lean-proof-refactor` + `@lean-sair-kernel-optimization`, `SAIR-LAW-06..10`, `SAIR-LAW-22`).
> **Compile-tested exemplar**: [`examples/Template_ComputableTwin_Csimp.lean`](examples/Template_ComputableTwin_Csimp.lean).

---

## 1. When to Use This Template

Use `Template_ComputableTwin_Csimp` whenever a concept must be **both**:
1. **Easy to reason about in `Prop` proofs** (clean structural induction, algebraic compositionality, zero bit-twiddling noise), AND
2. **Fast in kernel WHNF reduction (`rfl` / `decide +kernel`) or compiled C++/SIMD/SIMT codegen** (tail-recursive accumulator, unboxed flat state, `Nat.rec`/`Bool.rec`, SWAR word packing, or ZDD bitmasks).

---

## 2. Canonical Four-Block Architecture

```lean
set_option autoImplicit false

namespace ExampleProject.ComputableTwin

/-! ### §1 Abstract Specification (`specFn`) -- Proof-Friendly Layer -/

/-- Mathematical specification written for effortless structural induction. -/
def triangularSpec : Nat → Nat
  | 0 => 0
  | n + 1 => (n + 1) + triangularSpec n

/-! ### §2 Concrete Implementation (`fastFn`) -- Hardware / WHNF Layer
    * Zero `Prop` witnesses in runtime cone (`SAIR-LAW-22`)
    * Tail-recursive / structural `Nat.rec` or closed formula (`SAIR-LAW-06`, `SAIR-LAW-10`)
    * Bitwise `>>> 1` instead of `/ 2` in hot loops (`SAIR-LAW-14`) -/

@[inline] def triangularFast (n : Nat) : Nat :=
  (n * (n + 1)) >>> 1

/-! ### §3 Equivalence Proof & `@[csimp]` Compiler Bridge (`SAIR-LAW-07`) -/

theorem triangularSpec_eq_mul_div (n : Nat) :
    2 * triangularSpec n = n * (n + 1) := by
  induction n with
  | zero => rfl
  | succ k ih =>
    calc
      2 * triangularSpec (k + 1)
        = 2 * (k + 1) + 2 * triangularSpec k := by simp only [triangularSpec, Nat.mul_add]
      _ = 2 * (k + 1) + k * (k + 1) := by rw [ih]
      _ = (2 + k) * (k + 1) := by rw [← Nat.add_mul]
      _ = (k + 1) * (k + 2) := by rw [Nat.add_comm 2 k, Nat.mul_comm]

theorem triangularSpec_pointwise (n : Nat) :
    triangularSpec n = triangularFast n := by
  have h := triangularSpec_eq_mul_div n
  simp only [triangularFast, Nat.shiftRight_eq_div_pow]
  omega

/-- Compiler & `#eval` automatically rewrite `triangularSpec` -> `triangularFast`,
    while all downstream `Prop` theorems continue reasoning over `triangularSpec`! -/
@[csimp] theorem triangularSpec_csimp :
    @triangularSpec = @triangularFast := by
  funext n
  exact triangularSpec_pointwise n

/-! ### §4 Abstract Compositional Theorems + Non-Vacuity Witness -/

@[grind =] theorem triangularSpec_succ (n : Nat) :
    triangularSpec (n + 1) = triangularSpec n + n + 1 := by
  simp only [triangularSpec]
  omega

/-- Non-vacuity & kernel reduction sanity check (`0` extra axioms). -/
example : triangularFast 100 = 5050 := rfl

end ExampleProject.ComputableTwin
```

---

## 3. Checklist Before Handoff to `auditor`

- [ ] `specFn` carries zero bit-packing strides, fuel parameters, or accumulator noise.
- [ ] `fastFn` carries zero `Prop` arguments, `Subtype` wrappers, `Decidable`/`ite` dictionaries, or `WellFounded.fix`.
- [ ] `@[csimp] theorem specFn_csimp : @specFn = @fastFn` compiles with `0 sorry` and transitive axioms `⊆ [propext, Classical.choice, Quot.sound]`.
- [ ] Kernel WHNF hot paths invoke `fastFn` directly (note: `@[csimp]` rewrites compiled LLVM/C codegen, whereas inside pure kernel `rfl`/`decide +kernel` proofs you rewrite via `rw [specFn_pointwise]` once at the top of the witness).
