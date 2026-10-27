---
name: "research-synthesis-engine"
description: |
  USE FOR: running the 5-role synthesis engine (Α-S Scanner / Β-S Clusterer / Γ-S Distiller / Δ-S Verifier / Ε-S Publisher).
  DO NOT USE FOR: single-source literature review (@lean-research).
  TRIGGERS: synthesis, SYNTHESIZE loop, synthesis council, Α-S, Β-S, Γ-S.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-research", "skill:research-council", "skill:epistemic-discovery-engine"]
  successors: ["skill:lean-zettelkasten", "skill:lean-review-council", "skill:lean-doc-feedback", "skill:lean-report"]
metadata:
  version: "0.2.0"
  source_spec: "skills/research-synthesis-engine/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Research Synthesis Engine — Knowledge Generation Dual to Review Council
```

## Routing

- **USE FOR / DO NOT USE FOR / TRIGGERS** — see the `description` field in the YAML frontmatter above. Same dispatch contract is restated here for in-skill
  discovery.
- **USE FOR:** running the 5-role synthesis engine (Α-S Scanner / Β-S Clusterer / Γ-S Distiller / Δ-S Verifier / Ε-S Publisher) —
  Scan-Cluster-Distill-Verify-Publish (SYNTHESIZE) loop, four product tiers (Quick / Standard / Deep / Comprehensive), duality with the review-council
  RALPH loop, domain cross-references, Mathlib coverage tracking.

## Workflow

1. Decide the synthesis tier (Quick / Standard / Deep / Comprehensive) per handbook Part 3.
2. Convene the 5-role SYNTHESIZE loop (handbook Part 2) over the input corpus — Α-S scans, Β-S clusters, Γ-S distills, Δ-S verifies, Ε-S publishes.
3. Run handbook Part 4 to pair with `@lean-review-council` whenever the synthesis touches a proof artifact.
4. Emit the synthesis product (handbook Part 3 templates), and hand off Zettel cards to `@lean-zettelkasten`.
5. Update Mathlib coverage status (handbook Part 9) if the synthesis revealed a new gap or closed one.

## Recovery & STOP

- STOP if 2+ roles report contradictory distillations on the same input — escalate to `@lean-research` for evidence widening before re-running Δ-S.
- STOP if the SYNTHESIZE loop iterates 3+ times without convergence — switch tier (e.g., Quick → Standard) per handbook Part 6.
- STOP if the published product would over-claim Mathlib coverage — defer to handbook Part 9 cross-check.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`, `skill:research-council`, `skill:epistemic-discovery-engine`.
- **Successors:** `skill:lean-zettelkasten`, `skill:lean-review-council`, `skill:lean-doc-feedback`, `skill:lean-report`.

---

## Detailed reference

Full reference and lookup tables:
[`references/research-synthesis-engine-handbook.md`](../../references/research-synthesis-engine-handbook.md).

## See also

- [`../../references/research-synthesis-engine-handbook.md`](../../references/research-synthesis-engine-handbook.md) -- Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
