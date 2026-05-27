---
name: mathlib-build
description: REDIRECT — Lake build content has been generalised and moved to the new `lean-build` skill (W4 Wave 2 / move A3 of lab/design/07-cluster-workflow.md). The Mathlib-specific `lake exe cache get` note survives in the new skill. This stub preserves the slug for Ctrl-F discoverability and incoming cross-references (per the zero-deletions Chesterton protocol).
tier: "warm"
---

# SK-29: Building Mathlib (REDIRECT)

This skill no longer hosts content. The Lake build workflow was always
Lake-generic (only `lake exe cache get` is Mathlib-specific), so the
content moved to a generic `lean-build` skill that dispatches for any
Lake-managed project (Mathlib, Cslib, EASCI, downstream).

| Old section | New home |
|---|---|
| Build rule of thumb (including `lake exe cache get` Mathlib note) | [`../lean-build/SKILL.md`](../lean-build/SKILL.md) §Build rule of thumb |
| Lake command reference | Same file §Lake command reference |
| Stale artifact recovery | Same file §Stale artifact recovery |

Existing inbound links to "SK-29 / `mathlib-build`" should resolve
here and then follow the table above. `lean-gateway/REFERENCE.md`
registry row continues to resolve to this stub. Do not add new
content to this file — author it in `_overrides/lean-build/SKILL.md`
instead.

## See also

- [`../lean-build/SKILL.md`](../lean-build/SKILL.md) — full content (agnostic Lake build skill)
- [`../../../references/upstream/lean-bug-report-pipeline.md`](../../../references/upstream/lean-bug-report-pipeline.md) — Shared bug-report pipeline (sister W4 reference)
