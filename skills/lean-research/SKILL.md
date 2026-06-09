---
name: "lean-research"
description: |
  USE FOR: per-question Lean 4 research — picking a research method (Mathlib grep / Web / repo grep / sub-agent), running the discovery ladder for Mathlib/Loogle/Reservoir/GitHub/literature lookups, choosing depth (Shallow / Standard / Deep / Exhaustive), emitting a findings + recommended-strategy + Zettel triple, integrating with the Rumsfeld epistemic matrix and the review council, running a typed protocol (M / T / L / S / D / X / E).
  DO NOT USE FOR: full council convocation (use @research-council); synthesis emission (use @research-synthesis-engine); proof writing (use @lean-proof); review (use @lean-review-council).
  TRIGGERS: research, mathlib lookup, find lemma, theorem search, Loogle, Moogle, Reservoir, literature search, web search, what does X mean, typed research, M protocol, T protocol, L protocol.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-proof', 'skill:lean-proof-review', 'skill:lean-specification', 'skill:lean-blueprint']
  successors: ['skill:lean-zettelkasten', 'skill:research-council', 'skill:research-synthesis-engine', 'skill:lean-proof', 'skill:lean-proof-review']
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-research/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# Lean 4 Research Skill

Systematic methodology for investigating proof strategies, API availability, tactic behavior, and academic connections during Lean 4 formalization.

---

## Routing

- **USE FOR / DO NOT USE FOR / TRIGGERS** — see the `description` field in the YAML frontmatter above. Same dispatch contract is restated here for in-skill discovery.
- **USE FOR:** per-question Lean 4 research — picking a research method (Mathlib grep / Web / repo grep / sub-agent), running the discovery ladder for Mathlib/Loogle/Reservoir/GitHub/literature lookups, choosing depth (Shallow / Standard / Deep / Exhaustive), emitting a findings + recommended-strategy + Zettel triple, integrating with the Rumsfeld epistemic matrix and the review council, running a typed protocol (M / T / L / S / D / X / E).
- **DO NOT USE FOR:** full council convocation (use @research-council); synthesis emission (use @research-synthesis-engine); proof writing (use @lean-proof); review (use @lean-review-council).
- **TRIGGERS:** research, mathlib lookup, find lemma, theorem search, Loogle, Moogle, Reservoir, literature search, web search, what does X mean, typed research, M protocol, T protocol, L protocol.

## Workflow

1. Classify the research trigger (handbook Part 1) — confirm research is warranted vs proceeding with current evidence.
2. Pick a method (handbook Part 2), a depth level (handbook Part 4), and the
   applicable discovery-ladder type: Symbol, Package, Literature, or Strategy.
3. Run the discovery ladder in
   [`references/discovery-ladder.md`](../../references/discovery-ladder.md)
   whenever the answer depends on an existing theorem, package, or literature
   anchor. Record misses with the negative-result block from that reference.
4. If the question is typed, switch to the typed protocol (handbook Part 9: M = Mathlib, T = Tactic, L = Literature, S = Strategy, D = Domain, X = Cross-domain, E = Empirical).
5. Emit the standard output triple (handbook Part 3): Findings + Recommended Strategy + Zettel notes.
6. Hand off the recommended strategy to the consumer skill (handbook Part 7 mapping).

## Recovery & STOP

- STOP if findings contradict the Rumsfeld matrix classification (handbook Part 5) — re-classify the question first.
- STOP if Mathlib version drift is suspected — re-verify symbol existence at the current pin per the `verification discipline` memory.
- STOP before calling a negative theorem/package result exhaustive unless the
  discovery ladder's required rungs and query variants are recorded.
- STOP if the question would benefit from cross-disciplinary research (handbook Part 9 X-protocol) — escalate to `@research-council`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-proof`, `skill:lean-proof-review`, `skill:lean-specification`, `skill:lean-blueprint`.
- **Successors:** `skill:lean-zettelkasten`, `skill:research-council`, `skill:research-synthesis-engine`, `skill:lean-proof`, `skill:lean-proof-review`.

---

## Detailed reference

Full methodology content (Parts 1–9) lives in
[`references/lean-research-handbook.md`](../../references/lean-research-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and a parts index.

| Section | Topic | Covers |
|---|---|---|
| Part 1 | Research Triggers | When to research vs proceed |
| Part 2 | Research Methods | WebFetch / WebSearch / Mathlib grep / repo grep / sub-agent |
| Part 3 | Research Output Standards | Findings + recommended strategy + Zettel |
| Part 4 | Research Depth Levels | Shallow / Standard / Deep / Exhaustive |
| Part 5 | Epistemic Mapping Integration | Rumsfeld matrix bridge |
| Part 6 | Review Council Integration | Σ/Φ delegation paths |
| Part 7 | Domain Skill Cross-References | Per-domain skill dispatch |
| Part 8 | Research Anti-Patterns | What to avoid |
| Part 9 | Typed Research Protocols (M / T / L / S / D / X / E) | Mathlib / Tactic / Literature / Strategy / Domain / Cross / Empirical |

---

## See also

- [`../../references/lean-research-handbook.md`](../../references/lean-research-handbook.md) — Full handbook (extracted from this skill)
- [`../../references/discovery-ladder.md`](../../references/discovery-ladder.md) — Runged Mathlib/Loogle/Reservoir/GitHub/literature lookup protocol
- [`../../references/discovery-ladder-evals.md`](../../references/discovery-ladder-evals.md) — Evaluation prompts for the discovery ladder
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor
- [`../research-council/SKILL.md`](../research-council/SKILL.md) — Successor
- [`../research-synthesis-engine/SKILL.md`](../research-synthesis-engine/SKILL.md) — Successor
- [`../_overrides/lean-proof/SKILL.md`](../_overrides/lean-proof/SKILL.md) — Successor
- [`../lean-proof-review/SKILL.md`](../lean-proof-review/SKILL.md) — Successor
