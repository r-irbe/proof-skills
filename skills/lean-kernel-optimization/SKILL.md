---
name: "lean-kernel-optimization"
description: |
  USE FOR: Lean 4 kernel WHNF optimization, @[csimp] twins, BitVec/SWAR packing, ZDDs, and C++/SIMD codegen.
  DO NOT USE FOR: high-level Prop refactoring (@lean-proof-refactor) or basic proving (@lean-proof).
  TRIGGERS: kernel optimization, WHNF, csimp, SWAR, BitVec, ZDD, kernel_decide, instructions:u, lean-project.toml.
tier: hot
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
  - skill:lean-proof
  - skill:lean-proof-refactor
  successors:
  - skill:lean-proof-review
  - skill:lean-verification-gate
metadata:
  version: 0.6.0
  source_spec: KERNEL-LAW-01..31, WAVE-13 G1, Wave-20 Recursor Lambda Size, GMP Pow2/Sqr & PolyBitOp
  last_reviewed: '2026-11'
---

# Lean 4 Kernel WHNF, SWAR & Hardware Codegen (`KERNEL-LAW-01..31`)

Keep `Prop` specs abstract (`<= 1%` cost via `rfl`), while keeping hot `def`s and hardware targets (`PolyBitOp`
MLIR/PTX/AVX2/C++20) monomorphic and unboxed (`WAVE-13 G1`, `-31`).

## Routing
- **USE FOR:** `whnf`/`is_def_eq`, `@Nat.rec`/`Bool.rec`/`cond`, `@[csimp]` twins, SWAR/ZDDs, `twinlit` PMU runs, and
  `checked-small -> NeedsWide` lowering.
- **DO NOT USE FOR:** general proving (`@lean-proof`), `Prop` refactoring (`@lean-proof-refactor`), or contest-band
  cutoffs / lookup tables (`-29`, `-30`).

## Workflow
1. **Static Audit** -- Run `lean_diagnostics` and `lean_metrics` (`action: "altproof"`) for `brecOn` (`-06`), `ite`
   (`-08`), pow2 `/`/`%` (`-14`), typeclasses (`-23`), lookup tables (`-30`), and Section 1/2/3 splits (`-31`).
2. **Section-1/2/3 Split** -- Put `abbrev` specs in Sec. 1, zero-`Prop` `def`s + raw `nat_lit`s in Sec. 2 (`-25B`), and
   `rfl`/`@[csimp]` bridges in Sec. 3 (`WAVE-13 G1`).
3. **WHNF & GMP Scaling** -- Pair `Nat.succ`/`Nat.add 1` (`ADR-INV-0025`), `Nat.mul x x` on `< 2^63` scalars vs wide
   `Nat.pow x 2` (`0.58x` `mpn_sqr`, >=30 limbs) + `O(L)` single-limb scaling, refute huge Kronecker packing (`-29B`),
   cap branching step lambdas `<= 30` nodes (`-28`), and emit `checked-small -> NeedsWide` C++20/PTX.
4. **3-Axiom `no-grind` Gate** -- Keep `grind`/eqsat off submission paths; close with `kernel_decide` (`rfl | decide
   +kernel | omega`), set `profile = "kernel"`, and verify `real - twinlit` (`instructions:u`).

## Recovery & STOP
- Revert `let`-sharing (`-01B`), Kronecker blowup, or unrolling regressing full-pipeline `real - twinlit`.
- Never keep `grind`, `native_decide`, `unsafe`, `@[implemented_by]`, or `@[extern]` on scored paths.

## Handoffs
- **Predecessors:** `lean-proof`, `lean-proof-refactor`.
- **Successors:** `lean-proof-review`, `lean-verification-gate`.

## Detailed reference
- Card: [`../../references/cards/lean-kernel-optimization-tables.md`](../../references/cards/lean-kernel-optimization-tables.md)
- Handbook: [`../../references/handbooks/lean-kernel-optimization-handbook.md`](../../references/handbooks/lean-kernel-optimization-handbook.md)
- Templates: [`../../templates/core/Template_KernelWHNF.md`](../../templates/core/Template_KernelWHNF.md),
  [`../../templates/core/Template_ProofCarryingCodegen.md`](../../templates/core/Template_ProofCarryingCodegen.md)

## See also
- [`../lean-asymptotic-algorithms/SKILL.md`](../lean-asymptotic-algorithms/SKILL.md)
- [`../lean-computational-reflection/SKILL.md`](../lean-computational-reflection/SKILL.md)
- [`../lean-egraph-cpsat-superopt/SKILL.md`](../lean-egraph-cpsat-superopt/SKILL.md)
- [`../lean-unboxed-limbs-swar/SKILL.md`](../lean-unboxed-limbs-swar/SKILL.md)
- [`../lean-worker-wrapper-cps/SKILL.md`](../lean-worker-wrapper-cps/SKILL.md)
- [`../lean-proof-refactor/SKILL.md`](../lean-proof-refactor/SKILL.md)
- [`../lean-core-only/SKILL.md`](../lean-core-only/SKILL.md)
