---
name: lean-pr
description: PR workflow for any Lean ecosystem repository (leanprover/lean4, leanprover-community/mathlib4, cslib, downstream projects). Use when opening, titling, or labeling a PR against any Lean repo. DO NOT USE FOR in-tree review semantics (→ `lean-proof-review`) or Mathlib PR-review checklists (→ `references/upstream/mathlib4-review.md`).
---

# Lean Ecosystem PR Workflow

This SKILL is the agnostic PR workflow shared across the Lean
ecosystem. The two upstream-specific convention sets — Lean 4 core
(`leanprover/lean4`) and Mathlib 4 (`leanprover-community/mathlib4`) —
live as references and are dispatched into below.

W4 Wave 2 / move A1 of `lab/design/07-cluster-workflow.md` extracted
the per-repo content; `mathlib-pr` is now a REDIRECT stub pointing
back here.

## Dispatch — which conventions apply?

| Target repo | Read first | Title format |
|---|---|---|
| `leanprover/lean4` | [`references/upstream/lean4-pr.md`](../../references/upstream/lean4-pr.md) | `<type>: <subject>` |
| `leanprover-community/mathlib4` | [`references/upstream/mathlib4-pr.md`](../../references/upstream/mathlib4-pr.md) | `<type>(<scope>): <subject>` |
| Cslib (`cslib`) | [`references/upstream/mathlib4-pr.md`](../../references/upstream/mathlib4-pr.md) (closest convention sibling) | `<type>(<scope>): <subject>` |
| Downstream (EASCI, FLT, Carleson) | Repo-local CONTRIBUTING.md if present; otherwise [`references/upstream/mathlib4-pr.md`](../../references/upstream/mathlib4-pr.md) | repo-local |

## Generic workflow

1. **Branch from a fork.** Mathlib and Lean both reject PRs from
   branches on the main repo.
2. **Title using the upstream's convention.** Use the dispatch table
   above to pick the format. Imperative present tense, lowercase
   subject, no period — these are shared across the ecosystem.
3. **Description first paragraph carries the changelog text.** Start
   with `This PR ...` and keep it concise. Skip `## Summary`,
   `## Test plan`, and `## Implementation details` headers —
   CI handles tests, code handles details.
4. **Apply the right labels.** Mathlib: `changelog-*` is not used;
   instead `t-<topic>`, `easy`, `awaiting-author`. Lean core:
   `changelog-language`/`changelog-tactics`/etc. is mandatory for
   `feat`/`fix`. See per-repo reference.
5. **Run the upstream's update commands.** Mathlib:
   `lake exe mk_all` if files added/removed; Lean core: no analogue.
6. **Cross-link dependencies.** Both repos accept the
   `- [ ] depends on: #XXXX` checkbox syntax in PR descriptions.

## Common to all Lean-ecosystem PRs

- **Copyright headers** on new files in `src/` (Lean core) or any
  `.lean` file outside `tests/` (Mathlib, Cslib). Use the existing
  pattern in the directory.
- **Imperative present tense** in commit subjects across the
  ecosystem.
- **No trailing period** in subjects.
- **Squash on merge** is the default for both Lean core (via maintainer
  squash) and Mathlib (via bors). Your branch history is rewritten —
  keep the PR description complete because it becomes the merge
  commit body.

## Recovery & STOP

- If unsure which repo conventions apply, fall back to the dispatch
  table above and read the relevant reference before pushing.
- If a `changelog-*` label is missing on a Lean core `feat`/`fix` PR,
  CI will block — read [`references/upstream/lean4-pr.md`](../../references/upstream/lean4-pr.md) §Changelog labels.
- If Mathlib CI fails after a file rename, you likely forgot
  `lake exe mk_all`.
- For in-tree review feedback during PR review, hand off to
  [`lean-proof-review`](../lean-proof-review/SKILL.md).

---

## See also

- [`../../templates/Template_Refactoring.md`](../../templates/Template_Refactoring.md) — Template: Module splitting and import re-organization
- [`../../references/mathlib4-conventions.md`](../../references/mathlib4-conventions.md) — Naming, file headers, capitalization expected in PRs
- [`../../references/upstream/lean4-pr.md`](../../references/upstream/lean4-pr.md) — Lean 4 core (leanprover/lean4) PR conventions (W4 Wave 2)
- [`../../references/upstream/mathlib4-pr.md`](../../references/upstream/mathlib4-pr.md) — Mathlib4 PR conventions (W4 Wave 2)
- [`../../references/upstream/mathlib4-review.md`](../../references/upstream/mathlib4-review.md) — Mathlib PR review standards
- [`../mathlib-pr/SKILL.md`](../mathlib-pr/SKILL.md) — REDIRECT stub (legacy slug)
