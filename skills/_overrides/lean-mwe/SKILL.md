---
name: "lean-mwe"
description: |
  USE FOR: creating minimal working examples (MWEs) from Lean 4 errors for upstream bug reports, capturing diagnostics with `#guard_msgs`, capturing panics with `#guard_panic`, running `lake exe minimize`, resuming long minimisations with `--resume`, verifying repros with `lake env lean`.
  DO NOT USE FOR: bisecting which Lean version introduced the bug (use @lean-bisect after MWE), building or validating the live project (use @lean-build), repairing the proof itself (use @lean-proof), filing the report (use @lean-pr after MWE + bisect).
  TRIGGERS: MWE, minimal repro, "minimise the error", "#guard_msgs", "#guard_panic", `lake exe minimize`, upstream bug report.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors:
    - "skill:lean-proof"
    - "skill:lean-build"
  successors:
    - "skill:lean-bisect"
    - "skill:lean-pr"
metadata:
  version: "0.2.0"
  source_spec: "skills/_overrides/lean-mwe/SKILL.md"
  last_reviewed: "2026-05-27"
  migrated_from: "pre-v2 vendor mirror"
---

# lean-mwe

> Vendor-origin minimisation skill (mirrored from
> `vendor/leanprover-skills/skills/lean-mwe`); this override v2-wraps it
> so dispatch agents can route to it under the same contract as
> first-party skills.

## Routing

- **USE FOR:** wrapping a failing Lean fragment in a `#guard_msgs` / `#guard_panic` guard that captures the exact diagnostic, then driving `lake exe minimize` (or its Mathlib variant via `kim-em/mathlib-minimizer`) to delete imports + definitions until a self-contained reproducer remains; verifying the result with `lake env lean`; resuming interrupted minimisations with `--resume`.
- **DO NOT USE FOR:** bisecting which Lean commit broke the file (use `@lean-bisect` after the MWE is self-contained); building or running the live project (use `@lean-build`); rewriting the proof to *fix* the failure (use `@lean-proof`); filing the upstream report (use `@lean-pr` once MWE + optional bisect are in hand).
- **TRIGGERS:** MWE, minimal repro, "minimise the error", `#guard_msgs`, `#guard_panic`, `lake exe minimize`, upstream bug report.

## Workflow

1. **Set up the guard** — choose `#guard_msgs` (for errors / warnings) or `#guard_panic` (for panics). Paste the exact diagnostic text verbatim into the guard. Clone the right minimiser repo: `kim-em/mathlib-minimizer` for Mathlib-dependent bugs, `kim-em/lean-minimizer` for pure Lean 4 bugs.
2. **Verify the guard** — `lake env lean YourFile.lean` must produce no output (guard passes). If it errors, the guard text doesn't match; redesign before minimising. Always use `lake env lean`, never bare `lean`.
3. **Minimise** — `lake exe minimize YourFile.lean`. Use `--quiet` for long runs; `--resume` after Ctrl-C or manual edits to `.out.lean`; `--only-delete` / `--only-import-inlining` for surgical passes. Never `--no-import-inlining` — the point is a self-contained file.
4. **Review** — `lake env lean YourFile.out.lean` must compile to the expected error. Run the checklist: no Mathlib imports remain (ideal), exact `#guard_msgs` match, no stray `sorry` left over from debugging.

## Recovery & STOP

- Guard fails on first verify → STOP, the diagnostic text doesn't match the model's output character-for-character; widen the guard or fix the example before running the minimiser.
- Minimiser hangs > 60 min with `--resume` not progressing → STOP, hand to `@lean-bisect` if the failure may be version-dependent; otherwise reduce the input by hand.
- `.out.lean` still imports Mathlib after import inlining → STOP, the failure may depend on a Mathlib-internal definition that won't inline cleanly; either accept the partial repro or escalate to the Mathlib-side maintainer.
- Discovered the "bug" is intended behaviour during minimisation → STOP, write up the finding in `@lean-zettelkasten` and abandon the report.

## Handoffs

- **Predecessors / successors**: see FM `handoffs`. Typical inbound: `@lean-proof` (when a tactic fails unexpectedly) or `@lean-build` (when CI surfaces a build error worth filing). Typical outbound: `@lean-bisect` (find the introducing commit) or `@lean-pr` (file the issue/PR with the MWE attached).
- **Sister skill:** `@lean-bisect` — typically the next step after the MWE is Mathlib-free.
- **Source notes:** vendor mirror at `vendor/leanprover-skills/skills/lean-mwe/SKILL.md`.

---

# Minimizing Lean Errors

## Workflow

1. **Set up the guard** (`#guard_msgs` or `#guard_panic`)
2. **Run `lake exe minimize`**
3. **Review and polish** the output

## Repository Setup

For Mathlib-related bugs:
```bash
cd /tmp
git clone https://github.com/kim-em/mathlib-minimizer.git
cd mathlib-minimizer
lake exe cache get
```

For pure Lean 4 bugs:
```bash
cd /tmp
git clone https://github.com/kim-em/lean-minimizer.git
cd lean-minimizer
```

## Step 1: Create the Test File

### For Regular Errors

Use `#guard_msgs` to capture the exact error:

```lean
import Mathlib.SomeModule

/--
error: the exact error message
goes here verbatim
-/
#guard_msgs in
example : ... := by some_tactic
```

### For Panics

```lean
import Mathlib.SomeModule

#guard_msgs in
#guard_panic in
some_command_that_panics
```

## Step 2: Verify the Guard Works

```bash
lake env lean YourFile.lean
```

No output = success (guard passed). Error output = guard failed, and you need to redesign the test case.

Use `lake env lean`, not bare `lean`, so the reproduction uses the same
toolchain and package path as the project that exposed the bug.

## Step 3: Run the Minimizer

```bash
lake exe minimize YourFile.lean
```

Output is written to `YourFile.out.lean`.

### Useful Options

- `--resume`: Continue from the output file if interrupted
- `--quiet`: Suppress progress output
- `--only-delete`: Only run the deletion pass
- `--only-import-inlining`: Only inline imports

**Never use `--no-import-inlining`**. The entire point is to produce a self-contained file.

### For Long-Running Minimizations

Use `--resume` to continue from where you left off:

```bash
# Initial run (Ctrl-C if needed)
lake exe minimize YourFile.lean

# Resume later
lake exe minimize YourFile.lean --resume
```

After manually editing the `.out.lean` file, always use `--resume` to continue from the edited state.

## Step 4: Review the Output

```bash
lake env lean YourFile.out.lean
```

### Checklist Before Filing

- [ ] The `.out.lean` file compiles with the expected error/panic
- [ ] No Mathlib imports remain (ideal) or minimal imports remain
- [ ] The error message in `#guard_msgs` matches exactly
- [ ] Host-repository invariant: if the source repository forbids `sorry`, strip any `sorry` introduced during debugging before filing. Preserve the original tactic family in reproductions so the minimized failure remains faithful.

---

## See also

- [`../../../templates/Template_Foundation.md`](../../../templates/Template_Foundation.md) — Template: Minimal foundation module to start from
- [`../../../references/lean4-proof-strategy.md`](../../../references/lean4-proof-strategy.md) — Workflow: error priority, one-step-at-a-time
- [`../../../references/upstream/lean-bug-report-pipeline.md`](../../../references/upstream/lean-bug-report-pipeline.md) — Shared 5-stage bug-report pipeline (repro → guard → minimise → bisect → file) and `lean-mwe` ↔ `lean-bisect` hand-off contract
- [`../lean-bisect/SKILL.md`](../lean-bisect/SKILL.md) — Sister skill for commit-range narrowing
