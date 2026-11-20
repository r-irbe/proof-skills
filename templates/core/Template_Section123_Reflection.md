# `Template_Section123_Reflection.md` -- Section 1/2/3 Split & Computational Reflection Template

> **Status**: Canonical template (`@lean-proof-refactor`, aligned with `KERNEL-LAW-01..31`, `KERNEL-LAW-22`, `KERNEL-LAW-28`).

---

## 1. When to Use This Template

Use `Template_Section123_Reflection` whenever:
1. Proof scripts for iterative or fixed-schedule algorithms exceed 500 lines due to repetitive case splitting or tactic unfolding.
2. An algorithm must achieve maximal Lean 4 kernel WHNF reduction performance with zero heap allocation and zero `Prop` witness overhead.
3. Verification must adhere to the strict 3-axiom ceiling (`propext`, `Classical.choice`, `Quot.sound`) without `native_decide`, `bv_decide`, or `sorry`.

---

## 2. Canonical Structure

```lean
set_option autoImplicit false

namespace SolutionModule

/-!
# Module Overview: Section 1/2/3 Abstraction-Concrete Architecture
* Section 1: Derived Structural Constants, Motives & Syntax
* Section 2: Concrete Kernel Implementation & Fast-Path Twins
* Section 3: Universal Correctness Theorems & Reflective Proofs
-/

/-! ==================================================================== -/
/-! ### Section 1: Derived Structural Constants & Inductive Motives      -/
/-! ==================================================================== -/

inductive SynExpr where
  | val : Nat -> SynExpr
  | op  : SynExpr -> SynExpr -> SynExpr
  deriving Repr, DecidableEq

def denoteSyn : SynExpr -> Nat
  | .val n => n
  | .op a b => denoteSyn a + denoteSyn b

def normSyn : SynExpr -> SynExpr
  | .op (.val a) (.val b) => .val (a + b)
  | .op a b =>
      match normSyn a, normSyn b with
      | .val x, .val y => .val (x + y)
      | a', b' => .op a' b'
  | other => other

theorem normSyn_sound (e : SynExpr) : denoteSyn (normSyn e) = denoteSyn e := by
  induction e with
  | val n => rfl
  | op a b iha ihb =>
      dsimp [normSyn]
      split <;> (try dsimp [denoteSyn]; omega)
      rename_i x y hx hy
      dsimp [denoteSyn]
      rw [<- iha, <- ihb, hx, hy]

/-! ==================================================================== -/
/-! ### Section 2: Concrete Kernel Implementation & Fast Twins           -/
/-! ==================================================================== -/

/--
Concrete kernel implementation.
* Pure unboxed scalar state (< 2^63 lean_box tagged pointers).
* ZERO Prop witnesses in the runtime cone (KERNEL-LAW-22).
-/
@[inline] def impl (n : Nat) : Nat :=
  @Nat.rec (fun _ => Nat) 0 (fun _ acc => acc + 1) n

@[csimp] def impl_csimp_twin : @impl = @impl := rfl

/-! ==================================================================== -/
/-! ### Section 3: Universal Correctness & Reflection Bridge             -/
/-! ==================================================================== -/

theorem impl_correct (n : Nat) : impl n = n := by
  induction n with
  | zero => rfl
  | succ k ih =>
      dsimp [impl]
      rw [ih]
```

---

## 3. Quality Verification Checklist

- [ ] Section 1 contains only syntax, denotation, and cold constants.
- [ ] Section 2 contains zero `Prop` terms, witnesses, or tactics.
- [ ] Section 3 proves universal correctness with permitted axioms only (`propext`, `Classical.choice`, `Quot.sound`).
- [ ] Zero usage of `native_decide`, `bv_decide`, `sorry`, `partial`, or `@[extern]`.
