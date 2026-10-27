---
name: "lean-mwe"
description: |
  USE FOR: creating minimal working examples (MWEs) from Lean 4 errors for upstream bug reports.
  DO NOT USE FOR: bisecting which Lean version introduced the bug (@lean-bisect).
  TRIGGERS: MWE, minimal repro, "minimise the error", "#guard_msgs".
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors:
    - "skill:lean-proof"
    - "skill:lean-build"
  successors:
    - "skill:lean-bisect"
    - "skill:lean-pr"
    - "skill:lean-proof"
metadata:
  version: "0.3.0"
  source_spec: "skills/lean-mwe/SKILL.md"
  last_reviewed: "2026-09-16"
  migrated_from: "repo-native first-party promotion"
---

# Minimizing Lean Errors
> Agnostic Minimal Working Example (MWE) contract for Lean 4.
> Guides isolating tactic, elaborator, or compiler bugs into self-contained
> reproducers using `#guard_msgs`, `#guard_panic`, and LSP-guided dependency pruning.
## Routing
- **USE FOR:** wrapping a failing Lean fragment in a `#guard_msgs` / `#guard_panic` guard that captures the
  exact diagnostic, then
  driving
  `lake exe
  minimize` (or manual LSP-guided import pruning) to delete imports and definitions until a self-contained
  reproducer remains;
  verifying the
result with
  `lake env lean`; resuming interrupted minimisations with `--resume`.
- **DO NOT USE FOR:** bisecting which Lean commit broke the file (use `@lean-bisect` after the MWE is
  self-contained); building or
  running
  the live project
## Workflow
1. **Set up the guard** -- choose `#guard_msgs` (for errors / warnings) or `#guard_panic` (for panics). Paste
  the exact diagnostic
  text
   verbatim into the guard.
2. **Verify the guard** -- `lake env lean YourFile.lean` must produce no output (guard passes). If it errors,
  the guard text does
  not match;
   adjust the
   guard before minimising. Always use `lake env lean`, never bare `lean`.
3. **LSP-guided import pruning** -- before running heavy minimization, inspect the forward import tree via
  `$/lean/moduleHierarchy/imports`.
   Remove unused
   transitive imports to isolate the dependency closure.
4. **Minimise** -- `lake exe minimize YourFile.lean`. Use `--quiet` for long runs; `--resume` after manual
  edits to `.out.lean`;
   `--only-delete` /
   `--only-import-inlining` for surgical passes.
## Recovery & STOP
- Guard fails on first verify -> STOP, the diagnostic text doesn't match the model's output
  character-for-character; widen the
  guard or fix
  the example
  before running the minimiser.
- Minimiser hangs > 60 min with `--resume` not progressing -> STOP, hand to `@lean-bisect` if the failure may
  be
  version-dependent;
  otherwise reduce the
  input by hand.
## Handoffs
- **Predecessors / successors**: see FM `handoffs`. Typical inbound: `@lean-proof` (when a tactic fails
  unexpectedly) or
  `@lean-build` (when
  CI surfaces an
  unexpected compiler error). Typical outbound: `@lean-bisect` (find the introducing commit) or `@lean-pr`
  (file the issue/PR with
  the MWE
attached).
- **Sister skill:** `@lean-bisect` -- typically the next step after the MWE is Mathlib-free.
---
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-mwe-handbook.md`](../../references/lean-mwe-handbook.md) .
## See also
- [`../../references/lean-mwe-handbook.md`](../../references/lean-mwe-handbook.md) -- Handbook
  Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
