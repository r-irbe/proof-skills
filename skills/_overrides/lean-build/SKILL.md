---
name: "lean-build"
description: |
  USE FOR: building Lean 4 projects with Lake, validating Lean changes with `lake env lean`, picking targeted build commands (`lake build <Module>`), resolving stale build artifacts via `lake clean` + `lake exe cache get`, preparing CI-quality local checks. Applies to any Lake-managed project (Mathlib, Cslib, or downstream repositories).
  DO NOT USE FOR: bisecting which Lean version caused a regression (use @lean-bisect), minimising an error to a bug-report repro (use @lean-mwe), repairing the toolchain itself (use @lean-setup), writing or fixing the proof (use @lean-proof).
  TRIGGERS: build, lake, lake env lean, lake exe cache get, stale artifacts, lake clean, build error, CI prep.
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
metadata:
  version: "0.2.0"
  source_spec: "skills/_overrides/lean-build/SKILL.md"
  last_reviewed: "2026-05-27"
  migrated_from: "pre-v2 vendor mirror"
---

# lean-build

> Agnostic Lake-build skill, mirrored from `vendor/leanprover-skills`
> with the Mathlib-specific `lake exe cache get` note retained. The
> Mathlib-only `mathlib-build` slug now redirects here (W4 Wave 1).

## Routing

- **USE FOR:** running `lake env lean`, `lake build <Module>`, `lake exe cache get`, `lake clean`, `lake exe runLinter`, `lake update <dep>` — including merge-conflict resolution, targeted iteration, and CI-quality local checks across any Lake-managed project.
- **DO NOT USE FOR:** bisecting a Lean version-pin regression (use `@lean-bisect`); minimising a build failure to a self-contained MWE (use `@lean-mwe`); repairing or installing the Lean toolchain itself (use `@lean-setup`); fixing the underlying proof error that the build surfaces (use `@lean-proof`).
- **TRIGGERS:** build, lake, lake env lean, lake exe cache get, stale artifacts, lake clean, "build is slow", "CI failed locally", CI prep.

## Workflow

1. **Pick scope** — single-file (`lake env lean MyFile.lean`), targeted module (`lake build <Module>.Foo.Bar -q --log-level=info`), or full suite (only when broad / pre-CI). Default to targeted iteration to save tokens.
2. **Fetch cache** — for Mathlib projects, `lake exe cache get` (or `lake exe cache get!` if cache appears corrupt); for non-Mathlib Lake projects, skip this step (no shared cache).
3. **Build + parse** — run with `-q --log-level=info`. If unexpected results appear, run `lake clean` + cache-get + re-build before treating the diagnostic as real.
4. **Hand off the diagnostic** — proof failures → `@lean-proof`; toolchain version mismatch → `@lean-setup`; minimisation needed → `@lean-mwe`; suspect upstream regression → `@lean-bisect`; ready-to-file → `@lean-pr`.

## Recovery & STOP

- Build result looks impossible (e.g. ghost errors, missing oleans for a built module) → `lake clean`; for Mathlib, also `lake exe cache get`; re-run targeted build once. If still impossible, STOP and re-anchor.
- Build hangs > 10 min on a small target → STOP, suspect dependency cycle or runaway elaboration; hand to `@lean-mwe` to isolate.
- `lake update` accidentally invoked mid-iteration → STOP, `git diff lake-manifest.json`; revert unless the task is explicitly a dependency update.
- Bare `lean MyFile.lean` invoked instead of `lake env lean` → STOP, results are unreliable; re-run inside the Lake env.

## Handoffs

- **Predecessors / successors**: see FM `handoffs`. Typical inbound: `@lean-setup` (after a clean install) or `@lean-proof` (after a tactic write). Typical outbound: `@lean-mwe` / `@lean-bisect` / `@lean-pr` for any failure that survives a clean rebuild.
- **Sister skill:** `@lean-setup` for toolchain repair (which often manifests as build failures).
- **REDIRECT pointer:** `mathlib-build` slug routes here (preserved per Chesterton-protocol).
- **Source notes:** vendor mirror at `vendor/leanprover-skills/skills/lean-build/SKILL.md`.

---

# Building Lean Projects with Lake

This skill is the agnostic counterpart of `mathlib-build` (now a
REDIRECT stub — W4 Wave 1 / move A3 of
`lab/design/07-cluster-workflow.md`). The content is Lake-generic; the
single Mathlib-specific note (`lake exe cache get`) is called out
explicitly because the cache lives in the
`leanprover-community/mathlib4` repo, not in Lake itself.

## Build rule of thumb

Use the repository's Lake environment for every command. Prefer
targeted builds while iterating, and only run the full suite when the
change is broad or ready for CI.

**Mathlib-specific:** fetch the Mathlib olean cache before build:

```bash
lake exe cache get
```

Use `lake exe cache get!` (with `!`) to force re-download if the cache
appears corrupt. This script is provided by Mathlib; other Lake projects
typically do not ship an olean cache.

When building a large Lake project reduce verbosity to save on tokens:

```bash
lake build -q --log-level=info
```

For merge-conflict resolution or small fixes build only the affected
files: `lake build <Module>.Foo.Bar -q --log-level=info`. Often it is
fine to leave a complete build to CI. If you need a thorough local
build, run targeted commands per host repository; in Mathlib:
`lake build Mathlib MathlibTest Archive Counterexamples && lake exe runLinter`.

## Lake command reference

```bash
lake env lean MyFile.lean              # check one file in the project env
lake env lean --version                # verify the active Lean toolchain
lake build <Module>.Foo.Bar -q --log-level=info
lake exe runLinter                     # Mathlib-specific linter pass
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

- [`../../../templates/Template_Lakefile.md`](../../../templates/Template_Lakefile.md) — Template: Annotated lakefile and CI patterns
- [`../../../references/lean4-module-dependency-guide.md`](../../../references/lean4-module-dependency-guide.md) — DAG enforcement and splitting workflow
- [`../mathlib-build/SKILL.md`](../mathlib-build/SKILL.md) — REDIRECT stub (legacy slug)
