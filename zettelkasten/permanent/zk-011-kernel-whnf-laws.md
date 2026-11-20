---
id: zk-011
title: SAIR 39 kernel WHNF laws and nat_lit mechanics
created: 2026-11-15
updated: 2026-11-15
type: permanent
tags: [sair, whnf, kernel, optimization]
refs:
  - zk-008
  - zk-012
  - zk-013
status: validated
confidence: high
---

# SAIR 39 kernel WHNF laws and nat_lit mechanics

**Claim.** Lean 4's C++ kernel (`type_checker.cpp`) obeys 39 deterministic WHNF reduction laws across `m_whnf` caching, GMP `nat_lit` interceptors, structural `Nat.rec`/`Bool.rec` iota steps, and `ShareCommon` DAG hash-consing. Closed constant subterms evaluated via `eval_nat%` emit raw `Expr.lit (.natVal v)` literals with zero runtime instruction overhead, whereas `OfNat.ofNat` typeclass projections pay ~160K kernel instructions per unfolding.

**Evidence.** Codified in `references/lean-sair-kernel-optimization-handbook.md`, `templates/core/examples/Template_KernelWHNF_SAIR.lean`, and `packages/altproof/AltProof/Core.lean` (`eval_nat%`, `preunfold%`, `swar_unroll%`). Kernel profiling shows closed top-level definitions hit `m_st->m_whnf` after one evaluation, while open lambdas inside `Nat.rec` step functions bypass `m_whnf` and re-reduce on every iteration.

**Implication.** Kernel-hot definitions must avoid `WellFounded.fix`, pack fixed-width lanes into single GMP `Nat` words via SWAR Kronecker substitution, and pair concrete compute twins with clean specs via the `rfl` duality bridge in [[zk-012]]. Proof-carrying hardware lowering in [[zk-013]] and the unified tactic hierarchy in [[zk-008]] (`sair_decide` over banned `native_decide`) build directly on these 39 laws.

See also: [[zk-008]], [[zk-012]], [[zk-013]].
