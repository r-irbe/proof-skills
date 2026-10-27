---
name: "lean-convergence-verification-handbook"
description: "Reference handbook for @lean-convergence-verification."
extracted_from: "skills/lean-convergence-verification/SKILL.md"
---

# Lean 4 Discrete Lyapunov Convergence & Loop Bound Verification

Guide to proving finite convergence and loop termination bounds for iterative algorithms, numerical solvers, and GPU kernels in Lean 4.

## Routing

- **USE FOR:** discrete Lyapunov energy contraction, loop termination bounds, GPU power iteration limits, Euclidean integer ceiling division proofs via
  `Nat.div_add_mod` and `Nat.mod_lt`, and finite convergence verification in Lean 4.
- **DO NOT USE FOR:** continuous Lyapunov stability via differential equations (delegate to `@lean-math-dynamical`); simple for-loop syntax verification
  without energy functions (delegate to `@lean-build`).
- **TRIGGERS:** lyapunov, convergence, termination bound, gpu bound, power iteration, ceiling division, div_add_mod, residue decay.

## Workflow

1. Define state space and non-negative integer Lyapunov energy function `lyapunov : State -> Nat`.
2. Formulate the strict step decay condition `forall t < n, lyapunov (traj (t + 1)) + delta <= lyapunov (traj t)` with `delta > 0`.
3. Run `lean_diagnostics` (`{"filePath": "..."}`) to trigger the `lean-analyzer` static abstract interpretation engine (Zone DBM `decreasing_by` synthesis,
   Octagon conservation `±x_i ± x_j <= c`, Bourdoncle WTO loop widening, and trace partitioning) and verify that ceiling division `(v0 + delta - 1) /
   delta` and step-decay expressions are free of `NatSubTruncation` and `NatDivModByZero` defects (`delta > 0` and `v0 + delta >= 1`). Run
   `lean_counterexample_search` (with Galois-guided hypothesis domain pruning via `analyzeHeaderHypothesisDomains` / `pruneHeaderNatDomain`) and
   `lean-rules` (`node tools/lean-lsp-mcp/bin/lean-rules.js`) / `pi-lens` (`pilens_ast_grep_search`, `pilens_diagnostics`) before attempting manual
   induction.
4. Prove finite convergence by induction over step indices: rewrite non-linear terms `(t + 1) * delta` to `t * delta + delta` using `Nat.succ_mul` before
   calling `omega`.
5. Formulate ceiling division upper bound `n = (v0 + delta - 1) / delta`.
6. Prove the arithmetic floor bound `((v0 + delta - 1) / delta) * delta >= v0` by instantiating `Nat.div_add_mod` and `Nat.mod_lt` together with `omega`.
7. Conclude exact convergence `lyapunov (traj n) = 0`, guaranteeing finite GPU termination without warp divergence.
8. Verify against [`../../templates/Template_Lyapunov.md`](../../templates/Template_Lyapunov.md).

## Recovery & STOP

- STOP if estimated belief in inductive convergence hypothesis is below 0.90 -- ask user via HITL channel.
- STOP if `lean-analyzer` reports `NatSubTruncation` or `NatDivModByZero` on the ceiling bound `(v0 + delta - 1) / delta` -- add the missing `0 < delta`
  hypothesis before attempting `omega`.
- STOP if `omega` fails on non-linear division -- check that `Nat.div_add_mod` has been explicitly introduced into the local context.
- STOP if real numbers are introduced for discrete counters -- restrict all energy and step values strictly to `Nat`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-math-discrete` (discrete structures), `skill:lean-proof` (tactics).
- **Successors:** `skill:lean-proof` (inductive step discharge), `skill:lean-proof-review` (lockdown audit).
