---
name: "lean-pr"
description: |
  USE FOR: opening, titling, or labelling a PR against any Lean ecosystem repo (`leanprover/lean4`.
  DO NOT USE FOR: in-tree proof review (@lean-proof-review).
  TRIGGERS: PR, pull request, "open a PR", changelog label, bors.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
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
- **USE FOR:** any PR action against a Lean-ecosystem repo: branch-from-fork, title shaping (`<type>:
  <subject>` for Lean core,
  `<type>(<scope>):
  <subject>` for Mathlib), description authoring (first paragraph = changelog text), pre-flight validation
  (clean build, 0 sorry,
  0
warnings, 0 debug
  probes), label selection per repo, running `lake exe mk_all` after Mathlib file renames, cross-linking
  dependent PRs via `- [ ]
  depends
on: #XXXX`.
- **DO NOT USE FOR:** in-tree proof review (`@lean-proof-review`); Mathlib-specific review checklists
  (`references/upstream/mathlib4-review.md`); writing
## Workflow
1. **Pre-flight verification** -- ensure local build passes cleanly via `lake build`. Confirm zero `sorry`,
  zero `admit`, zero
  unproven
   goals, and no
   leftover `trace_state` or `#check` probes.
2. **Pick conventions** -- consult the dispatch table (Lean 4 core / Mathlib 4 / Batteries / downstream). Read
  the relevant
   `references/upstream/<repo>-pr.md` if unfamiliar. STOP and ask if the target repo isn't in the table.
3. **Title + description** -- imperative present tense, lowercase subject, no period. First paragraph of
  description = changelog
  text,
   starts with "This PR
   ...". Skip `## Summary` / `## Test plan` headers -- CI and git diff carry that.
## Recovery & STOP
- Unknown target repo (not in dispatch table) -> STOP, ask which conventions apply before pushing.
- Missing `changelog-*` label on Lean core `feat`/`fix` PR -> CI will block; read
  `references/upstream/lean4-pr.md` Section
  Changelog labels
  before re-pushing.
- Mathlib CI fails after file rename -> most common cause is forgetting `lake exe mk_all`; re-run and amend.
## Handoffs
- **Predecessors / successors**: see FM `handoffs`. Typical inbound: `@lean-build` (clean local build),
  `@lean-mwe` (for upstream
  bug-report
  PRs),
  `@lean-bisect` (when filing a known-version regression), `@lean-proof-review` (when review green-lit a
  contribution). Typical
  outbound:
  `@lean-proof-review` (for in-tree feedback) or `@lean-zettelkasten` (recording PR-process lessons).
- **REDIRECT pointer:** `lean-pr` slug routes here (preserved per Chesterton-protocol).
---
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-pr-handbook.md`](../../references/lean-pr-handbook.md) .
## See also
- [`../../references/lean-pr-handbook.md`](../../references/lean-pr-handbook.md) -- Handbook
  Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
