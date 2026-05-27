---
name: "epistemic-discovery-engine"
description: |
  USE FOR: epistemic discovery — picking a discovery mode (Census / Dependency / Literature / Cross-domain / Community), running an Unknown-Unknown (UU) hunting protocol at the right depth (Shallow / Standard / Deep / Exhaustive), emitting census + probe + trigger reports, anti-stagnation mechanisms, project relevance scoring.
  DO NOT USE FOR: a known research question (use @lean-research); council convocation on a known artifact (use @lean-review-council or @research-council); synthesis emission of known content (use @research-synthesis-engine).
  TRIGGERS: discovery, unknown unknown, UU hunt, epistemic discovery, census, dependency probe, cross-domain probe, community probe, anti-stagnation.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:research-council', 'skill:lean-research']
  successors: ['skill:research-council', 'skill:research-synthesis-engine', 'skill:lean-zettelkasten']
metadata:
  version: "0.2.0"
  source_spec: "skills/epistemic-discovery-engine/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# Epistemic Discovery Engine — Active UU Hunting

The Discovery Engine is the **operational arm** of epistemic-mapping. Where epistemic-mapping defines quadrants, scores, and transitions, the Discovery Engine executes the search protocols that keep the epistemic map current and the UU zone shrinking.

```
epistemic-mapping (the map) ←──updates──← epistemic-discovery-engine (the explorer)
research-council  (the strategists)  ←──feeds──← epistemic-discovery-engine (the scout)
```

---

## Routing

- **USE FOR / DO NOT USE FOR / TRIGGERS** — see the `description` field in the YAML frontmatter above. Same dispatch contract is restated here for in-skill discovery.
- **USE FOR:** epistemic discovery — picking a discovery mode (Census / Dependency / Literature / Cross-domain / Community), running an Unknown-Unknown (UU) hunting protocol at the right depth (Shallow / Standard / Deep / Exhaustive), emitting census + probe + trigger reports, anti-stagnation mechanisms, project relevance scoring.
- **DO NOT USE FOR:** a known research question (use @lean-research); council convocation on a known artifact (use @lean-review-council or @research-council); synthesis emission of known content (use @research-synthesis-engine).
- **TRIGGERS:** discovery, unknown unknown, UU hunt, epistemic discovery, census, dependency probe, cross-domain probe, community probe, anti-stagnation.

## Workflow

1. Pick the discovery mode (handbook Part 1) that matches the suspected blind spot.
2. Run the UU hunting protocol at the chosen depth (handbook Part 2).
3. Emit the corresponding report (handbook Part 3 — Census / Probe / Trigger templates).
4. Hand off promising leads to `@research-council` (deep) or `@lean-research` (single-question) per handbook Part 4.
5. Apply anti-stagnation mechanisms (handbook Part 5) when consecutive discovery sessions produce overlapping leads.

## Recovery & STOP

- STOP if the suspected unknown turns out to be a known-unknown after probe — re-classify and delegate to `@lean-research`.
- STOP if 3+ consecutive sessions in the same mode produce overlapping leads — switch mode per handbook Part 5.
- STOP if project relevance score (handbook Part 6) falls below threshold — close the discovery and document the negative result.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:research-council`, `skill:lean-research`.
- **Successors:** `skill:research-council`, `skill:research-synthesis-engine`, `skill:lean-zettelkasten`.

---

## Detailed reference

Full methodology content (Parts 1–7) lives in
[`references/epistemic-discovery-engine-handbook.md`](../../references/epistemic-discovery-engine-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and a parts index.

| Section | Topic | Covers |
|---|---|---|
| Part 1 | Discovery Modes | Census / Dependency / Literature / Cross-domain / Community |
| Part 2 | UU Hunting Protocols | Unknown-unknown probing per level |
| Part 3 | Reporting and Outputs | Census + probe + trigger templates |
| Part 4 | Integration Architecture | Wiring with research-council + synthesis |
| Part 5 | Anti-Stagnation Mechanisms | Discovery-loop diversifiers |
| Part 6 | Project Relevance | Per-project applicability scoring |
| Part 7 | Cross-References | Sibling skill inventory |

---

## See also

- [`../../references/epistemic-discovery-engine-handbook.md`](../../references/epistemic-discovery-engine-handbook.md) — Full handbook (extracted from this skill)
- [`../research-council/SKILL.md`](../research-council/SKILL.md) — Successor
- [`../research-synthesis-engine/SKILL.md`](../research-synthesis-engine/SKILL.md) — Successor
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor
