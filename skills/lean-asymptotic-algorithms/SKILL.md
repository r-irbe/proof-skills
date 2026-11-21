---
name: "lean-asymptotic-algorithms"
description: |
  USE FOR: asymptotic algorithm substitution -- subresultant PRS, Dulmage-Mendelsohn permanents,
    dynamic Meissel-Lehmer/Mobius sieves (`KERNEL-LAW-17`, `-29`, `-30`), and schedule folding.
  DO NOT USE FOR: low-level WHNF lambda/SWAR rewriting alone (`@lean-kernel-optimization`) or general graph/lattice math (`@lean-math-discrete`).
  TRIGGERS: subresultant, PRS, Habicht, Dulmage-Mendelsohn, permanent, Meissel-Lehmer, Mobius sieve, wheel sieve, schedule folding, anti-gating.
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
  source_spec: KERNEL-LAW-17, KERNEL-LAW-29, KERNEL-LAW-30, TAOCP Vol 2 Sec 4.6.1, Ducos 2000
  last_reviewed: '2026-11'
---

# Asymptotic Algorithm Substitution for Lean 4 Kernel Evaluation

Substitute asymptotically faster exact algorithms so kernel reductions (`rfl`, `decide +kernel`) scale across all input
regimes without static tables (`KERNEL-LAW-30`) or artificial cutoffs (`KERNEL-LAW-29`).

## Routing
- **USE FOR:** Subresultant PRS (Habicht/Ducos, avoiding Kronecker integer blowup), Dulmage-Mendelsohn sparse permanent
  factoring, dynamic Meissel-Lehmer / Mobius mod-30 sieves, and schedule folding.
- **DO NOT USE FOR:** WHNF lambda/SWAR rewriting (`@lean-kernel-optimization`) or general graph/lattice math
  (`@lean-math-discrete`).

## Workflow
1. **Diagnose Bottleneck** -- Spot exponential recursion, $2^{2^k}$ pseudo-remainder blowup, dense Kronecker packing
   (`> 100` limbs), or static tables via `lean_metrics` (`action: "altproof"`).
2. **Select Asymptotic Recurrence** -- Apply Subresultant PRS for discriminants/GCD, Dulmage-Mendelsohn Hopcroft-Karp +
   SCC blocks for permanents, or Legendre $\phi(x,a)$ + dynamic 8-spoke mod-30 sieve.
3. **Keep Kernel Total Functions** -- Implement Section-2 functions over primitive `Nat.*` / `@Nat.rec` with zero static
   tables (`KERNEL-LAW-30`) or band cutoffs (`KERNEL-LAW-29`).
4. **Certify & Benchmark** -- Prove `∀ n, fastFn n = specFn n` under 3 axioms (`kernel_decide`) and verify `real -
   twinlit` `instructions:u`.

## Recovery & STOP
- Reject embedded lookup tables or slow fallbacks past fixed cutoffs (`KERNEL-LAW-29` / `KERNEL-LAW-30`).
- Revert Kronecker packing if quadratic GMP growth loses to subresultant or limb arrays (`KERNEL-LAW-29B`).

## Handoffs
- **Predecessors:** `lean-specification`, `lean-math-discrete`.
- **Successors:** `lean-kernel-optimization`, `lean-proof-review`, `lean-verification-gate`.

## Detailed reference
- Card: [`../../references/cards/lean-asymptotic-algorithms-tables.md`](../../references/cards/lean-asymptotic-algorithms-tables.md)
- Handbook: [`../../references/handbooks/lean-asymptotic-algorithms-handbook.md`](../../references/handbooks/lean-asymptotic-algorithms-handbook.md)
- Template: [`../../templates/core/Template_AsymptoticAlgorithms.md`](../../templates/core/Template_AsymptoticAlgorithms.md)

## See also
- [`../lean-kernel-optimization/SKILL.md`](../lean-kernel-optimization/SKILL.md) -- `KERNEL-LAW-01..31` cost model
- [`../lean-unboxed-limbs-swar/SKILL.md`](../lean-unboxed-limbs-swar/SKILL.md) -- Unboxed `< 2^63` limbs & SWAR
