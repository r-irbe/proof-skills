---
name: "lean-bisect"
description: |
  USE FOR: bisecting Lean 4 toolchain versions or commits to find which one introduced a regression, using `script/lean-bisect` with `#guard_msgs` / exit-code signatures, ignoring messages with `--ignore-messages`, bisecting between nightlies or arbitrary commits.
  DO NOT USE FOR: building a project (use @lean-build), minimising a Mathlib repro to a self-contained file (use @lean-mwe first), writing or fixing the proof itself (use @lean-proof), filing the bug report (use @lean-pr after the bisect points at a culprit).
  TRIGGERS: bisect, regression, "which commit broke", "behavior changed between", nightly bisect.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors:
    - "skill:lean-mwe"
    - "skill:lean-proof"
  successors:
    - "skill:lean-pr"
    - "skill:lean-zettelkasten"
metadata:
  version: "0.2.0"
  source_spec: "skills/_overrides/lean-bisect/SKILL.md"
  last_reviewed: "2026-05-27"
  migrated_from: "pre-v2 vendor mirror"
---

# lean-bisect

> Vendor-origin skill (mirrored from `vendor/leanprover-skills/skills/lean-bisect`);
> this override v2-wraps it so dispatch agents can route to it under the same
> contract as first-party skills.

## Routing

- **USE FOR:** running `script/lean-bisect` on a self-contained Lean test file to identify the Lean 4 commit or nightly that introduced a behaviour change; comparing exit-code + stdout + stderr signatures across a commit range; isolating regressions in tactic behaviour, elaborator output, panic conditions, or build success.
- **DO NOT USE FOR:** building any Lake project (use `@lean-build`); reducing a Mathlib-dependent failure to a self-contained repro (use `@lean-mwe` first; bisect operates on standalone files); writing the proof or repairing the failure itself (use `@lean-proof`); filing the upstream bug report after the culprit commit is known (use `@lean-pr`).
- **TRIGGERS:** bisect, regression, "which commit broke", "behaviour changed between nightlies", nightly bisect.

## Workflow

1. **Prepare** — confirm the test file is self-contained (no `Mathlib` imports). If Mathlib-dependent, hand off to `@lean-mwe` first to produce a standalone repro. STOP otherwise.
2. **Verify endpoints** — manually run `lake env lean` (or bare `lean` for vendored toolchains) on the failing version *and* the known-good version. Confirm they show different behaviour before starting the bisect.
3. **Bisect** — `script/lean-bisect /tmp/test.lean <range>` with the appropriate `--timeout`. Use `--ignore-messages` if only exit code matters; use `#guard_msgs` to capture exact diagnostics; use `--nightly-only` to keep cycles bounded across long ranges.
4. **Report** — record the culprit commit + signature change in a Zettelkasten note (`@lean-zettelkasten`) and hand to `@lean-pr` if upstream filing is warranted.

## Recovery & STOP

- Same signature on both endpoints → STOP, the test does not discriminate; redesign before bisecting.
- Mathlib import re-appears after minimisation → STOP, route back to `@lean-mwe`; `lean-bisect` cannot test versions where the Mathlib toolchain pin doesn't match.
- Timeout exhaustion (3 consecutive `--timeout` increases without resolution) → STOP, the test is too slow; reduce or isolate further.
- Cache corruption signals (impossible signature, ghost regressions) → run `script/lean-bisect --selftest` then `--clear-cache`; re-attempt once before escalating.

## Handoffs

- **Predecessors / successors**: see FM `handoffs`. Typical inbound: `@lean-mwe` (after Mathlib-free repro) or direct from `@lean-proof` (when the operator already has a standalone file). Typical outbound: `@lean-pr` (upstream report) or `@lean-zettelkasten` (record the pattern).
- **Sister skill:** `@lean-mwe` — usually chained before bisect.
- **Source notes:** vendor mirror at `vendor/leanprover-skills/skills/lean-bisect/SKILL.md`.

---

# Bisecting Lean Toolchains

Use the `lean-bisect` script (in the lean4 repo at `script/lean-bisect`) to find which commit introduced a behavior change.

## Test File Requirements

Test files must be self-contained with no `Mathlib` imports (Mathlib is pinned to specific toolchains and will fail on most versions tested). See the minimization skill if you need to reduce a Mathlib test case to a standalone one.

## Usage

```bash
# Auto-find regression
script/lean-bisect /tmp/test.lean

# Bisect up to a given nightly
script/lean-bisect /tmp/test.lean ..nightly-2024-06-01

# Between nightlies
script/lean-bisect /tmp/test.lean nightly-2024-01-01..nightly-2024-06-01

# Between commits
script/lean-bisect /tmp/test.lean abc1234..def5678

# With timeout
script/lean-bisect /tmp/test.lean --timeout 30
```

## Pass/Fail Determination

The script compares a "signature" of exit code + stdout + stderr. It bisects to find where this signature changes. Use `--ignore-messages` to only consider exit code.

## Test File Patterns

### Using exit code

```lean
axiom G : Type
axiom op : G -> G -> G

example : ... := by
  <the failing tactic call>
```

### Using `#guard_msgs`

```lean
/--
error: the specific error that should appear
-/
#guard_msgs in
example : ... := by ...
```

## Options

- `--timeout N`: Timeout in seconds per test
- `--ignore-messages`: Only compare exit codes
- `--nightly-only`: Only test nightly releases when bisecting commits
- `--selftest`: Verify the script works
- `--clear-cache`: Clear `~/.cache/lean_build_artifact/`

## Workflow for Mathlib Issues

When the issue requires Mathlib:

1. Create a minimal test case
2. Use https://github.com/kim-em/mathlib-minimizer to produce a Mathlib-free version (see `lean-mwe` skill)
3. Run lean-bisect on the minimized file

## Tips

Verify endpoints of the range show different behavior before bisecting. Keep tests fast — each bisection step runs the full test.

**Project context (22,312 lines, ≥1,255 theorems, zero sorry, grind-first tactics):** when bisecting an Project regression, reproduce with the same tactic (`grind` before `omega`/`linarith`) for accurate isolation. Test files must have no sorry unless testing sorry-specific elaboration behavior.

---

## See also

- [`../../references/lean4-module-dependency-guide.md`](../../references/lean4-module-dependency-guide.md) — Layer discipline and cycle detection (debugging build cycles)
- [`../../../references/upstream/lean-bug-report-pipeline.md`](../../../references/upstream/lean-bug-report-pipeline.md) — Shared 5-stage bug-report pipeline (repro → guard → minimise → bisect → file) and `lean-mwe` ↔ `lean-bisect` hand-off contract
- [`../lean-mwe/SKILL.md`](../lean-mwe/SKILL.md) — Sister skill for MWE construction (typically chained before bisect)
