---
name: "lean-mwe"
description: |
  USE FOR: creating minimal working examples (MWEs) from Lean 4 errors for upstream bug reports, capturing diagnostics with `#guard_msgs`, capturing panics with `#guard_panic`, LSP-guided incremental minimization, stripping unused imports via `moduleHierarchy/imports`, running `lake exe minimize`, verifying repros with `lake env lean`.
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
    - "skill:lean-proof"
metadata:
  version: "0.3.0"
  source_spec: "skills/lean-mwe/SKILL.md"
  last_reviewed: "2026-09-16"
  migrated_from: "repo-native first-party promotion"
---

# lean-mwe

> Agnostic Minimal Working Example (MWE) contract for Lean 4.
> Guides isolating tactic, elaborator, or compiler bugs into self-contained
> reproducers using `#guard_msgs`, `#guard_panic`, and LSP-guided dependency pruning.

## Routing

- **USE FOR:** wrapping a failing Lean fragment in a `#guard_msgs` / `#guard_panic` guard that captures the exact diagnostic, then driving `lake exe minimize` (or manual LSP-guided import pruning) to delete imports and definitions until a self-contained reproducer remains; verifying the result with `lake env lean`; resuming interrupted minimisations with `--resume`.
- **DO NOT USE FOR:** bisecting which Lean commit broke the file (use `@lean-bisect` after the MWE is self-contained); building or running the live project (use `@lean-build`); rewriting the proof to *fix* the failure (use `@lean-proof`); filing the upstream report (use `@lean-pr` once MWE + optional bisect are in hand).
- **TRIGGERS:** MWE, minimal repro, "minimise the error", `#guard_msgs`, `#guard_panic`, `lake exe minimize`, upstream bug report.

## Workflow

1. **Set up the guard** -- choose `#guard_msgs` (for errors / warnings) or `#guard_panic` (for panics). Paste the exact diagnostic text verbatim into the guard.
2. **Verify the guard** -- `lake env lean YourFile.lean` must produce no output (guard passes). If it errors, the guard text does not match; adjust the guard before minimising. Always use `lake env lean`, never bare `lean`.
3. **LSP-guided import pruning** -- before running heavy minimization, inspect the forward import tree via `$/lean/moduleHierarchy/imports`. Remove unused transitive imports to isolate the dependency closure.
4. **Minimise** -- `lake exe minimize YourFile.lean`. Use `--quiet` for long runs; `--resume` after manual edits to `.out.lean`; `--only-delete` / `--only-import-inlining` for surgical passes.
5. **Review** -- `lake env lean YourFile.out.lean` must compile cleanly to the expected error. Run the checklist:
   - No Mathlib imports remain (ideal for Lean core bugs).
   - Exact `#guard_msgs` match.
   - No stray `sorry` or `trace_state` left over from debugging.

## Recovery & STOP

- Guard fails on first verify -> STOP, the diagnostic text doesn't match the model's output character-for-character; widen the guard or fix the example before running the minimiser.
- Minimiser hangs > 60 min with `--resume` not progressing -> STOP, hand to `@lean-bisect` if the failure may be version-dependent; otherwise reduce the input by hand.
- `.out.lean` still imports Mathlib after import inlining -> STOP, the failure may depend on a Mathlib-internal definition that won't inline cleanly; either accept the partial repro or escalate to the Mathlib maintainers.
- Discovered the "bug" is intended behaviour during minimisation -> STOP, write up the finding in `@lean-zettelkasten` and abandon the report.

## Handoffs

- **Predecessors / successors**: see FM `handoffs`. Typical inbound: `@lean-proof` (when a tactic fails unexpectedly) or `@lean-build` (when CI surfaces an unexpected compiler error). Typical outbound: `@lean-bisect` (find the introducing commit) or `@lean-pr` (file the issue/PR with the MWE attached).
- **Sister skill:** `@lean-bisect` -- typically the next step after the MWE is Mathlib-free.

---

# Minimizing Lean Errors

## Workflow

1. **Set up the guard** (`#guard_msgs` or `#guard_panic`)
2. **Prune imports via module hierarchy**
3. **Run `lake exe minimize`**
4. **Review and polish** the output

## Repository Setup

For Mathlib-related bugs:
```bash
cd /tmp
git clone https://github.com/kim-em/mathlib-minimizer.git
cd mathlib-minimizer
lake exe cache get
```

---

## See also

- [`../../references/lean4-lsp-guide.md`](../../references/lean4-lsp-guide.md) -- Lean 4 Language Server Protocol comprehensive guide
- [`../../references/upstream/lean-bug-report-pipeline.md`](../../references/upstream/lean-bug-report-pipeline.md) -- Upstream bug report pipeline
- [`../lean-bisect/SKILL.md`](../lean-bisect/SKILL.md) -- Git bisect across toolchain commits
- [`../lean-pr/SKILL.md`](../lean-pr/SKILL.md) -- Pull request preparation workflow
- [`../lean-proof/SKILL.md`](../lean-proof/SKILL.md) -- Interactive proving contract
