---
name: nightly-testing
description: REDIRECT — Lean/Mathlib nightly testing infrastructure notes (branches, tags, Zulip, mathlib4-nightly-testing fork) have been demoted to `references/upstream/lean-nightly-infrastructure.md`. This stub preserves the slug for Ctrl-F discoverability and incoming cross-references (per the zero-deletions Chesterton protocol).
---

# SK-34: Lean / Mathlib Nightly Testing (REDIRECT)

This skill no longer hosts content. The nightly-testing infrastructure
notes have been moved to a reference because they are a
"go-read-this-URL" document with no workflow, triggers, or callers
(verified zero callers across `skills/` and `references/` excluding
`lean-gateway/REFERENCE.md` which keeps it as a registry row).

| Old section | New home |
|---|---|
| Overview + `mathlib4-nightly-testing` fork explanation | [`references/upstream/lean-nightly-infrastructure.md`](../../references/upstream/lean-nightly-infrastructure.md) §Overview |
| Key branches (`nightly-testing`, `nightly-with-mathlib`, `bump/v4.X.Y`, `lean-pr-testing-NNNN`) | Same reference §Key branches |
| Zulip channel | Same reference §Zulip |
| Canonical reference URL | Same reference §Canonical reference |

Existing inbound links to "SK-34 / `nightly-testing`" should resolve
here and then follow the table above. Do not add new content to this
file — author it in
`references/upstream/lean-nightly-infrastructure.md` instead.

## See also

- [`../../../references/upstream/lean-nightly-infrastructure.md`](../../../references/upstream/lean-nightly-infrastructure.md) — full content
- [`../../../references/upstream/mathlib4-review.md`](../../../references/upstream/mathlib4-review.md) — Mathlib review standards (sister W4 Wave 1 demotion)
