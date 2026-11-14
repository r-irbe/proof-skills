# `Template_KernelWHNF_SAIR.md` -- Lean 4 Kernel WHNF, SWAR & Performance Engineering (v3)

> **Status**: v3 canonical template (`@lean-sair-kernel-optimization`, superseding v1 `Template_Performance.md`).
> **Compile-tested exemplars**: [`examples/Template_SairDecide.lean`](examples/Template_SairDecide.lean) and [`examples/Template_KernelWHNF_SAIR.lean`](examples/Template_KernelWHNF_SAIR.lean).
> **Reference card**: [`../../references/cards/lean-sair-kernel-optimization-tables.md`](../../references/cards/lean-sair-kernel-optimization-tables.md).

---

## 1. Two Distinct Performance Regimes in Lean 4

Always diagnose **which engine** is slow before optimizing:

| Regime | Bottleneck Engine | Primary Diagnostics | Canonical Fixes |
| :--- | :--- | :--- | :--- |
| **A. Elaborator / Tactic Search** | Typeclass synthesis, `simp` confluence, `aesop` branching | `lean_diagnostics`, local `set_option profiler true in` | Narrow `simp only [...]`, `@[reducible]` aliases, helper cuts (`@lean-proof-refactor`), local `set_option maxHeartbeats 400000 in` (never global `0` in library code). |
| **B. Kernel WHNF / `is_def_eq` & Codegen** | `type_checker.cpp` `whnf_core`, GMP `mpz` limbs, `brecOn` / `ite` unfolding | `perf stat -e instructions:u` against Twinlit control, `lean_metrics` | Apply `SAIR-LAW-01..25B` below (`Nat.rec`, `Bool.rec`, closed top-level WHNF constants, `@[csimp]`, SWAR Kronecker packing, ZDD/ANF masks). |

---

## 2. Core SAIR Kernel WHNF Skeleton (`SAIR-LAW-01..25B`)

```lean
set_option autoImplicit false

namespace ExampleProject.KernelWHNF

/-! ### 1. Closed Top-Level Constants (`SAIR-LAW-02`, `SAIR-LAW-11`)
    Closed `def` values without loose bvars are memoized once in `m_st->m_whnf`. -/
def laneWidth : Nat := 16
def laneMask  : Nat := (1 <<< 16) - 1

/-! ### 2. Unboxed Flat State (`SAIR-LAW-09`, `SAIR-LAW-22`)
    Never nest polymorphic `Prod` `(a, (b, c))` or carry `Prop` fields in hot state. -/
structure StepState where
  acc  : Nat
  prev : Nat

/-! ### 3. Direct `cond` Dispatch & Structural Fuel Loop (`SAIR-LAW-06`, `SAIR-LAW-08`, `SAIR-LAW-10`)
    * `cond` on `Nat.ble` avoids `Decidable` dictionary synthesis (`ite`), AND unlike raw
      `Bool.rec` / `Nat.rec` (which require `noncomputable` in Lean 4's LCNF compiler),
      `cond` + structural pattern-matching compiles in BOTH kernel WHNF and native C codegen!
    * Invariant parameters (`limit`) sit outermost (`SAIR-LAW-02B`). -/
@[inline] def stepFn (limit : Nat) (st : StepState) : StepState :=
  cond (Nat.ble limit st.prev)
    st
    { acc := (st.acc + st.prev) &&& laneMask, prev := st.prev + 1 }

def runLoop (limit : Nat) : Nat → StepState → StepState
  | 0, st => st
  | k + 1, st => runLoop limit k (stepFn limit st)

def runSteps (limit steps : Nat) : Nat :=
  (runLoop limit steps { acc := 0, prev := 0 }).acc

/-! ### 4. GMP Squaring & Bitwise Shift Laws (`SAIR-LAW-13`, `SAIR-LAW-14`) -/
def fastSquareLow16 (x : Nat) : Nat :=
  let y := x          -- Shared pointer triggers GMP `mpn_sqr` fast path when multi-limb
  (y * y) &&& laneMask

/-! ### 5. Kernel-Clean Decision Gate & Twinlit PMU Control -/
macro "sair_decide" : tactic =>
  `(tactic| first | rfl | decide +kernel | decide | omega)

theorem runSteps_demo : runSteps 4 6 = 6 := by sair_decide

end ExampleProject.KernelWHNF
```

---

## 3. Twinlit PMU Differential Benchmarking Protocol

Wall-clock timing below `1.25x` is noisy under turbo/NUMA jitter. Gate kernel WHNF optimizations on user-space hardware instruction counts (`perf stat -e instructions:u`) subtracting the module-load baseline (`TwinlitControl` in [`examples/Template_SairDecide.lean`](examples/Template_SairDecide.lean)):

```bash
perf stat -r 5 -e instructions:u,cycles:u lake env lean Candidate.lean
perf stat -r 5 -e instructions:u,cycles:u lake env lean TwinlitControl.lean
```

Require:
1. Net `instructions:u` reduction `>= 5%` on quiet cores,
2. Exact `[propext, Classical.choice, Quot.sound]` axiom subset (`#print axioms`),
3. Zero `Let` zeta-expansion regressions (`SAIR-LAW-01`: inline single-use `let` bindings inside recursive lambdas; hoist multi-use or closed expressions).
