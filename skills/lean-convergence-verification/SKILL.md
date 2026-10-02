---
name: "lean-convergence-verification"
description: |
  USE FOR: discrete Lyapunov energy contraction, loop termination bounds, GPU power iteration limits, Euclidean integer ceiling division proofs via Nat.div_add_mod and Nat.mod_lt, and finite convergence verification in Lean 4.
  DO NOT USE FOR: continuous Lyapunov stability via differential equations (use @lean-math-dynamical); simple for-loop syntax verification without energy functions (use @lean-build).
  TRIGGERS: lyapunov, convergence, termination bound, gpu bound, power iteration, ceiling division, div_add_mod, residue decay.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
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

Guide to proving finite convergence and loop termination bounds for iterative algorithms, numerical solvers, and GPU kernels in Lean 4.

## Routing

- **USE FOR:** discrete Lyapunov energy contraction, loop termination bounds, GPU power iteration limits, Euclidean integer ceiling division proofs via `Nat.div_add_mod` and `Nat.mod_lt`, and finite convergence verification in Lean 4.
- **DO NOT USE FOR:** continuous Lyapunov stability via differential equations (delegate to `@lean-math-dynamical`); simple for-loop syntax verification without energy functions (delegate to `@lean-build`).
- **TRIGGERS:** lyapunov, convergence, termination bound, gpu bound, power iteration, ceiling division, div_add_mod, residue decay.

## Workflow

1. Define state space and non-negative integer Lyapunov energy function `lyapunov : State -> Nat`.
2. Formulate the strict step decay condition `forall t < n, lyapunov (traj (t + 1)) + delta <= lyapunov (traj t)` with `delta > 0`.
3. Prove finite convergence by induction over step indices: rewrite non-linear terms `(t + 1) * delta` to `t * delta + delta` using `Nat.succ_mul` before calling `omega`.
4. Formulate ceiling division upper bound `n = (v0 + delta - 1) / delta`.
5. Prove the arithmetic floor bound `((v0 + delta - 1) / delta) * delta >= v0` by instantiating `Nat.div_add_mod` and `Nat.mod_lt` together with `omega`.
6. Conclude exact convergence `lyapunov (traj n) = 0`, guaranteeing finite GPU termination without warp divergence.
7. Verify against `templates/Template_Lyapunov.md`.

## Recovery & STOP

- STOP if estimated belief in inductive convergence hypothesis is below 0.90 -- ask user via HITL channel.
- STOP if `omega` fails on non-linear division -- check that `Nat.div_add_mod` has been explicitly introduced into the local context.
- STOP if real numbers are introduced for discrete counters -- restrict all energy and step values strictly to `Nat`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-math-discrete` (discrete structures), `skill:lean-proof` (tactics).
- **Successors:** `skill:lean-proof` (inductive step discharge), `skill:lean-proof-review` (lockdown audit).
