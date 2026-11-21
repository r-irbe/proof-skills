---
name: "lean-computational-reflection"
description: |
  USE FOR: CPDT Ch. 15 / FRAP computational reflection (`denote (compile e) = denote e`),
    Section 1/2/3 Duality (`KERNEL-LAW-22`, `-31`), `@[csimp]` twins, and proof compression.
  DO NOT USE FOR: ordinary proof refactoring (`@lean-proof-refactor`) or raw low-level SWAR bitboard tuning (`@lean-unboxed-limbs-swar`).
  TRIGGERS: computational reflection, CPDT, denote compile, Section 1/2/3, zero Prop leakage, csimp twin, kernel_decide.
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
  source_spec: KERNEL-LAW-07, KERNEL-LAW-22, KERNEL-LAW-22B, KERNEL-LAW-31, CPDT Ch. 15
  last_reviewed: '2026-11'
---

# Computational Reflection & Section 1/2/3 Duality (`KERNEL-LAW-22`, `KERNEL-LAW-31`)

Replace bloated tactical proof scripts over fixed schedules, circuits, and normal forms with certified computational
decision procedures checked once in Lean 4's kernel (`rfl`), isolated via the Section 1/2/3 Duality split.

## Routing
- **USE FOR:** reifying arithmetic/boolean/schedule syntax (`Expr`, `denote`), writing reflective simplifiers proved sound
  once (`∀ e, denote (simplify e) = denote e`), splitting cold specs/proofs from monomorphic runtime `def`s (`KERNEL-LAW-31`),
  and pairing inductive specs with fast `@[csimp]` twins (`KERNEL-LAW-07`).
- **DO NOT USE FOR:** general lemma extraction without reflection (`@lean-proof-refactor`) or e-graph solver search
  (`@lean-egraph-cpsat-superopt`).

## Workflow
1. **Isolate Section 1 (Cold Syntax & Spec)** -- Define inductive ASTs (`Expr`, `BitCircuit`), `abbrev` bit masks, and
   clean mathematical `denote` semantics completely outside the hot runtime cone (`KERNEL-LAW-25B`).
2. **Implement Section 2 (Zero-`Prop` Kernel Evaluator)** -- Write monomorphic concrete `def simplify`/`impl` over
   unboxed `Nat`/`Bool` with zero `Prop`, `Fin`, `Subtype`, or typeclass dictionaries (`KERNEL-LAW-22`, `KERNEL-LAW-23`).
3. **Prove Section 3 (Reflective Soundness & `@[csimp]`)** -- Prove generic soundness `∀ e, denote (simplify e) = denote e`
   and bridge concrete instantiations (`fast = spec`) via `rfl` (`<= 1%` overhead, avoiding the `1,600x..3,345x` penalty).
4. **Discharge Ground Goals via `kernel_decide`** -- Close concrete evaluations with `rfl | decide +kernel | omega`,
   strictly within `[propext, Classical.choice, Quot.sound]`.

## Recovery & STOP
- Stop immediately if any `Prop` witness, `Fin` proof field, or `Classical.choice` branch enters Section 2's transitive
  call cone (`KernelLawAuditor` Law 22 / `KERNEL-LAW-22`).
- Never use `native_decide` or `bv_decide` on kernel-scored reflective obligations.

## Handoffs
- **Predecessors:** `lean-proof`, `lean-proof-refactor`.
- **Successors:** `lean-kernel-optimization`, `lean-proof-review`, `lean-verification-gate`.

## Detailed reference
- Fast lookup card: [`../../references/cards/lean-computational-reflection-tables.md`](../../references/cards/lean-computational-reflection-tables.md)
- Full handbook: [`../../references/handbooks/lean-computational-reflection-handbook.md`](../../references/handbooks/lean-computational-reflection-handbook.md)
- Template: [`../../templates/core/Template_Section123_Reflection.md`](../../templates/core/Template_Section123_Reflection.md)

## See also
- [`../lean-proof-refactor/SKILL.md`](../lean-proof-refactor/SKILL.md) -- General proof refactoring and `AltProof.Closers`
- [`../lean-kernel-optimization/SKILL.md`](../lean-kernel-optimization/SKILL.md) -- Full `KERNEL-LAW-01..31` kernel cost model
