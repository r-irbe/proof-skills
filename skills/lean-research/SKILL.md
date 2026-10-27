---
name: "lean-research"
description: |
  USE FOR: per-question Lean 4 research: picking a research method (Mathlib grep / Web / repo grep / sub-agent).
  DO NOT USE FOR: full council convocation (@research-council).
  TRIGGERS: research, mathlib lookup, find lemma, theorem search, Loogle.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors:
    - "agent:gateway"
    - "skill:lean-proof"
    - "skill:lean-proof-review"
    - "skill:lean-specification"
    - "skill:lean-blueprint"
  successors:
    - 'skill:lean-zettelkasten'
    - 'skill:research-council'
    - 'skill:research-synthesis-engine'
    - 'skill:lean-package-research'
    - 'skill:lean-proof'
    - 'skill:lean-proof-review'
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-research/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Lean 4 Research Skill
Systematic methodology for investigating proof strategies, API availability, tactic behavior, and academic
connections during Lean
4
formalization.
---
## Routing
- **USE FOR / DO NOT USE FOR / TRIGGERS** — see the `description` field in the YAML frontmatter above. Same
  dispatch contract is
  restated
  here for in-skill
  discovery.
- **USE FOR:** per-question Lean 4 research — picking a research method (Mathlib grep / Web / repo grep /
  sub-agent), running the
  discovery
  ladder for
  Mathlib/Loogle/Reservoir/GitHub/literature lookups, choosing depth (Shallow / Standard / Deep / Exhaustive),
  emitting a findings
  +
recommended-strategy +
  Zettel triple, integrating with the Rumsfeld epistemic matrix and the review council, running a typed
  protocol (M / T / L / S /
  D / X /
E).
## Workflow
1. Classify the research trigger (handbook Part 1) — confirm research is warranted vs proceeding with current
  evidence.
2. Pick a method (handbook Part 2), a depth level (handbook Part 4), and the
   applicable discovery-ladder type: Symbol, Package, Literature, or Strategy.
3. Run the discovery ladder in
   [`references/discovery-ladder.md`](../../references/discovery-ladder.md)
   whenever the answer depends on an existing theorem, package, or literature
   anchor. Record misses with the negative-result block from that reference.
4. If the question is typed, switch to the typed protocol (handbook Part 9: M = Mathlib, T = Tactic, L =
  Literature, S = Strategy,
  D =
   Domain, X =
   Cross-domain, E = Empirical).
## Recovery & STOP
- STOP if findings contradict the Rumsfeld matrix classification (handbook Part 5) — re-classify the question
  first.
- STOP if Mathlib version drift is suspected — re-verify symbol existence at the current pin per the
  `verification discipline`
  memory.
- STOP before calling a negative theorem/package result exhaustive unless the
  discovery ladder's required rungs and query variants are recorded.
## Handoffs
- **Predecessors:** `agent:gateway`, `skill:lean-proof`, `skill:lean-proof-review`,
  `skill:lean-specification`,
  `skill:lean-blueprint`.
- **Successors:** `skill:lean-zettelkasten`, `skill:research-council`, `skill:research-synthesis-engine`,
  `skill:lean-package-research`,
  `skill:lean-proof`, `skill:lean-proof-review`.
---
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-research-handbook.md`](../../references/lean-research-handbook.md) .
## See also
- [`../../references/lean-research-handbook.md`](../../references/lean-research-handbook.md) -- Complete
  `lean-research` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
