---
name: "lean-build"
description: |
  USE FOR: building Lean 4 projects with Lake, validating changes with `lake env lean`.
  DO NOT USE FOR: bisecting which Lean version caused a regression (@lean-bisect).
  TRIGGERS: build, lake, lake env lean, lake exe cache get, stale artifacts.
tier: warm
runtime_targets:
- copilot-cli
- claude-code
- antigravity
- pi
- cursor
- gemini-cli
dispatch_targets: []
handoffs:
  predecessors:
  - skill:lean-setup
  - skill:lean-proof
  successors:
  - skill:lean-mwe
  - skill:lean-bisect
  - skill:lean-upstream-pr
  - skill:lean-proof
metadata:
  version: 0.5.0
  source_spec: skills/lean-build/SKILL.md
  last_reviewed: '2026-11'
---

# Building Lean Projects with Lake
> Agnostic Lake-build contract for any Lake-managed repository (`lakefile.lean`
> or `lakefile.toml`), with offline `.ilean` indexing and C99 IR inspection.

## Routing
- **USE FOR:** running `lake env lean`, `lake build <Module>`, `lake exe cache get`, `lake clean`, `lake exe runLinter`, `lake update <dep>`, targeted
  module iteration, offline `.ilean` inspection, generated C99 inspection in `.lake/build/ir/`, and `.olean` kernel verification.
- **DO NOT USE FOR:** bisecting a Lean version-pin regression (`@lean-bisect`); minimising a build failure to a self-contained MWE (`@lean-mwe`).

## Workflow
1. **Pick scope** -- single-file (`lake env lean MyFile.lean`), targeted module (`lake build <Module>.Foo.Bar -q --log-level=info`), or full suite
   (pre-CI). Default to targeted iteration to save compute and tokens.
2. **Fetch cache** -- for Mathlib-dependent projects, run `lake exe cache get` (or `lake exe cache get!` if corrupt). Skip for non-Mathlib projects.
3. **Build + parse** -- run with `-q --log-level=info`. Address errors in strict priority order: syntax -> type -> unsolved goals -> linters.
4. **Leverage build artifacts** -- inspect `.lake/build/lib/**/*.ilean` via `lean_lookup_symbol` / `lean_decl_references` for sub-5ms navigation without
   waiting for a full rebuild.

## Recovery & STOP
- Build result looks impossible (ghost errors, missing `.olean`s) -> `lake clean`; for Mathlib, `lake exe cache get`; re-run targeted build once.
- Build hangs > 10 min on a small target -> STOP, suspect dependency cycle or runaway elaboration; hand off to `@lean-mwe`.
- `lake update` accidentally invoked mid-iteration -> STOP, `git diff lake-manifest.json`; revert unless explicitly updating dependencies.

## Handoffs
- **Predecessors / successors**: inbound from `@lean-setup` or `@lean-proof`; outbound to `@lean-proof`, `@lean-mwe`, `@lean-bisect`, or `@lean-upstream-pr`.

## Detailed reference
- **Layer-1 Fast Lookup Card**: [`references/cards/lean-build-tables.md`](../../references/cards/lean-build-tables.md)
- **Layer-2 Handbook**: [`references/handbooks/lean-build-handbook.md`](../../references/handbooks/lean-build-handbook.md)

## See also
- [`../../references/handbooks/lean-build-handbook.md`](../../references/handbooks/lean-build-handbook.md) -- Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
- [`tests/lake-env.yaml`](tests/lake-env.yaml) -- Smoke test
