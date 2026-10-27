---
name: "lean-competitive-math"
description: |
  USE FOR: formalizing a Project-Euler / competition-math problem as a Lean 4 theorem that asserts a concrete numeric answer.
  DO NOT USE FOR: writing the theorem statement in isolation (@lean-specification).
  TRIGGERS: Project Euler, competition math, euler-prover.
tier: "hot"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["skill:lean-gateway", "skill:lean-specification", "skill:lean-research"]
  successors: ["skill:lean-proof", "skill:lean-proof-review", "skill:lean-quality-engine"]
metadata:
  version: "0.1.0"
  source_spec: "skills/lean-competitive-math/SKILL.md (this file)"
  last_reviewed: "2026-07-05"
---

# lean-competitive-math (euler-prover)
> **MANDATORY** (hot-tier): the answer-check gate (G-2), the axiom audit (G-4),
## Routing
- **USE FOR:** formalizing a Project-Euler / competition-math problem as a Lean 4
  theorem asserting a concrete numeric answer; getting a first green proof
  (typically Bronze `native_decide`); verifying the answer computes (`#eval` +
  the theorem closes); auditing the compiler-trust axiom via `#print axioms`;
  and driving the improvement pass up the ladder Bronze (`native_decide`) ->
  Silver (`decide` / `norm_num`) -> Gold (characterising property / closed form).
- **DO NOT USE FOR:** authoring the theorem statement alone (use `@lean-specification`);
  writing tactics one step at a time or triaging tactic errors (use `@lean-proof`);
## Workflow
Discover -> Plan -> Execute -> Validate -> Persist.
1. **Discover** [discover] -- read the problem; extract the KNOWN numeric answer
   from its source; locate or request the Lean/Mathlib encoding of `answer`;
   confirm `lake env lean` (or `lean`) resolves. If the theorem statement is not
   yet written, pull it from `@lean-specification`.
2. **Plan** [discover] -- choose the encoding of `answer` (Finset / List
   enumeration vs closed form) and the ladder rung to aim for. If the encoding
   or a needed Mathlib primitive is uncertain, hand to `@lean-research`. STOP if
   the answer is unknown / the problem is open (this skill needs a known target).
3. **Execute** [execute] -- state `theorem eulerN : answer = <KNOWN>` (G-1);
## Recovery & STOP
- **Novelty** -- answer unknown or the problem is open: STOP. This skill requires
  a known numeric target; ask for the target or decline.
- **Confidence** -- `native_decide` is the only feasible close and no
  structural follow-up can be scoped: STOP at belief < 0.90 and ask before
  shipping a permanent Bronze proof.
- Both `decide` and `native_decide` fail (recursion depth, timeout): STOP; hand
  the encoding to `@lean-research` for a closed-form / structural reduction
## Handoffs
- **Predecessors:** `@lean-gateway` routes the task; `@lean-specification`
  supplies the theorem statement; `@lean-research` supplies the encoding and the
  Mathlib primitives.
- **Successors:** `@lean-proof` (tactic-level proving), `@lean-proof-review`
  (audits under the L3 carve-out), `@lean-quality-engine` (project QA).
- **Source spec:** this file (self-specified); every G-rule's `AC-EM-NN` is the
  correspondingly-numbered guarantee in this card.
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-competitive-math-handbook.md`](../../references/lean-competitive-math-handbook.md) .
## See also
- [`../../references/lean-competitive-math-handbook.md`](../../references/lean-competitive-math-handbook.md)
  -- Complete
  `lean-competitive-math` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
