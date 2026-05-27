---
name: "math-nonlinear-dynamics"
description: |
  USE FOR: General nonlinear dynamics, chaos theory, bifurcation analysis, catastrophe theory, attractor geometry, Lyapunov methods, phase portraits, and control-theoretic stability. Use for any mathematical reasoning about dynamical systems BEFORE or BEYOND Lean formalization. Covers theory, intuition, calculation techniques, and connection to the project's phase portrait, cusp catastrophe, and governance dynamics.
  DO NOT USE FOR: Lean proofs in this domain (use @lean-math-dynamical); optimization theory (use @math-optimization-game); topology methods (use @math-topology-analysis).
  TRIGGERS: nonlinear dynamics, chaos theory, bifurcation, catastrophe theory, attractor, Lyapunov, phase portrait.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-math-dynamical', 'skill:lean-research', 'skill:lean-zettelkasten']
metadata:
  version: "0.2.0"
  source_spec: "skills/math-nonlinear-dynamics/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# General Nonlinear Dynamics & Catastrophe Theory

Comprehensive mathematical methodology for nonlinear dynamics — the theoretical backbone of the project's phase portrait, cusp catastrophe, Lyapunov stability, and governance convergence modules.

---

## Routing

- **USE FOR:** General nonlinear dynamics, chaos theory, bifurcation analysis, catastrophe theory, attractor geometry, Lyapunov methods, phase portraits, and control-theoretic stability. Use for any mathematical reasoning about dynamical systems BEFORE or BEYOND Lean formalization. Covers theory, intuition, calculation techniques, and connection to the project's phase portrait, cusp catastrophe, and governance dynamics.
- **DO NOT USE FOR:** Lean proofs in this domain (use @lean-math-dynamical); optimization theory (use @math-optimization-game); topology methods (use @math-topology-analysis).
- **TRIGGERS:** nonlinear dynamics, chaos theory, bifurcation, catastrophe theory, attractor, Lyapunov, phase portrait.

## Workflow

1. Classify the system: ODE / PDE / map / SDE / hybrid; identify the phase-space and invariants.
2. Pick the matching section (Lyapunov / bifurcation / catastrophe / chaos / control).
3. Produce the answer with explicit assumptions + regularity; cite the Mathlib namespace if applicable.
4. Hand off: to `@lean-math-dynamical` for the Lean proof, to `@math-optimization-game` if control becomes optimal-control, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the question is about optimisation (not dynamics) — delegate to `@math-optimization-game`.
- STOP if topological tools dominate — delegate to `@math-topology-analysis`.
- STOP if Mathlib lacks the needed lemma — escalate to `@lean-research`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-math-dynamical`, `skill:lean-research`, `skill:lean-zettelkasten`.

---

## Detailed reference

Full content for `math-nonlinear-dynamics` lives in
[`references/math-nonlinear-dynamics-handbook.md`](../../references/math-nonlinear-dynamics-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

| Section | Topic |
|---|---|
| Part 1 | Core Mathematical Framework |
| Part 2 | Bifurcation Analysis Methodology |
| Part 3 | Lyapunov Function Construction |
| Part 4 | Phase Portrait Analysis |
| Part 5 | Control-Theoretic Perspective |
| Part 6 | Connections to Other Mathematical Disciplines |
| Part 7 | Research Entry Points |

---

## See also

- [`../../references/math-nonlinear-dynamics-handbook.md`](../../references/math-nonlinear-dynamics-handbook.md) — Full handbook (extracted from this skill)
- [`../lean-math-dynamical/SKILL.md`](../lean-math-dynamical/SKILL.md) — Successor
- [`../lean-research/SKILL.md`](../lean-research/SKILL.md) — Successor
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor

