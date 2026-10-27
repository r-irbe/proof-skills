---
name: "lean-core-only"
description: |
  USE FOR: Lean 4 work in a CORE-ONLY lane -- a project whose artifact may import nothing but the Lean toolchain (no Mathlib.
  DO NOT USE FOR: Mathlib-dependent proving (@lean-proof).
  TRIGGERS: core Lean, no Mathlib, unknown module prefix, unknown tactic.
tier: "hot"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors:
    - "skill:lean-setup"
    - "skill:lean-specification"
  successors:
    - "skill:lean-proof"
    - "skill:lean-build"
    - "skill:lean-axiom-closure"
    - "skill:lean-mwe"
metadata:
  version: "0.1.0"
  source_spec: "skills/lean-core-only/SKILL.md (this file)"
  last_reviewed: "2026-10-16"
---

# lean-core-only
> **MANDATORY** (hot-tier): G-1 (prove the invocation), G-2 (no Mathlib-only
## Routing
- **USE FOR:** a core-only lane's tactic choices (core `omega` yes, `linarith` no);
  `import Spec` failing with `unknown module prefix`; `unknown tactic` from a
  Mathlib name; `maximum recursion depth` / `maximum heartbeats` on an otherwise
  correct-looking proof; project-root and `lakefile.toml` invocation questions;
  goal-state introspection without editing the artifact.
- **DO NOT USE FOR:** anything where Mathlib is allowed (use `@lean-proof` with
  the `@lean-math-analysis` family); the axiom-closure audit itself (use `@lean-axiom-closure`);
  toolchain brokenness (use `@lean-setup`).
## Workflow
1. **Discover** [discover] -- establish the root and the invocation: which
   directory holds `lakefile.lean` / `lakefile.toml`, which toolchain is pinned,
   whether the package declares dependencies. Confirm `lake env lean <file>`
   resolves the artifact's own imports before touching any proof.
2. **Plan** [discover] -- pick the tactic set from the core list (G-2); for each
   numeric step prefer `omega`, for definitional steps `rw`/`simp only` with an
   explicit lemma list, for case analysis `cases`/`induction` + `omega` per branch.
3. **Execute** [execute] -- one tactic at a time, checking the goal out of band
   (G-5) instead of editing probes into the artifact.
4. **Validate** [validate] -- `lake build` at DEFAULT limits (no local
## Recovery & STOP
- **Environment** -- `unknown module prefix` while the build is green: STOP,
  re-run through `lake env lean` from the project root (G-1) before diagnosing
  anything else.
- **Tactic availability** -- a needed step has no core-only equivalent: STOP and
  escalate. Do not smuggle in an import (G-3, G-7).
- **Recursion limits** -- the proof needs `maxRecDepth`/`maxHeartbeats` above
  defaults to elaborate: STOP and hand the declaration to `@lean-proof` for a
## Handoffs
- **Predecessors:** `@lean-setup` (toolchain), `@lean-specification` (statement).
- **Successors:** `@lean-proof` (structural fixes), `@lean-build` (build/CI
  mechanics), `@lean-axiom-closure` (trust base), `@lean-mwe` (isolation).
- **Handbook:** [`../../references/lean4-core-only-profile.md`](../../references/lean4-core-only-profile.md)
  -- the core/Mathlib tactic boundary, the recursion-limit triage table, and the
  goal-introspection loop.
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-core-only-handbook.md`](../../references/lean-core-only-handbook.md) .
## See also
- [`../../references/lean-core-only-handbook.md`](../../references/lean-core-only-handbook.md) -- Complete
  `lean-core-only`
  Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
