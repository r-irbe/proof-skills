# `Template_UnboxedLimbTuples_SWAR.md` -- Fiat-Crypto Unboxed Limbs & Guarded SWAR Template

> **Status**: Canonical template (`@lean-math-discrete`, aligned with `KERNEL-LAW-11`, `KERNEL-LAW-12`, `KERNEL-LAW-14`, `KERNEL-LAW-26`, `KERNEL-LAW-27`).

---

## 1. When to Use This Template

Use `Template_UnboxedLimbTuples_SWAR` whenever:
1. An algorithm requires tracking accumulators or bitboards larger than 63 bits (e.g. 128-bit, 256-bit, or 512-bit states) in kernel WHNF.
2. Multiple narrow integer fields (15-bit, 31-bit) can be computed in parallel inside single unboxed 63-bit scalar words.
3. Heap GMP `mpz_t` allocations must be completely eliminated to preserve kernel reduction throughput.

---

## 2. Canonical Structure

```lean
set_option autoImplicit false

namespace UnboxedSWARTemplate

/-! ### 1. Constants & Bit Masks (< 2^63) -/

def LIMB_BITS : Nat := 52
def LIMB_MASK : Nat := 0xFFFFFFFFFFFFF -- 2^52 - 1

def SWAR_LANE_MASK : Nat := 0x7FFFFFFF7FFFFFFF
def SWAR_GUARD_MASK : Nat := 0x8000000080000000

/-! ### 2. Unsaturated Limb Tuple Structure -/

structure Limbs4 where
  l0 : Nat
  l1 : Nat
  l2 : Nat
  l3 : Nat
  deriving Repr, DecidableEq

@[inline] def addLimbs4 (a b : Limbs4) : Limbs4 :=
  { l0 := a.l0 + b.l0
  , l1 := a.l1 + b.l1
  , l2 := a.l2 + b.l2
  , l3 := a.l3 + b.l3 }

@[inline] def carryLimbs4 (a : Limbs4) : Limbs4 :=
  let c0 := a.l0 >>> LIMB_BITS
  let r0 := a.l0 &&& LIMB_MASK
  let t1 := a.l1 + c0
  let c1 := t1 >>> LIMB_BITS
  let r1 := t1 &&& LIMB_MASK
  let t2 := a.l2 + c1
  let c2 := t2 >>> LIMB_BITS
  let r2 := t2 &&& LIMB_MASK
  let t3 := a.l3 + c2
  let r3 := t3 &&& LIMB_MASK
  { l0 := r0, l1 := r1, l2 := r2, l3 := r3 }

/-! ### 3. Guarded SWAR Arithmetic -/

@[inline] def swarAdd (a b : Nat) : Nat :=
  let sumNoGuard := (a &&& SWAR_LANE_MASK) + (b &&& SWAR_LANE_MASK)
  sumNoGuard ^^^ ((a ^^^ b) &&& SWAR_GUARD_MASK)

/-! ### 4. Branch-Free Zhegalkin Gadgets -/

@[inline] def zhegalkinCh (e f g : Nat) : Nat :=
  g ^^^ (e &&& (f ^^^ g))

@[inline] def zhegalkinMaj (a b c : Nat) : Nat :=
  (a &&& (b ^^^ c)) ^^^ (b &&& c)

end UnboxedSWARTemplate
```

---

## 3. Quality Verification Checklist

- [ ] All limb values strictly satisfy `l < 2^63` at every reduction step.
- [ ] Carry propagation uses bitwise shift `>>> 52` and mask `&&& LIMB_MASK` (never division or modulo).
- [ ] Zero usage of negative subtraction; bitwise inversion uses explicit XOR masks.
- [ ] Kernel WHNF execution exhibits 0 GMP allocations.
