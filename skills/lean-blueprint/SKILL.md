---
name: "lean-blueprint"
description: |
  USE FOR: generating Lean blueprint, annotating theorems with @[blueprint], scaffolding blueprint directory, building blueprint LaTeX, rendering blueprint web.
  DO NOT USE FOR: writing Lean proofs (use @lean-formalization), editing Mathlib (use @lean-mathlib-contrib).
  TRIGGERS: blueprint, leanblueprint, LeanArchitect, dependency-graph.
tier: "hot"
runtime_targets: [copilot-cli, claude-code]
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

- **USE FOR:** generating a navigable formal blueprint from a Lean 4 codebase; annotating definitions and theorems with `@[blueprint]`; scaffolding `blueprint/` with `leanblueprint new`; building blueprint LaTeX via `lake build :blueprint`; rendering the dependency graph and web view.
- **DO NOT USE FOR:** authoring new Lean proofs (use `@lean-formalization`); contributing to Mathlib (use `@lean-mathlib-contrib`); editing prose docs (use `@lean-doc-improvement`).
- **TRIGGERS:** blueprint, leanblueprint, LeanArchitect, dependency-graph.

## Behavioural rules (G-*)

- **G-1** (MUST): The blueprint pipeline MUST run the five stages in order (analyze → annotate → scaffold → extract → render). [Trace: AC-01]
- **G-2** (MUST): Every `@[blueprint]` annotation MUST carry a matching LaTeX statement in `content.tex`. [Trace: AC-02]
- **G-3** (MUST NOT): The skill MUST NOT mutate files outside `blueprint/` and the annotated `.lean` modules. [Trace: AC-03]
- **G-4** (SHOULD): The skill SHOULD fan out per-module annotators when ≥6 modules are in scope. [Trace: AC-04]
- **G-5** (MUST): `lake build :blueprint` MUST succeed before render. [Trace: AC-05]
- **G-6** (MUST): `leanblueprint pdf` and `leanblueprint web` MUST both produce artefacts under `blueprint/`. [Trace: AC-06]
- **G-7** (SHOULD NOT): The skill SHOULD NOT re-annotate modules already carrying complete `@[blueprint]` coverage. [Trace: AC-07]
- **G-8** (MUST): On any guard failure the skill MUST escalate per §Recovery & STOP. [Trace: AC-08]

## Workflow

1. **Discover** [discover] — read inputs, list Lean modules, locate `lakefile.lean` and prior `blueprint/`.
2. **Plan** [discover] — propose per-module annotator fan-out; STOP if confidence < 80 %.
3. **Annotate** [execute] — apply `@[blueprint]` annotations and LaTeX statements inside owned scope.
4. **Build** [execute] — run `lake build :blueprint`.
5. **Verify** [validate] — confirm artefacts exist; max 3 retries then escalate.
6. **Render** [execute] — run `leanblueprint pdf` and `leanblueprint web`.
7. **Persist** [persist] *(MANDATORY, FSIA-R-11-09)* — commit changes, update state tracker, tick `tasks.md`. Skipping Persist = incomplete.

## Recovery & STOP

- `lake build :blueprint` fails ×3 → STOP, escalate to human.
- Scope drift (touch outside `blueprint/` or annotated `.lean` files) → immediate STOP, re-anchor.
- Confidence < 80 % on annotation strategy → STOP, ask.
- Context degradation signals (≥2 from AGENTS.md) → recommend fresh session.

## Handoffs

- **Predecessors / successors**: see FM `handoffs` (grammar from ADR-0080).
- **Source spec**: `specs/lean/blueprint/requirements.md` — every G-rule traces to an AC there.
- **Related ADRs**: ADR-0076, ADR-0080.

## Common failure modes

> AI agents commonly: skip the Persist step; over-annotate stable modules;
> re-run `lake build` instead of escalating on third failure.
> Full registry: GUARDRAILS.md §Agent failure taxonomy.
