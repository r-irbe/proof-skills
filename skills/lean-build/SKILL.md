---
name: "lean-build"
description: |
  USE FOR: building Lean 4 projects with Lake, validating changes with `lake env lean`.
  DO NOT USE FOR: bisecting which Lean version caused a regression (@lean-bisect).
  TRIGGERS: build, lake, lake env lean, lake exe cache get, stale artifacts.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors:
    - "skill:lean-setup"
    - "skill:lean-proof"
  successors:
    - "skill:lean-mwe"
    - "skill:lean-bisect"
    - "skill:lean-pr"
    - "skill:lean-proof"
metadata:
  version: "0.3.0"
  source_spec: "skills/lean-build/SKILL.md"
  last_reviewed: "2026-09-16"
  migrated_from: "repo-native first-party promotion"
---

# Building Lean Projects with Lake
> Agnostic Lake-build contract for any Lake-managed repository (`lakefile.lean`
> or `lakefile.toml`). Replaces the legacy Mathlib-only `lean-build` slug,
> with general Lake conventions, offline `.ilean` indexing, and generated C99
> inspection.
## Routing
- **USE FOR:** running `lake env lean`, `lake build <Module>`, `lake exe cache get`, `lake clean`, `lake exe
  runLinter`, `lake
  update <dep>`
  -- including
  merge-conflict resolution, targeted module iteration, offline `.ilean` inspection, inspecting generated C99
  in
  `.lake/build/ir/`, binary
`.olean` kernel
  verification, and CI-quality local checks.
- **DO NOT USE FOR:** bisecting a Lean version-pin regression (use `@lean-bisect`); minimising a build failure
  to a self-contained
  MWE (use
  `@lean-mwe`);
## Workflow
1. **Pick scope** -- single-file (`lake env lean MyFile.lean`), targeted module (`lake build <Module>.Foo.Bar
  -q
  --log-level=info`), or full
   suite (only
   when broad / pre-CI). Default to targeted iteration to save compute and tokens.
2. **Fetch cache** -- for Mathlib-dependent projects, run `lake exe cache get` (or `lake exe cache get!` if
  cache appears
  corrupt). For
   non-Mathlib
   projects, skip this step (no shared cache).
3. **Build + parse** -- run with `-q --log-level=info`. Address errors in strict priority order: syntax errors
  -> type errors ->
  unsolved
   goals -> linters.
4. **Leverage build artifacts**:
   - **`.ilean` files** (`.lake/build/lib/**/*.ilean`): parse directly for zero-latency symbol definitions and
  cross-references
  without
     waiting for
## Recovery & STOP
- Build result looks impossible (ghost errors, missing oleans for a built module) -> `lake clean`; for
  Mathlib, also `lake exe
  cache get`;
  re-run targeted
  build once. If still impossible, STOP and re-anchor.
- Build hangs > 10 min on a small target -> STOP, suspect dependency cycle or runaway elaboration; hand to
  `@lean-mwe` to isolate.
- `lake update` accidentally invoked mid-iteration -> STOP, `git diff lake-manifest.json`; revert unless the
  task is explicitly a
  dependency
  update.
## Handoffs
- **Predecessors / successors**: see FM `handoffs`. Typical inbound: `@lean-setup` (after a clean install) or
  `@lean-proof` (after
  a tactic
  write). Typical
  outbound: `@lean-proof` (for active proof repair), `@lean-mwe` / `@lean-bisect` / `@lean-pr` for build
  failures surviving clean
  rebuilds.
- **Sister skill:** `@lean-setup` for toolchain repair; `@lean-proof` for interactive proving.
- **REDIRECT pointer:** `lean-build` slug routes here (preserved per Chesterton-protocol).
---
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-build-handbook.md`](../../references/lean-build-handbook.md) .
## See also
- [`../../references/lean-build-handbook.md`](../../references/lean-build-handbook.md) -- Complete
  `lean-build` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
