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
  version: 0.4.0
  source_spec: SAIR-LAW-01..25B kernel reduction & hardware lowering catalog
  last_reviewed: 2026-11
---

# Lean 4 Kernel WHNF, SWAR & Codegen Optimization (`SAIR-LAW-01..25B`)

Enforce the concrete-execution half of the Abstraction-Concrete Duality: keep `Prop` specifications clean and
abstract, while making computable witnesses, `rfl`/`decide +kernel` reductions, and C++/SIMD/SIMT extraction
targets monomorphic, unboxed, and cache-aligned.

## Routing
- **USE FOR:** speeding up `whnf` / `is_def_eq`, replacing `WellFounded.fix`/`brecOn` with `Nat.rec`/`Bool.rec`,
  bridging abstract specs to fast implementations via `@[csimp]`, GMP SWAR Kronecker packing, Frontier-ZDD state
  compression, and Twinlit PMU benchmarking.
- **DO NOT USE FOR:** general theorem proving (`@lean-proof`) or splitting long `Prop` proofs (`@lean-proof-refactor`).

## Workflow
1. **Baseline & Static Audit** -- Run `lean_diagnostics` and `lean_metrics` (`action: "altproof"`) to flag
  `KernelBrecOnTax`, `KernelPowerOfTwoDivMod`, `ite` dictionary synthesis (`SAIR-LAW-08`), and non-zero `Prop`
  runtime cones (`SAIR-LAW-22`).
2. **Separate Spec from Compute (`SAIR-LAW-07`)** -- Keep the public `specFn` mathematically clean; write a
  monomorphic `fastFn` over raw `Nat`/`BitVec`/flat `structure` or CPS (`SAIR-LAW-09..10`) and link via `@[csimp]
  theorem specFn_eq_fastFn : specFn = fastFn`.
3. **Apply WHNF & Word-Level Reductions** -- Hoist closed constants to top-level `def` (`SAIR-LAW-02`/`11`
  `m_st->m_whnf` cache), share repeated subtrees (`let y := x; y * y` for `mpn_sqr`, `SAIR-LAW-13`), replace `/
  2^k` and `% 2^k` with `>>>` and `&&&` (`SAIR-LAW-14`), and pack fixed-width DP/automaton lanes via Kronecker SWAR
  or ZDD/ANF masks (`SAIR-LAW-15..20`).
4. **Verify Kernel-Clean Axiom Gate & PMU Gain** -- Discharge decidable checks with `sair_decide` (`rfl | decide
  +kernel | omega`), never `native_decide` or `bv_decide` when `Lean.ofReduceBool` is forbidden, and verify >5%
  deterministic instruction reduction (`perf stat -e instructions:u` against a Twinlit control).

## Recovery & STOP
- If an unrolled or `let`-expanded rewrite regresses PMU instructions (`NR-024` zeta-expansion tax), revert
  immediately and hoist to a closed helper definition.
- Never alter public theorem statements or introduce `unsafe` / `@[implemented_by]` / `@[extern]` kernel escapes.

## Handoffs
- **Predecessors:** `lean-proof`, `lean-proof-refactor`.
- **Successors:** `lean-proof-review`, `lean-verification-gate`.

## Detailed reference
- Fast 3-table lookup card: [`../../references/cards/lean-sair-kernel-optimization-tables.md`](../../references/cards/lean-sair-kernel-optimization-tables.md)
- Full handbook: [`../../references/handbooks/lean-sair-kernel-optimization-handbook.md`](../../references/handbooks/lean-sair-kernel-optimization-handbook.md)
- Core template: [`../../templates/core/Template_KernelWHNF_SAIR.md`](../../templates/core/Template_KernelWHNF_SAIR.md)

## See also
- [`../lean-proof-refactor/SKILL.md`](../lean-proof-refactor/SKILL.md) -- Abstraction-Concrete Duality refactoring
- [`../lean-core-only/SKILL.md`](../lean-core-only/SKILL.md) -- Core-only proving without Mathlib
