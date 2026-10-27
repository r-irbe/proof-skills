---
name: "lean-doc-feedback"
description: |
  USE FOR: reviewing a Lean documentation draft, flagging undefined terms, suggesting cross-links.
  DO NOT USE FOR: rewriting prose end-to-end (@lean-doc-improvement).
  TRIGGERS: doc-review, readability, doc-feedback.
tier: "cold"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["skill:lean-doc-improvement"]
  successors: ["skill:lean-doc-requirements"]
metadata:
  version: "0.1.0"
  source_spec: "specs/lean/doc-feedback/requirements.md"
  last_reviewed: "2026-05-26"
---

# lean-doc-feedback
Operational dispatch contract for `@lean-doc-feedback`.
## Routing
- **USE FOR:** reviewing a Lean documentation draft; flagging undefined terms; suggesting cross-links to
  blueprint nodes; scoring
  readability against the
  project rubric.
- **DO NOT USE FOR:** rewriting prose end-to-end (use `@lean-doc-improvement`); generating new blueprints (use
  `@lean-blueprint`).
- **TRIGGERS:** doc-review, readability, doc-feedback.
## Workflow
1. **Discover** [discover] — read draft, locate rubric, list scope boundaries.
2. **Review** [execute] — emit line-anchored findings.
3. **Score** [validate] — apply rubric; max 3 attempts then escalate.
4. **Persist** [persist] — write `feedback.md`, tick `tasks.md`.
## Recovery & STOP
- Draft missing rubric reference → STOP, escalate.
- Scope drift (silent edit) → immediate STOP, restore.
- Confidence < 80 % on rubric criterion → STOP, ask.
## Handoffs
- **Predecessors / successors**: see FM `handoffs`.
- **Source spec**: `specs/lean/doc-feedback/requirements.md`.
- **Related ADRs**: ADR-0076.
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-doc-feedback-handbook.md`](../../references/lean-doc-feedback-handbook.md) .
## See also
- [`../../references/lean-doc-feedback-handbook.md`](../../references/lean-doc-feedback-handbook.md) --
  Complete
  `lean-doc-feedback` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
