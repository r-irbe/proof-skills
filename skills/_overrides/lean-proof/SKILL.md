---
name: "lean-proof"
description: |
  USE FOR: writing Lean 4 proofs one tactic at a time, fixing tactic errors by priority, planning sorry placeholders, cleaning a working proof, resolving dependent-type rewriting failures.
  DO NOT USE FOR: reviewing existing proofs (use @lean-proof-review), project-wide quality assessment (use @lean-quality-engine), minimising an error into a bug report (use @lean-mwe), discovering tactics or API (use @lean-research), authoring new theorem statements (use @lean-specification), repairing toolchains (use @lean-setup).
  TRIGGERS: prove, tactic, sorry, unsolved goals, motive is not type correct.
tier: "hot"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors:
    - "skill:lean-setup"
    - "skill:lean-specification"
    - "skill:lean-research"
  successors:
    - "skill:lean-proof-review"
    - "skill:lean-mwe"
    - "skill:lean-zettelkasten"
metadata:
  version: "0.2.0"
  source_spec: "specs/lean/proof/requirements.md"
  last_reviewed: "2026-05-30"
r_caveats: [F1, F6]
---

# lean-proof

> ⚠️ **MANDATORY** (hot-tier): the gates in §Behavioural rules and the Persist
> step in §Workflow are enforced. There is no CI in this repo — the gates are
> enforced by the proving agent itself plus `@lean-proof-review` downstream.
> Skipping Persist = incomplete, regardless of artefact quality (FSIA-R-11-09).

## Routing

- **USE FOR:** writing Lean 4 proofs one tactic at a time with `done`-driven diagnostics; resolving errors in syntax → type → unsolved-goals → linter order; planning `sorry` placeholders so the hardest case is attacked first; cleaning a working proof into its minimal form; recovering from `motive is not type correct` via generalise-then-instantiate.
- **DO NOT USE FOR:** reviewing or auditing existing proofs (use `@lean-proof-review`); project-level QA orchestration (use `@lean-quality-engine`); minimising a failing proof into a bug-report MWE (use `@lean-mwe`); searching Mathlib or exploring tactics in the abstract (use `@lean-research`); writing or revising the theorem statement itself (use `@lean-specification`); repairing the Lean toolchain or `lake env` (use `@lean-setup`).
- **TRIGGERS:** prove, tactic, sorry, unsolved goals, motive is not type correct.

## Behavioural rules (G-*)

- **G-1** (MUST): The skill MUST write exactly one tactic, then read diagnostics, before writing the next. [Trace: AC-01]
- **G-2** (MUST): The skill MUST use `done` to surface unsolved goals whenever an active proof has expected next steps. [Trace: AC-02]
- **G-3** (MUST): Errors MUST be addressed in the order syntax → type → unsolved goals → linter. A lower-priority diagnostic MUST NOT be touched while a higher-priority one is open in the same file. [Trace: AC-03]
- **G-4** (MUST): When an "unsolved goals" error appears on a `by` or `=>` line alongside a tactic error on a later line, the tactic error MUST be fixed first. [Trace: AC-04]
- **G-5** (MUST NOT): The skill MUST NOT write further tactics after any unresolved error. [Trace: AC-05]
- **G-6** (MUST): When working a target theorem, the skill MUST go directly to that theorem and MAY leave dependent helper lemmas as `sorry`. [Trace: AC-06]
- **G-7** (SHOULD): Within a case split, the skill SHOULD `sorry` the easy branches and prove the hardest branch first. [Trace: AC-07]
- **G-8** (MUST): After a proof closes, the skill MUST attempt cleanup (combine rewrites, test whether `simp` subsumes earlier steps) before declaring the proof done. [Trace: AC-08]
- **G-9** (SHOULD): On `motive is not type correct` or analogous dependent-type rewrite failure, the skill SHOULD apply the generalise-then-instantiate pattern (`suffices ∀ s, …` + `convert`) rather than fighting the rewrite. [Trace: AC-09]
- **G-10** (MUST NOT): The skill MUST NOT declare a proof complete while any `sorry` or error diagnostic remains in the closed term. [Trace: AC-10]
- **G-11** (MUST): The skill MUST persist (commit + state-tracker tick) before handing off to `@lean-proof-review`. [Trace: AC-11]

## Workflow

1. **Discover** [discover] — read the target theorem, locate its spec, list open `sorry`s and existing diagnostics. Confirm `lake env lean` resolves (else hand back to `@lean-setup`).
2. **Plan** [discover] — pick the target theorem (not a helper lemma); within it, pick the hardest case. STOP if confidence < 80 % on overall strategy and hand off to `@lean-research`.
3. **Execute** [execute] — write one tactic at a time, gated on `done`/diagnostics. Honour the error-priority order (G-3, G-4). Apply generalise-then-instantiate (G-9) if a rewrite hits the motive trap.
4. **Verify** [validate] — re-read diagnostics on the closed proof; cleanup pass (G-8); confirm no `sorry` or error remains (G-10). Max 3 cleanup attempts before escalating.
5. **Persist** [persist] *(MANDATORY, FSIA-R-11-09)* — commit the proof, update the state tracker, tick `tasks.md`, and (if a recurring pattern surfaced) emit a fleeting note via `@lean-zettelkasten`. **Skipping Persist = incomplete.**

## Recovery & STOP

- Same error class fails ×3 attempts → STOP, escalate to human or hand off to `@lean-mwe` to isolate the failure.
- Scope drift (edit outside the target theorem, its helper lemmas, or its imports) → immediate STOP, re-anchor on the target.
- Confidence < 80 % on tactic strategy → STOP and hand off to `@lean-research`.
- Context degradation signals (≥2 from AGENTS.md — repeated tactic, ignored prior diagnostic, persona drift) → recommend a fresh session and re-anchor the theorem.

## Handoffs

- **Predecessors / successors**: see FM `handoffs` (grammar from ADR-0080). Typical inbound: `@lean-setup` confirms toolchain; `@lean-specification` supplies the theorem; `@lean-research` supplies tactic strategy. Typical outbound: `@lean-proof-review` audits; `@lean-mwe` if stuck; `@lean-zettelkasten` records the pattern.
- **Source spec**: `specs/lean/proof/requirements.md` — every G-rule traces to an AC there.
- **Related ADRs**: ADR-0076 (skill-as-contract), ADR-0080 (handoff DAG), ADR-0079 (tier loading).

## Common failure modes

> AI agents commonly: write 3-5 tactics before reading diagnostics; chase a
> linter warning while an unsolved-goals error is open; fill helper-lemma
> `sorry`s before touching the target theorem; declare success while a
> `sorry` remains; fight `motive is not type correct` with more `rw` instead
> of generalising. Full registry: `GUARDRAILS.md §Agent failure taxonomy`.

## See also

- [`../../skills/skills/lean-proof/SKILL.md`](../../../skills/lean-proof/SKILL.md) — pre-v2 source skill (this is the migration).
- [`../../templates/Template_ProofStrategy.md`](../../../templates/Template_ProofStrategy.md) — proof methodology cheat sheet.
- [`../../references/lean4-proof-strategy.md`](../../../references/lean4-proof-strategy.md) — one-step-at-a-time, error priority, hardest case first.
- [`../../references/lean4-tactic-hierarchy.md`](../../../references/lean4-tactic-hierarchy.md) — tactic priority table.
