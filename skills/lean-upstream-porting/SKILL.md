---
name: "lean-upstream-porting"
description: |
  USE FOR: porting corpus lemmas or modules to mathlib/stdlib upstream: branch hygiene, PR body conventions.
  DO NOT USE FOR: the generic PR mechanics (open/label/bors/maintainer-merge - use @lean-pr).
  TRIGGERS: upstream, mathlib PR, port lemma, PR body, AI disclosure.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
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
## Recovery & STOP
- If `gh pr edit` silently drops body updates on the GraphQL path, read back the PR body and apply the update
  via `gh api -X PATCH
  repos/<owner>/<repo>/pulls/<n> -F body=@<body-file>`.
- If upstream module-system visibility (`public import` or sealed instances) breaks a corpus proof, isolate
  and repair the proof
  against
  upstream master
  via `@lean-proof` before updating the PR.
## Handoffs
- **Predecessors:** `lean-proof` (the proof is kernel-clean),
  `lean-proof-refactor` (the port is the slimmed form).
- **Successors:** `lean-research` (prior-art/citation sweeps), `lean-proof` (review fixes).
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-upstream-porting-handbook.md`](../../references/lean-upstream-porting-handbook.md) .
## See also
- [`../../references/lean-upstream-porting-handbook.md`](../../references/lean-upstream-porting-handbook.md)
  -- Complete
  `lean-upstream-porting` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
