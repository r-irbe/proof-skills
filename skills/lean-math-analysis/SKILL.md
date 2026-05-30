---
name: "lean-math-analysis"
description: |
  USE FOR: real analysis, functional analysis, topology, and measure theory in Lean 4 / Mathlib — continuous functions, derivatives, integrals, metric / normed spaces, filter-based convergence, contraction mappings, convex analysis, spectral theory, and the real-valued bridges from a Nat-scaled model.
  DO NOT USE FOR: stochastic / probabilistic convergence (use @lean-math-stochastic); deterministic dynamical-system stability proofs (use @lean-math-dynamical); pure optimization (use @lean-math-optimization); typeclass-tower reasoning (use @lean-math-foundations); writing one specific proof (use @lean-proof).
  TRIGGERS: continuous, derivative, integral, metric space, normed space, filter, convergence, topology, measure space, contraction, Banach.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-proof", "skill:lean-research"]
  successors: ["skill:lean-proof", "skill:lean-proof-review", "skill:lean-math-foundations"]
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-math-analysis/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Lean 4 Real Analysis & Topology

Guide to formalizing analysis and topology in Lean 4 using Mathlib's filter-based approach.

## Routing

- **USE FOR:** real analysis, functional analysis, topology, and measure theory in Lean 4 / Mathlib — continuous functions, derivatives, integrals, metric / normed spaces, filter-based convergence, contraction mappings, convex analysis, spectral theory, and the real-valued bridges from a Nat-scaled model.
- **DO NOT USE FOR:** stochastic / probabilistic convergence (delegate to `@lean-math-stochastic`); deterministic dynamical-system stability proofs (delegate to `@lean-math-dynamical`); pure optimization (delegate to `@lean-math-optimization`); typeclass-tower reasoning (delegate to `@lean-math-foundations`); writing one specific proof (delegate to `@lean-proof`).
- **TRIGGERS:** continuous, derivative, integral, metric space, normed space, filter, convergence, topology, measure space, contraction, Banach.

## Workflow

1. Map the problem to Mathlib's filter-based architecture (Part 1) — most analysis goals can be phrased as `Tendsto … atTop` or `ContinuousAt`.
2. Locate the relevant Part below (continuity, derivatives, integrals, normed spaces, measure theory) and apply the pattern.
3. If the result is a concrete proof obligation, handoff to `@lean-proof`; if it depends on a foundational instance, handoff to `@lean-math-foundations`.

## Recovery & STOP

- STOP if the lemma you need is not in Mathlib at the current pin — escalate to `@lean-research` to verify, then `@lean-proof` to author a local helper.
- STOP if a classical-only result is invoked and the project has documented constructive constraints — escalate to `@lean-review-council`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-proof` (mid-proof convergence goal), `skill:lean-research` (when a survey turns up an analysis API).
- **Successors:** `skill:lean-proof` (apply the analysis pattern), `skill:lean-proof-review` (audit the resulting proof), `skill:lean-math-foundations` (when the goal collapses to a typeclass-tower issue).

## Detailed reference

Full encyclopaedia content (Parts 1 through 8) lives in
[`references/lean4-math-analysis.md`](../../references/lean4-math-analysis.md). Load that file
when authoring; the SKILL.md only carries the dispatch contract and
the high-frequency pitfalls / recipes (kept inline below).

| Part | Topic | Covers |
|---|---|---|
| Part 1 | Mathlib's Analysis Architecture | filter-based convergence, topological-space layering |
| Part 2 | Continuity and Limits | Continuous, ContinuousAt, ContinuousOn, Tendsto |
| Part 3 | Differentiation | HasDerivAt, deriv, fderiv, mean-value theorem |
| Part 4 | Metric Spaces and Contraction | MetricSpace, LipschitzWith, ContractingWith, completeness |
| Part 5 | Convex Analysis | ConvexOn, ConvexHull, Jensen's inequality |
| Part 6 | Measure Theory Essentials | MeasureSpace, MeasureTheory.integral, intervalIntegral |
| Part 7 | Research Council Integration | (also kept inline below) — analysis-domain dispatch matrix |
| Part 8 | Host-Repository Analysis Extensions | repository-local Lyapunov / contraction / convex-on-Nat bridges |

## Part 8 — Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| `ℝ` vs `ℝ≥0` confusion | Type mismatch on nonneg results | Use `.toReal` or `NNReal.coe_*` lemmas |
| Filter direction wrong | `atTop` vs `atBot` | Check: are you going to ∞ or 0? |
| Missing `CompleteSpace` | Contraction theorem won't apply | Add hypothesis or use `instCompleteSpaceReal` |
| `norm` vs `abs` | `‖x‖` vs `|x|` for `ℝ` | They're definitionally equal on `ℝ`, but `rw [Real.norm_eq_abs]` may help |
| Derivative of composed function | `HasDerivAt` won't compose automatically | Use `HasDerivAt.comp` explicitly |
| Measure vs volume | Wrong default measure | Specify `volume` or `MeasureTheory.MeasureSpace.volume` |

---

## Part 9 — Tactic Priority for Analysis Goals

When a goal sits in the analysis family, try these in order before reaching for manual `.comp` chains:

1. **`fun_prop`** — Mathlib's general property-prover for `Continuous`, `Measurable`, `Differentiable`, `StronglyMeasurable` on composed functions. Prefer this over manual `Continuous.comp` / `Differentiable.comp` chains.
2. **`continuity`** — older specialised continuity solver; still helpful when `fun_prop` misses a Mathlib lemma.
3. **`measurability`** — for `Measurable` / `AEMeasurable` / `StronglyMeasurable` goals; complements `fun_prop`.
4. **`positivity`** — for `0 < x` / `0 ≤ x` goals involving `exp`, `log`, norms, integrals; pairs well with `gcongr` for inequality chaining.
5. **`gcongr`** — generalised congruence; replaces a long `MonoOn.*` chain for `≤` between integrals, norms, suprema, etc.
6. **`bound`** — newer Mathlib bound-prover; useful when `positivity` can't close (e.g., requires a hypothesis to bound).
7. **`norm_num` / `nlinarith`** — pure numeric / nonlinear arithmetic; last-resort closers for concrete numeric bounds.

If nothing fires, fall back to explicit `apply HasDerivAt.comp`, `apply Continuous.comp`, etc. — but those are last-resort.

---

## Part 10 — Filter-Convergence Escape Hatches

When `Tendsto` won't simp:

- **`eventually_atTop`** rewrites `∀ᶠ n in atTop, P n` to `∃ N, ∀ n ≥ N, P n` — switch when classical existence is easier than filter algebra.
- **`Filter.tendsto_atTop_atTop`** — discrete `f n → ∞`: prove `∀ b, ∃ N, ∀ n ≥ N, b ≤ f n`.
- **`Tendsto.comp`** — composition of limits; the most common building block.
- **`Filter.eventually_iff_exists_mem`** — convert between `∀ᶠ` and explicit set membership.
- **`Metric.tendsto_atTop`** — for metric-space convergence, use the `ε / δ` form directly when filter-arithmetic gets stuck.

When integration limits won't compute:

- **`MeasureTheory.integral_congr_ae`** — change the integrand on a null set without re-proving integrability.
- **`MeasureTheory.intervalIntegral.integral_congr`** — change of variables on a compact interval.
- **`MeasureTheory.lintegral_lt_top_iff_finite_set_of_pos`** — when proving an `lintegral` is finite, this often beats direct estimation.

---

## See also

- [`../../references/lean4-math-analysis.md`](../../references/lean4-math-analysis.md) — Real Analysis & Topology Encyclopaedia (full encyclopaedia, extracted from this skill)
- [`../../templates/Template_Analysis.md`](../../templates/Template_Analysis.md) — Template: Real analysis (continuity, Lipschitz, sqrt)
- [`../../references/lean4-proof-strategy.md`](../../references/lean4-proof-strategy.md) — Proof strategy & error priority
- [`../../references/lean4-tactic-hierarchy.md`](../../references/lean4-tactic-hierarchy.md) — Tactic priority for analysis goals
