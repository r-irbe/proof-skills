---
name: "lean-proof-repair"
description: |
  USE FOR: repairing broken Lean 4 proofs after toolchain upgrades, Mathlib bumps, or simp drift.
  DO NOT USE FOR: writing new proofs (@lean-proof) or bisecting commits (@lean-bisect).
  TRIGGERS: proof repair, broken proof, toolchain upgrade, Mathlib bump, simp drift.
tier: "hot"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["skill:lean-gateway", "skill:lean-build", "skill:lean-bisect", "skill:lean-proof"]
  successors: ["skill:lean-proof-review", "skill:lean-replay-verification", "skill:lean-enforcement"]
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-proof-repair/SKILL.md (this file)"
  last_reviewed: "2026-10-27"
---

# Lean 4 Automated & Interactive Proof Repair
Diagnose and repair broken Lean 4 tactic scripts caused by toolchain bumps, Mathlib API renames, `simp`
normal-form drift, or
upstream
definition changes without weakening theorem statements.
## Routing
- **USE FOR:** fixing broken proofs after `lean-toolchain` or `lake-manifest.json` updates, replacing renamed
  Mathlib lemmas,
  stabilizing
  broken `simp` calls into `simp only [...]`, and recovering from `omega`/`ring`/`aesop` regressions.
- **DO NOT USE FOR:** authoring new proofs from scratch (delegate to `@lean-proof`); bisecting toolchain
  commits (delegate to
  `@lean-bisect`); refactoring already-green proofs (delegate to `@lean-proof-refactor`).
- **TRIGGERS:** proof repair, broken proof, toolchain upgrade, Mathlib bump, unknown identifier in proof,
  `simp made no progress`,
  `unsolved
  goals` after bump.
## Workflow
1. **Snapshot Diagnostics via LSP (`lean_diagnostics`)**: Call `lean_diagnostics` on the broken file to
  collect exact line/column
  error
   spans and classify each failure (`UnknownIdentifier`, `TypeMismatch`, `UnsolvedGoals`, `SimpNoProgress`,
   `HeartbeatTimeout`).
2. **Inspect Pre/Post Goal State (`lean_goal`)**: Call `lean_goal` at the failing tactic line with `target:
  "tactic"` and `target:
   "altproof"` to compare the live goal against the expected intermediate state.
3. **Apply Targeted Repair Pattern**:
   - *Renamed / moved lemma*: query `lean_search(source: "code" | "loogle")` for the type shape and substitute
  the new identifier.
## Recovery & STOP
- **STOP** if repairing the proof appears to require weakening the theorem statement or adding a new
  hypothesis; escalate to
  `@lean-specification` (`specifier` role).
- **STOP** after 3 failed repair attempts on the same goal and run `lean_counterexample_search(strategy:
  "dense")` to check
  whether an
  upstream definition change invalidated the theorem statement.
## Handoffs
- **Predecessors:** `skill:lean-gateway`, `skill:lean-build` (surfaces broken build targets),
  `skill:lean-bisect` (identifies
  breaking
  commit), `skill:lean-proof`.
- **Successors:** `skill:lean-proof-review` (4-layer soundness audit), `skill:lean-replay-verification` (fresh
  kernel replay),
  `skill:lean-enforcement`.
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-proof-repair-handbook.md`](../../references/lean-proof-repair-handbook.md) .
## See also
- [`../../references/lean-proof-repair-handbook.md`](../../references/lean-proof-repair-handbook.md) --
  Complete
  `lean-proof-repair` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
