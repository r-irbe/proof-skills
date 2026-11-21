---
name: "lean-worker-wrapper-cps"
description: |
  USE FOR: GHC Core style Lean 4 WHNF tuning -- Worker/Wrapper unboxing, Join Points (`m_whnf`),
    `SpecConstr` specialization, and defunctionalized first-order CPS continuations.
  DO NOT USE FOR: statement-level Mixin/Mathlib generalization (`@lean-proof-refactor`) or raw SIMD/SWAR bit packing (`@lean-unboxed-limbs-swar`).
  TRIGGERS: worker-wrapper, join point, SpecConstr, defunctionalized CPS, Danvy, unboxed accumulator, WPair, instantiate_rev, KERNEL-LAW-09, KERNEL-LAW-10.
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
  - skill:lean-proof
  - skill:lean-proof-refactor
  successors:
  - skill:lean-kernel-optimization
  - skill:lean-proof-review
  - skill:lean-verification-gate
metadata:
  version: 0.6.0
  source_spec: KERNEL-LAW-01..10, KERNEL-LAW-24, KERNEL-LAW-27, Peyton Jones/Launchbury/Maurer PLDI 2017
  last_reviewed: '2026-11'
---

# Worker/Wrapper, Join Points, `SpecConstr` & Defunctionalized CPS in Lean 4

Eliminate tuple/record boxing, `instantiate_rev` substitution bloat, and higher-order closure allocation in hot `@Nat.rec`
loops using Worker/Wrapper splitting, non-escaping Join Points, `SpecConstr`, and closed defunctionalized CPS.

## Routing
- **USE FOR:** stripping structure/typeclass wrappers at entry (`wrapper -> worker`), flattening `Prod`/`WPair` state
  into `<= 6` unboxed scalar parameters (`KERNEL-LAW-09`, `KERNEL-LAW-10`, `KERNEL-LAW-24`), preserving `m_whnf` DAG
  sharing across merge branches via local Join Points, and replacing closure parameters with algebraic continuation tags.
- **DO NOT USE FOR:** general lemma extraction (`@lean-proof-refactor`) or pure asymptotic algorithm replacement
  (`@lean-asymptotic-algorithms`).

## Workflow
1. **Unpack at Wrapper** -- Strip records/typeclasses and bounds once at the entry wrapper; keep `@Nat.rec` workers
   monomorphic with `<= 6` unboxed scalar arguments.
2. **Factor Join Points & `SpecConstr`** -- Extract converging merge branches (`<= 30` AST nodes if branching,
   `KERNEL-LAW-28`) as closed helpers preserving `m_whnf` DAG sharing (`KERNEL-LAW-01C`).
3. **Defunctionalize CPS** -- Replace higher-order closures with closed continuation constructors or direct tail
   accumulators (`Nat.succ` vs `Nat.add 1`, `ADR-INV-0025`).
4. **Verify Full-Consumer Cost** -- Prove `wrapper n = spec n` and check end-to-end `real - twinlit` `instructions:u`
   to catch the Single-Consumer Isolation Paradox.

## Recovery & STOP
- Revert any CPS or Join-Point split regressing end-to-end `real - twinlit` instructions.
- Keep branching step lambdas `<= 30` AST nodes (`KERNEL-LAW-28`).

## Handoffs
- **Predecessors:** `lean-proof`, `lean-proof-refactor`.
- **Successors:** `lean-kernel-optimization`, `lean-proof-review`, `lean-verification-gate`.

## Detailed reference
- Card: [`../../references/cards/lean-worker-wrapper-cps-tables.md`](../../references/cards/lean-worker-wrapper-cps-tables.md)
- Handbook: [`../../references/handbooks/lean-worker-wrapper-cps-handbook.md`](../../references/handbooks/lean-worker-wrapper-cps-handbook.md)
- Template: [`../../templates/core/Template_WorkerWrapper_JoinPoints.md`](../../templates/core/Template_WorkerWrapper_JoinPoints.md)

## See also
- [`../lean-kernel-optimization/SKILL.md`](../lean-kernel-optimization/SKILL.md) -- `KERNEL-LAW-01..31` kernel cost model
- [`../lean-computational-reflection/SKILL.md`](../lean-computational-reflection/SKILL.md) -- Section 1/2/3 duality & reflection
