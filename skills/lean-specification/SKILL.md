---
name: "lean-specification"
description: |
  USE FOR: Design theorem specifications for Lean 4 proofs.
  DO NOT USE FOR: actual proof writing (@lean-proof).
  TRIGGERS: specification, theorem spec, three-part spec, lemma plan.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-proof', 'skill:lean-proof-review', 'skill:lean-zettelkasten']
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-specification/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# Lean 4 Theorem Specification

Structured process for specifying theorems before implementation. Every theorem passes through Specify → Design → Implement → Review → Merge, with each
stage tracked by document templates.

---

## Routing

- **USE FOR:** Design theorem specifications for Lean 4 proofs. Use when planning new theorems, lemmas, definitions, or tactics. Covers the three-part
  specification (requirements, design, documentation), lifecycle management, dependency analysis, and integration with the review council.
- **DO NOT USE FOR:** actual proof writing (use @lean-proof); requirement extraction (use @lean-doc-requirements); review (use @lean-proof-review).
- **TRIGGERS:** specification, theorem spec, three-part spec, lemma plan, tactic plan.

## Workflow

1. Identify the artifact: new theorem, new lemma, new definition, or new tactic.
2. Apply the three-part specification template from the body (signature, intent, traceability); verify Mathlib primitives exist at the pin.
3. Run mandatory specification fidelity checks before approving:
   - **Check 5 (Necessity & Sufficiency `↔` Pairing):** Every executable `Bool` checker `f ... : Bool` or decidable predicate MUST specify both soundness and completeness (`f x = true ↔ Spec x`), never a one-way `f x = true -> ...` implication alone (`ONE_WAY_BOOL_CHECKER`).
   - **Check 6 (Precondition Tightness & Boundary Counterexample Witness):** Every `Nat` subtraction `a - b` MUST carry an explicit ordering guard `b ≤ a` (`NAT_SUB_UNGUARDED`), every hypothesis/value binder MUST be consumed (`UNUSED_VALUE_OR_UNDERSCORE_BINDER`), conclusions MUST NOT echo hypotheses (`HYPOTHESIS_ECHO`), reduce to reflexive `lhs = lhs` (`REFLEXIVE_TAUTOLOGY`), or assert trivial `Nat` non-negativity `0 ≤ e` (`NAT_NONNEG_TRIVIALITY`), and boundary tightness SHOULD be witnessed by a counterexample when a hypothesis is dropped.
   - **Check 7 (100% Barrel Completeness & `Classical.choice`-Free Constructive Gate):** Every module MUST be imported in the package root barrel (`Rules.lean` / `Project.lean`), and first-order `Nat`/`Int`/`Bool`/`BitVec` specifications MUST stay `Classical.choice`-free (`Bool.and_eq_true` / `decide_eq_true_eq` / `bv_decide` instead of `split` on `&&`).
4. Run automated fidelity scanners (`python3 scripts/lean/proof_quality.py`, `python3 scripts/lean/tautology_scan.py`, `lean-analyzer`, and `lean_metrics` in `lean-lsp-mcp`) and hand off: to `@lean-proof` for the proof, to `@lean-proof-review` once proven, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the artifact is informal — extract requirements via `@lean-doc-requirements` first.
- STOP if the spec depends on Mathlib primitives missing at the pin — escalate to `@lean-research`.
- STOP if reviewer would reject on grounds the body covers (vacuous truth, missing hypothesis) — fix before publishing.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-proof`, `skill:lean-proof-review`, `skill:lean-zettelkasten`.

---

## Detailed reference

Full content for `lean-specification` lives in
[`references/lean-specification-handbook.md`](../../references/lean-specification-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

_(See handbook for full content.)_

---

## See also

- [`../../references/lean-specification-handbook.md`](../../references/lean-specification-handbook.md) — Full handbook (extracted from this skill)
- [`../lean-proof/SKILL.md`](../lean-proof/SKILL.md) — Successor
- [`../lean-proof-review/SKILL.md`](../lean-proof-review/SKILL.md) — Successor
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor
