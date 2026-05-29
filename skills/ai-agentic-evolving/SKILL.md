---
name: "ai-agentic-evolving"
description: |
  USE FOR: Agentic AI systems, multi-agent coordination, evolving agents, agent lifecycle management, emergent behavior, and trust dynamics in autonomous systems. Use for reasoning about agent architectures, communication protocols, coalition formation, reputation systems, and the mathematical foundations of agentic safety and multi-agent trust formalization.
  DO NOT USE FOR: formal verification of those AI systems (use @lean-ai-formalization); high-stakes / verifiable AI mode (use @ai-high-stakes-verifiable); causal/deontic reasoning (use @ai-causal-deontic).
  TRIGGERS: agentic AI, multi-agent, evolving agent, agent lifecycle, emergent behavior, trust dynamics, autonomous system.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-ai-formalization', 'skill:ai-high-stakes-verifiable', 'skill:lean-zettelkasten']
metadata:
  version: "0.2.0"
  source_spec: "skills/ai-agentic-evolving/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# Agentic & Evolving AI Systems

Mathematical and architectural foundations for autonomous agents, multi-agent systems, evolving capabilities, and formally verified trust/safety dynamics.

---

## Routing

- **USE FOR:** Agentic AI systems, multi-agent coordination, evolving agents, agent lifecycle management, emergent behavior, and trust dynamics in autonomous systems. Use for reasoning about agent architectures, communication protocols, coalition formation, reputation systems, and the mathematical foundations of agentic safety and multi-agent trust formalization.
- **DO NOT USE FOR:** formal verification of those AI systems (use @lean-ai-formalization); high-stakes / verifiable AI mode (use @ai-high-stakes-verifiable); causal/deontic reasoning (use @ai-causal-deontic).
- **TRIGGERS:** agentic AI, multi-agent, evolving agent, agent lifecycle, emergent behavior, trust dynamics, autonomous system.

## Workflow

1. Frame the system: how many agents, what each agent optimises for, what coordination signal exists, and which lifecycle phase (spawn / coordinate / evolve / retire) the question is about.
2. Pick the matching theoretical lens from the body — emergence, multi-agent game theory, mechanism design, evolutionary dynamics, or trust dynamics.
3. Run the reasoning at the methodological level; do not attempt formal proofs here. Belief floor 0.90 before publishing.
4. Hand off: to `@lean-ai-formalization` if a property needs Lean proof, to `@ai-high-stakes-verifiable` if the agents are safety-critical, to `@lean-zettelkasten` for the durable note.

## Recovery & STOP

- STOP if the question is about formal AI verification rather than agentic dynamics — hand to `@lean-ai-formalization`.
- STOP if the system collapses to single-agent — switch to whichever non-agentic AI skill matches (e.g., `@ai-symbolic-neuro` for KR, `@ai-commonsense-reasoning` for reasoning).
- STOP if emergence analysis would require empirical simulation rather than methodological reasoning — escalate to `@research-council`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-ai-formalization`, `skill:ai-high-stakes-verifiable`, `skill:lean-zettelkasten`.

---

## Detailed reference

Full content for `ai-agentic-evolving` lives in
[`references/ai-agentic-evolving-handbook.md`](../../references/ai-agentic-evolving-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

| Section | Topic |
|---|---|
| Part 1 | Agent Architectures |
| Part 2 | Multi-Agent Coordination |
| Part 3 | Evolving Agents |
| Part 4 | Safety in Agentic Systems |
| Part 5 | Reputation & Trust Systems |
| Part 6 | Connection to Project Lean Modules |
| Part 7 | Research Frontiers |

---

## See also

- [`../../references/ai-agentic-evolving-handbook.md`](../../references/ai-agentic-evolving-handbook.md) — Full handbook (extracted from this skill)
- [`../lean-ai-formalization/SKILL.md`](../lean-ai-formalization/SKILL.md) — Successor
- [`../ai-high-stakes-verifiable/SKILL.md`](../ai-high-stakes-verifiable/SKILL.md) — Successor
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor
