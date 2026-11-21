---
name: "lean-egraph-cpsat-superopt"
description: |
  USE FOR: e-graph equality saturation, OR-Tools CP-SAT/Z3 sharing-aware DAG extraction (`OptiSat`),
    Fraction signed BnB, context-fusion replay, and dual-certified `eqsat_rw` in Lean 4.
  DO NOT USE FOR: routine interactive proving (`@lean-proof`) or leaving `grind`/`bv_decide` inside strict `no-grind` submissions.
  TRIGGERS: e-graph, eqsat, CP-SAT, OptiSat, signed BnB, context fusion, eqsat_rw, dual-certified rewrite, superoptimizer, SmoothE.
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
  - skill:lean-kernel-optimization
  successors:
  - skill:lean-kernel-optimization
  - skill:lean-proof-review
  - skill:lean-verification-gate
metadata:
  version: 0.6.0
  source_spec: OptiSat, egg POPL 2021, AltProof signed-BnB & context-fusion, KERNEL-LAW-01C, KERNEL-LAW-28
  last_reviewed: '2026-11'
---

# Sharing-Aware E-Graph & CP-SAT Superoptimization for Lean 4

Synthesize DAG-optimal kernel expressions and dual-certified algebraic rewrites using equality saturation, exact CP-SAT
ILP or signed Fraction branch-and-bound extraction, and offline discovery (`grind`/`eqsat`) separated from `no-grind`
kernel proofs.

## Routing
- **USE FOR:** running `AltProof` e-graph superoptimization (`egraph_extractor.py`, `context_fusion.py`, `cost_ranker.py`),
  encoding sharing-aware DAG selection (`x_n`, `y_c`, topological levels `l_c`), fusing consecutive recursor passes, and
  emitting Lean-checked `eqsat_rw` / `dual-certified` rewrites.
- **DO NOT USE FOR:** leaving `grind`, `native_decide`, or solver bindings in final `no-grind` / 3-axiom contest artifacts.

## Workflow
1. **Calibrate Kernel Cost** -- Assign DAG weights for `>= 2^63` GMP limbs, branch vs ANF gates, step-lambda size
   (`<= 30`), and context-fusion trace gains.
2. **Saturate & Extract DAG** -- Run eqsat, compact e-classes, and solve CP-SAT ILP (`l_c >= l_c' + 1 - |C|(1 - x_n)`)
   or exact `Fraction` signed-cost BnB over shared e-classes.
3. **Dual-Certify Rewrites** -- Pair `lhs -> rhs` with a Lean soundness proof (`omega` / `eqsat_rw`) and verified cost
   drop (`TwoAxisEval` / `real - twinlit`).
4. **Harden `no-grind` Handoff** -- Run `grind`/eqsat off-path; materialize explicit `kernel_decide`/`rw` proofs for
   strict 3-axiom targets (`KERNEL-LAW-31`).

## Recovery & STOP
- Reject greedy tree extractors that duplicate shared DAG nodes or permit cyclic extractions.
- Guard `Nat` subtraction rewrites (`b <= a`, `SOUND-01`).

## Handoffs
- **Predecessors:** `lean-specification`, `lean-kernel-optimization`.
- **Successors:** `lean-kernel-optimization`, `lean-proof-review`, `lean-verification-gate`.

## Detailed reference
- Card: [`../../references/cards/lean-egraph-cpsat-superopt-tables.md`](../../references/cards/lean-egraph-cpsat-superopt-tables.md)
- Handbook: [`../../references/handbooks/lean-egraph-cpsat-superopt-handbook.md`](../../references/handbooks/lean-egraph-cpsat-superopt-handbook.md)
- Template: [`../../templates/core/Template_Egraph_CPSAT_Superopt.md`](../../templates/core/Template_Egraph_CPSAT_Superopt.md)

## See also
- [`../lean-kernel-optimization/SKILL.md`](../lean-kernel-optimization/SKILL.md) -- `KERNEL-LAW-01..31` kernel cost model
- [`../lean-worker-wrapper-cps/SKILL.md`](../lean-worker-wrapper-cps/SKILL.md) -- Worker/wrapper unboxing and DAG sharing
