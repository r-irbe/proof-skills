---
name: "math-strategy-studio"
description: |
  USE FOR: Strategic mathematical thinking: brainstorming, problem decomposition, proof strategy design.
  DO NOT USE FOR: strategy analysis methodology generally (@lean-knowledge-formalization).
  TRIGGERS: strategy studio, brainstorming, problem decomposition.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-research"]
  successors: ["skill:lean-specification", "skill:research-council", "skill:lean-retro-methodology"]
metadata:
  version: "0.5.0"
  source_spec: "skills/math-strategy-studio/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Mathematical Strategy Studio
Creative mathematical thinking and proof strategy design for Lean 4 formalization.
---
## Routing
- **USE FOR:** Strategic mathematical thinking -- brainstorming, problem decomposition, proof strategy design,
  creative hypothesis
  generation, and
  mathematical intuition development. Use when facing novel formalization challenges, when standard approaches
  fail, when
  exploring
connections between
  domains, or when the theorem specification needs creative mathematical insight. The creative counterpart to
  the systematic
research-council and
  review-council skills.
- **DO NOT USE FOR:** strategy analysis methodology generally (use @lean-knowledge-formalization); research
  synthesis (use
  @research-council); Lean
  specification (use @lean-specification).
- **TRIGGERS:** strategy studio, brainstorming, problem decomposition, proof strategy, creative hypothesis,
  mathematical
  intuition.
## Workflow
1. Frame the strategy question: brainstorming, problem decomposition, proof-strategy design, hypothesis
  generation, or
  intuition-building.
2. Pick the matching method from the body; surface 3-5 candidate strategies for evaluation.
3. Score the candidates; recommend the top strategy with explicit assumptions and fallbacks.
4. Hand off: to `@lean-specification` for proof-strategy execution, to `@research-council` for hypothesis
  vetting, to
  `@lean-retro-methodology`.
## Recovery & STOP
- STOP if the question is applied-strategy (not mathematical) -- delegate to `@lean-knowledge-formalization`.
- STOP if no candidate scores above the belief floor -- escalate to `@research-council`.
- STOP if the question is about synthesising prior work -- delegate to `@research-council`.
## Handoffs
- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-specification`, `skill:research-council`, `skill:lean-retro-methodology`.
---
## Detailed reference
Full content for `math-strategy-studio` lives in
[`handbooks/math-strategy-studio-handbook.md`](../../handbooks/math-strategy-studio-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.
| Section | Topic |
|---|---|
| Part 1 | Strategy Design Framework |
| Part 2 | Proof Strategy Patterns |
| Part 3 | Creative Techniques |
| Part 4 | Brainstorming Protocols |
| Part 5 | Problem Decomposition for Complex Theorems |
| Part 6 | Mathematical Intuition Development |
| Part 7 | Research Council Integration |
---
## See also
- [`../../handbooks/math-strategy-studio-handbook.md`](../../handbooks/math-strategy-studio-handbook.md) --
  Full handbook
  (extracted from this skill)
- [`../lean-specification/SKILL.md`](../../../../skills/lean-specification/SKILL.md) -- Successor
- [`../research-council/SKILL.md`](../../../../skills/research-council/SKILL.md) -- Successor
- [`../lean-zettelkasten/SKILL.md`](../../../../skills/lean-retro-methodology/SKILL.md) -- Successor
