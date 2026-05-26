---
name: mathlib-build
description: Build Lean 4 and Mathlib projects with Lake. Use when validating Lean or Mathlib changes, choosing targeted build commands, fetching olean caches, running `lake env lean`, debugging stale build artifacts, or preparing CI-quality local checks.
---

# Building Mathlib

## Build rule of thumb

Use the repository's Lake environment for every command. Prefer targeted builds
while iterating, and only run the full suite when the change is broad or ready
for CI.

Fetch the Mathlib olean cache before build:

```bash
lake exe cache get
```

Use `lake exe cache get!` (with `!`) to force re-download if the cache appears corrupt.

When building Mathlib reduce verbosity to save on tokens:

```bash
lake build -q --log-level=info
```

For merge conflict resolution or small fixes build only the affected files: `lake build Mathlib.Foo.Bar -q --log-level=info`.
Often it is fine to leave a complete build to CI. If you need a thorough local build, use `lake build Mathlib MathlibTest Archive Counterexamples && lake exe runLinter`.

## Lake command reference

```bash
lake env lean MyFile.lean              # check one file in the project env
lake env lean --version                # verify the active Lean toolchain
lake build Mathlib.Foo.Bar -q --log-level=info
lake exe runLinter                     # run Mathlib linters after build
lake clean                             # remove build artifacts
lake update mathlib                    # update one dependency intentionally
```

Do not use bare `lean MyFile.lean` inside a Lake project; it can bypass the
project toolchain, package path, and Lake environment.

## Stale artifact recovery

If a build result looks impossible, reset only generated artifacts:

```bash
lake clean
lake exe cache get
lake build Mathlib.Foo.Bar -q --log-level=info
```

Avoid `lake update` during routine validation unless the task is explicitly a
dependency update.

---

## See also

- [`../../templates/Template_Lakefile.md`](../../templates/Template_Lakefile.md) — Template: Annotated lakefile and CI patterns
- [`../../references/lean4-module-dependency-guide.md`](../../references/lean4-module-dependency-guide.md) — DAG enforcement and splitting workflow
