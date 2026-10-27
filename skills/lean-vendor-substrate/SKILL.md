---
name: "lean-vendor-substrate"
description: |
  USE FOR: executing a decided vendoring of a permissively-licensed Lean 4 formalization into a project tree: verifying.
  DO NOT USE FOR: deciding whether to adopt or vendor a package (@lean-package-research).
  TRIGGERS: vendor, vendoring, vendored code, upstream formalization.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["skill:lean-package-research", "skill:lean-research", "agent:gateway"]
  successors: ["skill:lean-enforcement", "skill:lean-quality-engine", "skill:lean-proof-review"]
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-vendor-substrate/SKILL.md (this file)"
---

# lean-vendor-substrate
Vendoring is the sanctioned alternative to re-derivation when a needed theorem
## Routing
- **USE FOR:** tasks routed to `@lean-vendor-substrate`.
- **DO NOT USE FOR:** out-of-scope tasks (delegate via `@lean-gateway`).
## Workflow
1. **Verify provenance before copying anything** [discover] — record the
   upstream repository, the exact commit hash, the date, and the license. Fetch
   the license text into the project (e.g. a `LICENSES/<name>-<license>.txt`
   file) unless the upstream ships one at the vendored path. A vendoring
   without a pinned commit is not reviewable; refuse to proceed without one.
2. **Check the license and the sorry-status claim** [validate] — confirm the
   license is permissive and compatible with the project license. If upstream
   claims CI-verified `sorry`-freedom, verify it locally after the port rather
   than trusting the claim; if the claim cannot be re-verified, downgrade to
   RESEARCH-MORE in `@lean-package-research` terms.
## Recovery & STOP
- STOP if the license is missing, unclear, copyleft-incompatible, or the
  upstream repo cannot be authenticated; return to `@lean-package-research`
  with the evidence.
- STOP if the port requires changes beyond import/namespace/option handling to
  make it compile (elaboration drift deeper than mechanical rewrites); surface
  the drift as a decision — either document a minimal, marker-commented
  adaptation or park the vendoring and record the blocker.
## Handoffs
- **Predecessors:** `@lean-package-research` for the adoption decision and
  package card, `@lean-research` for the source-discovery ladder (confirm
  absence at the pin, find permissive-license candidates), `agent:gateway` for
  vendoring-focused user requests.
- **Successors:** `@lean-enforcement` to run and own the gate results,
  `@lean-quality-engine` for milestone/package-health scoring,
  `@lean-proof-review` to review any corpus-authored wrapper modules built on
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-vendor-substrate-handbook.md`](../../references/lean-vendor-substrate-handbook.md) .
## See also
- [`../../references/lean-vendor-substrate-handbook.md`](../../references/lean-vendor-substrate-handbook.md)
  -- Complete
  `lean-vendor-substrate` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
