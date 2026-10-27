---
name: "lean-enforcement"
description: |
  USE FOR: running programmatic CI / pre-review / post-review gates for a Lean 4 project: axiom audit, council precheck.
  DO NOT USE FOR: semantic / judgement review (@lean-proof-review).
  TRIGGERS: enforcement, CI gate, axiom audit, council_precheck.
tier: "hot"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-quality-engine"]
  successors: ["skill:lean-review-council", "skill:lean-proof-review", "skill:lean-retro-methodology"]
metadata:
  version: "0.2.2"
  source_spec: "specs/lean/enforcement/requirements.md"
  last_reviewed: "2026-10-20"
---

# lean-enforcement
> ⚠️ **MANDATORY** (hot-tier): blocking scripts (`council_precheck.sh`,
> `axiom_audit.py` on `sorryAx`, `workflow_gate.py` on mandatory gates) are
> hard gates — a failure HALTS the calling workflow. Skipping Persist =
> incomplete.
## Routing
- **USE FOR:** running an individual enforcement script or the full `enforce_all.sh` pipeline; checking a
  build is clean before
  review;
  auditing axioms
  after a refactor; validating cross-module bridges; gating a workflow step.
- **DO NOT USE FOR:** deciding whether a proof is *correct* (delegate to `@lean-proof-review`); scoring
  repository quality
  (delegate to
  `@lean-quality-engine`); routing across skills (delegate to `@lean-gateway`).
- **TRIGGERS:** enforcement, CI gate, axiom audit, council_precheck, workflow_gate, ecosystem_health, sorry
  check.
## Workflow
1. **Discover** [discover] — identify the target gate (single script, group, `enforce_all.sh`,
  `lean_diagnostics` static abstract
   interpretation
   certificates [`NatSubTruncation`, `NatDivModByZero`, Zone DBM `decreasing_by` synthesis, Octagon
   conservation `±x_i ± x_j <=
   c`,
Bourdoncle WTO loop
   widening, trace partitioning], `lean_counterexample_search` with Galois-guided hypothesis domain pruning
[`analyzeHeaderHypothesisDomains` /
   `pruneHeaderNatDomain`], `lean-rules` via `node tools/lean-lsp-mcp/bin/lean-rules.js`, `pi-lens`
   [`pilens_ast_grep_search`,
`pilens_diagnostics`] as
   sub-second structural pre-checks before `lake build`, or `pi-harness-bridge` policy/unicode gates); read
   the repository's
   `lakefile.lean`
+ recent
   commit log.
## Recovery & STOP
- `axiom_audit.py` finds `sorryAx` → immediate STOP; escalate to proof author; do NOT mark the workflow green.
- `council_precheck.sh` fails → STOP; fix build / sorry / convention / git state before retrying.
- `workflow_gate.py` blocks a mandatory gate → STOP; complete the prerequisite gate, then retry.
- Any blocking script crashes ×3 → STOP; file a bug against this skill.
- Confidence < 90 % about which script to invoke → STOP, ask.
## Handoffs
- **Predecessors / successors:** see FM `handoffs` (grammar from ADR-0080).
- **Source spec:** `specs/lean/enforcement/requirements.md` — every G-rule traces to an AC there.
- **Related ADRs:** ADR-0076, ADR-0080.
- **Reference:** see
  [`references/lean-enforcement-handbook.md`](../../references/lean-enforcement-handbook.md) for the full
  script inventory, integration matrix, anti-patterns, and the workflow-gate enforcement
  model (original v1 content, preserved verbatim).
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-enforcement-handbook.md`](../../references/lean-enforcement-handbook.md) .
## See also
- [`../../references/lean-enforcement-handbook.md`](../../references/lean-enforcement-handbook.md) -- Complete
  `lean-enforcement`
  Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
