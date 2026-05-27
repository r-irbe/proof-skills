# Lean 4 (leanprover/lean4) PR Conventions (reference)

> Reference content extracted from the `lean-pr` SKILL during W4 Wave 2
> (move A1 of `lab/design/07-cluster-workflow.md`). Repo-specific
> conventions for PRs against `leanprover/lean4` live here; the
> generic Lean-ecosystem PR workflow stays in the
> [`lean-pr`](../../skills/_overrides/lean-pr/SKILL.md) SKILL.

## Commit message format

PR titles use:

```
<type>: <subject>
```

`<type>` is one of: `feat`, `fix`, `doc`, `style`, `refactor`, `test`,
`chore`, `perf`.

`<subject>`: imperative present tense, lowercase, no period.

For `feat`/`fix` PRs, begin the description with **`This PR `** — the
first paragraph is automatically used in release notes.

## Changelog labels

Every `feat` or `fix` PR must carry a `changelog-*` label:

| Label | Category |
|---|---|
| `changelog-language` | Language features and metaprograms |
| `changelog-tactics` | User-facing tactics |
| `changelog-server` | Language server, widgets, and IDE extensions |
| `changelog-pp` | Pretty printing |
| `changelog-library` | Library |
| `changelog-compiler` | Compiler, runtime, and FFI |
| `changelog-lake` | Lake |
| `changelog-doc` | Documentation |
| `changelog-ffi` | FFI changes |
| `changelog-other` | Other changes |
| `changelog-no` | Do not include in changelog |

## Module system for `src/` files

Files in `src/Lean/`, `src/Std/`, and `src/lake/Lake/` must have both
`module` and `prelude` declarations. With `prelude`, nothing is
auto-imported — you must explicitly import `Init.*` modules.

```lean
module

prelude
import Init.While
import Init.Data.String.TakeDrop
public import Lean.Compiler.NameMangling
```

Check existing files in the same directory for the pattern.

Files outside these directories (e.g. `tests/`, `script/`) use just
`module`.

## Copyright headers

New files in `src/` require a copyright header:

```
/-
Copyright (c) YYYY Author or Organization. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Author Name
-/
```

Check other recent files in the repository to determine the correct
copyright holder. Test files (in `tests/`) do not need copyright
headers.

## Description shape (project-wide convention)

- Start with a paragraph beginning **`This PR ...`** — no section headers
- No `## Summary` header — just start with the text
- No `## Test plan` section — CI is relied on
- No `## Implementation details` section — the code speaks for itself

## See also

- [`./mathlib4-pr.md`](./mathlib4-pr.md) — Mathlib4 PR conventions (sister upstream)
- [`./mathlib4-review.md`](./mathlib4-review.md) — Mathlib PR review standards
- [`../../skills/_overrides/lean-pr/SKILL.md`](../../skills/_overrides/lean-pr/SKILL.md) — Agnostic Lean-ecosystem PR SKILL
