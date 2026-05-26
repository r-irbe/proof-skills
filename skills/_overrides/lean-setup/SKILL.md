---
name: "lean-setup"
description: |
  USE FOR: bootstrapping a fresh leanprover/lean4 clone, repairing elan toolchains, linking stage0/stage1 builds, verifying that `lean` and `lake env lean` agree, cleaning up linked toolchains when done.
  DO NOT USE FOR: building Mathlib or downstream Lake projects (use @mathlib-build), bisecting a behavioural regression (use @lean-bisect), authoring a reproducer (use @lean-mwe), writing proofs (use @lean-proof), creating new lakefiles for downstream projects (use @lean-blueprint).
  TRIGGERS: elan, lean-toolchain, cmake preset, stage0, stage1.
tier: "hot"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: []
  successors:
    - "skill:lean-proof"
    - "skill:lean-bisect"
    - "skill:mathlib-build"
    - "skill:lean-mwe"
metadata:
  version: "0.2.0"
  source_spec: "specs/lean/setup/requirements.md"
  last_reviewed: "2026-05-30"
r_caveats: [F1]
---

# lean-setup

> ⚠️ **MANDATORY** (hot-tier): the gates in §Behavioural rules and the Persist
> step in §Workflow are enforced. There is no CI in this repo — the gates are
> enforced by the setup agent itself and reflected in the `lean-toolchain`
> files committed to the clone. Skipping Persist = incomplete, regardless of
> whether the build succeeded (FSIA-R-11-09).

## Routing

- **USE FOR:** running the first-time `cmake --preset release` + `make -j -C build/release` bootstrap; choosing a toolchain name (`lean4` or `lean4-XYZ`); linking `build/release/stage1` and `build/release/stage0` with `elan toolchain link`; pinning the four `lean-toolchain` files; verifying `lean --version` and `lake env lean --version` agree; uninstalling linked toolchains when the clone is retired.
- **DO NOT USE FOR:** building Mathlib or downstream Lake projects (use `@mathlib-build`); bisecting which commit changed behaviour (use `@lean-bisect`); minimising an error into a reproducer (use `@lean-mwe`); writing proofs against an existing toolchain (use `@lean-proof`); scaffolding new lakefiles for downstream projects (use `@lean-blueprint`).
- **TRIGGERS:** elan, lean-toolchain, cmake preset, stage0, stage1.

## Behavioural rules (G-*)

- **G-1** (MUST): On a fresh clone the skill MUST run `cmake --preset release` exactly once before any `make` invocation. [Trace: AC-01]
- **G-2** (MUST NOT): The skill MUST NOT re-run `cmake --preset release` on subsequent builds of the same clone. [Trace: AC-02]
- **G-3** (MUST): When the host already has a `lean4` toolchain linked, the skill MUST pick a disambiguated name `lean4-XYZ` rather than overwriting. [Trace: AC-03]
- **G-4** (MUST): The skill MUST link **both** `lean4-XYZ → build/release/stage1` and `lean4-XYZ-stage0 → build/release/stage0`. [Trace: AC-04]
- **G-5** (MUST): The skill MUST write all four toolchain pins together: `lean-toolchain`, `script/lean-toolchain`, `tests/lean-toolchain` (= stage1 name), and `src/lean-toolchain` (= stage0 name). [Trace: AC-05]
- **G-6** (MUST): After linking, the skill MUST verify `lean --version` resolves to the clone's commit hash, not a release tag. [Trace: AC-06]
- **G-7** (MUST): For any Lake project depending on the clone, the skill MUST additionally run `lake env lean --version` and confirm it agrees with `lean --version`. [Trace: AC-07]
- **G-8** (MUST NOT): If `lean --version` and `lake env lean --version` disagree, the skill MUST NOT hand off to `@lean-proof`; it MUST fix the override first. [Trace: AC-08]
- **G-9** (SHOULD): When the clone is being retired, the skill SHOULD run `elan toolchain uninstall` for both linked toolchains. [Trace: AC-09]
- **G-10** (MUST): The skill MUST persist (commit toolchain pins + state-tracker tick) before declaring setup complete. [Trace: AC-10]

## Workflow

1. **Discover** [discover] — inspect clone state: presence of `build/release/`, existing toolchain pins, `elan list`. Identify whether this is first-time bootstrap or repair.
2. **Plan** [discover] — choose toolchain name (`lean4` vs `lean4-XYZ`); enumerate which `lean-toolchain` files need writing. STOP if confidence < 80 % on naming or scope.
3. **Execute** [execute] — run `cmake --preset release` (first time only, G-2); `make -j -C build/release`; `elan toolchain link` for both stage0 and stage1; write the four `lean-toolchain` files.
4. **Verify** [validate] — `lean --version` shows commit hash (G-6); for any Lake project, `lake env lean --version` agrees (G-7). On disagreement, fix the override and re-verify; max 3 attempts then escalate.
5. **Persist** [persist] *(MANDATORY, FSIA-R-11-09)* — commit the toolchain pins, record the chosen name in the state tracker, tick `tasks.md`. If the clone is being retired, also `elan toolchain uninstall` and record the deletion. **Skipping Persist = incomplete.**

## Recovery & STOP

- `make -j -C build/release` fails ×3 → STOP, escalate to human; do not retry blindly.
- `lean --version` and `lake env lean --version` disagree after 3 fix attempts → STOP, escalate (G-8 forbids handing off).
- Scope drift (edit files outside the clone's `lean-toolchain` family, `build/`, or its lakefile overrides) → immediate STOP, re-anchor.
- Confidence < 80 % on toolchain naming (e.g. multiple existing `lean4-*` toolchains, unclear which is canonical) → STOP, ask.
- Context degradation signals (≥2 from AGENTS.md) → recommend a fresh session and re-read clone state.

## Handoffs

- **Predecessors / successors**: see FM `handoffs`. `lean-setup` is a root node — no predecessors. Typical outbound: `@lean-proof` (once `lean --version` and `lake env lean --version` agree), `@lean-bisect` (once toolchains are linked), `@mathlib-build` (for downstream builds), `@lean-mwe` (when the agent immediately needs to reproduce an issue against the new toolchain).
- **Source spec**: `specs/lean/setup/requirements.md` — every G-rule traces to an AC there.
- **Related ADRs**: ADR-0076 (skill-as-contract), ADR-0080 (handoff DAG), ADR-0028 (packaging — clone layout assumed).

## Common failure modes

> AI agents commonly: re-run `cmake --preset release` on every build; link
> only stage1 and forget stage0; pin only `lean-toolchain` and forget the
> three sibling files; declare success on a green `lean --version` without
> checking `lake env lean --version`; hand off to `@lean-proof` while the
> two `--version` commands disagree. Full registry:
> `GUARDRAILS.md §Agent failure taxonomy`.

## See also

- [`../../skills/skills/lean-setup/SKILL.md`](../../../skills/lean-setup/SKILL.md) — pre-v2 source skill (this is the migration).
- [`../../templates/Template_Lakefile.md`](../../../templates/Template_Lakefile.md) — annotated lakefile reference.
- [`../lean-proof/SKILL.md`](../lean-proof/SKILL.md) — v2 sibling, the typical successor in the DAG.
