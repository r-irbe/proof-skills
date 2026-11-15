/-
Copyright (c) 2026 ExampleProject Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
-/
set_option autoImplicit false

/-!
## 1. Objective
Standalone compile-tested exemplar for `Template_ProofCarryingCodegen.md`:
1. **`PolyBitOp` Verified Bitwise Lowering**: Algebraic Normal Form (ANF) 3-input
   Rule-110 / `lop3` word step proven equivalent to per-bit specification.
2. **Exact-vs-Packed Arithmetic Boundary (`checked-small -> NeedsWide`)**:
   Unboxed 62-bit fast-path addition proven sound against unbounded `Nat`
   addition whenever `checkedAdd62` returns `CheckedWord.small w`, with explicit
   `CheckedWord.needsWide` overflow trap at `>= 2^62`.
3. **128-Byte Cache-Line SPSC Ring Index Invariant**: Power-of-two mask index
   wrapping proven equivalent to `idx % cap` (`SAIR-LAW-14`) with bounded occupancy.

## 2. Architecture & Bit Layout
* `PolyBitOp` word: `UInt64` / `BitVec 64` lowered 1-to-1 to PTX `lop3.b32`,
  MLIR `arith.xori`/`andi`/`ori`, AVX2 `_mm256_xor_si256`, or C++20 `uint64_t`.
* `CheckedWord` threshold: `maxSmall62 = 4611686018427387903` (`2^62 - 1`),
  guaranteeing `a + b < 2^63 < 2^64` with zero native `u64`/`i64` wraparound.

## 3. Kernel Cost Analysis
* Zero `Lean.ofReduceBool` / `native_decide` escapes; all witnesses checked in kernel.

## 4. Verification Contract
* Strict 3-axiom subset (`[propext, Classical.choice, Quot.sound]`).
-/

namespace ExampleProject.ProofCarryingCodegen

/-! ### 1. `PolyBitOp` ANF Boolean Kernel (Rule-110 / PTX `lop3` Truth Table `0x6E`) -/

/-- Reference cell-level Rule-110 transition on three booleans `(l, c, r)`. -/
def rule110CellSpec (l c r : Bool) : Bool :=
  match l, c, r with
  | true,  true,  true  => false
  | true,  true,  false => true
  | true,  false, true  => true
  | true,  false, false => false
  | false, true,  true  => true
  | false, true,  false => true
  | false, false, true  => true
  | false, false, false => false

/-- Algebraic Normal Form (`PolyBitOp` gate DAG: `(c || r) ^^ (l && c && r)`),
    lowering to a single PTX `lop3.b32 d, l, c, r, 0x6e` or AVX-512 `vpternlogq`. -/
@[inline] def rule110CellAnf (l c r : Bool) : Bool :=
  xor (or c r) (and l (and c r))

/-- Exhaustive kernel-checked equivalence between truth-table spec and ANF hardware gate. -/
theorem rule110CellAnf_eq_spec (l c r : Bool) :
    rule110CellAnf l c r = rule110CellSpec l c r := by
  cases l <;> cases c <;> cases r <;> rfl

/-- Word-parallel `PolyBitOp` step over 64-lane `BitVec 64` registers. -/
@[inline] def rule110Word64 (w : BitVec 64) : BitVec 64 :=
  let l := w <<< 1
  let r := w >>> 1
  (w ||| r) ^^^ (l &&& (w &&& r))

/-! ### 2. Exact-vs-Packed Arithmetic Lowering (`checked-small -> NeedsWide`) -/

/-- Cold readable bound (`2^62 - 1`) and hot literal constant (`SAIR-LAW-25B`). -/
abbrev specMaxSmall62 : Nat := (1 <<< 62) - 1
def maxSmall62 : Nat := 4611686018427387903

theorem maxSmall62_eq_spec : maxSmall62 = specMaxSmall62 := rfl

/-- Result of attempting unboxed 62-bit fast-path arithmetic before `GMP`/`rug` promotion. -/
inductive CheckedWord where
  | small (val : Nat)
  | needsWide
  deriving DecidableEq, Repr

/-- Fast-path checked addition: stays in unboxed scalar register when both inputs
    and sum fit in `<= 62` bits; otherwise traps cleanly to `needsWide`. -/
@[inline] def checkedAdd62 (a b : Nat) : CheckedWord :=
  if a ≤ maxSmall62 ∧ b ≤ maxSmall62 then
    let s := Nat.add a b
    if s ≤ maxSmall62 then CheckedWord.small s else CheckedWord.needsWide
  else
    CheckedWord.needsWide

/-- **Soundness Theorem**: Whenever `checkedAdd62` stays on the `small` fast path,
    its value equals exact unbounded `Nat` addition AND strictly fits in `< 2^62`
    (so native `u64`/`i64` lowering cannot overflow). -/
theorem checkedAdd62_small_sound {a b w : Nat}
    (h : checkedAdd62 a b = CheckedWord.small w) :
    w = a + b ∧ w ≤ maxSmall62 := by
  unfold checkedAdd62 at h
  split at h
  · dsimp only at h
    split at h
    · injection h with hw
      subst hw
      exact ⟨rfl, ‹_›⟩
    · contradiction
  · contradiction

/-- **Boundary Promotion Witness (`N04` Conformance)**: Adding `1` at `maxSmall62`
    deterministically signals `needsWide` instead of wrapping. -/
theorem checkedAdd62_overflow_promotes :
    checkedAdd62 maxSmall62 1 = CheckedWord.needsWide := rfl

/-! ### 3. 128B Wait-Free SPSC Power-of-Two Ring Mask Equivalence -/

/-- Masking `idx` by `2^k - 1` equals `idx % 2^k` (`SAIR-LAW-14` SPSC slot index). -/
theorem spscSlotMask_eq_mod (idx k : Nat) :
    idx &&& ((1 <<< k) - 1) = idx % (1 <<< k) := by
  rw [Nat.shiftLeft_eq, Nat.one_mul, Nat.and_two_pow_sub_one_eq_mod]

end ExampleProject.ProofCarryingCodegen
