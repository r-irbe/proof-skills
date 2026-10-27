---
name: "lean-package-research"
description: |
  USE FOR: Lean 4 package and toolchain research: evaluating Reservoir/GitHub packages, Mathlib/cslib pin changes.
  DO NOT USE FOR: ordinary theorem lookup without a package decision (@lean-research).
  TRIGGERS: Lean package, Reservoir, GitHub Lean repo, Lake dependency.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["skill:lean-research", "skill:lean-integration-protocol", "agent:gateway"]
  successors: ["skill:lean-research", "skill:lean-enforcement", "skill:lean-quality-engine"]
metadata:
  version: "0.1.0"
  source_spec: "meta-audit-9w/topical/skills-improvement/package-research-skill-gap.md"
  last_reviewed: "2026-06-09"
---

# lean-package-research
Package research is separate from theorem lookup because dependency decisions
change reproducibility, build time, trust surface, and future maintenance. This
skill turns a candidate package or pin change into an adoption recommendation
with evidence, sequencing, and validation.
## Routing
- **USE FOR:** Lean 4 package and toolchain research — evaluating
  Reservoir/GitHub packages, Mathlib/cslib pin changes, Lake dependency health,
  package adoption classes, update sequencing, and external theorem-substrate
  candidates.
- **DO NOT USE FOR:** ordinary theorem lookup without a package decision (use
  `@lean-research`); package-file mutation or `lake update` execution (delegate
  validation to `@lean-enforcement` under an edit claim); proof writing (use
  `@lean-proof`); general project QA (use `@lean-quality-engine`).
- **TRIGGERS:** Lean package, Reservoir, GitHub Lean repo, Lake dependency,
## Workflow
1. **Scope the package question** [discover] — identify whether the caller wants
   theorem borrowing, dependency adoption, pin update, fork/vendor choice, or
   negative-result evidence. If the request only needs symbol lookup, hand off to
   `@lean-research`.
2. **Run the discovery ladder** [discover] — use
   [`../../references/discovery-ladder.md`](../../references/discovery-ladder.md)
   for Reservoir, GitHub, current-pin package source, theorem-search services,
   and literature checks. Record negative results rather than relying on memory.
3. **Assess dependency health** [validate] — inspect Lake metadata, toolchain
   compatibility, maintenance status, archive/staleness, license visibility,
   transitive dependencies, binary fetches, and whether the package is already
## Recovery & STOP
- STOP if the package would require editing `lean-toolchain`, `lakefile.lean`, or
  `lake-manifest.json` without an explicit edit claim and human authorization.
- STOP if the adoption class is ADOPT-NOW but confidence is below the local
  belief floor, validation is unknown, or the dependency graph is dirty.
- STOP if a package is archived, stale, or has unclear transitive dependencies
  and the caller asks for immediate adoption; return RESEARCH-MORE or
  DO-NOT-ADOPT-NOW with evidence.
## Handoffs
- **Predecessors:** `@lean-research` for symbol/literature leads,
  `@lean-integration-protocol` for project integration boundaries,
  `agent:gateway` for package-focused user requests.
- **Successors:** `@lean-research` for deeper theorem lookup,
  `@lean-enforcement` for validation commands, `@lean-quality-engine` for
  milestone/package-health scoring.
- **References:** discovery ladder
  ([`../../references/discovery-ladder.md`](../../references/discovery-ladder.md))
  and eval prompts
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-package-research-handbook.md`](../../references/lean-package-research-handbook.md) .
## See also
- [`../../references/lean-package-research-handbook.md`](../../references/lean-package-research-handbook.md)
  -- Complete
  `lean-package-research` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
