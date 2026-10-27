---
name: "epistemic-discovery-engine"
description: |
  USE FOR: epistemic discovery: picking a discovery mode (Census / Dependency / Literature / Cross-domain / Community).
  DO NOT USE FOR: a known research question (@lean-research).
  TRIGGERS: discovery, unknown unknown, UU hunt, epistemic discovery, census.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:research-council", "skill:lean-research"]
  successors: ["skill:research-council", "skill:research-synthesis-engine", "skill:lean-zettelkasten"]
metadata:
  version: "0.2.0"
  source_spec: "skills/epistemic-discovery-engine/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Epistemic Discovery Engine — Active UU Hunting
The Discovery Engine is the **operational arm** of epistemic-mapping. Where epistemic-mapping defines
quadrants, scores, and
transitions,
the Discovery
## Routing
- **USE FOR / DO NOT USE FOR / TRIGGERS** — see the `description` field in the YAML frontmatter above. Same
  dispatch contract is
  restated
  here for in-skill
  discovery.
- **USE FOR:** epistemic discovery — picking a discovery mode (Census / Dependency / Literature / Cross-domain
  / Community),
  running an
  Unknown-Unknown
  (UU) hunting protocol at the right depth (Shallow / Standard / Deep / Exhaustive), emitting census + probe +
  trigger reports,
anti-stagnation mechanisms,
  project relevance scoring.
- **DO NOT USE FOR:** a known research question (use @lean-research); council convocation on a known artifact
  (use
  @lean-review-council or
## Workflow
1. Pick the discovery mode (handbook Part 1) that matches the suspected blind spot.
2. Run the UU hunting protocol at the chosen depth (handbook Part 2).
3. Emit the corresponding report (handbook Part 3 — Census / Probe / Trigger templates).
4. Hand off promising leads to `@research-council` (deep) or `@lean-research` (single-question) per handbook
  Part 4.
5. Apply anti-stagnation mechanisms (handbook Part 5) when consecutive discovery sessions produce overlapping
  leads.
## Recovery & STOP
- STOP if the suspected unknown turns out to be a known-unknown after probe — re-classify and delegate to
  `@lean-research`.
- STOP if 3+ consecutive sessions in the same mode produce overlapping leads — switch mode per handbook Part
  5.
- STOP if project relevance score (handbook Part 6) falls below threshold — close the discovery and document
  the negative result.
## Handoffs
- **Predecessors:** `agent:gateway`, `skill:research-council`, `skill:lean-research`.
- **Successors:** `skill:research-council`, `skill:research-synthesis-engine`, `skill:lean-zettelkasten`.
---
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/epistemic-discovery-engine-handbook.md`](../../references/epistemic-discovery-engine-handbook.md)
.
## See also
- [`../../references/epistemic-discovery-engine-handbook.md`](../../references/epistemic-discovery-engine-handbook.md)
  -- Complete
  `epistemic-discovery-engine` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
