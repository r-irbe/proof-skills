---
name: "lean-setup"
description: |
  USE FOR: bootstrapping a Lean 4 project or toolchain, configuring elan, pinning `lean-toolchain`, setting up `lakefile.lean` server memory limits (`moreServerArgs`), resolving C FFI headers via `lean --print-prefix`, verifying that `lean` and `lake env lean` agree, and cleaning up toolchains.
  DO NOT USE FOR: building Lake projects (use @lean-build), bisecting regressions (use @lean-bisect), creating MWEs (use @lean-mwe), writing proofs (use @lean-proof).
  TRIGGERS: elan, lean-toolchain, lake serve, moreServerArgs, toolchain mismatch, lake env lean.
tier: "hot"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: []
  successors:
    - "skill:lean-build"
    - "skill:lean-proof"
    - "skill:lean-mwe"
    - "skill:lean-bisect"
metadata:
  version: "0.3.0"
  source_spec: "specs/lean/setup/requirements.md"
  last_reviewed: "2026-09-16"
r_caveats: [F1]
---

# lean-setup

> MANDATORY (hot-tier): the gates in Section Behavioural rules and the Persist
> step in Section Workflow are enforced. There is no CI in this repo -- the gates are
> enforced by the setup agent itself and reflected in the `lean-toolchain`
> files committed to the clone. Skipping Persist = incomplete, regardless of
> whether the build succeeded (FSIA-R-11-09).

## Routing

- **USE FOR:** configuring `elan` toolchains; pinning `lean-toolchain`; configuring Lake server arguments (`moreServerArgs`) to prevent OOM SIGKILL and stack exhaustion; discovering Lean C sysroot paths via `lean --print-prefix`; verifying `lean --version` and `lake env lean --version` agree; bootstrapping or repairing local builds.
- **DO NOT USE FOR:** building Mathlib or downstream Lake projects (use `@lean-build`); bisecting which commit changed behaviour (use `@lean-bisect`); minimising an error into a reproducer (use `@lean-mwe`); writing proofs against an existing toolchain (use `@lean-proof`); scaffolding new lakefiles for downstream projects (use `@lean-blueprint`).
- **TRIGGERS:** elan, lean-toolchain, lake serve, moreServerArgs, cmake preset, stage0, stage1, toolchain mismatch.

## Behavioural rules (G-*)

- **G-1** (MUST): On a fresh Lean source clone the skill MUST run `cmake --preset release` exactly once before any `make` invocation. [Trace: AC-01]
- **G-2** (MUST NOT): The skill MUST NOT re-run `cmake --preset release` on subsequent builds of the same clone. [Trace: AC-02]
- **G-3** (MUST): When the host already has a `lean4` toolchain linked, the skill MUST pick a disambiguated name `lean4-XYZ` rather than overwriting. [Trace: AC-03]
- **G-4** (MUST): The skill MUST link **both** `lean4-XYZ -> build/release/stage1` and `lean4-XYZ-stage0 -> build/release/stage0` when compiling from source. [Trace: AC-04]
- **G-5** (MUST): The skill MUST keep toolchain pins synchronized across the repository: `lean-toolchain` and subproject configurations must agree. [Trace: AC-05]
- **G-6** (MUST): After linking or installing, the skill MUST verify `lean --version` matches the expected toolchain or commit hash. [Trace: AC-06]
- **G-7** (MUST): For any Lake project, the skill MUST run `lake env lean --version` and confirm it strictly agrees with `lean --version`. [Trace: AC-07]
- **G-8** (MUST NOT): If `lean --version` and `lake env lean --version` disagree, the skill MUST NOT hand off to `@lean-proof` or `@lean-build`; it MUST fix the override first. [Trace: AC-08]
- **G-9** (SHOULD): When a custom toolchain clone is being retired, the skill SHOULD run `elan toolchain uninstall` for linked toolchains. [Trace: AC-09]
- **G-10** (MUST): The skill MUST persist (commit toolchain pins + state-tracker tick) before declaring setup complete. [Trace: AC-10]
- **G-11** (MUST): In projects running interactive language servers, the skill MUST configure `moreServerArgs` in `lakefile.lean` with heap and stack caps (`#["-M", "4096", "-s", "32768", "-D", "maxHeartbeats=500000"]`) to prevent Linux OOM SIGKILL and stack overflow on FileWorkers. [Trace: AC-11]
- **G-12** (SHOULD): When C FFI bindings or `clangd` language server support are required, the skill SHOULD query `lean --print-prefix` and supply `${prefix}/include` and `${prefix}/include/clang` to C compiler flags. [Trace: AC-12]

## Workflow

1. **Discover** [discover] -- inspect clone state: check `lean-toolchain`, `elan list`, and lakefile configuration. Identify whether this is fresh project setup, version bump, or toolchain repair.
2. **Plan** [discover] -- choose toolchain release or disambiguated name; identify required server arguments (`moreServerArgs`). STOP if confidence < 80% on naming or version target.
3. **Execute** [execute] -- install/link toolchain (`elan toolchain install` or `cmake` + `elan toolchain link`); write `lean-toolchain`; configure `moreServerArgs` in `lakefile.lean`.
4. **Verify** [validate] -- `lean --version` matches target (G-6); `lake env lean --version` agrees (G-7); `lake serve` starts without watchdog errors. On disagreement, fix overrides; max 3 attempts then escalate.
5. **Persist** [persist] *(MANDATORY, FSIA-R-11-09)* -- commit `lean-toolchain` and lakefile updates, record chosen toolchain in state tracker. **Skipping Persist = incomplete.**

## Recovery & STOP

- `make -j -C build/release` or `elan` download fails x3 -> STOP, escalate to human; do not retry blindly.
- `lean --version` and `lake env lean --version` disagree after 3 fix attempts -> STOP, escalate (G-8 forbids handing off).
- Scope drift (edit files outside `lean-toolchain` family or lakefile) -> immediate STOP, re-anchor.
- Confidence < 80% on toolchain naming or release compatibility -> STOP, ask.
- Context degradation signals (>=2 from AGENTS.md) -> recommend a fresh session and re-read toolchain state.

## Handoffs

- **Predecessors / successors**: see FM `handoffs`. `lean-setup` is a root node. Typical outbound: `@lean-build` (compile project), `@lean-proof` (start tactic proving), `@lean-bisect` (investigate regressions), `@lean-mwe` (reproduce toolchain bugs).
- **Sister skills:** `@lean-build` for Lake builds; `@lean-proof` for live proving.
- **Source spec**: `specs/lean/setup/requirements.md`.

## Common failure modes

> AI agents commonly: re-run `cmake --preset release` on every build; link
> only stage1 and forget stage0; pin only `lean-toolchain` and forget sibling
> configurations; declare success on a green `lean --version` without
> checking `lake env lean --version`; omit `moreServerArgs` leading to silent
> OOM SIGKILL of FileWorkers under heavy proof loads. Full registry:
> `GUARDRAILS.md Section Agent failure taxonomy`.

## See also

- This `SKILL.md` is the canonical v2 toolchain-setup contract for this package.
- [`../../templates/Template_Lakefile.md`](../../templates/Template_Lakefile.md) -- annotated lakefile reference.
- [`../../references/lean4-lsp-guide.md`](../../references/lean4-lsp-guide.md) -- comprehensive Lean 4 Language Server Protocol guide.
- [`../lean-build/SKILL.md`](../lean-build/SKILL.md) -- Lake build and cache retrieval contract.
- [`../lean-proof/SKILL.md`](../lean-proof/SKILL.md) -- v2 sibling, the typical successor in the DAG.
