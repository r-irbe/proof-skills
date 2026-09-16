---
name: "lean-pr"
description: |
  USE FOR: opening, titling, or labelling a PR against any Lean ecosystem repo (`leanprover/lean4`, `leanprover-community/mathlib4`, Batteries, or downstream projects), pre-flight build and sorry checks, picking commit-message conventions, applying upstream labels, cross-linking dependent PRs.
  DO NOT USE FOR: in-tree proof review (use @lean-proof-review), Mathlib PR-review checklists (use `references/upstream/mathlib4-review.md`), writing the actual proof (use @lean-proof), building the change locally (use @lean-build), minimising an upstream-bug repro (use @lean-mwe).
  TRIGGERS: PR, pull request, "open a PR", changelog label, bors, maintainer-merge, `lake exe mk_all`, upstream filing, ready to merge.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors:
    - "skill:lean-build"
    - "skill:lean-mwe"
    - "skill:lean-bisect"
    - "skill:lean-proof-review"
    - "skill:lean-proof"
  successors:
    - "skill:lean-proof-review"
    - "skill:lean-zettelkasten"
metadata:
  version: "0.3.0"
  source_spec: "skills/lean-pr/SKILL.md"
  last_reviewed: "2026-09-16"
  migrated_from: "repo-native first-party promotion"
---

# lean-pr

> Agnostic PR-workflow contract for the whole Lean ecosystem.
> Upstream-specific conventions (Lean 4 core, Mathlib 4) live in
> `references/upstream/lean4-pr.md` and `references/upstream/mathlib4-pr.md`;
> this skill dispatches into them based on target repository.

## Routing

- **USE FOR:** any PR action against a Lean-ecosystem repo: branch-from-fork, title shaping (`<type>: <subject>` for Lean core, `<type>(<scope>): <subject>` for Mathlib), description authoring (first paragraph = changelog text), pre-flight validation (clean build, 0 sorry, 0 warnings, 0 debug probes), label selection per repo, running `lake exe mk_all` after Mathlib file renames, cross-linking dependent PRs via `- [ ] depends on: #XXXX`.
- **DO NOT USE FOR:** in-tree proof review (`@lean-proof-review`); Mathlib-specific review checklists (`references/upstream/mathlib4-review.md`); writing or fixing the proof itself (`@lean-proof`); validating the build before pushing (`@lean-build`); creating a bug-report repro (`@lean-mwe`).
- **TRIGGERS:** PR, pull request, "open a PR", changelog label, bors, `maintainer-merge`, `lake exe mk_all`, "file upstream", "ready to merge".

## Workflow

1. **Pre-flight verification** -- ensure local build passes cleanly via `lake build`. Confirm zero `sorry`, zero `admit`, zero unproven goals, and no leftover `trace_state` or `#check` probes.
2. **Pick conventions** -- consult the dispatch table (Lean 4 core / Mathlib 4 / Batteries / downstream). Read the relevant `references/upstream/<repo>-pr.md` if unfamiliar. STOP and ask if the target repo isn't in the table.
3. **Title + description** -- imperative present tense, lowercase subject, no period. First paragraph of description = changelog text, starts with "This PR ...". Skip `## Summary` / `## Test plan` headers -- CI and git diff carry that.
4. **Labels + commands** -- apply the repo's label conventions (Mathlib: `t-<topic>` / `easy` / `awaiting-author`; Lean core: `changelog-language` / `changelog-tactics` for `feat`/`fix`). For Mathlib file moves: `lake exe mk_all`. For Lean core: confirm copyright header on new `.lean` files in `src/`.
5. **Cross-link + handoff** -- declare `- [ ] depends on: #XXXX` for any predecessor PR. On merge, history is squash-rewritten -> keep the PR description complete (it becomes the merge commit body). For review feedback received during PR review, hand to `@lean-proof-review`.

## Recovery & STOP

- Unknown target repo (not in dispatch table) -> STOP, ask which conventions apply before pushing.
- Missing `changelog-*` label on Lean core `feat`/`fix` PR -> CI will block; read `references/upstream/lean4-pr.md` Section Changelog labels before re-pushing.
- Mathlib CI fails after file rename -> most common cause is forgetting `lake exe mk_all`; re-run and amend.
- PR description fails to render the changelog correctly -> confirm the first paragraph starts with `This PR ` and does not have a leading heading.
- Branch was opened from main, not a fork -> STOP, push to a fork and re-open; both Mathlib and Lean reject PRs from same-repo branches.

## Handoffs

- **Predecessors / successors**: see FM `handoffs`. Typical inbound: `@lean-build` (clean local build), `@lean-mwe` (for upstream bug-report PRs), `@lean-bisect` (when filing a known-version regression), `@lean-proof-review` (when review green-lit a contribution). Typical outbound: `@lean-proof-review` (for in-tree feedback) or `@lean-zettelkasten` (recording PR-process lessons).
- **REDIRECT pointer:** `mathlib-pr` slug routes here (preserved per Chesterton-protocol).

---

## See also

- [`../../references/lean4-lsp-guide.md`](../../references/lean4-lsp-guide.md) -- Lean 4 Language Server Protocol comprehensive guide
- [`../../references/upstream/lean4-pr.md`](../../references/upstream/lean4-pr.md) -- Lean 4 core repository PR conventions
- [`../../references/upstream/mathlib4-pr.md`](../../references/upstream/mathlib4-pr.md) -- Mathlib 4 PR conventions
- [`../_overrides/mathlib-pr/SKILL.md`](../_overrides/mathlib-pr/SKILL.md) -- REDIRECT stub (legacy slug)
- [`../lean-build/SKILL.md`](../lean-build/SKILL.md) -- Project compilation and Lake environment
- [`../lean-proof-review/SKILL.md`](../lean-proof-review/SKILL.md) -- Proof review council contract
