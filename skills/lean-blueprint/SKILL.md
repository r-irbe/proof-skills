---
name: "lean-blueprint"
description: |
  USE FOR: generating Lean blueprint, annotating theorems with @[blueprint], scaffolding blueprint directory.
  DO NOT USE FOR: writing Lean proofs (use @lean-proof), opening Lean/Mathlib PRs (use @lean-pr).
  TRIGGERS: blueprint, leanblueprint, LeanArchitect, dependency-graph.
tier: "hot"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-specification"]
  successors: ["skill:lean-doc-improvement", "skill:lean-quality-engine"]
metadata:
  version: "0.2.0"
  source_spec: "specs/lean/blueprint/requirements.md"
  last_reviewed: "2026-05-26"
---

# lean-blueprint
> ⚠️ **MANDATORY** (hot-tier): the gates in §Behavioural rules and the Persist
> step in §Workflow are CI-enforced. Skipping Persist = incomplete, regardless
> of artefact quality (FSIA-R-11-09).
## Routing
- **USE FOR:** generating a navigable formal blueprint from a Lean 4 codebase; annotating definitions and
  theorems with
  `@[blueprint]`;
  scaffolding
  `blueprint/` with `leanblueprint new`; building blueprint LaTeX via `lake build :blueprint`; rendering the
  dependency graph and
  web view.
- **DO NOT USE FOR:** authoring new Lean proofs (use `@lean-proof`); opening Lean/Mathlib PRs (use
  `@lean-pr`); editing prose docs
  (use
  `@lean-doc-improvement`).
- **TRIGGERS:** blueprint, leanblueprint, LeanArchitect, dependency-graph.
## Workflow
1. **Discover** [discover] — read inputs, list Lean modules, locate `lakefile.lean` and prior `blueprint/`,
  and audit current
  coverage via
   `lean_blueprint`
   (`{"action": "status", "formalizationDir": "...", "blueprintDir": "..."}`).
2. **Plan** [discover] — propose per-module annotator fan-out; generate proof outlines with `lean_blueprint`
  (`{"action":
  "skeleton",
   "symbol": "..."}`) or
   `lean_blueprint(action: "skeleton")`; STOP if confidence < 80 %.
3. **Annotate** [execute] — scaffold LaTeX entries via `lean_blueprint` (`{"action": "scaffold", "symbol":
  "..."}`) or
   `lean_blueprint(action: "scaffold")`, and apply
   `@[blueprint]` annotations and LaTeX statements inside owned scope.
4. **Build** [execute] — run `lake build :blueprint`.
## Recovery & STOP
- `lake build :blueprint` fails ×3 → STOP, escalate to human.
- Scope drift (touch outside `blueprint/` or annotated `.lean` files) → immediate STOP, re-anchor.
- Confidence < 80 % on annotation strategy → STOP, ask.
- Context degradation signals (≥2 from AGENTS.md) → recommend fresh session.
## Handoffs
- **Predecessors / successors**: see FM `handoffs` (grammar from ADR-0080).
- **Source spec**: `specs/lean/blueprint/requirements.md` — every G-rule traces to an AC there.
- **Related ADRs**: ADR-0076, ADR-0080.
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-blueprint-handbook.md`](../../references/lean-blueprint-handbook.md) .
## See also
- [`../../references/lean-blueprint-handbook.md`](../../references/lean-blueprint-handbook.md) -- Complete
  `lean-blueprint`
  Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
