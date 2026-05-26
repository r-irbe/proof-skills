---
name: "lean-zettelkasten"
description: |
  USE FOR: creating fleeting/literature/permanent ZK notes during Lean proof reviews, linking notes bidirectionally, running synthesis after a council session, detecting orphan and island notes, maintaining `_index.md` and `_tags.md`.
  DO NOT USE FOR: running the review council itself (use @lean-review-council), reviewing a single proof (use @lean-proof-review), updating external papers from results (use @lean-doc-improvement), authoring the review methodology retro (use @lean-retro-methodology), generating a project blueprint (use @lean-blueprint).
  TRIGGERS: zettel, ZK-, fleeting note, permanent note, synthesis.
tier: "cold"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors:
    - "skill:lean-proof-review"
    - "skill:lean-review-council"
    - "skill:lean-retro-methodology"
    - "skill:lean-proof"
  successors:
    - "skill:lean-doc-improvement"
    - "skill:lean-quality-engine"
metadata:
  version: "0.2.0"
  source_spec: "specs/lean/zettelkasten/requirements.md"
  last_reviewed: "2026-05-30"
r_caveats: [F1, F6]
---

# lean-zettelkasten

> Cold-tier skill — invoked explicitly by name (`@lean-zettelkasten`) from
> review and synthesis flows. No MANDATORY preamble: the gates in §Behavioural
> rules are advisory and reviewed at synthesis time rather than per-note.
> Persist is still required (FSIA-R-11-09) but is local to the
> `docs/project/lean/docs/zettelkasten/` tree.

## Routing

- **USE FOR:** creating a fleeting note from a council observation; creating a literature note when citing lean-pitfalls / Mathlib docs / a paper; promoting a cluster of ≥3 notes to a permanent note via the Synthesizer; bidirectional linking (`Related`, `Contradicts`, `Supports`, `Supersedes`); running orphan / island / contradiction / staleness / coverage scans; updating `_index.md` and `_tags.md`.
- **DO NOT USE FOR:** running the review council itself (use `@lean-review-council`); reviewing a specific proof (use `@lean-proof-review`); updating external papers from Lean results (use `@lean-doc-improvement`); authoring the council retro / methodology (use `@lean-retro-methodology`); generating a project blueprint (use `@lean-blueprint`).
- **TRIGGERS:** zettel, ZK-, fleeting note, permanent note, synthesis.

## Behavioural rules (G-*)

- **G-1** (MUST): Every note MUST use the `ZK-YYYYMMDD-NNN` ID grammar, with `NNN` sequential within that date. [Trace: AC-01]
- **G-2** (MUST): Every note MUST declare `Type`, `Created`, `Author`, `Source`, and at least one tag. [Trace: AC-02]
- **G-3** (SHOULD): Fleeting notes SHOULD remain minimal — capture the observation; do not perfect prose. [Trace: AC-03]
- **G-4** (MUST): A permanent note MUST link to all source fleeting/literature notes it synthesises, and the sources MUST be marked `superseded`. [Trace: AC-04]
- **G-5** (MUST NOT): The skill MUST NOT promote a cluster to a permanent note unless ≥3 source notes converge on the pattern. [Trace: AC-05]
- **G-6** (SHOULD): The skill SHOULD propose a downstream `@lean-proof-review` or `@lean-quality-engine` skill update when a permanent note implies a methodology change. [Trace: AC-06]

## Workflow

1. **Discover** [discover] — read the triggering event (council session, new literature citation, scheduled scan). Locate `_index.md`, current note counts, recent tag activity.
2. **Plan** [discover] — pick note type (fleeting / literature / permanent) or scan type (orphan / island / contradiction / staleness / coverage). For permanent promotion, verify ≥3 source notes (G-5). STOP if cluster size < 3 and downgrade to literature note.
3. **Execute** [execute] — write the note(s) under the correct directory (`fleeting/`, `literature/`, or `permanent/<category>/`); establish bidirectional links; flag contradictions for SDR.
4. **Verify** [validate] — re-check ID uniqueness, link reciprocity, tag presence (G-1, G-2). Max 3 re-checks then escalate.
5. **Persist** [persist] — commit the new/updated notes, update `_index.md` and `_tags.md`, and (if applicable) open a skill-update proposal for `@lean-proof-review` or `@lean-quality-engine` (G-6). Persist is local to `docs/project/lean/docs/zettelkasten/`.

## Recovery & STOP

- Permanent-note promotion attempted with < 3 source notes → STOP, downgrade to literature note (G-5).
- Contradiction detected during synthesis → STOP this synthesis pass; emit a fleeting note flagging both sides for SDR.
- Orphan scan returns > 10 % of notes orphaned → STOP, hand off to `@lean-retro-methodology` for a knowledge-coverage retro.
- Confidence < 80 % on which category a permanent note belongs in (`tactics/`, `pitfalls/`, `conventions/`, `cross-module/`, `proofs/`) → STOP, ask.

## Handoffs

- **Predecessors / successors**: see FM `handoffs`. Inbound: `@lean-proof-review`, `@lean-review-council`, `@lean-retro-methodology`, and `@lean-proof` (post-proof pattern capture) seed fleeting notes. Outbound: `@lean-doc-improvement` consumes permanent notes that imply paper updates; `@lean-quality-engine` consumes permanent notes that imply skill or methodology changes.
- **Source spec**: `specs/lean/zettelkasten/requirements.md` — every G-rule traces to an AC there.
- **Related ADRs**: ADR-0076 (skill-as-contract), ADR-0080 (handoff DAG), ADR-0079 (cold-tier loading rationale).

## Common failure modes

> AI agents commonly: over-polish fleeting notes (defeats the speed of
> capture); promote 1–2-note clusters to permanent notes; create permanent
> notes without back-linking the sources or marking them `superseded`;
> silently resolve a contradiction instead of flagging it for SDR; skip
> `_index.md` and `_tags.md` updates so the graph view rots. Full registry:
> `GUARDRAILS.md §Agent failure taxonomy`.

## See also

- [`../../skills/skills/lean-zettelkasten/SKILL.md`](../../../skills/lean-zettelkasten/SKILL.md) — pre-v2 source skill (this is the migration).
- [`../../zettelkasten/_index.md`](../../../zettelkasten/_index.md) — live ZK index this skill maintains.
- [`../lean-doc-feedback/SKILL.md`](../lean-doc-feedback/SKILL.md) — v2 sibling on the documentation side of the DAG.
