---
name: "applied-intelligence-analysis"
description: |
  USE FOR: Intelligence analysis methodology — structured analytic techniques (SATs), evidence reasoning, hypothesis generation, cognitive bias mitigation, competitive intelligence, and their formalization. Use for analysis of competing hypotheses (ACH), link analysis, timeline reconstruction, source reliability assessment, and connections to the project's quality gates, provenance, and multi-agent trust.
  DO NOT USE FOR: formalising intelligence reasoning in Lean (use @lean-applied-reasoning); strategy analysis (use @applied-strategy-analysis); legal reasoning (use @applied-legal-reasoning).
  TRIGGERS: structured analytic techniques, SATs, evidence reasoning, hypothesis generation, cognitive bias, intelligence analysis, competing hypotheses.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-applied-reasoning', 'skill:applied-strategy-analysis', 'skill:lean-knowledge-formalization']
metadata:
  version: "0.2.0"
  source_spec: "skills/applied-intelligence-analysis/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# Intelligence Analysis

Structured analytic techniques and evidence-based reasoning frameworks for intelligence, investigative, and analytical contexts.

---

## Routing

- **USE FOR:** Intelligence analysis methodology — structured analytic techniques (SATs), evidence reasoning, hypothesis generation, cognitive bias mitigation, competitive intelligence, and their formalization. Use for analysis of competing hypotheses (ACH), link analysis, timeline reconstruction, source reliability assessment, and connections to the project's quality gates, provenance, and multi-agent trust.
- **DO NOT USE FOR:** formalising intelligence reasoning in Lean (use @lean-applied-reasoning); strategy analysis (use @applied-strategy-analysis); legal reasoning (use @applied-legal-reasoning).
- **TRIGGERS:** structured analytic techniques, SATs, evidence reasoning, hypothesis generation, cognitive bias, intelligence analysis, competing hypotheses.

## Workflow

1. Classify the analytic task: hypothesis generation, evidence aggregation, competing-hypothesis evaluation, or bias mitigation.
2. Pick the matching SAT (ACH, key-assumptions check, devil's advocacy, red-team) from the body.
3. Apply the SAT to the concrete intelligence question; produce the structured output (hypothesis matrix, assumption ledger).
4. Hand off: to `@lean-applied-reasoning` for Lean encoding, to `@applied-strategy-analysis` for downstream strategy work, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the question is purely about strategy creation — delegate to `@applied-strategy-analysis`.
- STOP if evidence is missing for hypothesis evaluation — escalate to `@research-council`.
- STOP if the legal/regulatory dimension dominates — delegate to `@applied-legal-reasoning`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-applied-reasoning`, `skill:applied-strategy-analysis`, `skill:lean-knowledge-formalization`.

---

## Detailed reference

Full content for `applied-intelligence-analysis` lives in
[`references/applied-intelligence-analysis-handbook.md`](../../references/applied-intelligence-analysis-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

| Section | Topic |
|---|---|
| Part 1 | Structured Analytic Techniques (SATs) |
| Part 2 | Analysis of Competing Hypotheses (ACH) |
| Part 3 | Evidence Reasoning |
| Part 4 | Cognitive Bias Mitigation |
| Part 5 | Link Analysis & Network Intelligence |
| Part 6 | Scenario Analysis & Forecasting |
| Part 7 | Source Handling & HUMINT Reasoning |
| Part 8 | Cross-References |

---

## See also

- [`../../references/applied-intelligence-analysis-handbook.md`](../../references/applied-intelligence-analysis-handbook.md) — Full handbook (extracted from this skill)
- [`../lean-applied-reasoning/SKILL.md`](../lean-applied-reasoning/SKILL.md) — Successor
- [`../applied-strategy-analysis/SKILL.md`](../applied-strategy-analysis/SKILL.md) — Successor
- [`../lean-knowledge-formalization/SKILL.md`](../lean-knowledge-formalization/SKILL.md) — Successor

