---
name: "lean-math-optimization"
description: |
  USE FOR: optimization theory, convex optimization, game theory, reinforcement-learning theory (Bellman equations, value / policy iteration), Nash equilibria, minimax theorems, decision theory, and fixed-point iterations in Lean 4.
  DO NOT USE FOR: stochastic policies / Markov chains (use @lean-math-stochastic); pure analysis (use @lean-math-analysis); Lyapunov / control-stability proofs (use @lean-math-dynamical); writing one specific proof (use @lean-proof).
  TRIGGERS: optimization, convex, game theory, Bellman, value iteration, policy iteration, Nash, minimax, fixed point, KKT.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-proof", "skill:lean-research"]
  successors: ["skill:lean-proof", "skill:lean-proof-review", "skill:lean-math-analysis"]
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-math-optimization/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Lean 4 Optimization & Decision Theory

Guide to formalizing optimization, game theory, RL theory, and decision-making in Lean 4.

## Routing

- **USE FOR:** optimization theory, convex optimization, game theory, reinforcement-learning theory (Bellman equations, value / policy iteration), Nash equilibria, minimax theorems, decision theory, and fixed-point iterations in Lean 4.
- **DO NOT USE FOR:** stochastic policies / Markov chains (delegate to `@lean-math-stochastic`); pure analysis (delegate to `@lean-math-analysis`); Lyapunov / control-stability proofs (delegate to `@lean-math-dynamical`); writing one specific proof (delegate to `@lean-proof`).
- **TRIGGERS:** optimization, convex, game theory, Bellman, value iteration, policy iteration, Nash, minimax, fixed point, KKT.

## Workflow

1. Identify the optimality structure (Part 1) — unconstrained, convex, equilibrium, dynamic-programming.
2. Pick the matching tool below (gradient / KKT, contraction / Banach fixed-point, Bellman backup, Nash-equilibrium argument).
3. Handoff to `@lean-proof`; if the contraction step requires a normed-space lemma, handoff to `@lean-math-analysis`.

## Recovery & STOP

- STOP if the proof requires a Banach-contraction instance not yet imported — handoff to `@lean-math-analysis`.
- STOP if a stochastic policy or expected-value argument appears — re-route to `@lean-math-stochastic`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-proof` (mid-proof optimization goal), `skill:lean-research` (Bellman / Nash-equilibrium API survey).
- **Successors:** `skill:lean-proof` (apply the optimization pattern), `skill:lean-proof-review` (audit fixed-point claim), `skill:lean-math-analysis` (contraction / normed-space reduction).

## Detailed reference

Full encyclopaedia content (Parts 1 through 7) lives in
[`references/lean4-math-optimization.md`](../../references/lean4-math-optimization.md). Load that file
when authoring; the SKILL.md only carries the dispatch contract and
the high-frequency pitfalls / recipes (kept inline below).

| Part | Topic | Covers |
|---|---|---|
| Part 1 | Optimization Fundamentals | objective / feasible-set / optimum vocabulary in Mathlib |
| Part 2 | Convex Optimization | ConvexOn, KKT (project-side), Jensen, gradient conditions |
| Part 3 | Fixed-Point Iterations | Banach contraction; iteration-bound estimates |
| Part 4 | Game Theory | Nash equilibrium, zero-sum, minimax, saddle-point hypotheses |
| Part 5 | Reinforcement Learning Theory | Bellman backup, value/policy iteration, discount factor |
| Part 6 | Multi-Objective Optimization | Pareto frontier, lexicographic ordering |
| Part 7 | Decision Theory | bounded rationality + project alignment |

## Part 8 — Research Council Integration

Consolidated into the single canonical routing matrix:
[`references/research-council-skill-map.md`](../../references/research-council-skill-map.md)
(see the "Optimization" section).  When dispatching a question to a
council member, cite that table rather than restating the rows here.

---

## Part 9 — Common Pitfalls (Convex / RL / Game Theory)

| Pitfall | Symptom | Recovery |
|---|---|---|
| Bellman without `0 ≤ γ < 1` | Value-iteration convergence won't close | Add hypothesis `hγ : γ < 1`; the Bellman backup is a contraction in `‖·‖∞` *only* under this condition |
| Convex but not *strictly* convex | Uniqueness of optimum fails | Strengthen to `StrictConvexOn` instead of `ConvexOn`; pair with strict-monotonicity for the optimum step |
| Banach contraction missing `[CompleteSpace α]` | `ContractingWith.fixedPoint` won't apply | Add the instance, or restrict to a closed ball with induced completeness |
| Minimax order flipped | `inf sup ≤ sup inf` doesn't close | Saddle-point requires compact + convex + continuous on both sides; check Sion's-theorem hypotheses (no Sion in Mathlib at current pin — local construction or `@lean-research`) |
| Discount factor used as `ℝ` while state is `ℕ` | Coercion warnings; `^` won't elaborate | Use `(γ : ℝ) ^ n` and prove with `Real.rpow_lt_one` family (or `pow_lt_one_iff_of_nonneg`) |
| Non-empty / non-bounded feasible set assumed | `IsLeast` / `IsGLB` won't construct | Bound the feasible set explicitly; for unbounded LP, no Mathlib fixed-point applies — use `@lean-research` |

### RL-theory escape hatches

- **Finite horizon:** `Finset.sum_range_succ` unfolding usually beats induction on a `valueFn`.
- **Infinite horizon:** only meaningful with `0 ≤ γ < 1`; the geometric-series bound is `Real.geom_series_lt` / `tsum_geometric_lt_one` / `summable_geometric_of_lt_one`.
- **Value-iteration convergence:** prove the Bellman backup is a contraction in `‖·‖∞`, then apply the Banach fixed-point theorem (see `@lean-math-dynamical` Part 10 for the recipe).
- **Policy iteration:** equivalence to value iteration is *not* in Mathlib — author a local lemma per project and cite it.

---

## Part 10 — Convex-Optimization Cross-Reference

| Goal | Mathlib lemma / tactic |
|---|---|
| Jensen's inequality | `ConvexOn.inner_le_iff`, `ConvexOn.smul_le_sum` |
| Strict convexity → unique minimum | `StrictConvexOn.eq_of_le_of_le` (project-side lemma usually required) |
| Convex hull of a finite set | `Mathlib.Analysis.Convex.Hull` — `convexHull_eq` |
| Polytope vertices | `Mathlib.Analysis.Convex.Extrema` — extreme-point characterisation |
| KKT conditions | *No general KKT API in Mathlib*; author locally and cite |
| `stdSimplex.le_one` (single-coord ≤ 1) | `Mathlib/Analysis/Convex/StdSimplex.lean:304` — prefer over `(mem_Icc_of_mem_stdSimplex h x).2` for single-coordinate queries |

---

## See also

- [`../../references/lean4-math-optimization.md`](../../references/lean4-math-optimization.md) — Optimization & Decision Theory Encyclopaedia (full encyclopaedia, extracted from this skill)
- [`../../templates/Template_Dynamics.md`](../../templates/Template_Dynamics.md) — Template: Fixed-point and contraction iterations
- [`../../templates/Template_Arithmetic.md`](../../templates/Template_Arithmetic.md) — Template: Scaled-Nat thresholds and convex bounds
- [`../../references/lean4-tactic-hierarchy.md`](../../references/lean4-tactic-hierarchy.md) — Tactic priority for arithmetic goals
