---
name: "lean-proof-review"
description: |
  USE FOR: reviewing one Lean 4 proof / file for correctness, soundness, statement faithfulness, non-triviality.
  DO NOT USE FOR: writing a new proof (@lean-proof).
  TRIGGERS: proof review, audit proof, verify Lean, 4-layer checklist.
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
  - agent:gateway
  - skill:lean-proof
  successors:
  - skill:lean-review-council
  - skill:lean-verification-gate
  - skill:lean-doc-sync
metadata:
  version: 0.5.0
  source_spec: specs/lean/proof-review/requirements.md
  last_reviewed: '2026-10-20'
---

# lean-proof-review
> **MANDATORY** (hot-tier): layers L1 (soundness) and L2 (statement) are
> hard gates -- a failure at either MUST block sign-off, regardless of L3/L4.
> Skipping Persist = incomplete.
## Routing
- **USE FOR:** auditing a Lean 4 proof or file across the 4-layer checklist (L1 soundness, L2 statement &
  terminology faithfulness, L3 non-triviality, L4 quality) and spotting vacuous truth, unused hypotheses, facade
  stubs, or scope drift.
- **DO NOT USE FOR:** authoring proofs (`@lean-proof`), multi-agent councils (`@lean-review-council`), or CI gates
  (`@lean-verification-gate`).
- **TRIGGERS:** proof review, audit proof, verify Lean, 4-layer checklist, lean-pitfalls, proof quality.
## Workflow
1. **Discover** [discover] -- read the target file, locate theorem(s), source spec / paper claim, and concordance.
2. **L1 soundness** [validate] -- confirm `0 sorry`, `0 admit`, `0 sorryAx`, `0` `@[deprecated]` shims, and `0`
  unauthorized `Lean.ofReduceBool` via `lean_axiom_closure` and `lean_diagnostics`; verify exact axioms (`omega` /
  `decide` often pull `propext` or `Quot.sound`, so never certify `(0 axioms)` unchecked).
3. **L2 statement & terminology faithfulness** [validate] -- check quantifier order, positivity/non-emptiness,
  `Nat` truncation, two-sided `Bool = true <-> Prop` reflection, absence of facade stubs or existence-as-input
  shortcuts, and primary-literature terminology/provenance accuracy.
4. **L3 non-triviality & L4 hygiene** [validate] -- confirm non-vacuity witnesses (`@lean-tautology-triage`),
  explicit non-terminal `simp only [...]`, and clean docstrings with zero dangling references.
## Recovery & STOP
- L1 fails (`sorry` / `admit` / `sorryAx`) -> STOP, do NOT proceed to L2-L4; escalate to author.
- L2 fails (statement or terminology drift) -> STOP, escalate to spec owner before proof judgement.
- `lake build` red on containing file -> STOP, ask author to fix build first.
- Confidence < 90 % on a tactic suggestion -> mark as advisory, do NOT block.
- Scope drift (edits to non-proof files) -> immediate STOP, re-anchor.
## Handoffs
- **Predecessors / successors:** see FM `handoffs`.
- **Source spec:** `specs/lean/proof-review/requirements.md` -- every G-rule traces to an AC there.
## Detailed reference
- **Layer-1 Card**: [`references/cards/lean-proof-review-tables.md`](../../references/cards/lean-proof-review-tables.md)
- **Handbook**: [`references/handbooks/lean-proof-review-handbook.md`](../../references/handbooks/lean-proof-review-handbook.md)
## See also
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
- [`tests/route-independence.yaml`](tests/route-independence.yaml) -- Smoke test
- [`tests/search-review.yaml`](tests/search-review.yaml) -- Smoke test
