---
name: "lean-bisect"
description: |
  USE FOR: bisecting Lean 4 toolchain versions or commits to find which one introduced a regression.
  DO NOT USE FOR: building a project (@lean-build).
  TRIGGERS: bisect, regression, "which commit broke".
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors:
    - "skill:lean-mwe"
    - "skill:lean-proof"
    - "skill:lean-setup"
  successors:
    - "skill:lean-pr"
    - "skill:lean-zettelkasten"
metadata:
  version: "0.3.0"
  source_spec: "skills/lean-bisect/SKILL.md"
  last_reviewed: "2026-09-16"
  migrated_from: "repo-native first-party promotion"
---

# Bisecting Lean Toolchains
> Toolchain bisecting contract for Lean 4 and Mathlib. Guides pinpointing
> introducing commits across compiler releases or nightlies using `script/lean-bisect`.
## Routing
- **USE FOR:** running `script/lean-bisect` on a self-contained Lean test file to identify the Lean 4 commit
  or nightly that
  introduced a
  behaviour change;
  comparing exit-code, stdout, and stderr signatures across a commit range; isolating regressions in tactic
  behaviour, elaborator
  output,
panic conditions,
  or build success.
- **DO NOT USE FOR:** building any Lake project (use `@lean-build`); reducing a Mathlib-dependent failure to a
  self-contained
  repro (use
  `@lean-mwe` first;
  bisect operates on standalone files); writing the proof or repairing the failure itself (use `@lean-proof`);
  filing the upstream
  bug
report after the
## Workflow
1. **Prepare** -- confirm the test file is self-contained (no `Mathlib` imports). If Mathlib-dependent, hand
  off to `@lean-mwe`
  first to
   produce a
   standalone repro. STOP otherwise.
2. **Verify endpoints** -- manually run `lake env lean` (or bare `lean` for vendored toolchains) on the
  failing version *and* the
  known-good
   version.
   Confirm they show different behaviour before starting the bisect.
3. **Bisect** -- `script/lean-bisect /tmp/test.lean <range>` with the appropriate `--timeout`. Use
  `--ignore-messages` if only
  exit code
   matters; use
   `#guard_msgs` to capture exact diagnostics; use `--nightly-only` to keep cycles bounded across long ranges.
## Recovery & STOP
- Same signature on both endpoints -> STOP, the test does not discriminate; redesign before bisecting.
- Mathlib import re-appears after minimisation -> STOP, route back to `@lean-mwe`; `lean-bisect` cannot test
  versions where the
  Mathlib
  toolchain pin
  doesn't match.
- Timeout exhaustion (3 consecutive `--timeout` increases without resolution) -> STOP, the test is too slow;
  reduce or isolate
  further.
## Handoffs
- **Predecessors / successors**: see FM `handoffs`. Typical inbound: `@lean-mwe` (after Mathlib-free repro) or
  direct from
  `@lean-proof`
  (when the operator
  already has a standalone file). Typical outbound: `@lean-pr` (upstream report) or `@lean-zettelkasten`
  (record the pattern).
- **Sister skill:** `@lean-mwe` -- usually chained before bisect.
---
Use the `lean-bisect` script (in the lean4 repo at `script/lean-bisect`) to find which commit introduced a
behavior change.
---
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-bisect-handbook.md`](../../references/lean-bisect-handbook.md) .
## See also
- [`../../references/lean-bisect-handbook.md`](../../references/lean-bisect-handbook.md) -- Complete
  `lean-bisect` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
