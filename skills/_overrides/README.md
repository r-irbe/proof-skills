# skills/_overrides/ — repo-local overrides for `vendor/leanprover-skills`

This folder mirrors a subset of `vendor/leanprover-skills/skills/`
with locally-maintained `SKILL.md` (and supporting files) that take
**precedence** over the upstream copies at dispatch time.

## Why overrides exist

Each file under `skills/_overrides/<slug>/` was originally derived
from the upstream `leanprover/skills` and has since received
locally-maintained edits (updated theorem counts, tactic-priority
notes, deprecation guidance, etc.). Carrying the overrides in this
repo preserves that local maintenance work without rewriting the
upstream submodule.

## Dispatch rule

Per `AGENT.md` §3, an agent loading a skill by slug **must** resolve
in this order:

1. `skills/<slug>/` — repo-native skills.
2. `skills/_overrides/<slug>/` — overrides for upstream-derived
   skills (this folder).
3. `vendor/leanprover-skills/skills/<slug>/` — upstream baseline,
   pinned via submodule.

The first hit wins. Do not load both an override and the underlying
upstream copy in the same dispatch.

## Legacy REDIRECT stubs (4)

The core toolchain skills (`lean-proof`, `lean-setup`, `lean-build`, `lean-mwe`,
`lean-bisect`, `lean-pr`) have been promoted to repo-native first-party skills
under `skills/<slug>/` for native APM collection discovery. This folder now
preserves only the legacy Mathlib-specific slugs as REDIRECT stubs per the
Chesterton zero-deletions protocol.

| slug | upstream provenance | reason for stub |
|---|---|---|
| `mathlib-build` | `leanprover/skills` | **REDIRECT stub** — content moved to first-party `skills/lean-build` |
| `mathlib-pr` | `leanprover/skills` | **REDIRECT stub** — content moved to first-party `skills/lean-pr` + `references/upstream/mathlib4-pr.md` |
| `mathlib-review` | `leanprover/skills` | **REDIRECT stub** — content demoted to `references/upstream/mathlib4-review.md` |
| `nightly-testing` | `leanprover/skills` | **REDIRECT stub** — content demoted to `references/upstream/lean-nightly-infrastructure.md` |

## Adding / removing overrides

- **Adding**: copy the upstream folder to `skills/_overrides/<slug>/`,
  apply your changes, add a row to the table above, and ensure
  `AGENT.md` still documents the precedence rule.
- **Removing**: if upstream catches up to your override, delete the
  folder, remove the row above, and let `vendor/leanprover-skills/`
  serve the slug directly. Bump the upstream submodule pin in the
  same commit.

## Licensing

Override files inherit the Apache-2.0 license used by upstream; see
the repo-root `NOTICE` for attribution.
