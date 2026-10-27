---
name: "lean-proof-review"
description: |
  USE FOR: reviewing one Lean 4 proof / file for correctness, soundness, statement faithfulness, non-triviality.
  DO NOT USE FOR: writing a new proof (@lean-proof).
  TRIGGERS: proof review, audit proof, verify Lean, 4-layer checklist.
tier: "hot"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-proof"]
  successors: ["skill:lean-review-council", "skill:lean-enforcement", "skill:lean-doc-feedback"]
metadata:
  version: "0.2.2"
  source_spec: "specs/lean/proof-review/requirements.md"
  last_reviewed: "2026-10-20"
---

# lean-proof-review
> ⚠️ **MANDATORY** (hot-tier): layers L1 (soundness) and L2 (statement) are
> hard gates — a failure at either MUST block sign-off, regardless of L3/L4.
> Skipping Persist = incomplete.
## Routing
- **USE FOR:** auditing a single Lean 4 proof or file across the 4-layer checklist (L1 soundness, L2
  statement, L3 non-triviality,
  L4
  quality);
  cross-checking that imported tactics from the project automation stack are used correctly; spotting common
  pitfalls (vacuous
  truth, unused
hypothesis,
  broken simp set, scope drift).
- **DO NOT USE FOR:** authoring the proof (delegate to `@lean-proof`); convening a multi-agent review
  (delegate to
  `@lean-review-council`);
  running the CI
  scripts (delegate to `@lean-enforcement`).
- **TRIGGERS:** proof review, audit proof, verify Lean, 4-layer checklist, lean-pitfalls, proof quality.
## Workflow
1. **Discover** [discover] — read the target file, locate the theorem(s), find the source spec and any prior
  review record.
2. **L1 soundness** [validate] — confirm no `sorry`, no `admit`, no `sorryAx`, and no unauthorized
  `Lean.ofReduceBool` via
   `lean_axiom_closure`
   (`{"symbol": "...", "module": "..."}`) and `lean_diagnostics` (`{"filePath": "..."}`); defer to
   `@lean-enforcement` for
   full-module axiom
audit if
   needed.
## Recovery & STOP
- L1 fails (`sorry` / `admit` / `sorryAx`) → STOP, do NOT proceed to L2-L4; escalate to author.
- L2 fails (statement drift) → STOP, escalate to spec owner before any proof judgement.
- `lake build` red on containing file → STOP, ask author to fix build first.
- Confidence < 90 % on a tactic suggestion → mark as advisory, do NOT block.
- Scope drift (edits to non-proof files) → immediate STOP, re-anchor.
## Handoffs
- **Predecessors / successors:** see FM `handoffs` (grammar from ADR-0080).
- **Source spec:** `specs/lean/proof-review/requirements.md` — every G-rule traces to an AC there.
- **Related ADRs:** ADR-0076, ADR-0080.
- **Reference:** see
  [`references/lean-proof-review-handbook.md`](../../references/lean-proof-review-handbook.md) for the full
  project automation stack, proof-search priority table, reusable `Tactics` lemma library,
  common Lean pitfalls, and the 4-layer verification checklist (original v1 content, preserved verbatim).
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-proof-review-handbook.md`](../../references/lean-proof-review-handbook.md) .
## See also
- [`../../references/lean-proof-review-handbook.md`](../../references/lean-proof-review-handbook.md) --
  Complete
  `lean-proof-review` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
