---
name: "lean-math-dynamical"
description: |
  USE FOR: nonlinear dynamical systems, Lyapunov stability, bifurcation theory, catastrophe theory, control theory, phase-portrait analysis, attractor classification, and any deterministic system with state evolution over time in Lean 4.
  DO NOT USE FOR: stochastic dynamics (use @lean-math-stochastic); pure analysis / topology (use @lean-math-analysis); optimization-only control problems (use @lean-math-optimization); writing one specific proof (use @lean-proof).
  TRIGGERS: Lyapunov, stability, bifurcation, cusp catastrophe, attractor, phase portrait, dynamical system, control theory, equilibrium.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-proof", "skill:lean-research"]
  successors: ["skill:lean-proof", "skill:lean-proof-review", "skill:lean-math-analysis"]
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-math-dynamical/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Lean 4 Nonlinear Dynamics & Stability

Guide to formalizing dynamical systems, stability theory, and bifurcation in Lean 4.

## Routing

- **USE FOR:** nonlinear dynamical systems, Lyapunov stability, bifurcation theory, catastrophe theory, control theory, phase-portrait analysis, attractor classification, and any deterministic system with state evolution over time in Lean 4.
- **DO NOT USE FOR:** stochastic dynamics (delegate to `@lean-math-stochastic`); pure analysis / topology (delegate to `@lean-math-analysis`); optimization-only control problems (delegate to `@lean-math-optimization`); writing one specific proof (delegate to `@lean-proof`).
- **TRIGGERS:** Lyapunov, stability, bifurcation, cusp catastrophe, attractor, phase portrait, dynamical system, control theory, equilibrium.

## Workflow

1. Classify the system (Part 1) — discrete-time, continuous-time, gradient, conservative, controlled.
2. Pick the appropriate technique below (Lyapunov, contraction, bifurcation-normal-form, catastrophe-classification).
3. Handoff to `@lean-proof` for the concrete proof; if it bottoms out in a derivative / measure step, handoff to `@lean-math-analysis`.

## Recovery & STOP

- STOP if the proof depends on a manifold or smooth-structure API not in Mathlib at the current pin — escalate to `@lean-research`.
- STOP if a stochastic perturbation enters the model — re-route to `@lean-math-stochastic`; this skill covers only deterministic dynamics.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-proof` (mid-proof stability goal), `skill:lean-research` (catastrophe-theory result survey).
- **Successors:** `skill:lean-proof` (apply the dynamical pattern), `skill:lean-proof-review` (audit Lyapunov candidate), `skill:lean-math-analysis` (continuous-derivative or contraction reduction).

## Detailed reference

Full encyclopaedia content (Parts 1 through 6) lives in
[`references/lean4-math-dynamical.md`](../../references/lean4-math-dynamical.md). Load that file
when authoring; the SKILL.md only carries the dispatch contract and
the high-frequency pitfalls / recipes (kept inline below).

| Part | Topic | Covers |
|---|---|---|
| Part 1 | Dynamical Systems Taxonomy | discrete-time, continuous-time, gradient, conservative, controlled |
| Part 2 | Lyapunov Stability Theory | candidate construction, positive-definiteness, LaSalle |
| Part 3 | Bifurcation and Catastrophe Theory | cusp / fold / pitchfork normal forms |
| Part 4 | Phase Space Analysis | phase portraits, equilibria classification |
| Part 5 | Control Theory Connections | Lyapunov-control, control-Lyapunov functions |
| Part 6 | Nonlinear Methods Toolbox | linearisation, normal-form reduction, numerical-continuation hints |

## Part 7 — Research Council Integration

Consolidated into the single canonical routing matrix:
[`references/research-council-skill-map.md`](../../references/research-council-skill-map.md)
(see the "Dynamical" section).  When dispatching a question to a
council member, cite that table rather than restating the rows here.

---

## Part 8 — IVT Sign-Change Pattern

Extracted to single canonical reference:
[`references/lean4-ivt-patterns.md`](../../references/lean4-ivt-patterns.md).
That file owns the canonical incantation, the
`asymmetric_three_roots_ivt` walk-through, and the polynomial-continuity
prerequisite.

---

## Part 9 — Common Pitfalls (Stability & Bifurcation)

| Pitfall | Symptom | Recovery |
|---|---|---|
| Lyapunov candidate not positive-definite | `V 0 = 0` proved, but `V x > 0` for `x ≠ 0` fails | Add a quadratic-form witness (`x^T Q x` with `Q` PSD); check `posDef_iff_eigenvalues_pos` family |
| Contraction map without `[CompleteSpace α]` | `ContractingWith.fixedPoint` won't apply | Add `[CompleteSpace α]` instance or restrict to a closed subset and use `IsCompact.completeSpace` |
| IVT sign-error in bifurcation diagram | Existential `∃ c, f c = 0` won't close | Re-check sign of `f a` and `f b`; see `references/lean4-ivt-patterns.md` for the canonical `asymmetric_three_roots_ivt` walk-through |
| Catastrophe normal form drifted from repository canon | `cusp` / `fold` polynomial signs don't match expectations | Compare against `Mathlib.Analysis.SpecialFunctions.Pow.Real`; there is *no* canonical catastrophe API in Mathlib — keep local definitions in the host repository's catastrophe namespace |
| Discrete- vs continuous-time confusion | `Tendsto` with the wrong filter | Discrete: `atTop` on `ℕ`; continuous: `atTop` on `ℝ` (often with a measure-preserving step) |
| Spurious equilibrium from `simp` overreach | `f x = x` "proved" by simplifying both sides to `0` | Disable `simp` for the candidate equilibrium proof; use `linear_combination` or explicit substitution |

### Cross-reference: repository stability tactics

- Host-repository Lyapunov modules — quadratic-form Lyapunov constructions for local cusp + phase-portrait models.
- Host-repository catastrophe modules — cusp-form polynomial bifurcation (the 3-real-roots case).
- [`references/lean4-ivt-patterns.md`](../../references/lean4-ivt-patterns.md) — `asymmetric_three_roots_ivt` walk-through (canonical entry-point for sign-change existence).
- [`references/lean4-contraction-catalog.md`](../../references/lean4-contraction-catalog.md) — catalog of contraction-mapping templates (uses `ContractingWith` / `LipschitzWith`).

---

## Part 10 — Banach Fixed-Point Recipe

The most common "I need a fixed point" pattern in this corpus:

```lean
-- Given a self-map f : α → α and a contraction constant K < 1:
example {α : Type*} [MetricSpace α] [CompleteSpace α]
    (f : α → α) {K : NNReal} (hK : K < 1)
    (hC : ContractingWith K f) :
    ∃! x, f x = x :=
  ⟨hC.fixedPoint, hC.fixedPoint_isFixedPt,
   fun y hy => hC.fixedPoint_unique hy⟩
```

Project-relevant adaptations:

- **Sub-Banach setting:** `IsCompact.completeSpace` lets you restrict to a closed ball when global completeness is unwieldy.
- **Iteration bounds:** `ContractingWith.aux_dist_le` gives `dist (f^[n] x) (fixedPoint) ≤ K^n * dist x (fixedPoint) / (1 - K)`.
- **Existence-only (no uniqueness):** Schauder fixed-point — *not* in Mathlib at the current pin; use `@lean-research` to confirm before authoring.

---

## See also

- [`../../references/lean4-math-dynamical.md`](../../references/lean4-math-dynamical.md) — Nonlinear Dynamics Encyclopaedia (full encyclopaedia, extracted from this skill)
- [`../../templates/Template_Dynamics.md`](../../templates/Template_Dynamics.md) — Template: Lyapunov / Markov / contraction mappings
- [`../../references/lean4-proof-strategy.md`](../../references/lean4-proof-strategy.md) — Proof strategy: real-valued contraction patterns
