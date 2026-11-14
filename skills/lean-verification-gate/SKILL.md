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
  - skill:lean-sair-kernel-optimization
  - skill:lean-proof-repair
  successors:
  - skill:lean-proof-review
  - skill:lean-review-council
  - skill:lean-doc-sync
metadata:
  version: 0.4.0
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
1. **Static & Hygiene Gate** -- Run `lean_diagnostics` and enforcement scripts to verify `0 sorry`, `0 admit`,
  `set_option autoImplicit false`, and `0` forbidden metaprograms (`native_decide` / `Lean.ofReduceBool` unless
  explicitly whitelisted).
2. **Transitive Axiom Closure** -- Invoke `lean_axiom_closure` across all exported declarations and verify every
  transitive closure is a subset of `[propext, Classical.choice, Quot.sound]`.
3. **Kernel Replay Verification** -- After `sorry` removal or toolchain bumps, run targeted/cold `lake build`
  replay so cached `.olean` artifacts cannot mask unchecked terms.
4. **Emit Gate Certificate** -- Record the exact module manifest count and axiom set before handing off to `@lean-proof-review` or `@lean-review-council`.

## Recovery & STOP
- Any custom `axiom`, `sorryAx`, or unapproved `Lean.ofReduceBool` / `Lean.trustCompiler` dependency is a hard
  blocker; return immediately to `@lean-proof` or `@lean-sair-kernel-optimization`.
- Always quote the scanned declaration/module count (never treat an empty scan manifest as a pass).

## Handoffs
- **Predecessors:** `lean-proof`, `lean-sair-kernel-optimization`, `lean-proof-repair`.
- **Successors:** `lean-proof-review`, `lean-review-council`, `lean-doc-sync`.

## Detailed reference
- Fast 3-table lookup card: [`../../references/cards/lean-verification-gate-tables.md`](../../references/cards/lean-verification-gate-tables.md)
- Full handbook: [`../../references/handbooks/lean-verification-gate-handbook.md`](../../references/handbooks/lean-verification-gate-handbook.md)
- Verification template: [`../../templates/core/Template_Verification.md`](../../templates/core/Template_Verification.md)

## See also
- [`../lean-proof-review/SKILL.md`](../lean-proof-review/SKILL.md) -- 4-layer semantic proof review
- [`../lean-corpus-audit/SKILL.md`](../lean-corpus-audit/SKILL.md) -- Whole-corpus 7-dimension audit
