---
name: "lean-corpus-audit-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-corpus-audit-handbook.md."
generated_from: "references/handbooks/lean-corpus-audit-handbook.md"
skill_ref: "skills/lean-corpus-audit/SKILL.md"
---

# `lean-corpus-audit` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-corpus-audit-handbook.md`](../handbooks/lean-corpus-audit-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Whole-repository milestone health check | 7-dimension QA sweep | Run census + `proof_quality.py` + `FIDELITY-01..08` audit |
| Theorem `(a0 a1 a2 a3 : Nat)` fixed arity | `FIDELITY-08` (`OverConcreteFixedArity`) | Generalize to `List ` / `Fin n -> ` (`@lean-proof-refactor`) |
| `def checkFoo : Bool` with only `= true -> ...` | `FIDELITY-07` (`OneWayBoolChecker`) | Upgrade to bidirectional `iff` soundness + completeness |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Audit an existing Lean repo retroactively | `lean_metrics(action: "census")` + wave stratification | Audit Layer 0 foundations first before higher layers |
| Spot vacuous or truncated Nat theorems | Static fidelity scan (`FIDELITY-01..08`) | Route flagged declarations to `@lean-tautology-triage` |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Declaration census undercounts modules | Census ran mid-rebuild with partial `.olean` files | Finish `lake build` before running `lean_metrics` / `olean_census.lean` |
| High long-proof density (>80 LOC) | Monolithic tactic scripts without helper cuts | Dispatch batch to `@lean-proof-refactor` |
