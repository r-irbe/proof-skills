---
id: zk-012
title: Abstraction-concrete duality and hot parameterization penalty
created: 2026-11-15
updated: 2026-11-15
type: permanent
tags: [duality, refactoring, whnf, kernel]
refs:
  - zk-008
  - zk-009
  - zk-011
  - zk-013
status: validated
confidence: high
---

# Abstraction-concrete duality and hot parameterization penalty

**Claim.** Abstract algebraic typeclasses (`CommRing`, `Module`, `IsOrderedRing`) belong in theorem statements and compositional proofs, whereas concrete monomorphic representations (`Nat`, `BitVec w`, `UInt64`, `Array`) belong in kernel-reduced definitions and codegen targets. Passing dictionary typeclasses inside hot kernel loops incurs a **1,600x-3,345x** WHNF instruction penalty; bridging an abstract spec `f_spec` to a concrete twin `f_fast` via `theorem f_eq : f_fast = f_spec := rfl` or `@[csimp]` adds `<= 1%` proof overhead.

**Evidence.** Verified in `references/handbooks/lean-proof-refactor-handbook.md` (`WAVE-13 G1` duality benchmarks) and `templates/core/examples/Template_KernelWHNF.lean`. Rewriting theorems against `f_spec` preserves Mathlib composability (`sum_congr_ring`, `finset_mono` from [[zk-008]]), while `#eval` and `rfl` execute `f_fast` under the WHNF laws in [[zk-011]].

**Implication.** Never thread `Semiring` or `DecidableEq` dictionaries through inner `Nat.rec` compute bodies, and never prove global algebraic properties directly over bit-packed SWAR loops. Split spec and compute twins cleanly, apply the consolidation rubric in [[zk-009]] to shared bridges, and feed `f_fast` into the hardware lowering pipeline in [[zk-013]].

See also: [[zk-008]], [[zk-009]], [[zk-011]], [[zk-013]].
