---
name: "lean-upstream-pr"
description: |
  USE FOR: porting lemmas to Mathlib/Stdlib and opening, labelling, or managing upstream Lean 4 PRs.
  DO NOT USE FOR: in-tree review (@lean-proof-review) or package vendoring (@lean-dependency-management).
  TRIGGERS: upstream PR, mathlib PR, port lemma, open a PR, bors, changelog label, AI disclosure.
tier: warm
runtime_targets:
- copilot-cli
- claude-code
- antigravity
- pi
- cursor
- gemini-cli
dispatch_targets: []
handoffs:
  predecessors:
  - skill:lean-proof-review
  - skill:lean-proof-refactor
  - skill:lean-mwe
  successors:
  - skill:lean-retro-methodology
metadata:
  version: 0.4.0
  source_spec: Unified from lean-pr and lean-upstream-porting
  last_reviewed: 2026-11
---

# Lean 4 & Mathlib Upstream Porting and PR Lifecycle

Generalize reusable in-tree lemmas to Mathlib4/Stdlib conventions and manage the full upstream pull-request lifecycle cleanly and transparently.

## Routing
- **USE FOR:** generalizing project-local lemmas to Mathlib4 style, branch/commit hygiene, PR titles/labels
  (`feat(Algebra/...): ...`), AI-assistance disclosure, and `bors` review loops.
- **DO NOT USE FOR:** shrinking upstream bug reproducers (`@lean-mwe`) or vendoring external repos into your project (`@lean-dependency-management`).

## Workflow
1. **Deduplicate & Generalize** -- Search `lean_search(source: "loogle" | "code")` to confirm the lemma is absent
  upstream; strip project-specific scaling/wrappers and generalize typeclasses to minimal Mathlib4 mixins.
2. **Enforce Mathlib4 Style** -- Apply `snake_case` naming, `set_option autoImplicit false` compatibility, `/-- ...
  -/` docstrings, explicit module imports, and `#lint` pass (`references/protocols/mathlib4-conventions.md`).
3. **Prepare PR & Disclosure** -- Format conventional title, summary, dependency links (`- [ ] depends on: #...`),
  and mandatory AI-tooling disclosure per upstream repository policy.
4. **Human-in-the-Loop Gate** -- Present the final diff, `#lint` output, and PR body for explicit human approval before executing `gh pr create`.

## Recovery & STOP
- Never push directly to `main`/`master` or open an external upstream PR without explicit human sign-off.
- If `lean_search` finds an existing Mathlib lemma up to argument order or ring morphism, abort the port and replace the local copy with the Mathlib lemma.

## Handoffs
- **Predecessors:** `lean-proof-review`, `lean-proof-refactor`, `lean-mwe`.
- **Successors:** `lean-retro-methodology`.

## Detailed reference
- **Layer-1 Fast Lookup Card (read first)**: [`references/cards/lean-upstream-pr-tables.md`](../../references/cards/lean-upstream-pr-tables.md)
- Full handbook: [`../../references/handbooks/lean-upstream-pr-handbook.md`](../../references/handbooks/lean-upstream-pr-handbook.md)
- PR template: [`../../templates/workflow/Template_PR.md`](../../templates/workflow/Template_PR.md)

## See also
- [`../../references/protocols/mathlib4-conventions.md`](../../references/protocols/mathlib4-conventions.md) -- Mathlib4 style & naming guide
- [`../lean-mwe/SKILL.md`](../lean-mwe/SKILL.md) -- Minimal working examples for upstream bug reports
