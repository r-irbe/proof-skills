/-
Copyright (c) 2026 ExampleProject Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
-/
set_option autoImplicit false

/-!
## 1. Objective
Compile-tested exemplar for `Template_KernelWHNF.md` demonstrating the
42 kernel WHNF laws (`KERNEL-LAW-01..28`), `WAVE-13 G1` Section-1/2/3 Duality,
`ADR-INV-0025` step-vs-counter dispatch, `Nat`-safe 1-bit shift overlap
(`KERNEL-LAW-18B`), and branch-free truncating low-bit cut (`KERNEL-LAW-14`).

## 2. Architecture & Bit Layout
* SWAR 2-lane 16-bit word: `[bits 0..15: lo lane | bits 16..31: hi lane]`
* `laneMask16 = 65535` (`(1 <<< 16) - 1`, raw `nat_lit` in hot defs + Section-1 `abbrev` pin).

## 3. Kernel Cost Analysis
* Zero `Prop`, `Fin`, or typeclass dictionaries (`+`, `<<<`, `&&&`) in Section 2 hot `def`s (`KERNEL-LAW-22`, `KERNEL-LAW-23`).
* `cond` avoids `ite`/`Decidable` dictionary synthesis (`KERNEL-LAW-08`) while compiling in BOTH kernel WHNF and Lean 4's LCNF code generator.

## 4. Verification Contract
* Strict 3-axiom gate via 3-rung `kernel_decide` (`rfl | decide +kernel | omega`).
-/

namespace ExampleProject.KernelWHNF

/-! ### Section 1: Cold Readable Spec Constants (`KERNEL-LAW-25B`) -/
abbrev specLaneWidth : Nat := 16
abbrev specLaneMask16 : Nat := (1 <<< specLaneWidth) - 1

/-! ### Section 2: Hot Computational Kernel (`KERNEL-LAW-02`, `08`, `14`, `15`, `18B`, `23`, `25B`) -/

/-- Closed top-level raw `nat_lit` cached in `m_st->m_whnf` (`KERNEL-LAW-02`, `25B`). -/
def laneMask16 : Nat := 65535

/-- Pack two 16-bit lanes into one unboxed `Nat` word using primitive `Nat.*` ops (`KERNEL-LAW-15`, `23`). -/
@[inline] def pack2x16 (lo hi : Nat) : Nat :=
  Nat.lor (Nat.land lo 65535) (Nat.shiftLeft (Nat.land hi 65535) 16)

@[inline] def unpackLo16 (w : Nat) : Nat := Nat.land w 65535
@[inline] def unpackHi16 (w : Nat) : Nat := Nat.land (Nat.shiftRight w 16) 65535

/-- Branch-free low-bit cut (`KERNEL-LAW-14`, Nov 11-12 contract):
    when `k <= s`, `Nat.sub k s = 0` so `1 <<< 0 - 1 = 0` without any branch! -/
@[inline] def branchFreeLowCut (w k s : Nat) : Nat :=
  Nat.land (Nat.shiftRight w s) (Nat.sub (Nat.shiftLeft 1 (Nat.sub k s)) 1)

/-- `Nat`-safe adjacent-bit overlap (`KERNEL-LAW-18B` -- never `0 - x` on `Nat`!). -/
@[inline] def adjacentBitOverlap (w : Nat) : Nat :=
  Nat.land w (Nat.shiftRight w 1)

/-- Flat monomorphic state carrying zero `Prop` fields (`KERNEL-LAW-09`, `KERNEL-LAW-22`). -/
structure AccState where
  sum : Nat
  idx : Nat

/-- `cond` on `Nat.ble` avoids `ite`/`Decidable` synthesis (`KERNEL-LAW-08`);
    `Nat.add 1 st.idx` puts small constant on LHS (`KERNEL-LAW-03`, `ADR-INV-0025`). -/
@[inline] def boundedStep (cap : Nat) (st : AccState) : AccState :=
  cond (Nat.ble cap st.idx)
    st
    { sum := Nat.add st.sum st.idx, idx := Nat.add 1 st.idx }

/-- Structural fuel loop (`KERNEL-LAW-06`, `KERNEL-LAW-10`) free of `WellFounded.fix`/`brecOn`. -/
def runBoundedLoop (cap : Nat) : Nat → AccState → AccState
  | 0, st => st
  | fuel + 1, st => runBoundedLoop cap fuel (boundedStep cap st)

def runBoundedSum (cap fuel : Nat) : Nat :=
  (runBoundedLoop cap fuel { sum := 0, idx := 0 }).sum

/-! ### Section 3: Cold Pins, `WAVE-13 G1` Abstract Bridge & `kernel_decide` Proofs -/

macro "kernel_decide" : tactic =>
  `(tactic| first | rfl | decide +kernel | omega)

/-- `KERNEL-LAW-25B` zero-cost `rfl` pin linking hot `nat_lit` to readable Section-1 `abbrev`. -/
theorem laneMask16_eq_spec : laneMask16 = specLaneMask16 := rfl

/-- `WAVE-13 G1` Cold Parametric Spec: abstract loop over arbitrary step `f`, bridged to hot kernel via `rfl`. -/
def abstractLoop {α : Type} (f : α → α) : Nat → α → α
  | 0, s => s
  | fuel + 1, s => abstractLoop f fuel (f s)

theorem runBoundedLoop_eq_abstract (cap fuel : Nat) (st : AccState) :
    runBoundedLoop cap fuel st = abstractLoop (boundedStep cap) fuel st := by
  induction fuel generalizing st with
  | zero => rfl
  | succ k ih => exact ih (boundedStep cap st)

theorem unpackLo16_pack2x16_sample : unpackLo16 (pack2x16 42 99) = 42 := by kernel_decide
theorem unpackHi16_pack2x16_sample : unpackHi16 (pack2x16 42 99) = 99 := by kernel_decide
theorem branchFreeLowCut_zero_when_le (w : Nat) : branchFreeLowCut w 4 6 = 0 := by
  show (w >>> 6) &&& 0 = 0
  exact Nat.and_zero (w >>> 6)
theorem adjacentBitOverlap_sample : adjacentBitOverlap 0b11011 = 0b01001 := by kernel_decide
theorem runBoundedSum_witness : runBoundedSum 5 8 = 10 := by kernel_decide

end ExampleProject.KernelWHNF
