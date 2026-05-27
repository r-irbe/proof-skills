---
name: lean-build
description: Build Lean 4 projects with Lake. Use when validating Lean changes, choosing targeted build commands, running `lake env lean`, debugging stale build artifacts, or preparing CI-quality local checks. Applies to any Lake-managed project (Mathlib, Cslib, EASCI, downstream).
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
build, run targeted commands per project; in Mathlib:
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

- [`../../templates/Template_Lakefile.md`](../../templates/Template_Lakefile.md) — Template: Annotated lakefile and CI patterns
- [`../../references/lean4-module-dependency-guide.md`](../../references/lean4-module-dependency-guide.md) — DAG enforcement and splitting workflow
- [`../mathlib-build/SKILL.md`](../mathlib-build/SKILL.md) — REDIRECT stub (legacy slug)
