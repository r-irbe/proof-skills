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

## Current overrides (9)

| slug | upstream provenance | reason for override |
|---|---|---|
| `lean-bisect` | `leanprover/skills` | refreshed bisect tooling + tactic-priority notes; W4 Wave 1 See-also link to `references/upstream/lean-bug-report-pipeline.md` |
| `lean-mwe` | `leanprover/skills` | updated MWE workflow + Mathlib pointers; W4 Wave 1 See-also link to `references/upstream/lean-bug-report-pipeline.md` |
| `lean-pr` | `leanprover/skills` | PR conventions reconciled with current Mathlib practice |
| `lean-proof` | `leanprover/skills` | tactic-priority order, current theorem-count baseline |
| `lean-setup` | `leanprover/skills` | toolchain/elan notes for recent Lean releases |
| `mathlib-build` | `leanprover/skills` | build-flag and verbosity updates |
| `mathlib-pr` | `leanprover/skills` | label/queueboard refresh |
| `mathlib-review` | `leanprover/skills` | **REDIRECT stub** — content demoted to `references/upstream/mathlib4-review.md` in W4 Wave 1 (move A2); slug preserved for Ctrl-F per Chesterton protocol |
| `nightly-testing` | `leanprover/skills` | **REDIRECT stub** — content demoted to `references/upstream/lean-nightly-infrastructure.md` in W4 Wave 1 (move A4); slug preserved for Ctrl-F per Chesterton protocol |

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
