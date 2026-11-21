---
name: "lean-unboxed-limbs-swar"
description: |
  USE FOR: Fiat-Crypto unsaturated `< 2^63` `lean_box` limbs (`5 x 52-bit`), zero GMP allocation,
    guarded SWAR arithmetic, and branch-free Zhegalkin ANF circuits (`Maj`, `Ch`) in Lean 4.
  DO NOT USE FOR: general real analysis (`@lean-math-analysis`) or high-level `Prop` refactoring (`@lean-proof-refactor`).
  TRIGGERS: lean_box, 2^63, unsaturated limbs, Fiat-Crypto, SWAR, broadword, Zhegalkin, ANF, Maj, Ch, mpz_t, carry headroom.
tier: warm
runtime_targets:
- copilot-cli
- claude-code
- antigravity
- pi
- cursor
- gemini-cli
dispatch_targets: []
handoffs:
  predecessors:
  - skill:lean-specification
  - skill:lean-math-discrete
  successors:
  - skill:lean-kernel-optimization
  - skill:lean-proof-review
  - skill:lean-verification-gate
metadata:
  version: 0.6.0
  source_spec: KERNEL-LAW-13..16B, KERNEL-LAW-18B, KERNEL-LAW-20, KERNEL-LAW-24, Fiat-Crypto S&P 2019
  last_reviewed: '2026-11'
---

# Unboxed `< 2^63` Limb Tuples & Guarded SWAR in Lean 4 Kernel WHNF

Eliminate `mpz_t` heap allocations in Lean 4's C++ reduction kernel by keeping all hot scalars strictly below $2^{63}$
(`lean_box` immediate tagged pointers) via unsaturated multi-limb tuples, guarded SWAR lanes, and branch-free ANF logic.

## Routing
- **USE FOR:** splitting 128-to-512-bit integers into unsaturated `< 2^63` limbs (`5 x 52-bit` with 11-bit carry headroom),
  packing parallel bounded counters into 62-bit SWAR lanes (`mask`/`guard` cross-lane isolation), and compiling conditionals
  into 3-gate Zhegalkin ANF circuits (`Maj`, `Ch`).
- **DO NOT USE FOR:** general algebraic proofs (`@lean-proof`) or single-file refactorings (`@lean-proof-refactor`).

## Workflow
1. **Audit Allocation & Limb Width** -- Check whether intermediate `Nat` states cross $2^{63}$ (`mpz_t`) and pick unsaturated
   limb widths `w < 63` giving enough carry headroom ($2^{63 - w}$ unnormalized additions before carry propagation).
2. **Enforce Guarded SWAR & Width-2 Pareto** -- For parallel integer lanes inside one scalar `< 2^63`, separate sums with
   `(mask, guard)` bits or prefer width-2 register pairs `(loWord, hiWord)` with 1-bit steps (`KERNEL-LAW-24`).
3. **Compile Branches to ANF** -- Replace branching `Bool.rec`/`if` inside hot recursor steps with branch-free Zhegalkin
   polynomials (`Maj(a,b,c) = (a &&& (b ^^^ c)) ^^^ (b &&& c)`), avoiding `0 - x` on truncating `Nat` (`KERNEL-LAW-18B`).
4. **Prove Equivalence & Lowering Guards** -- Bridge packed/limb execution to the mathematical spec in Section 3 (`rfl` or
   `omega`) and pair multi-limb C++20/Rust targets with `checked-small -> NeedsWide` guards (`N01..N12`).

## Recovery & STOP
- Never emit `x &&& (0 - x)` on `Nat` (`0 - x = 0`); use `Nat.land x (Nat.sub x 1)` or `BitVec w` (`KERNEL-LAW-18B`).
- Re-check carry overflow invariants (`sum < 2^63`) whenever unrolling more additions between carry passes.

## Handoffs
- **Predecessors:** `lean-specification`, `lean-math-discrete`.
- **Successors:** `lean-kernel-optimization`, `lean-proof-review`, `lean-verification-gate`.

## Detailed reference
- Fast lookup card: [`../../references/cards/lean-unboxed-limbs-swar-tables.md`](../../references/cards/lean-unboxed-limbs-swar-tables.md)
- Full handbook: [`../../references/handbooks/lean-unboxed-limbs-swar-handbook.md`](../../references/handbooks/lean-unboxed-limbs-swar-handbook.md)
- Template: [`../../templates/core/Template_UnboxedLimbTuples_SWAR.md`](../../templates/core/Template_UnboxedLimbTuples_SWAR.md)

## See also
- [`../lean-kernel-optimization/SKILL.md`](../lean-kernel-optimization/SKILL.md) -- `KERNEL-LAW-01..31` kernel cost model
- [`../lean-asymptotic-algorithms/SKILL.md`](../lean-asymptotic-algorithms/SKILL.md) -- Asymptotic algorithm selection
