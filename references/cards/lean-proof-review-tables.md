---
name: "lean-proof-review-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-proof-review-handbook.md."
generated_from: "references/handbooks/lean-proof-review-handbook.md"
skill_ref: "skills/lean-proof-review/SKILL.md"
---

# `lean-proof-review` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-proof-review-handbook.md`](../handbooks/lean-proof-review-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Completed `sorry`-free theorem in PR | 4-Layer Checklist (Soundness, Faithfulness, Non-Vacuity, Hygiene) | Read-only `auditor` pass via `lean_diagnostics` + `lean_axiom_closure` |
| Theorem over `Nat` subtraction or division | Layer 2 Faithfulness & Truncation check | Verify `b <= a` / `d != 0` hypotheses prevent degenerate triviality |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Audit whether formal statement matches paper claim | Clause-by-clause paper-to-Lean bijection table | Flag any dropped hypothesis, weakened quantifier, or one-way `Bool` implication |
| Check proof hygiene & maintainability | Inspect `simp` non-terminal calls, `maxHeartbeats` overrides, and axioms | Require `simp only [...]` on non-terminal steps |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| `#print axioms` reveals `Classical.choice` in constructive lane | `open Classical` or `by_cases` used on decidable predicate | Route to `@lean-sair-kernel-optimization` Route 9 (`Bool.rec` / `decide`) |
| Theorem has `0 sorry` but conclusion echoes hypothesis | `FIDELITY-01` (`HYPOTHESIS_ECHO`) | Reject in Layer 3 Non-Vacuity check and escalate to `specifier` |
