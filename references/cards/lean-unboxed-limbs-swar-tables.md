---
name: "lean-unboxed-limbs-swar-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-unboxed-limbs-swar-handbook.md."
generated_from: "references/handbooks/lean-unboxed-limbs-swar-handbook.md"
skill_ref: "skills/lean-math-discrete/SKILL.md"
---

# `lean-unboxed-limbs-swar` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-unboxed-limbs-swar-handbook.md`](../handbooks/lean-unboxed-limbs-swar-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Wide state accumulator (256/512-bit) | `Fiat-Crypto Unsaturated Limbs` | `structure Limbs where (l0 l1 l2 l3 l4 : Nat); def add := ...` |
| Parallel 2-lane 31-bit addition | `Guarded SWAR Addition` | `((a &&& mask) + (b &&& mask)) ^^^ ((a ^^^ b) &&& guard)` |
| Bitfield extraction `(x / 2^s) % 2^k` | `Branch-Free Low Cut` | `(w >>> s) &&& ((1 <<< k) - 1)` |
| Ternary conditional `if c then a else b` | `Zhegalkin Multiplexer` | `b ^^^ (c &&& (a ^^^ b))` |
| Bitwise choice `(e &&& f) ^^^ (~~~e &&& g)` | `3-Gate Ch Circuit` | `g ^^^ (e &&& (f ^^^ g))` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Eliminate heap GMP allocations in wide states | `Limb tuple unboxing` | Replaces single `Nat >= 2^63` with 5-tuple of 52-bit `< 2^63` limbs |
| Pack two 31-bit lanes into one 63-bit scalar | `(x &&& 0x7FFFFFFF) ||| ((y &&& 0x7FFFFFFF) <<< 31)` | Keeps value strictly `< 2^62 < 2^63` (lean_box scalar) |
| Prevent cross-lane carry corruption | `Bitwise SWAR guard mask` | Separates carry bits with top-lane zero guard positions |
| Prove branch-free circuit equivalence | `dsimp; omega` | Verifies `g ^^^ (e &&& (f ^^^ g)) = (e &&& f) ^^^ (~~~e &&& g)` |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Kernel WHNF slows down by 10x | Limb value exceeded `2^63 - 1`, allocating GMP mpz | Insert `&&& 0xFFFFFFFFFFFFF` mask at consumption points to maintain unboxed bound |
| `0 - x evaluates to 0 on Nat` | Truncated subtraction on Lean 4 `Nat` | Use bitwise NOT via XOR with explicit mask `x ^^^ 0xFFFFFFFF` rather than subtraction from zero |
| Carry bits corrupt adjacent SWAR lane | Insufficient guard bits in SWAR packing | Restrict lane width to 31 bits with explicit MSB zero guard bit |
| Recursion timeout on wide limb propagation | Monolithic loop unrolling | Factor carry chain into linear unrolled struct update with tail-call passing |
