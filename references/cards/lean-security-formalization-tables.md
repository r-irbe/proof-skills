---
name: "lean-security-formalization-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-security-formalization-handbook.md."
generated_from: "references/handbooks/lean-security-formalization-handbook.md"
skill_ref: "skills/lean-security-formalization/SKILL.md"
---

# `lean-security-formalization` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-security-formalization-handbook.md`](../handbooks/lean-security-formalization-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Confidentiality / no-read-up & no-write-down policy | Bell-LaPadula / Biba lattice monotonicity (`s <= s`) | Model security labels as `PartialOrder` / `Lattice` |
| Two-run noninterference `low_eq s s -> low_eq (step s) (step s)` | Relational unwinding lemma | Prove single-step unwinding and lift by structural induction on trace |
| Capability / RBAC / ABAC authorization check | Decidable policy predicate + soundness `iff` | Pair executable `Bool` guard with bidirectional `Prop` specification |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Formalize information-flow or access-control guarantees | Abstract lattice spec + concrete bitmask `@[csimp]` twin | Keep policy theorems over `Lattice L`; implement runtime labels as `BitVec` |
| Audit security proof for vacuous unreachable states | `@lean-tautology-triage` reachability witness | Prove `exists  s, ValidInit s` and reachable trace transitions |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Noninterference holds vacuously because `step` is deterministic no-op | Missing liveness / functional correctness companion theorem | Pair security noninterference with functional progress specification |
| Bitwise permission mask bug in concrete policy checker | Unverified gap between `Bool` mask and abstract policy | Prove `@[csimp]` / `iff` equivalence via `decide +kernel` or `bv_decide` |
