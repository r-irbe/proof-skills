---
name: "lean-math-analysis-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-math-analysis-handbook.md."
generated_from: "references/handbooks/lean-math-analysis-handbook.md"
skill_ref: "skills/lean-math-analysis/SKILL.md"
---

# `lean-math-analysis` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-math-analysis-handbook.md`](../handbooks/lean-math-analysis-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| `Continuous (fun x => f (g x))` | `fun_prop` / `continuity` | `by fun_prop` |
| `Tendsto (fun x => f x + g x) l ( (a + b))` | `Tendsto.add` | `exact hf.add hg` |
| `HasDerivAt f f' x` | `HasDerivAt` rules | `exact (hf.mul hg).add ...` |
| `dist (f x) (f y) <= K * dist x y` | `LipschitzWith` | `rw [dist_eq_norm]; ...` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Prove continuity, differentiability, or measurability | `by fun_prop` | Supersedes legacy `continuity` for most composite expressions |
| Work with eventualities `forall  x in l, P x` | `filter_upwards [h1, h2] with x hx1 hx2` | Avoids unfolding `Filter.Eventually` |
| Convert normed distance `dist x y` to `x - y` | `simp only [dist_eq_norm]` | Bridges `MetricSpace` and `NormedAddCommGroup` |
| Apply Extreme Value Theorem on compact set | `IsCompact.exists_isMinOn` / `IsCompact.exists_isMaxOn` | Requires `hs : IsCompact s`, `hne : s.Nonempty`, `hf : ContinuousOn f s` |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| `deriv f x` rewrites fail | `deriv f x` returns `0` if `f` is not differentiable at `x` | Prove `HasDerivAt f f' x` first, then apply `HasDerivAt.deriv` |
| `(, )` proof explosion on limit goal | Unfolded `Metric.tendsto_nhds` prematurely | Keep `Tendsto` abstract and compose `Tendsto.comp` / `Tendsto.add` |
| Punctured vs full neighborhood mismatch | `[!=] x` vs ` x` | Use `tendsto_nhdsWithin_of_tendsto_nhds` to weaken ` x` to `[s] x` |
