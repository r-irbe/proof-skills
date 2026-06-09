---
name: "lean-tautology-triage"
description: |
  USE FOR: triaging Lean 4 theorem statements or proof sites that may be vacuous, tautological, smoke-test-only, reflexive-by-rfl, `: True` placeholders, bare `decide` closures, or automation-only proofs of supposedly substantive claims. Use this skill whenever proof review reports "vacuous", "tautology", "trivial", "placeholder", "smoke theorem", "rfl self-projection", "DEFINITE", or "HIGH" proof-quality risk.
  DO NOT USE FOR: ordinary proof writing (use @lean-proof); whole-project QA lifecycle (use @lean-quality-engine); running one enforcement script without interpretation (use @lean-enforcement); theorem search (use @lean-research).
  TRIGGERS: tautology, vacuous, trivial proof, smoke theorem, placeholder theorem, proof quality, `: True`, `by decide`, `by rfl`, rfl self-projection, suspicious automation, non-triviality audit.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ["skill:lean-proof-review", "skill:lean-quality-engine", "skill:lean-enforcement"]
  successors: ["skill:lean-proof-review", "skill:lean-research", "skill:lean-quality-engine"]
metadata:
  version: "0.1.0"
  source_spec: "meta-audit-9w/topical/skills-improvement/proof-quality-skill-spec.md"
  last_reviewed: "2026-06-09"
---

# lean-tautology-triage

This skill is a focused review mode for statements that elaborate but may not
prove the claim the name, surrounding text, or paper anchor suggests. It does
not declare a theorem bad merely because the proof is short; it classifies why a
short proof is acceptable or why it needs renaming, strengthening, quarantine, or
removal.

## Routing

- **USE FOR:** triaging Lean 4 theorem statements or proof sites that may be
  vacuous, tautological, smoke-test-only, reflexive-by-rfl, `: True`
  placeholders, bare `decide` closures, or automation-only proofs of supposedly
  substantive claims.
- **DO NOT USE FOR:** ordinary proof writing (use `@lean-proof`); whole-project
  QA lifecycle (use `@lean-quality-engine`); running one enforcement script
  without interpretation (use `@lean-enforcement`); theorem search (use
  `@lean-research`).
- **TRIGGERS:** tautology, vacuous, trivial proof, smoke theorem, placeholder
  theorem, proof quality, `: True`, `by decide`, `by rfl`, rfl self-projection,
  suspicious automation, non-triviality audit.

## Workflow

1. **Locate the claim** [discover] — capture theorem name, statement, proof body,
   surrounding docstring, imports, and downstream uses. A claim with downstream
   uses is not automatically substantive, but the use sites explain risk.
2. **Classify statement content** [validate] — use:
   - VALID-CONTENT: theorem states the intended mathematical/program property.
   - VALID-SMOKE: theorem intentionally checks elaboration or examples only.
   - VACUOUS: theorem is true because hypotheses are impossible or conclusion is
     `True`.
   - MISALIGNED: theorem is true but the name/docstring overclaims.
   - UNVERIFIED: statement may be content-bearing but lacks evidence.
   - SUSPECT-FALSE: likely mathematically false or contradicted by examples.
3. **Classify proof-quality risk** [validate] — use LOW, MEDIUM, HIGH, or
   DEFINITE. `: True` placeholders and named smoke tests with theorem-like names
   are usually DEFINITE; bare `decide` or `rfl` on substantive names is HIGH until
   statement review explains it.
4. **Run static support** [execute] — use
   `scripts/lean/proof_quality.py` for candidate discovery, then manually inspect
   each P1/P2 result. The script is a triage helper, not a final verdict.
5. **Choose remediation** [persist] — recommend one of: keep as smoke and rename,
   restate/strengthen, replace with a real theorem, quarantine as research-only,
   delete/retire, or ask HITL.

## Triage record

```markdown
## Tautology triage: <decl>

- Location:
- Statement summary:
- Proof shape:
- Downstream uses:
- Statement class:
- Proof-quality risk:
- Evidence:
- Recommended remediation:
- Confidence:
- HITL needed:
```

## Recovery & STOP

- STOP if the statement could be SUSPECT-FALSE or UNVERIFIED and confidence is
  below the repo belief floor; ask before recommending keep/delete.
- STOP before deleting or weakening a public theorem without an explicit edit
  claim and rollback path.
- STOP if static `proof_quality.py` output conflicts with manual inspection;
  cite both and ask which risk posture to use.
- STOP if a proof is short because of a verified definitional theorem in Mathlib;
  hand off to `@lean-research` before labeling it vacuous.

## Handoffs

- **Predecessors:** `@lean-proof-review` for proof-site review,
  `@lean-quality-engine` for project-level quality gates,
  `@lean-enforcement` for script execution.
- **Successors:** `@lean-proof-review` for final review, `@lean-research` for
  theorem/source lookup, `@lean-quality-engine` for gate rollups.
- **Script:** `scripts/lean/proof_quality.py` surfaces candidates; reviewers own
  final classification.
