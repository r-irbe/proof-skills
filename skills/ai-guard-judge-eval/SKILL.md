---
name: "ai-guard-judge-eval"
id: ai-guard-judge-eval
title: "Evaluating guard-style LLM judges: bands, adapters, distributions"
description: |
  USE FOR: benchmarking LLM judges used as safety guards or escalation adjudicators: building a stratified band set from real.
  DO NOT USE FOR: continuous-score quality rating or preference ranking of chat models.
  TRIGGERS: LLM judge, safety guard eval, escalation adjudicator.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["skill:applied-data-information-security", "skill:lean-ai-formalization"]
  successors: ["skill:lean-ai-formalization", "skill:applied-engineering-disciplines"]
---

# ai-guard-judge-eval
Operational dispatch contract for `@ai-guard-judge-eval`.
## Routing
- **USE FOR:** tasks routed to `@ai-guard-judge-eval`.
- **DO NOT USE FOR:** out-of-scope tasks (delegate via `@lean-gateway`).
## Workflow
1. Extract the real command/decision corpus; dedup by exact text.
2. Run the deterministic gate + active profile over it; bucket by
   effective verdict; sample caps per class token for W.
3. Write synthetic probes covering each dangerous-verb family the
   gate defends (reverse shells, encoded pipes, credential exfil,
   persistence, destruction).
4. Emit the set with seed + label provenance in metadata; commit it.
5. Per judge: schema adapter + prompt style; smoke on 3 unsafe items
   (verify parseability) before any full run.
6. Full band runs; aggregate per band; record the table.
7. For rubric changes: gen N+1 runs full set x repeat 3; adopt only if
   target band improves AND benign specificity holds within one flip;
   register the distribution deltas and any negative results.
## Recovery & STOP
- If a judge emits unparseable output during the 3-item smoke check, stop the full run and fix the per-judge
  schema adapter or
  disable
  thinking-channel
  capture before spending full-set compute.
- If E-band disagreements trace to deterministic gate regex false positives, record them as label noise and
  fix the gate pattern
  separately
  rather than
  tuning the judge rubric to mimic gate bugs.
## Handoffs
- **Predecessors:** `@applied-data-information-security` (policy threat model), `@lean-ai-formalization`
  (assurance requirements).
- **Successors:** `@lean-ai-formalization` (certification evidence), `@applied-engineering-disciplines`
  (reliability & testing
  integration).
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/ai-guard-judge-eval-handbook.md`](../../references/ai-guard-judge-eval-handbook.md) .
## See also
- [`../../references/ai-guard-judge-eval-handbook.md`](../../references/ai-guard-judge-eval-handbook.md) --
  Complete
  `ai-guard-judge-eval` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
