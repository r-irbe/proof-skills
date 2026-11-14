---
name: "lean-bisect-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-bisect-handbook.md."
generated_from: "references/handbooks/lean-bisect-handbook.md"
skill_ref: "skills/lean-bisect/SKILL.md"
---

# `lean-bisect` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-bisect-handbook.md`](../handbooks/lean-bisect-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Proof broke across Lean nightly / release range | `git bisect run lake env lean Repro.lean` | Minimize to standalone `<50 LOC` MWE (`@lean-mwe`) before bisecting |
| Exit code `125` on unbuildable intermediate commit | `exit 125` (`git bisect skip`) | Never conflate build-infra failure with target regression |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Find exact Mathlib commit that renamed/removed lemma | `git bisect` with `lean_lookup_symbol` / `lake env lean` | Feed culprit commit message directly to `@lean-proof-repair` |
| Test across Lean `lean-toolchain` nightlies | Toolchain pin sweep script | Pin `leanprover/lean4:nightly-YYYY-MM-DD` in isolated temp dir |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Bisect takes hours rebuilding Mathlib at each step | Running full `lake build` on uncached commits | Fetch `lake exe cache get` per step or reduce to Core-only MWE |
| Flaky timeout produces wrong first-bad commit | `maxHeartbeats` borderline threshold | Fix deterministic `--memory` / `maxHeartbeats` margin in reproducer |
