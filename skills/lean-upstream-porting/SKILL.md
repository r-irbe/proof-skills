---
name: "lean-upstream-porting"
description: |
  USE FOR: porting corpus lemmas or modules to mathlib/stdlib upstream - branch hygiene, PR body conventions, AI-assistance disclosure, module-system pitfalls, claim-approval flow, PR lifecycle management via REST.
  DO NOT USE FOR: the generic PR mechanics (open/label/bors/maintainer-merge - use @lean-pr); writing the Lean proofs themselves (use @lean-proof); refactoring within the corpus (use @lean-proof-refactor); toolchain setup (use @lean-setup).
  TRIGGERS: upstream, mathlib PR, port lemma, PR body, AI disclosure, draft PR, branch hygiene, squash merge.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ["skill:lean-proof", "skill:lean-proof-refactor", "skill:lean-pr"]
  successors: ["skill:lean-pr", "skill:lean-research", "skill:lean-proof"]
metadata:
  version: "0.1.0"
  source_spec: "distilled from two live mathlib PRs (measurability + Cesaro, 2026-10)"
  last_reviewed: "2026-10"
---

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
   `gh api -X PATCH repos/<owner>/<repo>/pulls/<n> -F body=@file.md`
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

## Handoffs

- **Predecessors:** `lean-proof` (the proof is kernel-clean),
  `lean-proof-refactor` (the port is the slimmed form).
- **Successors:** `lean-research` (prior-art/citation sweeps), `lean-proof` (review fixes).
