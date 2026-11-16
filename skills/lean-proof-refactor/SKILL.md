---
name: "lean-proof-refactor"
description: |
  USE FOR: slimming long proofs, helper-lemma extraction, and Abstraction-Concrete Duality (@[csimp] bridges).
  DO NOT USE FOR: soundness review (@lean-proof-review) or SWAR tuning (@lean-sair-kernel-optimization).
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
  - skill:lean-sair-kernel-optimization
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
1. **Scan & Classify** -- Run `scripts/lean/proof_quality.py --lean-dir <dir>` for long/branchy proofs and `python3 -m altproof.coupling_scanner` to
   classify `Real` statements into `abstraction-safe`, `nat-mixed`, or `real-specific`.
2. **Kernel-Verified Auto-Slimmer (Single-Theorem Compression)** -- Before manual extraction, run the MCP tool `lean_autoslim` (`{"filePath": "<file.lean>", "apply": true, "allowAltProofImport": true}`) or CLI `python3 scripts/lean/altproof/cli.py autoslim <file.lean> --apply --allow-altproof-import`. It harvests exact `by ...` proof-span quickfixes from `lean-analyzer`, cascades each `ALTPROOF-ROUTE` tactic candidate against Lean 4 (`lean-lsp` live worker when warm, or batch `lake env lean` probe), and commits only strictly shorter, `0`-error/`0`-warning/`0`-`sorry` replacements.
3. **Adjudicate (`CUT / CONSIDERED-NEGATIVE / DEFER`)** -- Extract (`CUT`) only when a block is reusable (`>= 2` sites or clean mathematical boundary);
   log `CONSIDERED-NEGATIVE` on single-use glue to prevent negative bundle-effect bloat.
4. **Apply `WAVE-13 G1` Abstraction-Concrete Duality** -- Abstract in `Prop` (`[CommRing R] [LinearOrder R] [IsOrderedRing R]`, parametric step
   theorems) and stay concrete in hot `def`s (avoiding the `1,600x..3,345x` parametric WHNF penalty; `rfl`-bridged abstract proofs add `<= 1%` cost).
5. **Gate** -- Preserve public signatures byte-for-byte; verify `0` errors/warnings under `lake build` and record before/after metrics.

## Recovery & STOP
- If an extraction fails to compile, forces >8 awkward context parameters, or increases net complexity without reuse, revert immediately and record
  `CONSIDERED-NEGATIVE`.
- On transient stale-`.olean` errors in shared trees, retry targeted `lake build` once before diagnosing a regression.

## Handoffs
- **Predecessors:** `lean-proof`, `lean-corpus-audit`.
- **Successors:** `lean-sair-kernel-optimization`, `lean-proof-review`, `lean-proof`.

## Detailed reference
- Fast 3-table lookup card: [`../../references/cards/lean-proof-refactor-tables.md`](../../references/cards/lean-proof-refactor-tables.md)
- Full handbook: [`../../references/handbooks/lean-proof-refactor-handbook.md`](../../references/handbooks/lean-proof-refactor-handbook.md)
- Core templates: [`../../templates/core/Template_Refactoring.md`](../../templates/core/Template_Refactoring.md),
  [`../../templates/core/Template_ComputableTwin_Csimp.md`](../../templates/core/Template_ComputableTwin_Csimp.md)

## See also
- [`../lean-sair-kernel-optimization/SKILL.md`](../lean-sair-kernel-optimization/SKILL.md) -- Kernel WHNF, SWAR & hardware lowering
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
