/-
  templates/Template_SairDecide.lean
  Kernel-clean 3-rung decision macro (`sair_decide`) for Core-only and SAIR lanes.
  Never invokes `native_decide` or `bv_decide` (which introduce `Lean.ofReduceBool`).
  Scoped Unicode policy (INV-001; typographic-free by default).
-/

/--
  `sair_decide` attempts to close a concrete decidable or linear-arithmetic goal
  using only kernel-verified tactics that preserve the strict 3-axiom gate
  (`[propext, Classical.choice, Quot.sound]`):
    1. `rfl` (definitional equality in WHNF, 0 Decidable dictionary overhead)
    2. `decide +kernel` (kernel-reduced Boolean reflection)
    3. `omega` (verified Presburger linear integer/natural arithmetic)
-/
macro "sair_decide" : tactic =>
  `(tactic| first
    | rfl
    | decide +kernel
    | decide
    | omega)

/--
  `twinlit_pair lhs rhs v` packages a target equality `lhs = rhs` alongside its
  twinlit control `(lhs = lhs) /\ (v = v)` for PMU differential measurement.
-/
def TwinlitControl (α β : Type) (x : α) (v : β) : Prop :=
  (x = x) /\ (v = v)

theorem twinlit_control_rfl {α β : Type} (x : α) (v : β) : TwinlitControl α β x v :=
  ⟨rfl, rfl⟩

-- Sanity checks:
example : 2 + 3 = 5 := by sair_decide
example (n : Nat) (h : n < 10) : n <= 10 := by sair_decide
