---
name: "lean-doc-feedback-handbook"
description: "Reference handbook for @lean-doc-feedback."
extracted_from: "skills/lean-doc-feedback/SKILL.md"
---

# lean-doc-feedback

## Routing

- **USE FOR:** reviewing a Lean documentation draft; flagging undefined terms; suggesting cross-links to blueprint nodes; scoring readability against the
  project rubric.
- **DO NOT USE FOR:** rewriting prose end-to-end (use `@lean-doc-improvement`); generating new blueprints (use `@lean-blueprint`).
- **TRIGGERS:** doc-review, readability, doc-feedback.

## Behavioural rules (G-*)

- **G-1** (MUST): Feedback MUST be line-anchored to the draft. [Trace: AC-01]
- **G-2** (SHOULD): Feedback SHOULD prefer minimal-diff suggestions over rewrites. [Trace: AC-02]
- **G-3** (MUST NOT): The skill MUST NOT silently edit the draft. [Trace: AC-03]
- **G-4** (SHOULD): The skill SHOULD link each finding to a rubric criterion. [Trace: AC-04]

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

## Common failure modes

> AI agents commonly: rewrite instead of annotating; omit rubric anchors;
> bundle many findings into one comment. Full registry:
> GUARDRAILS.md §Agent failure taxonomy.
