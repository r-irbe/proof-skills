# `Template_KernelWHNF_SAIR.md` -- Lean 4 Kernel WHNF, SWAR & Duality Engineering (v3.1)

> **Status**: v3.1 canonical template (`@lean-sair-kernel-optimization`, aligned with all 39 laws `SAIR-LAW-01..25B`, `ADR-INV-0025`, and `WAVE-13 G1`).
> **Compile-tested exemplars**: [`examples/Template_SairDecide.lean`](examples/Template_SairDecide.lean), [`examples/Template_KernelWHNF_SAIR.lean`](examples/Template_KernelWHNF_SAIR.lean), and [`examples/Template_ProofCarryingCodegen.lean`](examples/Template_ProofCarryingCodegen.lean).
> **Reference card & handbook**: [`../../references/cards/lean-sair-kernel-optimization-tables.md`](../../references/cards/lean-sair-kernel-optimization-tables.md), [`../../references/handbooks/lean-sair-kernel-optimization-handbook.md`](../../references/handbooks/lean-sair-kernel-optimization-handbook.md).

---

## 1. Two Distinct Performance Regimes in Lean 4

Always diagnose **which engine** is slow before optimizing:

| Regime | Bottleneck Engine | Primary Diagnostics | Canonical Fixes |
| :--- | :--- | :--- | :--- |
| **A. Elaborator / Tactic Search** | Typeclass synthesis, `simp` confluence, `aesop` branching | `lean_diagnostics`, local `set_option profiler true in` | Narrow `simp only [...]`, `@[reducible]` aliases, helper cuts (`@lean-proof-refactor`), local `set_option maxHeartbeats 400000 in` (never global `0` in library code). |
| **B. Kernel WHNF / `is_def_eq` & Codegen** | `type_checker.cpp` `whnf_core`, GMP `mpz` limbs, `brecOn` / `ite` / dictionary unfolding | `perf stat -e instructions:u` sum-of-medians-of-three (`real - twinlit`), `lean_metrics` | Apply `SAIR-LAW-01..25B` + `WAVE-13 G1` Section-1/2/3 split (`@Nat.rec` / `cond`, primitive `Nat.*` ops, raw `nat_lit` pins, width-2 SWAR, ZDD/ANF masks). |

---

## 2. Canonical Four-Section Header & Section-1/2/3 Duality Skeleton

Every SAIR / WHNF kernel module uses the 4-section doc header (`SAIR-LAW-25`) and strictly separates **Section 1 (Cold Spec `abbrev`s)**, **Section 2 (Monomorphic Hot `def`s)**, and **Section 3 (Cold Parametric Proofs & `rfl` Pins)** (`SAIR-LAW-22B`, `SAIR-LAW-25B`, `WAVE-13 G1`):

```lean
set_option autoImplicit false

/-!
## 1. Objective
<One-sentence problem & target complexity.>

## 2. Architecture & Bit Layout
* SWAR 2-lane 16-bit word: `[bits 0..15: lo lane | bits 16..31: hi lane]`

## 3. Kernel Cost Analysis
* Zero `Prop`/`Fin` (`SAIR-LAW-22`) and zero typeclass dictionaries (`SAIR-LAW-23`) in Section 2.
* `WAVE-13 G1`: hot `boundedStep` is concrete (avoiding the `1,600x..3,345x` parametric penalty);
  parametric reasoning lives in Section 3 (`<= 1%` cost via `rfl` bridge).

## 4. Verification Contract
* Strict 3-axiom gate (`[propext, Classical.choice, Quot.sound]`) via 3-rung `sair_decide`.
-/

namespace ExampleProject.KernelWHNF

/-! ### Section 1: Cold Readable Spec Constants (`SAIR-LAW-25B`) -/
abbrev specLaneWidth : Nat := 16
abbrev specLaneMask16 : Nat := (1 <<< specLaneWidth) - 1

/-! ### Section 2: Hot Computational Kernel (`SAIR-LAW-02`, `08`, `14`, `15`, `18B`, `23`, `25B`) -/

/-- Closed raw `nat_lit` cached in `m_st->m_whnf` (never unfold `abbrev` formulas in hot loops!). -/
def laneMask16 : Nat := 65535

@[inline] def pack2x16 (lo hi : Nat) : Nat :=
  Nat.lor (Nat.land lo 65535) (Nat.shiftLeft (Nat.land hi 65535) 16)

/-- Branch-free low-bit cut (`SAIR-LAW-14`): `Nat.sub k s = 0` when `k <= s` -> `0` mask without branching. -/
@[inline] def branchFreeLowCut (w k s : Nat) : Nat :=
  Nat.land (Nat.shiftRight w s) (Nat.sub (Nat.shiftLeft 1 (Nat.sub k s)) 1)

/-- `Nat`-safe adjacent-bit overlap (`SAIR-LAW-18B` -- NEVER write `0 - x` on `Nat`!). -/
@[inline] def adjacentBitOverlap (w : Nat) : Nat :=
  Nat.land w (Nat.shiftRight w 1)

structure AccState where
  sum : Nat
  idx : Nat

/-- `cond` avoids `ite`/`Decidable` synthesis (`SAIR-LAW-08`) and compiles in both WHNF and LCNF;
    `Nat.add 1 st.idx` keeps small constant on LHS (`SAIR-LAW-03`, `ADR-INV-0025`). -/
@[inline] def boundedStep (cap : Nat) (st : AccState) : AccState :=
  cond (Nat.ble cap st.idx)
    st
    { sum := Nat.add st.sum st.idx, idx := Nat.add 1 st.idx }

def runBoundedLoop (cap : Nat) : Nat → AccState → AccState
  | 0, st => st
  | fuel + 1, st => runBoundedLoop cap fuel (boundedStep cap st)

def runBoundedSum (cap fuel : Nat) : Nat :=
  (runBoundedLoop cap fuel { sum := 0, idx := 0 }).sum

/-! ### Section 3: Cold Pins & Strict 3-Rung `sair_decide` Proofs -/

macro "sair_decide" : tactic =>
  `(tactic| first | rfl | decide +kernel | omega)

theorem laneMask16_eq_spec : laneMask16 = specLaneMask16 := rfl
theorem runBoundedSum_witness : runBoundedSum 5 8 = 10 := by sair_decide

end ExampleProject.KernelWHNF
```

---

## 3. Sum-of-Medians-of-Three `twinlit` PMU Benchmarking Protocol

1. **Single-Consumer Isolation Guard (`ADR-INV-0025`)**: Never accept a micro-optimization measured only on an isolated helper; benchmark the **complete consumer theorem** end-to-end.
2. **Per-Slot Medians of Three**: For each scale slot `i in 1..K`, execute 3 interleaved runs of `Candidate_i.lean` and `TwinlitControl_i.lean` (`(impl n_i = impl n_i) ∧ (ans_i = ans_i)`):
   ```bash
   perf stat -e instructions:u lake env lean Candidate_slot1.lean
   perf stat -e instructions:u lake env lean TwinlitControl_slot1.lean
   ```
   Compute `delta_i = median_3(Candidate_i) - median_3(TwinlitControl_i)` and evaluate total score **`S = sum_i delta_i`**.
3. **Hard Gates**:
   - `#print axioms` subset of `[propext, Classical.choice, Quot.sound]` (`0` `Lean.ofReduceBool`),
   - Multi-limb `let y := expr; Nat.mul y y` (`SAIR-LAW-13`) gated to `>= 30` GMP limbs (`NR-076`),
   - Zero `0 - x` underflow bugs on `Nat` (`SAIR-LAW-18B`).
