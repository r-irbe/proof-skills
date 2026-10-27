---
name: "lean-replay-verification"
description: |
  USE FOR: verifying that completed proofs are genuinely kernel-checked after `sorry` removal.
  DO NOT USE FOR: writing or fixing the proof itself (@lean-proof).
  TRIGGERS: sorry removed, proof completed, replay, fresh rebuild.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["skill:lean-proof", "skill:lean-proof-review"]
  successors: ["skill:lean-axiom-closure", "skill:lean-quality-engine"]
---

# Replay Verification After Sorry Removal
Operational dispatch contract for `@lean-replay-verification`.
## Routing
- **USE FOR:** tasks routed to `@lean-replay-verification`.
- **DO NOT USE FOR:** out-of-scope tasks (delegate via `@lean-gateway`).
## Workflow
1. Identify the proof-completion event (sorry removed / new theorem
   accepted as load-bearing).
2. Run R1 (cold full build); capture pin, job count, rc into the
   commit message or ledger.
3. Run R2 against the expected-axioms allowlist; quote the verdict.
4. Check R3 status: is a newer pin available? Run it via the
   project's migration flow or record the deferral.
5. For load-bearing batches, run R4 with trepplein or lean4lean and
   record checker + version + lineage caveat.
6. Link the replay evidence from the review record (commit, ledger,
   or review file) so a later reader can re-derive it.
## Recovery & STOP
- If R1 (`lake clean` + `lake build`) fails on a tree that passed incrementally, treat the proof as unverified
  and hand back to
  `@lean-proof` or
  `@lean-build` to fix the hidden stale-artifact dependency.
- If R2 surfaces `sorryAx` or an unexpected axiom in the closure, block acceptance and route to
  `@lean-axiom-closure` /
  `@lean-proof`.
## Handoffs
- **Predecessors:** `@lean-proof` (sorry removed), `@lean-proof-review` (single-proof review).
- **Successors:** `@lean-axiom-closure` (R2 compile-time lockdown), `@lean-quality-engine` (milestone QA
  gate).
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-replay-verification-handbook.md`](../../references/lean-replay-verification-handbook.md) .
## See also
- [`../../references/lean-replay-verification-handbook.md`](../../references/lean-replay-verification-handbook.md)
  -- Complete
  `lean-replay-verification` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
