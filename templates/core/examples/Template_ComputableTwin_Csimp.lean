/-
Copyright (c) 2026 ExampleProject Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
-/
set_option autoImplicit false

/-!
# `Template_ComputableTwin_Csimp` -- Compile-Tested Exemplar

Demonstrates the Abstraction-Concrete Duality (`SAIR-LAW-07`, `SAIR-LAW-14`, `SAIR-LAW-22`):
1. `triangularSpec`: clean structural-recursion specification for `Prop` proofs.
2. `triangularFast`: concrete bitwise shift implementation without `Prop` runtime witnesses.
3. `triangularSpec_csimp`: `@[csimp]` equivalence theorem bridging spec to fast codegen.
-/

namespace ExampleProject.ComputableTwin

/-- Proof-friendly specification over `Nat`. -/
def triangularSpec : Nat → Nat
  | 0 => 0
  | n + 1 => (n + 1) + triangularSpec n

/-- Hardware-friendly implementation using `>>> 1` (`SAIR-LAW-14`). -/
@[inline] def triangularFast (n : Nat) : Nat :=
  (n * (n + 1)) >>> 1

theorem two_mul_triangularSpec (n : Nat) :
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

theorem triangularSpec_eq_fast (n : Nat) :
    triangularSpec n = triangularFast n := by
  have h := two_mul_triangularSpec n
  simp only [triangularFast, Nat.shiftRight_eq_div_pow]
  omega

@[csimp] theorem triangularSpec_csimp :
    @triangularSpec = @triangularFast := by
  funext n
  exact triangularSpec_eq_fast n

/-- Non-vacuity and kernel reduction witness. -/
theorem triangularFast_100 : triangularFast 100 = 5050 := rfl

end ExampleProject.ComputableTwin
