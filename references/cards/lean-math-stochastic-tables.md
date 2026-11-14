---
name: "lean-math-stochastic-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-math-stochastic-handbook.md."
generated_from: "references/handbooks/lean-math-stochastic-handbook.md"
skill_ref: "skills/lean-math-stochastic/SKILL.md"
---

# `lean-math-stochastic` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-math-stochastic-handbook.md`](../handbooks/lean-math-stochastic-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| `Measurable (fun x => f (g x))` | `measurability` / `fun_prop` | `by measurability` (or `by fun_prop`) |
| `forall  x , P x  Q x` | `filter_upwards` | `filter_upwards [hP, hQ] with x hxP hxQ using hxP, hxQ` |
| `int x, (f x + g x)  = int x, f x  + int x, g x ` | `integral_add` | `exact integral_add hf_int hg_int` |
| Scaled simplex `w + w + w = 100` | Scaled `Nat` simplex (`x 100`) | `by omega` |
| Markov kernel row-stochasticity `sum j, P i j = 1` | `Finset.sum` / `PMF` | `simp only [...]; ring` (or `omega` on scaled `Nat`) |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Discharge measurability of composite function | `by measurability` or `by fun_prop` | Handles arithmetic, continuous, and borel maps |
| Combine finitely many `forall  x ` hypotheses | `filter_upwards [h1, h2] with x hx1 hx2` | Avoids manual null-set union bookkeeping |
| Bound expectation / integral monotonically | `apply integral_mono_ae hf hg` | Pair with `filter_upwards` for pointwise bound |
| Prove probability bound in `[0, 1]` | `positivity` / `linarith` | For `ENNReal`, check `!= ` before `ENNReal.toReal` |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| `ENNReal` subtraction cancellation fails | ` -  = 0` and truncated subtraction in `>=0` | Prove finiteness `h : x != ` before using `ENNReal.sub_add_cancel` |
| `integral_add` fails to apply | Missing `Integrable f ` side conditions | Establish `hf : Integrable f ` before linearity rewrites |
| Scaled integer probability underflow | `100 - p` truncates if `p <= 100` is missing | Include `hp : p <= 100` in structure invariants and pass to `omega` |
