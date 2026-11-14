---
name: "lean-corpus-audit"
description: |
  USE FOR: whole-corpus Lean 4 audits, 7-dimension QA scoring, milestone health, and retroactive onboarding.
  DO NOT USE FOR: single-file review (@lean-proof-review) or CI axiom gates (@lean-verification-gate).
  TRIGGERS: corpus audit, quality engine, deep audit, retroactive audit, QA gate, project health.
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
  - skill:lean-verification-gate
  - skill:lean-blueprint
  successors:
  - skill:lean-proof-refactor
  - skill:lean-tautology-triage
  - skill:lean-retro-methodology
metadata:
  version: 0.4.0
  source_spec: Unified from lean-quality-engine, lean-deep-audit, and lean-retroactive-audit
  last_reviewed: 2026-11
---

# Lean 4 Whole-Corpus Quality & Audit Engine

Assess an entire Lean 4 formalization across seven dimensions (soundness, faithfulness, non-vacuity, abstraction
hygiene, proof modularity, DAG health, and documentation parity), whether at milestone gates or when onboarding an
existing codebase.

## Routing
- **USE FOR:** multi-module quality sweeps, 7-dimension QA scorecards, wave-stratified corpus audits, and retroactive council onboarding.
- **DO NOT USE FOR:** reviewing a single theorem (`@lean-proof-review`) or running a 5-member council vote on one batch (`@lean-review-council`).

## Workflow
1. **Census & DAG Stratification** -- Run `lean_metrics(action: "census")` and `lean_module_hierarchy` to stratify
  modules from Layer 0 foundations up to top-level corollaries.
2. **Automated Defect Sweep** -- Scan for the 8 fidelity categories (`FIDELITY-01..08`, including `Nat` truncation,
  hypothesis echo, one-way Bool checkers, and over-concrete fixed-arity signatures) plus long-proof hotspots
  (`scripts/lean/proof_quality.py`).
3. **7-Dimension Scoring** -- Score soundness, statement faithfulness, completeness, non-vacuity, tactic
  modularity, kernel efficiency, and prose traceability with file-level citations.
4. **Remediation Dispatch** -- Route vacuous/truncated theorems to `@lean-tautology-triage`, long/repetitive proofs
  to `@lean-proof-refactor`, and systemic patterns to `@lean-retro-methodology`.

## Recovery & STOP
- Never batch-edit theorem statements during an audit; audits are read-only diagnostics that emit prioritized remediation backlogs.
- Re-run `lake build` before taking a final declaration census so mid-build `.olean` gaps do not undercount modules.

## Handoffs
- **Predecessors:** `lean-verification-gate`, `lean-blueprint`.
- **Successors:** `lean-proof-refactor`, `lean-tautology-triage`, `lean-retro-methodology`.

## Detailed reference
- **Layer-1 Fast Lookup Card (read first)**: [`references/cards/lean-corpus-audit-tables.md`](../../references/cards/lean-corpus-audit-tables.md)
- Full handbook: [`../../references/handbooks/lean-corpus-audit-handbook.md`](../../references/handbooks/lean-corpus-audit-handbook.md)

## See also
- [`../lean-review-council/SKILL.md`](../lean-review-council/SKILL.md) -- 5-member Review Council orchestration
- [`../lean-tautology-triage/SKILL.md`](../lean-tautology-triage/SKILL.md) -- Vacuity and tautology triage
