set_option autoImplicit false

/-
  templates/core/examples/Template_SairDecide.lean
  Kernel-clean 3-rung decision macro (`sair_decide`) for Core-only and SAIR lanes.
  Never invokes `native_decide` or `bv_decide` (which introduce `Lean.ofReduceBool`).
  Scoped Unicode policy (INV-001; typographic-free by default).
-/

/--
  `sair_decide` attempts to close a concrete decidable or linear-arithmetic goal
  using only the 3 kernel-verified rungs that preserve the strict 3-axiom gate
  (`[propext, Classical.choice, Quot.sound]`):
    1. `rfl` (definitional equality in WHNF, 0 Decidable dictionary overhead)
    2. `decide +kernel` (kernel-reduced Boolean reflection, bypassing elaborator WHNF)
    3. `omega` (verified Presburger linear integer/natural arithmetic)
-/
macro "sair_decide" : tactic =>
  `(tactic| first
    | rfl
    | decide +kernel
    | omega)

/--
  `TwinlitControl` packages a target equality `x = x` alongside its answer-literal
  control `v = v` so `real - twinlit` PMU differentials cancel startup, elaboration,
  AND decimal literal parsing (`sum-of-per-slot-medians-of-three`).
-/
def TwinlitControl (α β : Type) (x : α) (v : β) : Prop :=
  (x = x) ∧ (v = v)

theorem twinlit_control_rfl {α β : Type} (x : α) (v : β) : TwinlitControl α β x v :=
  ⟨rfl, rfl⟩

-- Sanity checks across all 3 rungs:
example : 2 + 3 = 5 := by sair_decide
example : decide (3 < 7) = true := by sair_decide
example (n : Nat) (h : n < 10) : n ≤ 10 := by sair_decide
