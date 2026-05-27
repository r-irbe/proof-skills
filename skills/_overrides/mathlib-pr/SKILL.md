---
name: mathlib-pr
description: REDIRECT — Mathlib PR workflow has been merged into the agnostic `lean-pr` SKILL, with Mathlib-specific conventions extracted to `references/upstream/mathlib4-pr.md` (W4 Wave 2 / move A1 of lab/design/07-cluster-workflow.md). This stub preserves the slug for Ctrl-F discoverability and incoming cross-references (per the zero-deletions Chesterton protocol).
---

# SK-30: Mathlib PR (REDIRECT)

This skill no longer hosts content. The generic PR workflow and the
Mathlib-specific conventions are now separated cleanly: the agnostic
workflow lives in [`lean-pr`](../lean-pr/SKILL.md), and the
Mathlib-only deltas (commit format with `(<scope>)`, labels, merge
process via bors, `lake exe mk_all`) live in the upstream reference.

| Old section | New home |
|---|---|
| Commit message format (`<type>(<scope>): <subject>`) | [`references/upstream/mathlib4-pr.md`](../../../references/upstream/mathlib4-pr.md) §Commit message format |
| Workflow (forks, `mk_all`, depends-on, `!bench`) | Same reference §Workflow |
| Labels (author-managed / topic / downstream / automated) | Same reference §Labels |
| Merge process (`maintainer-merge` → `ready-to-merge` → bors) | Same reference §Merge process |
| Style and naming URLs | Same reference §Style and naming |
| Generic agnostic PR workflow (dispatch, title shape, common ecosystem rules) | [`../lean-pr/SKILL.md`](../lean-pr/SKILL.md) |

Existing inbound links to "SK-30 / `mathlib-pr`" should resolve here
and then follow the table above. `lean-gateway/REFERENCE.md` registry
row continues to resolve to this stub. Do not add new content to this
file — author it in `references/upstream/mathlib4-pr.md` (Mathlib-
specific) or `_overrides/lean-pr/SKILL.md` (generic) instead.

## See also

- [`../lean-pr/SKILL.md`](../lean-pr/SKILL.md) — agnostic Lean-ecosystem PR SKILL (parent)
- [`../../../references/upstream/mathlib4-pr.md`](../../../references/upstream/mathlib4-pr.md) — full Mathlib-specific content
- [`../../../references/upstream/lean4-pr.md`](../../../references/upstream/lean4-pr.md) — Lean 4 core sister reference
- [`../../../references/upstream/mathlib4-review.md`](../../../references/upstream/mathlib4-review.md) — Mathlib PR review standards (sister W4 Wave 1)
