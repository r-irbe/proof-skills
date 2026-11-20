---
name: "lean-sair-kernel-optimization"
description: |
  USE FOR: Lean 4 kernel WHNF optimization, @[csimp] twins, BitVec/SWAR packing, ZDDs, and C++/SIMD codegen.
  DO NOT USE FOR: high-level Prop refactoring (@lean-proof-refactor) or basic proving (@lean-proof).
  TRIGGERS: SAIR, WHNF, kernel optimization, csimp, SWAR, BitVec, ZDD, sair_decide, instructions:u.
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
  source_spec: SAIR-LAW-01..28 (42 laws), WAVE-13 G1, Wave-20 Recursor Lambda Size & PolyBitOp lowering
  last_reviewed: '2026-11'
---

# Lean 4 Kernel WHNF, SWAR & Proof-Carrying Codegen (`SAIR-LAW-01..28`)

Enforce the concrete half of Abstraction-Concrete Duality (`WAVE-13 G1`): keep `Prop` specs abstract (`<= 1%` cost via `rfl` bridges), while making hot `def`
kernels and hardware targets (`PolyBitOp` MLIR / CUDA `sm_89` / AVX2 / C++20) monomorphic and unboxed (avoiding the `1,600x..3,345x` parametric hot penalty).

## Routing
- **USE FOR:** speeding up `whnf` / `is_def_eq`, explicit `Nat.rec`/`Bool.rec`/`cond` lowering, `@[csimp]` twins, SWAR packing (`width-2 + 1-bit`), ZDD
  bitboards, sum-of-medians-of-three `twinlit` PMU profiling, and proof-carrying SWAR/SIMD/SIMT/C++20 codegen (`checked-small -> NeedsWide`).
- **DO NOT USE FOR:** general theorem proving (`@lean-proof`) or splitting long `Prop` proofs (`@lean-proof-refactor`).

## Workflow
1. **Static Audit** -- Run `lean_diagnostics` and `lean_metrics` (`action: "altproof"`) to detect `brecOn` (`SAIR-LAW-06`), `ite` (`SAIR-LAW-08`), power-of-two
   `/` or `%` (`SAIR-LAW-14`), typeclass dictionaries (`SAIR-LAW-23`), and `Prop`/`Fin` in hot cones (`SAIR-LAW-22`).
2. **`WAVE-13 G1` Section-1/2/3 Split** -- Put readable `abbrev` formulas in Section 1, specialize hot `def`s in Section 2 to primitive `Nat.*` ops + raw
   `nat_lit` constants (`SAIR-LAW-25B`), and bridge to abstract theorems in Section 3 via `rfl` (`@[csimp]` for LCNF).
3. **WHNF, SWAR & Lowering Laws** -- Use `Nat.succ` for `Nat.rec` step accumulators vs `Nat.add 1` for counters, share multi-limb squares only above ~30 limbs
   (`SAIR-LAW-13`), keep **branching** recursor step-lambda bodies small (`<= 30` AST nodes) via first-order helper `def`s rather than inlined macros while keeping 100% branch-free step bodies inline (`SAIR-LAW-26` / `SAIR-LAW-28`),
   use tail-recursive unboxed accumulators instead of non-tail `WPair.rec`/`Prod.rec` unpack-repack (`SAIR-LAW-27`), use `Nat.land w (Nat.shiftRight w s)` or `w &&& (w - 1)` on `Nat` (`SAIR-LAW-18B`), and enforce `checked-small -> NeedsWide` + operand
   snapshotting in C++20/PTX (`Template_ProofCarryingCodegen.md`).
4. **3-Axiom & PMU Gate** -- Close checks with `sair_decide` (`first | rfl | decide +kernel | omega`), never `native_decide`, and verify net `real - twinlit`
   gain via sum-of-per-slot-medians-of-three (`perf stat -e instructions:u`).

## Recovery & STOP
- Revert any `let`-sharing (`SAIR-LAW-01B`) or unrolling rewrite that regresses full-pipeline `real - twinlit` instructions.
- Never alter public theorem signatures or introduce `unsafe` / `@[implemented_by]` / `@[extern]` escapes on kernel-scored paths.

## Handoffs
- **Predecessors:** `lean-proof`, `lean-proof-refactor`.
- **Successors:** `lean-proof-review`, `lean-verification-gate`.

## Detailed reference
- Fast lookup card: [`../../references/cards/lean-sair-kernel-optimization-tables.md`](../../references/cards/lean-sair-kernel-optimization-tables.md)
- Full handbook: [`../../references/handbooks/lean-sair-kernel-optimization-handbook.md`](../../references/handbooks/lean-sair-kernel-optimization-handbook.md)
- Templates: [`../../templates/core/Template_KernelWHNF_SAIR.md`](../../templates/core/Template_KernelWHNF_SAIR.md),
  [`../../templates/core/Template_ProofCarryingCodegen.md`](../../templates/core/Template_ProofCarryingCodegen.md)

## See also
- [`../lean-proof-refactor/SKILL.md`](../lean-proof-refactor/SKILL.md)
- [`../lean-core-only/SKILL.md`](../lean-core-only/SKILL.md)
