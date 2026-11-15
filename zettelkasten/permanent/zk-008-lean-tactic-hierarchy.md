---
id: zk-008
title: Lean 4 unified tactic priority hierarchy
created: 2026-05-27
updated: 2026-11-15
type: permanent
tags: [lean-proofs, tactics, pattern]
refs:
  - zk-002
  - zk-009
  - zk-011
status: validated
confidence: high
---

# Lean 4 unified tactic priority hierarchy

**Claim.** Unfamiliar Lean 4 goals should be attacked in strict kernel-cost and determinism order: (1) `rfl` / `exact` / `assumption`, (2) `bv_decide` / `decide +kernel` / `norm_num` / `ring`, (3) `omega` / `linarith` / `positivity` / `gcongr`, (4) `grind` / `eqsat_rw`, (5) `simp only [...]` (never bare non-terminal `simp`), and (6) `backchain` (`solve_by_elim`) before `aesop` as last resort. `native_decide` is unconditionally banned.

**Evidence.** Codified in `references/lean4-tactic-hierarchy.md`, `GUARDRAILS.md` (`GT-30/31`), and `packages/altproof/AltProof/{Core,Tactics}.lean`. Replacing `native_decide` with `decide +kernel`, `bv_decide`, or `omega` eliminates `Lean.trustCompiler` from `#print axioms` while respecting the WHNF laws in [[zk-011]].

**Implication.** Every proving skill (`@lean-proof`, `@lean-proof-review`, `@lean-proof-refactor`) encodes this hierarchy inside its template-v2 G-rules per [[zk-002]], while single-site project-specific tactic aliases are pruned under the consolidation rubric in [[zk-009]].

See also: [[zk-002]], [[zk-009]], [[zk-011]].
