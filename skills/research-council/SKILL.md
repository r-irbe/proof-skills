---
name: "research-council"
description: |
  USE FOR: orchestrating a 5-member Lean 4 research council (Α / Β / Γ / Δ / Ε): RESEARCH loop (dual to RALPH).
  DO NOT USE FOR: single proof or single literature lookup (@lean-research).
  TRIGGERS: research council, RESEARCH loop, Rumsfeld matrix.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-research", "skill:epistemic-discovery-engine"]
  successors: ["skill:research-synthesis-engine", "skill:lean-zettelkasten", "skill:lean-review-council", "skill:lean-research"]
metadata:
  version: "0.2.0"
  source_spec: "skills/research-council/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Research Council — Scholarly Dual to the Review Council
The Research Council is a 5-member multi-agent system for systematic knowledge acquisition, domain
exploration, and epistemic
mapping. It is
the **input
## Routing
- **USE FOR / DO NOT USE FOR / TRIGGERS** — see the `description` field in the YAML frontmatter above. Same
  dispatch contract is
  restated
  here for in-skill
  discovery.
- **USE FOR:** orchestrating a 5-member Lean 4 research council (Α / Β / Γ / Δ / Ε) — RESEARCH loop (dual to
  RALPH), Rumsfeld
  epistemic
  mapping
  (known/unknown × known/unknown), cross-disciplinary research domains (Mathlib / AI / Physics / Bio /
  Social), session protocol,
  literature
synthesis,
  self-improvement meta-loop.
- **DO NOT USE FOR:** single proof or single literature lookup (use @lean-research); proof review (use
  @lean-review-council);
  synthesis-only
  emission (use
## Workflow
1. Frame the question (handbook Part 3 — locate it on the Rumsfeld matrix).
2. Convene the 5-member RESEARCH loop (handbook Part 2 —
  Reframe-Explore-Synthesize-Evaluate-Archive-Refine-Connect-Handoff).
3. Run the session per handbook Part 5; pull literature via handbook Part 6.
4. Emit the session report + handoff: to `@research-synthesis-engine` for the final product, to
  `@lean-zettelkasten` for archive,
  to
   `@lean-review-council`
   for any artifact-touching findings (Hub-Spoke topology).
5. Update the project snapshot (handbook Part 9) on session close.
## Recovery & STOP
- STOP if a question maps to known-knowns only — do not convene the council; delegate to `@lean-research`.
- STOP if the RESEARCH loop iterates 3+ times without Γ (Synthesize) producing distinct candidates — escalate
  to
  `@epistemic-discovery-engine` for a
  discovery mode shift.
- STOP if cross-disciplinary handoff (handbook Part 4) lands on a domain with no @-skill — open a
  `research-needed` Zettel and
  pause.
## Handoffs
- **Predecessors:** `agent:gateway`, `skill:lean-research`, `skill:epistemic-discovery-engine`.
- **Successors:** `skill:research-synthesis-engine`, `skill:lean-zettelkasten`, `skill:lean-review-council`,
  `skill:lean-research`.
---
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/research-council-handbook.md`](../../references/research-council-handbook.md) .
## See also
- [`../../references/research-council-handbook.md`](../../references/research-council-handbook.md) -- Complete
  `research-council`
  Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
