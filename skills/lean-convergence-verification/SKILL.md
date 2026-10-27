---
name: "lean-convergence-verification"
description: |
  USE FOR: discrete Lyapunov energy contraction, loop termination bounds, GPU power iteration limits.
  DO NOT USE FOR: continuous Lyapunov stability via differential equations (@lean-math-dynamical).
  TRIGGERS: lyapunov, convergence, termination bound, gpu bound.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-math-discrete", "skill:lean-proof"]
  successors: ["skill:lean-proof", "skill:lean-proof-review", "skill:lean-math-analysis"]
metadata:
  version: "0.1.0"
  source_spec: "skills/lean-convergence-verification/SKILL.md (this file)"
  last_reviewed: "2026-10-02"
---

# Lean 4 Discrete Lyapunov Convergence & Loop Bound Verification
Guide to proving finite convergence and loop termination bounds for iterative algorithms, numerical solvers,
and GPU kernels in
Lean 4.
## Routing
- **USE FOR:** discrete Lyapunov energy contraction, loop termination bounds, GPU power iteration limits,
  Euclidean integer
  ceiling division
  proofs via
  `Nat.div_add_mod` and `Nat.mod_lt`, and finite convergence verification in Lean 4.
- **DO NOT USE FOR:** continuous Lyapunov stability via differential equations (delegate to
  `@lean-math-dynamical`); simple
  for-loop syntax
  verification
  without energy functions (delegate to `@lean-build`).
- **TRIGGERS:** lyapunov, convergence, termination bound, gpu bound, power iteration, ceiling division,
  div_add_mod, residue
  decay.
## Workflow
1. Define state space and non-negative integer Lyapunov energy function `lyapunov : State -> Nat`.
2. Formulate the strict step decay condition `forall t < n, lyapunov (traj (t + 1)) + delta <= lyapunov (traj
  t)` with `delta >
  0`.
3. Run `lean_diagnostics` (`{"filePath": "..."}`) to trigger the `lean-analyzer` static abstract
  interpretation engine (Zone DBM
   `decreasing_by` synthesis,
   Octagon conservation `±x_i ± x_j <= c`, Bourdoncle WTO loop widening, and trace partitioning) and verify
   that ceiling division
   `(v0 +
delta - 1) /
   delta` and step-decay expressions are free of `NatSubTruncation` and `NatDivModByZero` defects (`delta > 0`
   and `v0 + delta >=
   1`). Run
## Recovery & STOP
- STOP if estimated belief in inductive convergence hypothesis is below 0.90 -- ask user via HITL channel.
- STOP if `lean-analyzer` reports `NatSubTruncation` or `NatDivModByZero` on the ceiling bound `(v0 + delta -
  1) / delta` -- add
  the missing
  `0 < delta`
  hypothesis before attempting `omega`.
- STOP if `omega` fails on non-linear division -- check that `Nat.div_add_mod` has been explicitly introduced
  into the local
  context.
## Handoffs
- **Predecessors:** `agent:gateway`, `skill:lean-math-discrete` (discrete structures), `skill:lean-proof`
  (tactics).
- **Successors:** `skill:lean-proof` (inductive step discharge), `skill:lean-proof-review` (lockdown audit).
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-convergence-verification-handbook.md`](../../references/lean-convergence-verification-handbook.md)
.
## See also
- [`../../references/lean-convergence-verification-handbook.md`](../../references/lean-convergence-verification-handbook.md)
  --
  Complete `lean-convergence-verification` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
