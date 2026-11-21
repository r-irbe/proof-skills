---
name: "lean-verification-gate"
description: |
  USE FOR: deterministic Lean 4 CI gates: axiom-closure lockdown, cold kernel replay, and pre-review checks.
  DO NOT USE FOR: semantic proof review (@lean-proof-review) or council voting (@lean-review-council).
  TRIGGERS: verification gate, enforcement, axiom closure, print axioms, replay verification, CI gate.
tier: hot
runtime_targets:
- copilot-cli
- claude-code
- antigravity
- pi
- cursor
- gemini-cli
dispatch_targets: []
handoffs:
  predecessors:
  - skill:lean-proof
  - skill:lean-kernel-optimization
  - skill:lean-proof-repair
  successors:
  - skill:lean-proof-review
  - skill:lean-review-council
  - skill:lean-doc-sync
metadata:
  version: 0.5.0
  source_spec: Unified from lean-enforcement, lean-axiom-closure, and lean-replay-verification
  last_reviewed: 2026-11
---

# Lean 4 Deterministic Verification Gate (Enforcement, Axiom Closure & Replay)

Execute all deterministic, machine-verifiable trust gates over a Lean 4 build before semantic human/council review.

## Routing
- **USE FOR:** project-wide `#print axioms` lockdown (`[propext, Classical.choice, Quot.sound]`), cold kernel
  replay (`lake build` / `lean4checker`), zero-`sorry` / `autoImplicit false` linting, and pre-council CI checks.
- **DO NOT USE FOR:** single-file mathematical faithfulness review (`@lean-proof-review`) or whole-corpus quality scoring (`@lean-corpus-audit`).

## Workflow
1. **Static, Deprecation & Hygiene Gate** -- Run `lean_diagnostics`, `lean-rules`, and `paper_supplement_audit.py`
  to verify `0 sorry`, `0 admit`, `0 @[deprecated]` shims in `.lean` source, `set_option autoImplicit false`,
  scoped `INV-001` Unicode, and `0` forbidden `native_decide` (`Lean.ofReduceBool`).
2. **Fresh Manifest & Transitive Axiom Closure** -- Regenerate `#print axioms` probe scripts after any rename
  (`axiom_audit.py --generate-script`), invoke `lean_axiom_closure`, and verify closures stay within
  `[propext, Classical.choice, Quot.sound]`.
3. **Cold In-Process Kernel Replay** -- Run `scripts/lean/replay_verify.sh` / `cold_kernel_replay.lean`
  (`Lean.Kernel.Environment.replay` + `Lean.collectAxioms` across 100% of `.olean` constants on top of external
  imports alone) with `0` compiler warnings.
4. **Emit Honest Gate Certificate** -- Quote exact scanned module/constant counts, any coverage-gap notes, and only
  verification tools physically executed on this host before handing off to `@lean-review-council` or `@lean-doc-sync`.

## Recovery & STOP
- Any custom `axiom`, `sorryAx`, `@[deprecated]` shim, or unapproved `Lean.ofReduceBool` / `Lean.trustCompiler`
  dependency is a hard blocker; return immediately to `@lean-proof` or `@lean-kernel-optimization`.
- Always quote scanned declaration/module counts; never treat a stale manifest or unexecuted binary as a pass.

## Handoffs
- **Predecessors:** `lean-proof`, `lean-kernel-optimization`, `lean-proof-repair`.
- **Successors:** `lean-proof-review`, `lean-review-council`, `lean-doc-sync`.

## Detailed reference
- **Layer-1 Card**: [`../../references/cards/lean-verification-gate-tables.md`](../../references/cards/lean-verification-gate-tables.md)
- **Handbook**: [`../../references/handbooks/lean-verification-gate-handbook.md`](../../references/handbooks/lean-verification-gate-handbook.md)
- **Supplement Protocol**:
  [`../../references/protocols/double-blind-paper-and-supplement-release.md`](../../references/protocols/double-blind-paper-and-supplement-release.md)
- **Template**: [`../../templates/core/Template_Verification.md`](../../templates/core/Template_Verification.md)

## See also
- [`../lean-proof-review/SKILL.md`](../lean-proof-review/SKILL.md) -- 4-layer semantic proof review
- [`../lean-corpus-audit/SKILL.md`](../lean-corpus-audit/SKILL.md) -- Whole-corpus 7-dimension audit
