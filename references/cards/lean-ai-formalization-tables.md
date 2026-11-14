---
name: "lean-ai-formalization-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-ai-formalization-handbook.md."
generated_from: "references/handbooks/lean-ai-formalization-handbook.md"
skill_ref: "skills/lean-ai-formalization/SKILL.md"
---

# `lean-ai-formalization` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-ai-formalization-handbook.md`](../handbooks/lean-ai-formalization-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| `SafetyInv (step state action)` | Inductive safety barrier | `unfold SafetyInv step; omega` (or `linarith`) |
| `Simplex3 p q r` (`p + q + r = 100`) | Scaled-integer simplex invariant | `rcases h with hp, hq, hr, hsum; omega` |
| Escalation gate `risk >= threshold -> route = .human` | High-stakes guard | `intro h_risk; unfold route; split_ifs <;> omega` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Prove safety invariant preserved across N agent steps | `induction n with | zero => ... | succ n ih => ...` | Induct on trace/horizon length |
| Falsify candidate guard threshold before proving | `lean_counterexample_search(strategy: "dense")` | Catches off-by-one boundary leaks (`<` vs `<=`) |
| Verify non-vacuity of safety contract | Construct explicit witness `example : exists  s, SafetyInv s` | Prevents contradictory precondition bugs |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Guard proof passes trivially for all inputs | Precondition `risk > 100` is unsatisfiable on `[0, 100]` | Run `@lean-tautology-triage` and add inhabited witness theorem |
| `Nat.sub` underflow in trust-decay update | `trust - penalty` truncates at `0` | Guard with `min trust penalty` or `if penalty <= trust` + `omega` |
