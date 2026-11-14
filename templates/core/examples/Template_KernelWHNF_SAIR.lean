/-
Copyright (c) 2026 ExampleProject Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
-/
set_option autoImplicit false

/-!
# `Template_KernelWHNF_SAIR` -- Compile-Tested Exemplar

Demonstrates closed top-level WHNF constants (`SAIR-LAW-02`, `SAIR-LAW-11`),
unboxed flat `structure` state (`SAIR-LAW-09`, `SAIR-LAW-22`), `cond` / `match`
boolean dispatch without `Decidable` dictionary synthesis (`SAIR-LAW-08`, and
unlike raw `Bool.rec`, supported by Lean 4's LCNF native compiler!), structural
tail recursion (`SAIR-LAW-06`, `SAIR-LAW-10`), and SWAR 2-lane 16-bit word
packing (`SAIR-LAW-15`).
-/

namespace ExampleProject.KernelWHNF

/-- Closed top-level masks cached once in `m_st->m_whnf` (`SAIR-LAW-02`). -/
def laneMask16 : Nat := (1 <<< 16) - 1

/-- Pack two 16-bit lanes into one unboxed `Nat` word (`SAIR-LAW-15` Kronecker SWAR). -/
@[inline] def pack2x16 (lo hi : Nat) : Nat :=
  (lo &&& laneMask16) ||| ((hi &&& laneMask16) <<< 16)

@[inline] def unpackLo16 (w : Nat) : Nat := w &&& laneMask16
@[inline] def unpackHi16 (w : Nat) : Nat := (w >>> 16) &&& laneMask16

/-- Round-trip correctness for bounded 16-bit lanes. -/
theorem unpackLo16_pack2x16_sample : unpackLo16 (pack2x16 42 99) = 42 := rfl
theorem unpackHi16_pack2x16_sample : unpackHi16 (pack2x16 42 99) = 99 := rfl

/-- Flat monomorphic state carrying zero `Prop` fields (`SAIR-LAW-09`, `SAIR-LAW-22`). -/
structure AccState where
  sum : Nat
  idx : Nat

/-- `cond` on `Nat.ble` avoids `ite`/`Decidable` dictionary synthesis (`SAIR-LAW-08`)
    while compiling cleanly in both kernel WHNF and Lean 4's LCNF code generator. -/
@[inline] def boundedStep (cap : Nat) (st : AccState) : AccState :=
  cond (Nat.ble cap st.idx)
    st
    { sum := st.sum + st.idx, idx := st.idx + 1 }

/-- Structural fuel loop (`SAIR-LAW-06`, `SAIR-LAW-10`) free of `WellFounded.fix`/`brecOn`. -/
def runBoundedLoop (cap : Nat) : Nat → AccState → AccState
  | 0, st => st
  | fuel + 1, st => runBoundedLoop cap fuel (boundedStep cap st)

def runBoundedSum (cap fuel : Nat) : Nat :=
  (runBoundedLoop cap fuel { sum := 0, idx := 0 }).sum

theorem runBoundedSum_witness : runBoundedSum 5 8 = 10 := rfl

end ExampleProject.KernelWHNF
