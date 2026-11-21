---
name: lean-unboxed-limbs-swar-handbook
description: Reference handbook for Fiat-Crypto unsaturated limb arithmetic, unboxed < 2^63 scalar tuples, and guarded SWAR broadword computation in Lean 4 kernel WHNF.
extracted_from: skills/lean-unboxed-limbs-swar/SKILL.md
---

# Fiat-Crypto < 2^63 Unboxed Limb Tuples & Guarded SWAR Arithmetic Handbook (Lean 4)

## Overview & Memory Architecture

In the Lean 4 C++ reduction kernel (`src/kernel/type_checker.cpp` and `src/runtime/mpz.cpp`), numbers are represented in two radically different memory layouts:
1. **Immediate Tagged Pointers (`lean_box`)**: Values strictly less than $2^{63}$ (`val < 2^63`) are encoded directly into pointer words with the low bit set. They incur **0 heap allocations**, **0 reference counts**, and **0 GMP `mpz_t` limb allocations**.
2. **Multi-Limb Heap Bignums (`mpz_t`)**: Values greater than or equal to $2^{63}$ (`val >= 2^63`) allocate heap structures managed by GMP. Every addition, bitwise operation, and shift on bignums performs dynamic heap allocations and limb copying.

When evaluating multi-word cryptographic state, wide cellular automata, or combinatorics in kernel WHNF, representing state as a single large `Nat >= 2^63` (e.g. 256-bit or 512-bit integers) degrades performance by $10\times$ to $50\times$ due to millions of heap allocations.

Drawing on the **Fiat-Crypto** architecture (Chlipala, Erbsen, Philipoom, Gross, Sloan; S&P 2019) and Knuth's broadword computation (*TAOCP* Vol 4A §7.1.3), this handbook provides the blueprints for **unsaturated unboxed limb tuples** and **guarded SWAR arithmetic**, keeping all intermediate values strictly below $2^{63}$.

---

## Unsaturated Limb Tuple Architecture

Instead of packing 256 bits into a single `Nat >= 2^63`, the word is split into five unsaturated 52-bit limbs:
$$\text{State} = (l_0, l_1, l_2, l_3, l_4) \quad \text{where } l_i < 2^{52} < 2^{63}$$

```
+-----------+-----------+-----------+-----------+-----------+
| Limb 4    | Limb 3    | Limb 2    | Limb 1    | Limb 0    |
| (52 bits) | (52 bits) | (52 bits) | (52 bits) | (52 bits) |
+-----------+-----------+-----------+-----------+-----------+
 <----------------------- 260 bits total -------------------->
```

### Carry Headroom
Each 52-bit limb in a 64-bit word has $63 - 52 = 11$ guard bits of carry headroom. This allows up to $2^{11} = 2048$ limb additions to be accumulated without carry overflow before a normalization pass is required:
$$\sum_{j=1}^{K} l_{i, j} < 2048 \times 2^{52} = 2^{63}$$

---

## Guarded SWAR (SIMD Within A Register) Arithmetic

SIMD Within A Register enables parallel evaluation of multiple integer lanes inside a single 63-bit unboxed scalar.

### Two-Lane 31-Bit SWAR Addition
To add two 31-bit lanes packed into a 62-bit scalar without cross-lane carry corruption:
$$\text{mask} = \mathtt{0x7FFFFFFF7FFFFFFF}, \quad \text{guard} = \mathtt{0x8000000080000000}$$

$$\text{sum} = ((a \ \&\ \text{mask}) + (b \ \&\ \text{mask})) \oplus ((a \oplus b) \ \&\ \text{guard})$$

### Branch-Free Zhegalkin 4-Gate Circuits
Conditional branching in recursor steps disrupts kernel subterm sharing (`KERNEL-LAW-26`). Replace branching boolean functions with Algebraic Normal Form (ANF) Zhegalkin circuits:
- **Majority**: $\operatorname{Maj}(a, b, c) = (a \ \&\ (b \oplus c)) \oplus (b \ \&\ c)$ (3 bitwise ops, 0 branch)
- **Choice**: $\operatorname{Ch}(e, f, g) = g \oplus (e \ \&\ (f \oplus g))$ (3 bitwise ops, eliminates complement mask)

---

## Canonical Lean 4 Implementation Exemplar

```lean
set_option autoImplicit false

namespace UnboxedSWAR

/-- 5-tuple of unsaturated 52-bit limbs representing a 256-bit accumulator. -/
structure Limb5 where
  l0 : Nat
  l1 : Nat
  l2 : Nat
  l3 : Nat
  l4 : Nat
  deriving Repr, DecidableEq

def LIMB_MASK : Nat := 0xFFFFFFFFFFFFF -- 2^52 - 1

@[inline] def addLimb5 (a b : Limb5) : Limb5 :=
  { l0 := a.l0 + b.l0
  , l1 := a.l1 + b.l1
  , l2 := a.l2 + b.l2
  , l3 := a.l3 + b.l3
  , l4 := a.l4 + b.l4 }

@[inline] def carryPropagate (a : Limb5) : Limb5 :=
  let c0 := a.l0 >>> 52
  let r0 := a.l0 &&& LIMB_MASK
  let t1 := a.l1 + c0
  let c1 := t1 >>> 52
  let r1 := t1 &&& LIMB_MASK
  let t2 := a.l2 + c1
  let c2 := t2 >>> 52
  let r2 := t2 &&& LIMB_MASK
  let t3 := a.l3 + c2
  let c3 := t3 >>> 52
  let r3 := t3 &&& LIMB_MASK
  let t4 := a.l4 + c3
  let r4 := t4 &&& LIMB_MASK
  { l0 := r0, l1 := r1, l2 := r2, l3 := r3, l4 := r4 }

/-- Guarded 2-lane 31-bit SWAR addition on unboxed < 2^63 Nat. -/
def SWAR_MASK : Nat := 0x7FFFFFFF7FFFFFFF
def SWAR_GUARD : Nat := 0x8000000080000000

@[inline] def swarAdd2 (a b : Nat) : Nat :=
  let sumWithoutGuard := (a &&& SWAR_MASK) + (b &&& SWAR_MASK)
  sumWithoutGuard ^^^ ((a ^^^ b) &&& SWAR_GUARD)

@[inline] def branchFreeChoice (e f g : Nat) : Nat :=
  g ^^^ (e &&& (f ^^^ g))

@[inline] def branchFreeMajority (a b c : Nat) : Nat :=
  (a &&& (b ^^^ c)) ^^^ (b &&& c)

end UnboxedSWAR
```

---

## Goal-Shape Templates (templates)

| Goal Shape | Target Typeclass / Lemma | Proof Template |
| :--- | :--- | :--- |
| Wide state accumulator (256/512-bit) | `Fiat-Crypto Unsaturated Limbs` | `structure Limbs where (l0 l1 l2 l3 l4 : Nat); def add := ...` |
| Parallel 2-lane 31-bit addition | `Guarded SWAR Addition` | `((a &&& mask) + (b &&& mask)) ^^^ ((a ^^^ b) &&& guard)` |
| Bitfield extraction `(x / 2^s) % 2^k` | `Branch-Free Low Cut` | `(w >>> s) &&& ((1 <<< k) - 1)` |
| Ternary conditional `if c then a else b` | `Zhegalkin Multiplexer` | `b ^^^ (c &&& (a ^^^ b))` |
| Bitwise choice `(e &&& f) ^^^ (~~~e &&& g)` | `3-Gate Ch Circuit` | `g ^^^ (e &&& (f ^^^ g))` |

## Intent-to-Tactic Phrasebook (phrasebook)

| Mathematical Intent | Lean 4 / Mathlib Tactic | Notes |
| :--- | :--- | :--- |
| Eliminate heap GMP allocations in wide states | `Limb tuple unboxing` | Replaces single `Nat >= 2^63` with 5-tuple of 52-bit `< 2^63` limbs |
| Pack two 31-bit lanes into one 63-bit scalar | `(x &&& 0x7FFFFFFF) \|\|\| ((y &&& 0x7FFFFFFF) <<< 31)` | Keeps value strictly `< 2^62 < 2^63` (lean_box scalar) |
| Prevent cross-lane carry corruption | `Bitwise SWAR guard mask` | Separates carry bits with top-lane zero guard positions |
| Prove branch-free circuit equivalence | `dsimp; omega` | Verifies `g ^^^ (e &&& (f ^^^ g)) = (e &&& f) ^^^ (~~~e &&& g)` |

## Error-to-Fix Table (errors)

| Error / Symptom | Root Cause | Fix |
| :--- | :--- | :--- |
| Kernel WHNF slows down by 10x | Limb value exceeded `2^63 - 1`, allocating GMP mpz | Insert `&&& 0xFFFFFFFFFFFFF` mask at consumption points to maintain unboxed bound |
| `0 - x evaluates to 0 on Nat` | Truncated subtraction on Lean 4 `Nat` | Use bitwise NOT via XOR with explicit mask `x ^^^ 0xFFFFFFFF` rather than subtraction from zero |
| Carry bits corrupt adjacent SWAR lane | Insufficient guard bits in SWAR packing | Restrict lane width to 31 bits with explicit MSB zero guard bit |
| Recursion timeout on wide limb propagation | Monolithic loop unrolling | Factor carry chain into linear unrolled struct update with tail-call passing |
