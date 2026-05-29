---
name: "applied-strategy-analysis"
description: |
  USE FOR: Strategy creation, analysis, and evaluation — game-theoretic foundations, competitive analysis, decision frameworks, SWOT/PESTLE, wargaming, and their mathematical underpinnings. Use for strategic reasoning about complex multi-agent scenarios, organizational strategy, research strategy, and mathematical planning for governance and optimization layers.
  DO NOT USE FOR: formalising strategic models in Lean (use @lean-applied-reasoning); intelligence analysis (use @applied-intelligence-analysis); game-theoretic optimization (use @math-optimization-game).
  TRIGGERS: strategy, SWOT, PESTLE, wargaming, decision framework, competitive analysis, game-theoretic strategy.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-applied-reasoning', 'skill:math-optimization-game', 'skill:applied-intelligence-analysis']
metadata:
  version: "0.2.0"
  source_spec: "skills/applied-strategy-analysis/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# Strategy Creation & Analysis

Mathematical and systematic frameworks for creating, evaluating, and executing strategies in competitive and cooperative environments.

---

## Routing

- **USE FOR:** Strategy creation, analysis, and evaluation — game-theoretic foundations, competitive analysis, decision frameworks, SWOT/PESTLE, wargaming, and their mathematical underpinnings. Use for strategic reasoning about complex multi-agent scenarios, organizational strategy, research strategy, and mathematical planning for governance and optimization layers.
- **DO NOT USE FOR:** formalising strategic models in Lean (use @lean-applied-reasoning); intelligence analysis (use @applied-intelligence-analysis); game-theoretic optimization (use @math-optimization-game).
- **TRIGGERS:** strategy, SWOT, PESTLE, wargaming, decision framework, competitive analysis, game-theoretic strategy.

## Workflow

1. Frame the strategic situation: competitors, payoffs, information structure, time horizon.
2. Pick the matching framework (SWOT, PESTLE, Porter, wargame, game-theoretic equilibrium) from the body.
3. Run the analysis; produce the strategic recommendation with explicit assumptions + sensitivities.
4. Hand off: to `@lean-applied-reasoning` if formalisation is needed, to `@math-optimization-game` if game-theoretic structure dominates, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the question collapses to a pure optimization problem — delegate to `@math-optimization-game`.
- STOP if intelligence-analysis methodology is what's needed — delegate to `@applied-intelligence-analysis`.
- STOP if the legal/regulatory dimension dominates — delegate to `@applied-legal-reasoning`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-applied-reasoning`, `skill:math-optimization-game`, `skill:applied-intelligence-analysis`.

---

## Detailed reference

Full content for `applied-strategy-analysis` lives in
[`references/applied-strategy-analysis-handbook.md`](../../references/applied-strategy-analysis-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

| Section | Topic |
|---|---|
| Part 1 | Strategic Reasoning Foundations |
| Part 2 | Game-Theoretic Strategy |
| Part 3 | Decision Frameworks |
| Part 4 | Competitive Analysis Frameworks |
| Part 5 | Wargaming & Red Teaming |
| Part 6 | Proof Strategy Design |
| Part 7 | Research Strategy |
| Part 8 | Cross-References |

---

## See also

- [`../../references/applied-strategy-analysis-handbook.md`](../../references/applied-strategy-analysis-handbook.md) — Full handbook (extracted from this skill)
- [`../lean-applied-reasoning/SKILL.md`](../lean-applied-reasoning/SKILL.md) — Successor
- [`../math-optimization-game/SKILL.md`](../math-optimization-game/SKILL.md) — Successor
- [`../applied-intelligence-analysis/SKILL.md`](../applied-intelligence-analysis/SKILL.md) — Successor
