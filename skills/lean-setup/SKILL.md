---
name: "lean-setup"
description: |
  USE FOR: bootstrapping a Lean 4 project or toolchain, configuring elan, pinning `lean-toolchain`.
  DO NOT USE FOR: building Lake projects (@lean-build); bisecting regressions (@lean-bisect).
  TRIGGERS: elan, lean-toolchain, lake serve, moreServerArgs.
tier: "hot"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors:
    - "agent:lean-gateway"
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
## Routing
- **USE FOR:** configuring `elan` toolchains; pinning `lean-toolchain`; configuring Lake server arguments
  (`moreServerArgs`) to
  prevent OOM
  SIGKILL and
  stack exhaustion; discovering Lean C sysroot paths via `lean --print-prefix`; verifying `lean --version` and
  `lake env lean
  --version`
agree;
  bootstrapping or repairing local builds.
- **DO NOT USE FOR:** building Mathlib or downstream Lake projects (use `@lean-build`); bisecting which commit
  changed behaviour
  (use
  `@lean-bisect`);
  minimising an error into a reproducer (use `@lean-mwe`); writing proofs against an existing toolchain (use
  `@lean-proof`);
  scaffolding new
lakefiles for
## Workflow
1. **Discover** [discover] -- inspect clone state: check `lean-toolchain`, `elan list`, and lakefile
  configuration. Identify
  whether this is
   fresh project
   setup, version bump, or toolchain repair.
2. **Plan** [discover] -- choose toolchain release or disambiguated name; identify required server arguments
  (`moreServerArgs`).
  STOP if
   confidence < 80%
   on naming or version target.
3. **Execute** [execute] -- install/link toolchain (`elan toolchain install` or `cmake` + `elan toolchain
  link`); write
  `lean-toolchain`;
   configure
   `moreServerArgs` in `lakefile.lean`.
4. **Verify** [validate] -- `lean --version` matches target (G-6); `lake env lean --version` agrees (G-7);
  `lake serve` starts
  without
   watchdog errors. On
   disagreement, fix overrides; max 3 attempts then escalate.
## Recovery & STOP
- `make -j -C build/release` or `elan` download fails x3 -> STOP, escalate to human; do not retry blindly.
- `lean --version` and `lake env lean --version` disagree after 3 fix attempts -> STOP, escalate (G-8 forbids
  handing off).
- Scope drift (edit files outside `lean-toolchain` family or lakefile) -> immediate STOP, re-anchor.
- Confidence < 80% on toolchain naming or release compatibility -> STOP, ask.
## Handoffs
- **Predecessors / successors**: see FM `handoffs`. `lean-setup` is a root node. Typical outbound:
  `@lean-build` (compile
  project),
  `@lean-proof` (start
  tactic proving), `@lean-bisect` (investigate regressions), `@lean-mwe` (reproduce toolchain bugs).
- **Sister skills:** `@lean-build` for Lake builds; `@lean-proof` for live proving.
- **Source spec**: `specs/lean/setup/requirements.md`.
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-setup-handbook.md`](../../references/lean-setup-handbook.md) .
## See also
- [`../../references/lean-setup-handbook.md`](../../references/lean-setup-handbook.md) -- Complete
  `lean-setup` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
