---
name: "lean-zettelkasten"
description: |
  USE FOR: creating fleeting/literature/permanent ZK notes during Lean proof reviews, linking notes bidirectionally.
  DO NOT USE FOR: running the review council itself (@lean-review-council).
  TRIGGERS: zettel, ZK-, fleeting note, permanent note, synthesis.
tier: "cold"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
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
## Routing
- **USE FOR:** creating a fleeting note from a council observation; creating a literature note when citing
  lean-pitfalls / Mathlib
  docs / a
  paper;
  promoting a cluster of ≥3 notes to a permanent note via the Synthesizer; bidirectional linking (`Related`,
  `Contradicts`,
  `Supports`,
`Supersedes`);
  running orphan / island / contradiction / staleness / coverage scans; updating `_index.md` and `_tags.md`.
- **DO NOT USE FOR:** running the review council itself (use `@lean-review-council`); reviewing a specific
  proof (use
  `@lean-proof-review`);
  updating
## Workflow
1. **Discover** [discover] — read the triggering event (council session, new literature citation, scheduled
  scan). Locate
  `_index.md`,
   current note counts,
   recent tag activity.
2. **Plan** [discover] — pick note type (fleeting / literature / permanent) or scan type (orphan / island /
  contradiction /
  staleness /
   coverage). For
   permanent promotion, verify ≥3 source notes (G-5). STOP if cluster size < 3 and downgrade to literature
   note.
3. **Execute** [execute] — write the note(s) under the correct directory (`fleeting/`, `literature/`, or
  `permanent/<category>/`);
  establish
   bidirectional
   links; flag contradictions for SDR.
4. **Verify** [validate] — re-check ID uniqueness, link reciprocity, tag presence (G-1, G-2). Max 3 re-checks
  then escalate.
## Recovery & STOP
- Permanent-note promotion attempted with < 3 source notes → STOP, downgrade to literature note (G-5).
- Contradiction detected during synthesis → STOP this synthesis pass; emit a fleeting note flagging both sides
  for SDR.
- Orphan scan returns > 10 % of notes orphaned → STOP, hand off to `@lean-retro-methodology` for a
  knowledge-coverage retro.
- Confidence < 80 % on which category a permanent note belongs in (`tactics/`, `pitfalls/`, `conventions/`,
  `cross-module/`,
  `proofs/`) →
  STOP, ask.
## Handoffs
- **Predecessors / successors**: see FM `handoffs`. Inbound: `@lean-proof-review`, `@lean-review-council`,
  `@lean-retro-methodology`, and
  `@lean-proof`
  (post-proof pattern capture) seed fleeting notes. Outbound: `@lean-doc-improvement` consumes permanent notes
  that imply paper
  updates;
  `@lean-quality-engine` consumes permanent notes that imply skill or methodology changes.
- **Source spec**: `specs/lean/zettelkasten/requirements.md` — every G-rule traces to an AC there.
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-zettelkasten-handbook.md`](../../references/lean-zettelkasten-handbook.md) .
## See also
- [`../../references/lean-zettelkasten-handbook.md`](../../references/lean-zettelkasten-handbook.md) --
  Complete
  `lean-zettelkasten` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
