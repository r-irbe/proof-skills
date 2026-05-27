---
name: "lean-pr"
description: |
  USE FOR: opening, titling, or labelling a PR against any Lean ecosystem repo (`leanprover/lean4`, `leanprover-community/mathlib4`, Cslib, downstream EASCI/FLT/Carleson), picking the right commit-message convention, applying upstream-specific labels (changelog-* for Lean core; t-* / easy / awaiting-author for Mathlib), running `lake exe mk_all` for Mathlib file renames, cross-linking dependent PRs.
  DO NOT USE FOR: in-tree proof review (use @lean-proof-review), Mathlib PR-review checklists (use `references/upstream/mathlib4-review.md`), writing the actual proof (use @lean-proof), building the change locally (use @lean-build), minimising an upstream-bug repro (use @lean-mwe).
  TRIGGERS: PR, pull request, "open a PR", changelog label, bors, maintainer-merge, `lake exe mk_all`, upstream filing.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors:
    - "skill:lean-build"
    - "skill:lean-mwe"
    - "skill:lean-bisect"
    - "skill:lean-proof-review"
  successors:
    - "skill:lean-proof-review"
    - "skill:lean-zettelkasten"
metadata:
  version: "0.2.0"
  source_spec: "skills/_overrides/lean-pr/SKILL.md"
  last_reviewed: "2026-05-27"
  migrated_from: "pre-v2 vendor mirror"
---

# lean-pr

> Agnostic PR-workflow skill for the whole Lean ecosystem.
> Upstream-specific conventions (Lean 4 core; Mathlib 4) live in
> `references/upstream/lean4-pr.md` and `references/upstream/mathlib4-pr.md`;
> this skill dispatches into them based on target repo.

## Routing

- **USE FOR:** any PR action against a Lean-ecosystem repo: branch-from-fork, title shaping (`<type>: <subject>` for Lean core, `<type>(<scope>): <subject>` for Mathlib), description authoring (first paragraph = changelog text), label selection per repo, running `lake exe mk_all` after Mathlib file renames, cross-linking dependent PRs via `- [ ] depends on: #XXXX`.
- **DO NOT USE FOR:** in-tree proof review (`@lean-proof-review`); Mathlib-specific review checklists (`references/upstream/mathlib4-review.md`); writing or fixing the proof itself (`@lean-proof`); validating the build before pushing (`@lean-build`); creating a bug-report repro (`@lean-mwe`).
- **TRIGGERS:** PR, pull request, "open a PR", changelog label, bors, `maintainer-merge`, `lake exe mk_all`, "file upstream", "ready to merge".

## Workflow

1. **Pick conventions** — consult the dispatch table (Lean 4 core / Mathlib 4 / Cslib / downstream). Read the relevant `references/upstream/<repo>-pr.md` if unfamiliar. STOP and ask if the target repo isn't in the table.
2. **Title + description** — imperative present tense, lowercase subject, no period. First paragraph of description = changelog text, starts with "This PR ...". Skip `## Summary` / `## Test plan` / `## Implementation details` headers — CI + code carry that.
3. **Labels + commands** — apply the repo's label conventions (Mathlib: `t-<topic>` / `easy` / `awaiting-author`; Lean core: `changelog-language` / `changelog-tactics` / etc. for `feat`/`fix`). For Mathlib file moves: `lake exe mk_all`. For Lean core: confirm copyright header on new `.lean` files in `src/`.
4. **Cross-link + handoff** — declare `- [ ] depends on: #XXXX` for any predecessor PR. On merge, history is squash-rewritten → keep the PR description complete (it becomes the merge commit body). For in-tree review feedback received during PR review, hand to `@lean-proof-review`.

## Recovery & STOP

- Unknown target repo (not in dispatch table) → STOP, ask which conventions apply before pushing.
- Missing `changelog-*` label on Lean core `feat`/`fix` PR → CI will block; read `references/upstream/lean4-pr.md` §Changelog labels before re-pushing.
- Mathlib CI fails after file rename → most common cause is forgetting `lake exe mk_all`; re-run and amend.
- PR description fails to render the changelog correctly → confirm the first paragraph starts with `This PR ` and does not have a leading heading.
- Branch was opened from main, not a fork → STOP, push to a fork and re-open; both Mathlib and Lean reject PRs from same-repo branches.

## Handoffs

- **Predecessors / successors**: see FM `handoffs`. Typical inbound: `@lean-build` (clean local build), `@lean-mwe` (for upstream bug-report PRs), `@lean-bisect` (when filing a known-version regression), `@lean-proof-review` (when the council green-lit a contribution). Typical outbound: `@lean-proof-review` (for in-tree feedback) or `@lean-zettelkasten` (recording PR-process lessons).
- **REDIRECT pointer:** `mathlib-pr` slug routes here (preserved per Chesterton-protocol).
- **Source notes:** vendor mirror at `vendor/leanprover-skills/skills/lean-pr/SKILL.md`.

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
