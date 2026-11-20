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
| Proof `> 50 LOC` with repeated sub-block | `CUT` -> private/module helper lemma | Extract only when reusable (`>= 2` call sites or clean conceptual invariant) |
| Concrete coordinate/`Real` proof using only ring/order ops | Statement-level mixin generalization | Generalize `[CommRing R] [LinearOrder R] [IsOrderedRing R]`; keep `Real` theorem as 1-line corollary |
| Slow `Prop`-friendly `specFn` vs fast monomorphic `fastFn` | `@[csimp] theorem specFn_eq_fastFn` (`KERNEL-LAW-07`) | Keep `specFn` clean for proofs; route LCNF execution & `rw` to `fastFn` |
| Parametric hot kernel step (`1,600x..3,345x` WHNF penalty) | `WAVE-13 G1` `rfl`-bridged Duality | Specialize hot `def` to raw unboxed `Nat`; prove parametric lemma in cold section; bridge via `rfl` |
| Verbose `Finset.sum` linearity or monotonicity block | `sum_congr_ring` / `finset_mono` / `finset_nonneg` | Collapse 15-40 line `Finset.sum` proofs to 1-line AltProof combinators |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Slim a long proof corpus without regressions | `scripts/lean/proof_quality.py` + `CUT / CONSIDERED-NEGATIVE / DEFER` | Preserve public theorem signatures byte-for-byte; gate every batch on `0` warnings/errors |
| Eliminate single-use helper bloat ("bundle effect") | `CONSIDERED-NEGATIVE` adjudication | Do not split linear single-use glue that merely relocates line count |
| Audit which `Real`-typed theorems can be generalized | `python3 -m altproof.coupling_scanner` | Classify into `abstraction-safe` (algebraic/order), `nat-mixed`, or `real-specific` (`exp`/`log`/`nhds`) |
| Share proof structure across multiple concrete bit/SWAR kernels | `WAVE-13 G1` Cold Parametric Theorem + `rfl` Bridge | Prove once over `(step : State -> State)`; instantiate on concrete `fastStep` at `<= 1%` WHNF cost |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Extracted helper requires 9+ awkward context variables | Cut boundary sliced mid-tactic state | Widen cut to a natural mathematical invariant or mark `CONSIDERED-NEGATIVE` |
| Generalizing a hot `def` slowed `rfl`/`decide` by `> 1,000x` | `WAVE-13 G1`: dictionary/closure dispatch inside hot `@Nat.rec` | Revert hot `def` to concrete monomorphic `Nat.*` ops; move polymorphism strictly to cold `theorem` layer |
| Public theorem signature changed during refactor | Hard API boundary violation | Revert signature edit; add generalized lemma alongside and prove original signature via 1-liner |
| Commute-diagram lift increased total LOC on tiny state | Commute pattern overhead (`<= 5` state ops) | Apply Commute diagram lifts only above the `> 20` state-operation threshold |
