---
name: lean-upstream-pr-handbook
description: Unified reference handbook for @lean-upstream-pr (Mathlib/Stdlib upstream
  porting, PR authoring, labels, and bors lifecycle).
extracted_from: skills/lean-upstream-pr/SKILL.md
---

## Quick-Lookup Indexing Tables (`mathcomp-skills` Three-Entry-Point Pattern)

### Table 1: Goal-Shape-First (`templates` Entry Point)

| Goal / Term Shape | Primary Tactic / Pattern | Canonical Recipe / Notes |
| :--- | :--- | :--- |
| Reusable general lemma inside domain repo | Generalize + Mathlib4 style pass | Strip project wrappers, minimize typeclasses, verify `#lint` |
| Multi-file upstream contribution | Stacked PR split (`<= 300 LOC` per PR) | Track dependencies via `- [ ] depends on: #NNN` |

### Table 2: Intent-First (`phrasebook` Entry Point)

| User / Engineer Intent | Recommended Tool / Idiom | Actionable Recipe |
| :--- | :--- | :--- |
| Check if lemma already exists in Mathlib | `lean_search(source: "loogle" | "code")` | Search modulo commutativity and ring morphisms before porting |
| Prepare Mathlib4 PR description & labels | `feat(Topic): summary` + AI disclosure | Require explicit human approval before `gh pr create` |

### Table 3: Error / Bottleneck-First (`errors` Entry Point)

| Symptom / Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| `#lint` fails on `docBlame` or `unusedArguments` | Missing `/-- ... -/` docstring or extra typeclass | Add Mathlib docstring and prune unused `[Fintype α]` hypotheses |
| Upstream CI rejects `autoImplicit` reliance | Implicit free variables in signature | Bind all universe and type parameters explicitly |

---

<!-- Merged from lean-pr-handbook.md -->

# lean-pr

> Agnostic PR-workflow contract for the whole Lean ecosystem.
> Upstream-specific conventions (Lean 4 core, Mathlib 4) live in
> `references/upstream/lean4-pr.md` and `references/upstream/mathlib4-pr.md`;
> this skill dispatches into them based on target repository.

## Routing

- **USE FOR:** any PR action against a Lean-ecosystem repo: branch-from-fork, title shaping (`<type>: <subject>` for Lean core, `<type>(<scope>):
  <subject>` for Mathlib), description authoring (first paragraph = changelog text), pre-flight validation (clean build, 0 sorry, 0 warnings, 0 debug
  probes), label selection per repo, running `lake exe mk_all` after Mathlib file renames, cross-linking dependent PRs via `- [ ] depends on: #XXXX`.
- **DO NOT USE FOR:** in-tree proof review (`@lean-proof-review`); Mathlib-specific review checklists (`references/upstream/mathlib4-review.md`); writing
  or fixing the proof itself (`@lean-proof`); validating the build before pushing (`@lean-build`); creating a bug-report repro (`@lean-mwe`).
- **TRIGGERS:** PR, pull request, "open a PR", changelog label, bors, `maintainer-merge`, `lake exe mk_all`, "file upstream", "ready to merge".

## Workflow

1. **Pre-flight verification** -- ensure local build passes cleanly via `lake build`. Confirm zero `sorry`, zero `admit`, zero unproven goals, and no
   leftover `trace_state` or `#check` probes.
2. **Pick conventions** -- consult the dispatch table (Lean 4 core / Mathlib 4 / Batteries / downstream). Read the relevant
   `references/upstream/<repo>-pr.md` if unfamiliar. STOP and ask if the target repo isn't in the table.
3. **Title + description** -- imperative present tense, lowercase subject, no period. First paragraph of description = changelog text, starts with "This PR
   ...". Skip `## Summary` / `## Test plan` headers -- CI and git diff carry that.
4. **Labels + commands** -- apply the repo's label conventions (Mathlib: `t-<topic>` / `easy` / `awaiting-author`; Lean core: `changelog-language` /
   `changelog-tactics` for `feat`/`fix`). For Mathlib file moves: `lake exe mk_all`. For Lean core: confirm copyright header on new `.lean` files in
   `src/`.
5. **Cross-link + handoff** -- declare `- [ ] depends on: #XXXX` for any predecessor PR. On merge, history is squash-rewritten -> keep the PR description
   complete (it becomes the merge commit body). For review feedback received during PR review, hand to `@lean-proof-review`.

## Recovery & STOP

- Unknown target repo (not in dispatch table) -> STOP, ask which conventions apply before pushing.
- Missing `changelog-*` label on Lean core `feat`/`fix` PR -> CI will block; read `references/upstream/lean4-pr.md` Section Changelog labels before re-pushing.
- Mathlib CI fails after file rename -> most common cause is forgetting `lake exe mk_all`; re-run and amend.
- PR description fails to render the changelog correctly -> confirm the first paragraph starts with `This PR ` and does not have a leading heading.
- Branch was opened from main, not a fork -> STOP, push to a fork and re-open; both Mathlib and Lean reject PRs from same-repo branches.

## Handoffs

- **Predecessors / successors**: see FM `handoffs`. Typical inbound: `@lean-build` (clean local build), `@lean-mwe` (for upstream bug-report PRs),
  `@lean-bisect` (when filing a known-version regression), `@lean-proof-review` (when review green-lit a contribution). Typical outbound:
  `@lean-proof-review` (for in-tree feedback) or `@lean-zettelkasten` (recording PR-process lessons).
- **REDIRECT pointer:** `lean-pr` slug routes here (preserved per Chesterton-protocol).

---

## See also

- [`../../references/lean4-lsp-guide.md`](../../references/lean4-lsp-guide.md) -- Lean 4 Language Server Protocol comprehensive guide
- [`../../references/upstream/lean4-pr.md`](../../references/upstream/lean4-pr.md) -- Lean 4 core repository PR conventions
- [`../../references/upstream/mathlib4-pr.md`](../../references/upstream/mathlib4-pr.md) -- Mathlib 4 PR conventions
- [`../lean-build/SKILL.md`](../lean-build/SKILL.md) -- Project compilation and Lake environment
- [`../lean-proof-review/SKILL.md`](../lean-proof-review/SKILL.md) -- Proof review council contract


---

<!-- Merged from lean-upstream-porting-handbook.md -->

# Upstream Porting (corpus lemma -> mathlib PR)

Port a proven result to upstream with its history, conventions, and
review surface intact.

## Routing

- **USE FOR:** preparing, filing, and maintaining upstream PRs from a
  proven corpus.
- **DO NOT USE FOR:** the mathematics itself; in-corpus refactors.

## Workflow

1. **Route the artifact first.** Math lemmas go to the math library
   (mathlib); methodologies, rubrics, and scanner tooling go to the
   skills repo. Never send methodology to mathlib or library code to
   the skills repo.
2. **Dossier before branch**: statement inventory, generalization
   framing, prior-art check (`#check` the twins; text search misses
   `@[to_additive]`/generated names), and the AI-assistance history.
   Get operator approval on each PR-body claim before filing.
3. **Branch hygiene**: one branch per independent PR, built against
   current master, 0 errors/0 warnings; never force-push shared
   branches; stack with `depends on:` lines only when semantics
   require it.
4. **PR body conventions** (mathlib; the generic PR contract is
   @lean-pr's to teach): title `feat(scope): summary` becomes the
   squash-commit first line; co-authors via `Co-authored-by:` lines;
   `Moves:`/`Deletions:` lists when relocating declarations;
   **AI-assistance disclosure is required by the contribution guide** -
   one honest sentence naming the tooling and stating the author's
   responsibility is the accepted minimal form.
5. **Module-system pitfalls** before building: notation reaches a file
   only through `public import` chains; `Real`'s norm/abs instances are
   sealed (rewrite explicitly, never rely on defeq); positional
   application stops at unassigned implicits; module docstring precedes
   `@[expose] public section`. Details:
   `references/mathlib-module-system-notes.md`.
6. **PR lifecycle via REST**: `gh pr edit` (GraphQL path) can fail
   silently - verify every edit with a read-back, and use
   `gh api -X PATCH repos/<owner>/<repo>/pulls/<n> -F body=@<body-file>`
   when it does. `gh pr create` on a branch that already has a PR
   surfaces the existing PR - update it rather than duplicating.

## Pitfalls

- Corollaries that specialize in one line: upstream prefers them as
  test-file worked examples over new public API surface.
- CI status lags the branch; say what is verified locally (master
  build, kernel checks) and what awaits CI, and never claim CI green
  without the run.
- Reviewers weight the generalization framing: state the general form
  once, show the corpus use as the motivating instance, and keep the
  body laconic - every sentence must survive a maintainer's skim.

## Recovery

- If `gh pr edit` silently drops body updates on the GraphQL path, read back the PR body and apply the update via `gh api -X PATCH
  repos/<owner>/<repo>/pulls/<n> -F body=@<body-file>`.
- If upstream module-system visibility (`public import` or sealed instances) breaks a corpus proof, isolate and repair the proof against upstream master
  via `@lean-proof` before updating the PR.

## Handoffs

- **Predecessors:** `lean-proof` (the proof is kernel-clean),
  `lean-proof-refactor` (the port is the slimmed form).
- **Successors:** `lean-research` (prior-art/citation sweeps), `lean-proof` (review fixes).

