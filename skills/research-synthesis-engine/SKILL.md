---
name: "research-synthesis-engine"
description: |
  USE FOR: running the 5-role synthesis engine (Α-S Scanner / Β-S Clusterer / Γ-S Distiller / Δ-S Verifier / Ε-S Publisher) — Scan-Cluster-Distill-Verify-Publish (SYNTHESIZE) loop, four product tiers (Quick / Standard / Deep / Comprehensive), duality with the review-council RALPH loop, domain cross-references, Mathlib coverage tracking.
  DO NOT USE FOR: single-source literature review (use @lean-research); proof or formalization work (use @lean-proof or @lean-ai-formalization); review of a finished synthesis (use @lean-review-council); Zettelkasten card emission only (use @lean-zettelkasten).
  TRIGGERS: synthesis, SYNTHESIZE loop, synthesis council, Α-S, Β-S, Γ-S, Δ-S, Ε-S, scanner, clusterer, distiller, verifier, publisher, quick synthesis, deep synthesis.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research', 'skill:research-council', 'skill:epistemic-discovery-engine']
  successors: ['skill:lean-zettelkasten', 'skill:lean-review-council', 'skill:lean-doc-feedback', 'skill:lean-report']
metadata:
  version: "0.2.0"
  source_spec: "skills/research-synthesis-engine/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# Research Synthesis Engine — Knowledge Generation Dual to Review Council

```
                    ┌─────────────────────────┐
                    │   FORMALIZATION PIPELINE │
                    └─────────────────────────┘

INPUT SIDE                                           OUTPUT SIDE
═══════════                                          ═══════════
Research Synthesis Engine                            Review Council
   (Α,Β,Γ,Δ,Ε)                                       (Σ,Φ,Ν,Λ,Ω)
   "What should we prove?"                            "Is the proof good?"
   Knowledge → Specifications                        Proofs → Verdicts
   SYNTHESIZE loop                                   RALPH loop
```

The Research Synthesis Engine is the **generative counterpart** to the Review Council. It transforms raw research findings, literature, cross-domain knowledge, and epistemic-discovery-engine outputs into structured, actionable specification packages that feed the formalization pipeline.

---

---

## Routing

- **USE FOR / DO NOT USE FOR / TRIGGERS** — see the `description` field in the YAML frontmatter above. Same dispatch contract is restated here for in-skill discovery.
- **USE FOR:** running the 5-role synthesis engine (Α-S Scanner / Β-S Clusterer / Γ-S Distiller / Δ-S Verifier / Ε-S Publisher) — Scan-Cluster-Distill-Verify-Publish (SYNTHESIZE) loop, four product tiers (Quick / Standard / Deep / Comprehensive), duality with the review-council RALPH loop, domain cross-references, Mathlib coverage tracking.
- **DO NOT USE FOR:** single-source literature review (use @lean-research); proof or formalization work (use @lean-proof or @lean-ai-formalization); review of a finished synthesis (use @lean-review-council); Zettelkasten card emission only (use @lean-zettelkasten).
- **TRIGGERS:** synthesis, SYNTHESIZE loop, synthesis council, Α-S, Β-S, Γ-S, Δ-S, Ε-S, scanner, clusterer, distiller, verifier, publisher, quick synthesis, deep synthesis.

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

Full methodology content (Parts 1–9) lives in
[`references/research-synthesis-engine-handbook.md`](../../references/research-synthesis-engine-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and a parts index.

| Section | Topic | Covers |
|---|---|---|
| Part 1 | The Five Synthesis Roles | Α-S / Β-S / Γ-S / Δ-S / Ε-S personas |
| Part 2 | The SYNTHESIZE Loop | Scan-Cluster-Distill-Verify-Publish protocol |
| Part 3 | Synthesis Products | Quick / Standard / Deep / Comprehensive templates |
| Part 4 | Duality with Review Council | Council ↔ synthesis cross-loop |
| Part 5 | Domain Integration | Cross-skill consumption + emission |
| Part 6 | Synthesis Workflows | End-to-end synthesis pipelines |
| Part 7 | Quality Assurance | Verification + calibration |
| Part 8 | Cross-References | Sibling skills + Zettel inputs |
| Part 9 | Mathlib Coverage Status & Known Gaps | 2026-04-06 snapshot |

---

## See also

- [`../../references/research-synthesis-engine-handbook.md`](../../references/research-synthesis-engine-handbook.md) — Full handbook (extracted from this skill)
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor
- [`../lean-review-council/SKILL.md`](../lean-review-council/SKILL.md) — Successor
- [`../lean-doc-feedback/SKILL.md`](../lean-doc-feedback/SKILL.md) — Successor
- [`../lean-report/SKILL.md`](../lean-report/SKILL.md) — Successor
