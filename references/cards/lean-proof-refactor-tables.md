---
name: "lean-proof-refactor-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-proof-refactor-handbook.md."
generated_from: "references/handbooks/lean-proof-refactor-handbook.md"
skill_ref: "skills/lean-proof-refactor/SKILL.md"
---

# `lean-proof-refactor` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-proof-refactor-handbook.md`](../handbooks/lean-proof-refactor-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Proof `> 50 LOC` with repeated sub-block | `CUT` -> private helper lemma | Extract only when reusable (`>= 2` call sites or clean conceptual boundary) |
| Concrete coordinate/bit-level proof duplicated | Abstraction-Concrete Duality lift | Prove once over abstract algebraic/order structure; instantiate at call sites |
| Slow `Prop`-friendly recursive `specFn` in runtime path | `@[csimp] theorem specFn_eq_fastFn` (`SAIR-LAW-07`) | Keep `specFn` for proofs; route execution to monomorphic `fastFn` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Slim a long proof corpus without regressions | `scripts/lean/proof_quality.py` + `CUT / CONSIDERED-NEGATIVE / DEFER` | Preserve public theorem signatures byte-for-byte |
| Eliminate single-use helper bloat ('bundle effect') | `CONSIDERED-NEGATIVE` adjudication | Do not split linear single-use glue that merely relocates line count |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Extracted helper requires 9 awkward context variables | Cut boundary sliced mid-tactic state | Widen cut to a natural mathematical invariant or mark `CONSIDERED-NEGATIVE` |
| Public theorem signature changed during refactor | Hard boundary violation | Revert signature edit; add generalized lemma alongside and prove old via 1-liner |
