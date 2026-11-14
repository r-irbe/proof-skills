---
name: "lean-tautology-triage-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-tautology-triage-handbook.md."
generated_from: "references/handbooks/lean-tautology-triage-handbook.md"
skill_ref: "skills/lean-tautology-triage/SKILL.md"
---

# `lean-tautology-triage` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-tautology-triage-handbook.md`](../handbooks/lean-tautology-triage-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| `theorem foo (h : P) : P := h` or `x = x` | `FIDELITY-01` / `FIDELITY-02` Tautology | Classify `GENUINE_VACUITY` vs intentional `DEFINITIONAL_WITNESS` |
| `theorem bar (a b : Nat) : a - b + b >= a` | `FIDELITY-04` (`NatSubTruncation`) | Check `a < b` collapse; require `b <= a` or `Int` carrier |
| Contradictory hypotheses `h1 : x < 0`, `h2 : x > 0` | Ex-falso vacuity probe | Require constructive witness showing hypotheses are jointly satisfiable |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Triage static vacuity/truncation scanner findings | `lean_diagnostics` + `lean_counterexample_search` | Separate true mathematical defects from intentional smoke/API lemmas |
| Prove non-vacuity of complex precondition bundle | Constructive `example : exists  x, Preconditions x` | Attach non-vacuity witness adjacent to main theorem |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Scanner flags `a + b >= 0` on `Nat` (`FIDELITY-03`) | Unsigned `Nat` makes `>= 0` unconditionally true | Lift carrier to `Int`/`` or state the intended non-trivial lower bound |
| One-way checker `check x = true -> Valid x` returns `false` always | `FIDELITY-07` (`OneWayBoolChecker`) | Require `check x = true <-> Valid x` or non-empty `= true` witness |
