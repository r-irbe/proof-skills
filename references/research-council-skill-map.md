---
title: "Research-council skill map (single canonical routing matrix)"
status: reference
source: consolidated from `Part 7 — Research Council Integration` in all 7 lean-math-* + lean-ai-formalization SKILL.md files
owners: research-council, lean-gateway
date: 2026-05-27
---

# Research-council skill map

Single, canonical routing matrix from **mathematical topic → research
council member**.  Each consumer skill replaces its bespoke "Part 7 —
Research Council Integration" table with a one-line `See also` pointer
to this file.

The council roles are abbreviated:

| Abbrev | Role |
|---|---|
| Α | Foundations Architect |
| Β | Structure Strategist |
| Γ | Methods Scholar |
| Δ | Bounds Analyst |
| LC | Lean community (mathlib4 Zulip) |
| Lit | Literature search |

## Foundations (logic, sets, algebra, typeclasses, induction)

| Topic | Council member |
|---|---|
| Universe-level issues | Α |
| Typeclass inference failures | Α + LC |
| Algebraic hierarchy choice | Β |
| Order-theoretic formulation | Β |
| Proof-technique selection | Γ |
| Induction-schema choice | Γ |
| Constructive vs classical choice | Α |

## Analysis (continuity, derivatives, metric, convex, measure)

| Topic | Council member |
|---|---|
| Filter / topology formulation | Β |
| Derivative computation | Γ |
| Contraction bound tightness | Δ |
| Measure-theoretic formulation | Β |
| Convexity arguments | Γ |
| Spectral analysis | Δ + Lit |
| Functional analysis (Banach) | Α |

## Dynamical (Lyapunov, bifurcation, catastrophe, phase, control)

| Topic | Council member |
|---|---|
| Lyapunov function design | Β |
| Lyapunov proof closure | Γ |
| Bifurcation classification | Β + Lit |
| Cusp-catastrophe geometry | Β |
| Phase-portrait formalisation | Β |
| Control-system reduction | Β |
| Tight contraction-rate bounds | Δ |

## Stochastic (probability, Markov, spectral gap, stochastic stability)

| Topic | Council member |
|---|---|
| Probability-space setup | Α |
| Markov-chain stationary existence | Β |
| Spectral-gap estimation | Δ + Lit |
| Mean-square / a.s. stability | Γ |
| Coupling / mixing argument | Γ |
| Stochastic-deterministic bridge | Β |

## Optimization (convex, fixed-point, Bellman, games, RL theory)

| Topic | Council member |
|---|---|
| Convex-function characterisation | Β |
| Banach fixed-point setup | Α |
| Bellman / γ-contraction | Β |
| Game-theoretic equilibrium | Β + Lit |
| Mechanism-design property | Β + Lit |
| RL convergence bound tightness | Δ |
| Pareto-front structure | Γ |

## Discrete (graph, DAG, lattice, combinatorics, WQO, FSM)

| Topic | Council member |
|---|---|
| Graph-representation choice | Β |
| DAG topological-sort proof | Γ |
| Lattice / Galois-connection setup | Β |
| Combinatorial-counting argument | Γ |
| Well-quasi-order termination | Γ |
| FSM-property formalisation | Β |

## AI formalisation (safety, agentic, alignment, EU AI Act, NN)

| Topic | Council member |
|---|---|
| Safety-property taxonomy | Β + Lit |
| Agent-model contract | Β |
| Alignment / reward spec | Β + Lit |
| EU AI Act compliance | Β + Lit |
| NN property (Lipschitz / monotone) | Γ (routes to convergence) |
| Multi-agent composition | Β |
| Causal-DAG reasoning | Β |

## Cross-cutting notes

- **Δ (Bounds Analyst)** typically owns *tightness* questions: "is this
  rate the best you can prove?".  Routed independently of which math
  domain the question lives in.
- **Lit** = a literature search step is unavoidable.  These topics are
  where Mathlib's coverage is thin and the council member needs to
  hand-translate from a paper.
- **LC (Lean community)** is the right escalation point for *typeclass
  inference failures* and *Mathlib symbol drift*; do not waste council
  time on a question that is fundamentally "what is the current name?".

## See also

- `references/lean4-ivt-patterns.md` — co-canonical reference for
  IVT applications, often cited by Β + Γ together.
- `references/lean4-contraction-catalog.md` — co-canonical reference
  for Banach / Lyapunov bridges, often cited by Α + Β.
- `skills/research-council/SKILL.md` — the role-charter doc, owner
  of this routing matrix's authoritative version.
