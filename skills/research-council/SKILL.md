---
name: "research-council"
description: |
  USE FOR: orchestrating a 5-member Lean 4 research council (Α / Β / Γ / Δ / Ε) — RESEARCH loop (dual to RALPH), Rumsfeld epistemic mapping (known/unknown × known/unknown), cross-disciplinary research domains (Mathlib / AI / Physics / Bio / Social), session protocol, literature synthesis, self-improvement meta-loop.
  DO NOT USE FOR: single proof or single literature lookup (use @lean-research); proof review (use @lean-review-council); synthesis-only emission (use @research-synthesis-engine); proof itself (use @lean-proof).
  TRIGGERS: research council, RESEARCH loop, Rumsfeld matrix, epistemic mapping, research session, literature synthesis council, cross-disciplinary research.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research', 'skill:epistemic-discovery-engine']
  successors: ['skill:research-synthesis-engine', 'skill:lean-zettelkasten', 'skill:lean-review-council', 'skill:lean-research']
metadata:
  version: "0.2.0"
  source_spec: "skills/research-council/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# Research Council — Scholarly Dual to the Review Council

The Research Council is a 5-member multi-agent system for systematic knowledge acquisition, domain exploration, and epistemic mapping. It is the **input side** of the formalization pipeline, while the Review Council is the **output side**.

```
Research Council → Specification → Implementation → Review Council
    (what to prove)                                    (is the proof good?)
```

---

## Routing

- **USE FOR / DO NOT USE FOR / TRIGGERS** — see the `description` field in the YAML frontmatter above. Same dispatch contract is restated here for in-skill discovery.
- **USE FOR:** orchestrating a 5-member Lean 4 research council (Α / Β / Γ / Δ / Ε) — RESEARCH loop (dual to RALPH), Rumsfeld epistemic mapping (known/unknown × known/unknown), cross-disciplinary research domains (Mathlib / AI / Physics / Bio / Social), session protocol, literature synthesis, self-improvement meta-loop.
- **DO NOT USE FOR:** single proof or single literature lookup (use @lean-research); proof review (use @lean-review-council); synthesis-only emission (use @research-synthesis-engine); proof itself (use @lean-proof).
- **TRIGGERS:** research council, RESEARCH loop, Rumsfeld matrix, epistemic mapping, research session, literature synthesis council, cross-disciplinary research.

## Workflow

1. Frame the question (handbook Part 3 — locate it on the Rumsfeld matrix).
2. Convene the 5-member RESEARCH loop (handbook Part 2 — Reframe-Explore-Synthesize-Evaluate-Archive-Refine-Connect-Handoff).
3. Run the session per handbook Part 5; pull literature via handbook Part 6.
4. Emit the session report + handoff: to `@research-synthesis-engine` for the final product, to `@lean-zettelkasten` for archive, to `@lean-review-council` for any artifact-touching findings (Hub-Spoke topology).
5. Update the project snapshot (handbook Part 9) on session close.

## Recovery & STOP

- STOP if a question maps to known-knowns only — do not convene the council; delegate to `@lean-research`.
- STOP if the RESEARCH loop iterates 3+ times without Γ (Synthesize) producing distinct candidates — escalate to `@epistemic-discovery-engine` for a discovery mode shift.
- STOP if cross-disciplinary handoff (handbook Part 4) lands on a domain with no @-skill — open a `research-needed` Zettel and pause.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`, `skill:epistemic-discovery-engine`.
- **Successors:** `skill:research-synthesis-engine`, `skill:lean-zettelkasten`, `skill:lean-review-council`, `skill:lean-research`.

---

## Detailed reference

Full methodology content (Parts 1–9) lives in
[`references/research-council-handbook.md`](../../references/research-council-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and a parts index.

| Section | Topic | Covers |
|---|---|---|
| Part 1 | The Five Research Members | Α / Β / Γ / Δ / Ε research personas |
| Part 2 | The RESEARCH Loop (Dual to RALPH) | Reframe-Explore-Synthesize-Evaluate-Archive-Refine-Connect-Handoff |
| Part 3 | Epistemic Mapping (Rumsfeld Matrix) | Known/unknown × known/unknown quadrants |
| Part 4 | Cross-Disciplinary Research Domains | Mathlib / AI / Physics / Bio / Social |
| Part 5 | Research Session Protocol | Session lifecycle + report template |
| Part 6 | Literature Synthesis Protocol | Source vetting + citation graph |
| Part 7 | Integration with Other Skills | Cross-skill dispatch matrix |
| Part 8 | Self-Improvement | Meta-loop |
| Part 9 | Project Current State & Proven Methodology | Snapshot at last review |

---

## See also

- [`../../references/research-council-handbook.md`](../../references/research-council-handbook.md) — Full handbook (extracted from this skill)
- [`../research-synthesis-engine/SKILL.md`](../research-synthesis-engine/SKILL.md) — Successor
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor
- [`../lean-review-council/SKILL.md`](../lean-review-council/SKILL.md) — Successor
- [`../lean-research/SKILL.md`](../lean-research/SKILL.md) — Successor
