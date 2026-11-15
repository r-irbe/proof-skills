---
name: "lean-tautology-triage"
description: |
  USE FOR: triaging Lean 4 theorem statements or proof sites that may be vacuous, tautological, smoke-test-only.
  DO NOT USE FOR: ordinary proof writing (@lean-proof).
  TRIGGERS: tautology, vacuous, trivial proof, smoke theorem.
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
  - skill:lean-proof-review
  - skill:lean-corpus-audit
  - skill:lean-verification-gate
  successors:
  - skill:lean-proof-review
  - skill:lean-research
  - skill:lean-corpus-audit
metadata:
  version: 0.5.0
  source_spec: meta-audit-9w/topical/skills-improvement/proof-quality-skill-spec.md
  last_reviewed: '2026-06-09'
---

# lean-tautology-triage
This skill is a focused review mode for statements that elaborate but may not
## Routing
- **USE FOR:** triaging Lean 4 theorem statements or proof sites that may be
  vacuous, tautological, smoke-test-only, reflexive-by-rfl, `: True`
  placeholders, bare `decide` closures, or automation-only proofs of supposedly
  substantive claims.
- **DO NOT USE FOR:** ordinary proof writing (use `@lean-proof`); whole-project
  QA lifecycle (use `@lean-corpus-audit`); running one enforcement script
  without interpretation (use `@lean-verification-gate`); theorem search (use
  `@lean-research`).
- **TRIGGERS:** tautology, vacuous, trivial proof, smoke theorem, placeholder
## Workflow
1. **Locate the claim** [discover] -- capture theorem name, statement, proof body,
   surrounding docstring, imports, and downstream uses (via `lean_navigate` `{"operation": "references", ...}` or
   `lean_decl_references` with `{"symbol": "...",
   "direction":
   "usedBy"}`). A claim
with downstream
   uses is not automatically substantive, but the use sites explain risk.
2. **Classify statement content** [validate] -- use:
   - VALID-CONTENT: theorem states the intended mathematical/program property.
   - VALID-SMOKE: theorem intentionally checks elaboration or examples only.
   - VACUOUS: theorem is true because hypotheses are impossible or conclusion is
     `True`.
   - MISALIGNED: theorem is true but the name/docstring overclaims.
   - UNVERIFIED: statement may be content-bearing but lacks evidence.
## Recovery & STOP
- STOP if the statement could be SUSPECT-FALSE or UNVERIFIED and confidence is
  below the repo belief floor; ask before recommending keep/delete.
- STOP before deleting or weakening a public theorem without an explicit edit
  claim and rollback path.
- STOP if static `proof_quality.py` output conflicts with manual inspection;
  cite both and ask which risk posture to use.
- STOP if a proof is short because of a verified definitional theorem in Mathlib;
## Handoffs
- **Predecessors:** `@lean-proof-review` for proof-site review,
  `@lean-corpus-audit` for project-level quality gates,
  `@lean-verification-gate` for script execution.
- **Successors:** `@lean-proof-review` for final review, `@lean-research` for
  theorem/source lookup, `@lean-corpus-audit` for gate rollups.
- **Script:** `scripts/lean/proof_quality.py` surfaces candidates; reviewers own
  final classification.
## Detailed reference
- **Layer-1 Fast Lookup Card (read first)**: [`references/cards/lean-tautology-triage-tables.md`](../../references/cards/lean-tautology-triage-tables.md)
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/handbooks/lean-tautology-triage-handbook.md`](../../references/handbooks/lean-tautology-triage-handbook.md) .
## See also
- [`../../references/handbooks/lean-tautology-triage-handbook.md`](../../references/handbooks/lean-tautology-triage-handbook.md)
  -- Complete
  `lean-tautology-triage` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
