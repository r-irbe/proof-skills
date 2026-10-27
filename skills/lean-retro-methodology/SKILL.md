---
name: "lean-retro-methodology"
description: |
  USE FOR: running a Lean 4 corpus retrospective: RETRO protocol (Refactor-Extract-Test-Refine-Optimize).
  DO NOT USE FOR: single proof review (@lean-proof-review).
  TRIGGERS: retro, retrospective, RETRO protocol.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-review-council", "skill:lean-research"]
  successors: ["skill:lean-enforcement", "skill:lean-zettelkasten", "skill:lean-doc-feedback", "skill:lean-review-council"]
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-retro-methodology/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# SK-35: Retroactive Formalization Methodology
Operational dispatch contract for `@lean-retro-methodology`.
## Routing
- **USE FOR / DO NOT USE FOR / TRIGGERS** — see the `description` field in the YAML frontmatter above. Same
  dispatch contract is
  restated
  here for in-skill
  discovery.
- **USE FOR:** running a Lean 4 corpus retrospective — RETRO protocol (Refactor-Extract-Test-Refine-Optimize),
  adapting to project
  scale
  (Solo / Small /
  Medium / Large), per-phase enforcement scripts, cross-skill optimization rules, retro personas, tracking
  documents, embedded
  RALPH inside
RETRO phases.
- **DO NOT USE FOR:** single proof review (use @lean-proof-review); council convocation (use
  @lean-review-council); research (use
  @lean-research);
## Workflow
1. Pick the project scale (handbook Part 2) — determines depth + cadence.
2. Sequence the RETRO phases (handbook Part 1 — Refactor → Extract → Test → Refine → Optimize); inside each
  phase run the embedded
  RALPH
   loop (handbook Part 7).
3. Apply per-phase enforcement scripts (handbook Part 3) as the phase gate.
4. Apply cross-skill optimization rules (handbook Part 4) once Refine + Optimize have data.
5. Emit the per-phase tracking docs (handbook Part 6) and audit against handbook Part 8 anti-patterns.
## Recovery & STOP
- STOP if a phase's enforcement script fails (handbook Part 3) — do not advance to the next phase.
- STOP if Optimize phase produces no actionable cross-skill rewires after RALPH iteration 3 (handbook Part 7)
  — close the retro
  and document
  why.
- STOP on detection of any handbook Part 8 anti-pattern — back out and re-plan.
## Handoffs
- **Predecessors:** `agent:gateway`, `skill:lean-review-council`, `skill:lean-research`.
- **Successors:** `skill:lean-enforcement`, `skill:lean-zettelkasten`, `skill:lean-doc-feedback`,
  `skill:lean-review-council`.
---
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-retro-methodology-handbook.md`](../../references/lean-retro-methodology-handbook.md) .
## See also
- [`../../references/lean-retro-methodology-handbook.md`](../../references/lean-retro-methodology-handbook.md)
  -- Complete
  `lean-retro-methodology` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
