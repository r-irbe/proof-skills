---
name: mathlib-review
description: REDIRECT — Mathlib PR review standards (attributes API, simp squeezing, normal forms, transparency, file size, naming/style URLs) have been demoted to `references/upstream/mathlib4-review.md`. Generic Lean proof review lives in `lean-proof-review`. This stub preserves the slug for Ctrl-F discoverability and incoming cross-references (per the zero-deletions Chesterton protocol).
---

# SK-31: Mathlib PR Review (REDIRECT)

This skill no longer hosts content. The Mathlib-specific review
checklist has been moved to a reference because it has no workflow,
no triggers, and no callers other than the gateway registry row.
Generic Lean proof review (workflow, behavioural rules, recovery)
remains in [`lean-proof-review`](../../lean-proof-review/SKILL.md).

| Old section | New home |
|---|---|
| Attributes and API | [`references/upstream/mathlib4-review.md`](../../../references/upstream/mathlib4-review.md) §Attributes and API |
| Style points specific to Mathlib (simp squeezing, normal forms, transparency, file size) | Same reference §Style points specific to Mathlib |
| Reference guides (review/naming/style/doc URLs) | Same reference §Reference guides |
| Routing for any general Lean proof review | [`lean-proof-review`](../../lean-proof-review/SKILL.md) (existing) |

Existing inbound links to "SK-31 / `mathlib-review`" should resolve
here and then follow the table above. Do not add new content to this
file — author it in `references/upstream/mathlib4-review.md` instead.

## See also

- [`../../../references/upstream/mathlib4-review.md`](../../../references/upstream/mathlib4-review.md) — full content
- [`../../lean-proof-review/SKILL.md`](../../lean-proof-review/SKILL.md) — generic proof review (parent skill)
- [`../../../references/upstream/lean-nightly-infrastructure.md`](../../../references/upstream/lean-nightly-infrastructure.md) — Nightly testing infrastructure (sister W4 Wave 1 demotion)
