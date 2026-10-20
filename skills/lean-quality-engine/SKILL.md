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

- **USE FOR:** running the seven-dimension quality lifecycle (Q1 soundness, Q2 faithfulness, Q3 completeness, Q4 novelty, Q5 elegance, Q6 integration, Q7
  documentation); computing the weighted `Q_score`; deciding go/no-go at a milestone.
- **DO NOT USE FOR:** running a single script (delegate to `@lean-enforcement`); reviewing one proof (delegate to `@lean-proof-review`); facilitating a
  council session (delegate to `@lean-review-council`).
- **TRIGGERS:** QA, quality gate, milestone check, project health, qa-engine, quality score, QA lifecycle.

## Behavioural rules (G-*)

- **G-1** (MUST): Q1 (soundness) and Q2 (faithfulness) MUST both pass before any other dimension is scored. [Trace: AC-01]
- **G-2** (MUST): A failed hard gate (Q1 or Q2) MUST halt the lifecycle and route to recovery, regardless of other dimension scores. [Trace: AC-02]
- **G-3** (MUST): Every dimension score MUST cite the underlying script or review record (no inferred scores). [Trace: AC-03]
- **G-4** (SHOULD): Soft gates (Q3, Q6, Q7) SHOULD report gaps but MAY proceed when the owner has accepted the risk in writing. [Trace: AC-04]
- **G-5** (MUST NOT): The engine MUST NOT re-implement checks owned by `@lean-enforcement`; it MUST call out to that skill. [Trace: AC-05]
- **G-6** (MUST): The weighted `Q_score` MUST be persisted to the repository's quality tracker with timestamp, commit, and per-dimension breakdown. [Trace:
  AC-06]
- **G-7** (SHOULD): When `Q_score` regresses ≥ 5 % vs prior milestone, the engine SHOULD escalate before proceeding. [Trace: AC-07]
- **G-8** (MUST): On any guard failure the skill MUST escalate per §Recovery & STOP. [Trace: AC-08]

## Workflow

1. **Discover** [discover] — read prior `Q_score`, list active milestone, locate latest enforcement / council / coverage artefacts.
2. **Run hard gates** [execute] — invoke `@lean-enforcement` for Q1 (axiom audit, sorry check, `lean_diagnostics` static abstract interpretation
   certificates: `NatSubTruncation`, `NatDivModByZero`, Zone DBM `decreasing_by` synthesis, Octagon conservation `±x_i ± x_j <= c`, Bourdoncle WTO loop
   widening, trace partitioning) and Q2 (faithfulness via doc-requirements traceability and `lean_counterexample_search` with Galois-guided hypothesis
   domain pruning `analyzeHeaderHypothesisDomains` / `pruneHeaderNatDomain`).
3. **Halt-check** [validate] — if Q1 or Q2 failed, STOP and route to recovery; do NOT proceed to soft gates.
4. **Run soft gates** [execute] — coverage (Q3), novelty (Q4), elegance (Q5 via `proof_quality.py`, `lean-rules` via `node
   tools/lean-lsp-mcp/bin/lean-rules.js`, and `pi-lens` via `pilens_ast_grep_search` / `pilens_diagnostics` as sub-second structural pre-checks before
   `lake build`), integration (Q6 via `bridge_validate.py` and `pi-harness-bridge` policy gates), documentation (Q7) via the appropriate scripts and
   council snapshots.
5. **Score** [validate] — compute weighted `Q_score`; compare to prior milestone; flag regressions ≥ 5 %.
6. **Persist** [persist] *(MANDATORY)* — write the `Q_score` breakdown to the project tracker, update milestone status, tick the QA checklist. Skipping
   Persist = incomplete.

## Recovery & STOP

- Q1 or Q2 fails → immediate STOP; escalate to human; do NOT compute `Q_score`.
- Enforcement script crashes ×3 in one lifecycle → STOP, file a bug against `@lean-enforcement`.
- `Q_score` regression ≥ 10 % vs prior milestone → STOP, ask before persisting.
- Confidence < 90 % on dimension weighting → STOP, ask.

## Handoffs

- **Predecessors / successors:** see FM `handoffs` (grammar from ADR-0080).
- **Source spec:** `specs/lean/quality-engine/requirements.md` — every G-rule traces to an AC there.
- **Related ADRs:** ADR-0076, ADR-0080.
- **Reference:** see [`REFERENCE.md`](./REFERENCE.md) for the seven-dimension matrix, weights, lifecycle phases, anti-patterns, and reliability-engineering
  details (original v1 content, preserved verbatim).

## Common failure modes

> AI agents commonly: score soft gates before hard gates pass; persist a `Q_score`
> that includes a failed hard gate; re-implement an enforcement check inline
> instead of calling `@lean-enforcement`; skip the regression delta against prior
> milestone. Full registry: GUARDRAILS.md §Agent failure taxonomy.
