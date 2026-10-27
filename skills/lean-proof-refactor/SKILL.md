---
name: "lean-proof-refactor"
description: |
  USE FOR: slimming long proofs after they are proven (decomposition into reusable lemmas).
  DO NOT USE FOR: reviewing proofs for correctness (@lean-proof-review).
  TRIGGERS: long-proof, decompose proof, slim proof, helper-lemma extraction.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["skill:lean-proof", "skill:lean-quality-engine"]
  successors: ["skill:lean-proof-review", "skill:lean-proof"]
metadata:
  version: "0.1.0"
  source_spec: "campaign methodology distilled from a 13-decomposition series (2026-09/10)"
  last_reviewed: "2026-10"
---

# Lean Proof Refactoring (post-hoc proof slimming)
A proven proof that is long is a maintenance liability and a reuse
opportunity. This skill runs the campaign loop that turns long proofs
into short callers plus named, reusable lemmas - without regressions.
## Routing
- **USE FOR:** finding and adjudicating long-proof findings; extracting
  shared lemmas; running multi-batch refactor campaigns.
- **DO NOT USE FOR:** first-time proving, correctness review, tautology triage.
## Workflow
1. **Find** - scan the corpus for long proofs. A generic scanner exists:
   `scripts/lean/proof_quality.py --lean-dir <dir> --output <report.md>`
   (line count + branch points + style classes). Repos wrap it with
   their own config defaults; never edit the scanner per-repo.
2. **Adjudicate each finding** against one test: *can a generic block be
   named once and called elsewhere?* Three verdicts:
   - **CUT** - extract the shared lemma (see 3).
   - **CONSIDERED-NEGATIVE** - the proof is single-use glue; record the
     reason in the tracking doc. Forcing a cut creates single-use
     lemmas (the bundle effect: extraction that only relocates length).
   - **DEFER** - branchy or threshold-sitting proofs wait for a calmer
     window (2 branch points +  50 lines is the sweet spot).
## Recovery & STOP
- If a candidate helper extraction fails to compile or increases total proof complexity without reuse, revert
  the cut and record a
  `CONSIDERED-NEGATIVE`
  entry in the batch ledger.
- On transient stale-`.olean` errors in shared build directories, retry the targeted build once before
  diagnosing a proof
  regression.
## Handoffs
- **Predecessors:** `lean-proof` (the proof exists), `lean-quality-engine` (findings).
- **Successors:** `lean-proof-review` (audit the extraction), `lean-proof` (fix the caller).
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-proof-refactor-handbook.md`](../../references/lean-proof-refactor-handbook.md) .
## See also
- [`../../references/lean-proof-refactor-handbook.md`](../../references/lean-proof-refactor-handbook.md) --
  Complete
  `lean-proof-refactor` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
