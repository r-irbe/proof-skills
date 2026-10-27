---
name: "lean-quality-engine"
description: |
  USE FOR: assessing overall Lean 4 project quality across seven dimensions (soundness, faithfulness, completeness, novelty.
  DO NOT USE FOR: running a single enforcement script (@lean-enforcement).
  TRIGGERS: QA, quality gate, milestone check, project health, qa-engine.
tier: "hot"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-specification"]
  successors: ["skill:lean-enforcement", "skill:lean-review-council", "skill:lean-retro-methodology"]
metadata:
  version: "0.2.1"
  source_spec: "specs/lean/quality-engine/requirements.md"
  last_reviewed: "2026-10-20"
---

# lean-quality-engine
> ⚠️ **MANDATORY** (hot-tier): the soundness and faithfulness gates in
> §Behavioural rules are hard gates — a failure HALTS the QA lifecycle.
> Skipping Persist = incomplete.
## Routing
- **USE FOR:** running the seven-dimension quality lifecycle (Q1 soundness, Q2 faithfulness, Q3 completeness,
  Q4 novelty, Q5
  elegance, Q6
  integration, Q7
  documentation); computing the weighted `Q_score`; deciding go/no-go at a milestone.
- **DO NOT USE FOR:** running a single script (delegate to `@lean-enforcement`); reviewing one proof (delegate
  to
  `@lean-proof-review`);
  facilitating a
  council session (delegate to `@lean-review-council`).
- **TRIGGERS:** QA, quality gate, milestone check, project health, qa-engine, quality score, QA lifecycle.
## Workflow
1. **Discover** [discover] — read prior `Q_score`, list active milestone, locate latest enforcement / council
  / coverage
  artefacts.
2. **Run hard gates** [execute] — invoke `@lean-enforcement` for Q1 (axiom audit, sorry check,
  `lean_diagnostics` static abstract
   interpretation
   certificates: `NatSubTruncation`, `NatDivModByZero`, Zone DBM `decreasing_by` synthesis, Octagon
   conservation `±x_i ± x_j <=
   c`,
Bourdoncle WTO loop
   widening, trace partitioning) and Q2 (faithfulness via doc-requirements traceability and
   `lean_counterexample_search` with
   Galois-guided
hypothesis
   domain pruning `analyzeHeaderHypothesisDomains` / `pruneHeaderNatDomain`).
3. **Halt-check** [validate] — if Q1 or Q2 failed, STOP and route to recovery; do NOT proceed to soft gates.
## Recovery & STOP
- Q1 or Q2 fails → immediate STOP; escalate to human; do NOT compute `Q_score`.
- Enforcement script crashes ×3 in one lifecycle → STOP, file a bug against `@lean-enforcement`.
- `Q_score` regression ≥ 10 % vs prior milestone → STOP, ask before persisting.
- Confidence < 90 % on dimension weighting → STOP, ask.
## Handoffs
- **Predecessors / successors:** see FM `handoffs` (grammar from ADR-0080).
- **Source spec:** `specs/lean/quality-engine/requirements.md` — every G-rule traces to an AC there.
- **Related ADRs:** ADR-0076, ADR-0080.
- **Reference:** see
  [`references/lean-quality-engine-handbook.md`](../../references/lean-quality-engine-handbook.md) for the
  seven-dimension matrix, weights, lifecycle phases, anti-patterns, and reliability-engineering
  details (original v1 content, preserved verbatim).
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-quality-engine-handbook.md`](../../references/lean-quality-engine-handbook.md) .
## See also
- [`../../references/lean-quality-engine-handbook.md`](../../references/lean-quality-engine-handbook.md) --
  Complete
  `lean-quality-engine` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
