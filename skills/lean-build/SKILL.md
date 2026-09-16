---
name: "lean-build"
description: |
  USE FOR: building Lean 4 projects with Lake, validating changes with `lake env lean`, targeted module compilation (`lake build <Module>`), fast offline symbol navigation via `.ilean`, inspecting emitted C99 in `.lake/build/ir/`, resolving stale build artifacts via `lake clean` + cache get, binary `.olean` kernel audits, preparing CI-quality local checks. Applies to any Lake-managed project.
  DO NOT USE FOR: bisecting which Lean version caused a regression (use @lean-bisect), minimising an error to a bug-report repro (use @lean-mwe), repairing the toolchain itself (use @lean-setup), writing or fixing the proof (use @lean-proof).
  TRIGGERS: build, lake, lake env lean, lake exe cache get, stale artifacts, lake clean, build error, ilean, olean, CI prep.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
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

# lean-build

> Agnostic Lake-build contract for any Lake-managed repository (`lakefile.lean`
> or `lakefile.toml`). Replaces the legacy Mathlib-only `mathlib-build` slug,
> with general Lake conventions, offline `.ilean` indexing, and generated C99
> inspection.

## Routing

- **USE FOR:** running `lake env lean`, `lake build <Module>`, `lake exe cache get`, `lake clean`, `lake exe runLinter`, `lake update <dep>` -- including merge-conflict resolution, targeted module iteration, offline `.ilean` inspection, inspecting generated C99 in `.lake/build/ir/`, binary `.olean` kernel verification, and CI-quality local checks.
- **DO NOT USE FOR:** bisecting a Lean version-pin regression (use `@lean-bisect`); minimising a build failure to a self-contained MWE (use `@lean-mwe`); repairing or installing the Lean toolchain itself (use `@lean-setup`); fixing the underlying proof error that the build surfaces (use `@lean-proof`).
- **TRIGGERS:** build, lake, lake env lean, lake exe cache get, stale artifacts, lake clean, "build is slow", "CI failed locally", ilean, CI prep.

## Workflow

1. **Pick scope** -- single-file (`lake env lean MyFile.lean`), targeted module (`lake build <Module>.Foo.Bar -q --log-level=info`), or full suite (only when broad / pre-CI). Default to targeted iteration to save compute and tokens.
2. **Fetch cache** -- for Mathlib-dependent projects, run `lake exe cache get` (or `lake exe cache get!` if cache appears corrupt). For non-Mathlib projects, skip this step (no shared cache).
3. **Build + parse** -- run with `-q --log-level=info`. Address errors in strict priority order: syntax errors -> type errors -> unsolved goals -> linters.
4. **Leverage build artifacts**:
   - **`.ilean` files** (`.lake/build/lib/**/*.ilean`): parse directly for zero-latency symbol definitions and cross-references without waiting for language server elaboration.
   - **Emitted C99** (`.lake/build/ir/*.c`): inspect generated C code to evaluate memory boxing, reference-counting overhead (`lean_inc`/`lean_dec`), or FFI linkage.
   - **Binary `.olean` inspection**: run `Lean.readModuleData` scripts to audit kernel-level theorems and verify zero axioms without brittle text grepping.
5. **Hand off the diagnostic** -- proof failures -> `@lean-proof`; toolchain version mismatch -> `@lean-setup`; minimisation needed -> `@lean-mwe`; suspect upstream regression -> `@lean-bisect`; ready-to-file -> `@lean-pr`.

## Recovery & STOP

- Build result looks impossible (ghost errors, missing oleans for a built module) -> `lake clean`; for Mathlib, also `lake exe cache get`; re-run targeted build once. If still impossible, STOP and re-anchor.
- Build hangs > 10 min on a small target -> STOP, suspect dependency cycle or runaway elaboration; hand to `@lean-mwe` to isolate.
- `lake update` accidentally invoked mid-iteration -> STOP, `git diff lake-manifest.json`; revert unless the task is explicitly a dependency update.
- Bare `lean MyFile.lean` invoked instead of `lake env lean` -> STOP, results are unreliable; re-run inside the Lake env.

## Handoffs

- **Predecessors / successors**: see FM `handoffs`. Typical inbound: `@lean-setup` (after a clean install) or `@lean-proof` (after a tactic write). Typical outbound: `@lean-proof` (for active proof repair), `@lean-mwe` / `@lean-bisect` / `@lean-pr` for build failures surviving clean rebuilds.
- **Sister skill:** `@lean-setup` for toolchain repair; `@lean-proof` for interactive proving.
- **REDIRECT pointer:** `mathlib-build` slug routes here (preserved per Chesterton-protocol).

---

# Building Lean Projects with Lake

## Build rule of thumb

Use the repository's Lake environment for every command. Prefer
targeted builds while iterating, and only run the full suite when the
change is broad or ready for CI.

**Mathlib-specific:** fetch the Mathlib olean cache before build:

```bash
lake exe cache get
```

Use `lake exe cache get!` (with `!`) to force re-download if the cache
appears corrupt.

When building a large Lake project reduce verbosity to save on tokens:

```bash
lake build -q --log-level=info
```

For merge-conflict resolution or small fixes build only the affected
files: `lake build <Module>.Foo.Bar -q --log-level=info`. Often it is
fine to leave a complete build to CI.

## Lake command reference

```bash
lake env lean MyFile.lean              # check one file in the project env
lake env lean --version                # verify the active Lean toolchain
lake build <Module>.Foo.Bar -q --log-level=info
lake exe runLinter                     # linter pass
lake clean                             # remove build artifacts (current package only)
lake update <dep>                      # update one dependency intentionally
```

Do not use bare `lean MyFile.lean` inside a Lake project; it can bypass
the project toolchain, package path, and Lake environment.

## Stale artifact recovery

If a build result looks impossible, reset only generated artifacts:

```bash
lake clean
lake exe cache get        # if the project is Mathlib (otherwise omit)
lake build <Module>.Foo.Bar -q --log-level=info
```

Avoid `lake update` during routine validation unless the task is
explicitly a dependency update.

---

## See also

- [`../../templates/Template_Lakefile.md`](../../templates/Template_Lakefile.md) -- Template: Annotated lakefile and CI patterns
- [`../../references/lean4-module-dependency-guide.md`](../../references/lean4-module-dependency-guide.md) -- DAG enforcement and splitting workflow
- [`../../references/lean4-lsp-guide.md`](../../references/lean4-lsp-guide.md) -- Lean 4 Language Server Protocol comprehensive guide
- [`../lean-proof/SKILL.md`](../lean-proof/SKILL.md) -- Interactive LSP proving contract
- [`../_overrides/mathlib-build/SKILL.md`](../_overrides/mathlib-build/SKILL.md) -- REDIRECT stub (legacy slug)
