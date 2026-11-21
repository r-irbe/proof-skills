---
name: "lean-proof-refactor"
description: |
  USE FOR: slimming long proofs, helper-lemma extraction, and Abstraction-Concrete Duality (@[csimp] bridges).
  DO NOT USE FOR: soundness review (@lean-proof-review) or SWAR tuning (@lean-kernel-optimization).
  TRIGGERS: long-proof, decompose proof, slim proof, abstraction-concrete, helper-lemma extraction.
tier: warm
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
  - skill:lean-corpus-audit
  successors:
  - skill:lean-kernel-optimization
  - skill:lean-proof-review
  - skill:lean-proof
metadata:
  version: 0.5.0
  source_spec: campaign methodology + WAVE-13 G1 Abstraction-Concrete Duality & coupling_scanner
  last_reviewed: '2026-11'
---

# Lean Proof Refactoring & Abstraction-Concrete Duality

Turn long, concrete, or duplicated proofs into short callers backed by reusable abstract lemmas -- while keeping executable `def` kernels strictly
concrete (`WAVE-13 G1`).

## Routing
- **USE FOR:** adjudicating long-proof findings (`CUT / CONSIDERED-NEGATIVE / DEFER`), extracting shared lemmas, generalizing `abstraction-safe` `Real`
  statements to ordered-ring mixins, and bridging abstract `Prop` specs to concrete `def`s via `rfl` / `@[csimp]`.
- **DO NOT USE FOR:** first-time proving (`@lean-proof`), correctness review (`@lean-proof-review`), or tautology triage (`@lean-tautology-triage`).

## Workflow
1. **Scan & Classify** -- Run `scripts/lean/proof_quality.py --lean-dir <dir>` for long/branchy proofs and
   `python3 -m altproof.coupling_scanner` to classify `Real` statements (`abstraction-safe`, `nat-mixed`,
   `real-specific`).
2. **Auto-Slim & Harvest Closers** -- Run `lean_autoslim`
   (`{"filePath": "<file.lean>", "apply": true, "allowAltProofImport": true}`) or
   `python3 scripts/lean/altproof/cli.py autoslim <file.lean> --apply --allow-altproof-import` to apply strictly
   shorter, 0-error/0-warning/0-`sorry` `ALTPROOF-ROUTE` quickfixes; harvest recurring patterns into
   `packages/altproof/` (`AltProof.Closers` + `elegance?`, `GT-68`).
3. **Adjudicate & Clean Renames** -- Extract (`CUT`) only when reusable (`>= 2` sites); log `CONSIDERED-NEGATIVE`
   on single-use glue. Delete `@[deprecated]` shims from `.lean` files and log renames in a Markdown ledger (`GT-66`).
4. **Apply `WAVE-13 G1` Duality** -- Abstract in `Prop` (`[CommRing R] [LinearOrder R] [IsOrderedRing R]`) and stay
   concrete in hot `def`s (avoiding `1,600x..3,345x` parametric WHNF penalties; `rfl` bridges add `<= 1%` cost).
5. **Gate & Slice** -- Verify `0` errors/warnings under `lake build`, regenerate `#print axioms` manifests after
   renames, and use `altproof tree-shake` for standalone supplements.

## Recovery & STOP
- If an extraction fails to compile, forces >8 awkward context parameters, or increases net complexity without reuse, revert immediately and record
  `CONSIDERED-NEGATIVE`.
- On transient stale-`.olean` errors in shared trees, retry targeted `lake build` once before diagnosing a regression.

## Handoffs
- **Predecessors:** `lean-proof`, `lean-corpus-audit`.
- **Successors:** `lean-kernel-optimization`, `lean-proof-review`, `lean-proof`.

## Detailed reference
- Fast 3-table lookup card: [`../../references/cards/lean-proof-refactor-tables.md`](../../references/cards/lean-proof-refactor-tables.md)
- Full handbook: [`../../references/handbooks/lean-proof-refactor-handbook.md`](../../references/handbooks/lean-proof-refactor-handbook.md)
- Core templates: [`../../templates/core/Template_Refactoring.md`](../../templates/core/Template_Refactoring.md),
  [`../../templates/core/Template_ComputableTwin_Csimp.md`](../../templates/core/Template_ComputableTwin_Csimp.md)

## See also
- [`../lean-kernel-optimization/SKILL.md`](../lean-kernel-optimization/SKILL.md) -- Kernel WHNF, SWAR & hardware lowering
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
