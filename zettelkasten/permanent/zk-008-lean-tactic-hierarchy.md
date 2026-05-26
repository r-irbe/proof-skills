---
id: zk-008
title: Lean 4 tactic priority hierarchy
created: 2026-05-27
updated: 2026-05-27
type: permanent
tags: [lean-proofs, tactics, pattern]
refs:
  - zk-002
  - zk-009
status: validated
confidence: high
---

# Lean 4 tactic priority hierarchy

**Claim.** For an unfamiliar Lean 4 goal, try tactics in a fixed
priority order — fastest first, specialised closers before general
search. The canonical sequence is: `grind` → `omega` → `norm_num` →
`simp only [lemmas]` → `nlinarith [sq_nonneg ...]` → `linarith` →
`ring` → `positivity` → `field_simp` → `decide` → cast normalisation
(`push_cast` / `norm_cast` / `zify`) → `aesop` (last resort).

**Evidence.** Codified in `references/lean4-tactic-hierarchy.md` and
the project-tuned variant inside `skills/lean-proof-review/SKILL.md`
§"Proof Search Priority" (lines 26-48). `grind` is the headline
default — it subsumes roughly 54% of `omega` and 64% of `linarith`
call-sites in the project's 22,312-line corpus. `native_decide` is
**banned** in the project (adds `Lean.trustCompiler`; all 23 occurrences
were replaced with `decide`).

**Implication.** This hierarchy is part of the *contract* of
`lean-proof-review`, not advisory background. Migrating that skill to
the template-v2 schema described in [[zk-002]] means lifting these
rows into `G-1 … G-N` MUST/SHOULD lines with `[Source:
references/lean4-tactic-hierarchy.md]` trace tags. The deprecated
`proj_*` macros (rows 8–14 in the project variant) are a textbook
candidate for the consolidation rubric in [[zk-009]] — zero
cross-module uses means *delete*, not *re-document*.

See also: [[zk-002]], [[zk-009]].
