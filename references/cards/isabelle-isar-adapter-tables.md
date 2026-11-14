---
name: "isabelle-isar-adapter-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/isabelle-isar-adapter-handbook.md."
generated_from: "references/handbooks/isabelle-isar-adapter-handbook.md"
skill_ref: "skills/isabelle-isar-adapter/SKILL.md"
---

# `isabelle-isar-adapter` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/isabelle-isar-adapter-handbook.md`](../handbooks/isabelle-isar-adapter-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| `fix x assume h: "P x" show "Q x"` | `CONC-02-FORWARD-HAVE-OBTAIN` | `intro x h; ...` |
| `obtain y where hy: "R x y" using h` | `CONC-10-SUBTYPES-SIGMA` | `obtain y, hy := h` |
| `have "a = b" ... also have "... < c" ... finally` | `CONC-06-CALCULATION-BLOCKS` | `calc a = b := by ... _ < c := by ...` |
| `proof (induct n arbitrary: m rule: nat.induct)` | `CONC-01-CASE-INDUCTION` | `induction n generalizing m with | zero => ... | succ n ih => ...` |
| `function f ... termination by (relation "measure g")` | `CONC-15-WELL-FOUNDED-RECURSION` | `def f ... termination_by g x decreasing_by omega` + `fun_induction f` |
| `integralN M f` / `LINT x:M. f x` / `AE x in M. P x` | `CONC-16-MEASURE-INTEGRATION-BOCHNER` | `int x, f x ` / `int x, f x ` / `forall  x , P x` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| `by simp` / `by (simp only: thms)` | `by simp` / `by simp only [thms]` | Prefer `simp only [...]` for non-terminal steps |
| `by auto` / `by fastforce` / `by blast` | `by aesop` / `by grind` / `by tauto` | Tableau & rewrite automation (`CONC-05`) |
| `by metis thms` / `sledgehammer` | `by grind [thms]` / `exact?` / `aesop` | Reconstruct Sledgehammer premise lists via `grind` or `have` |
| `by linarith` / `by presburger` / `by algebra` | `by linarith` / `by omega` / `by ring` | Arithmetic decision procedures (`CONC-13`) |
| `by (simp add: field_simps)` | `field_simp; ring` | Clears non-zero denominators (`CONC-14`) |
| `by word_bitwise` / `by unat_arith` | `by bv_decide` / `by bv_omega` | Fixed-width machine words (`CONC-18`) |
| `proof (rule ccontr) assume " P"` | `by_contra! h` | Classical contradiction + `push_neg` (`CONC-11`) |
| `eventually_mono` (`forall F x in F. P x`) | `filter_upwards [h1, h2] with x hx1 hx2` | Filter eventualities (`CONC-20`) |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Limit / derivative proof fails at `x = a` | Isabelle `at a` is the *punctured* filter `[!=] a`; `nhds a` is unpunctured ` a` | Map Isabelle `(f  l) (at a)` to `Tendsto f ([!=] a) ( l)` and `(f  l) (nhds a)` to `Tendsto f ( a) ( l)` |
| `(sumxinA. f x)` lacks `Finset` in Lean | Isabelle `sum` takes `'a set` and returns `0` if `infinite A` | Either type `A : Finset ` with `sum x in A, f x` or use `sum x in A, f x` (`finsum`) |
| Type variable `'a` assumed non-empty | Every HOL type `'a` is inhabited (`exists  x :: 'a. True`); Lean `Type u` can be empty | Add `[Nonempty ]` or `[Inhabited ]` when a proof uses `SOME x. True` (`Classical.arbitrary`) |
| `space M` carrier membership hypotheses `x in space M` | Isabelle `measure` carries a subset `space M subset UNIV` | Drop `x in space M` when `M` is a measure on the type ``, or restrict via `Measure.restrict  s` |
| Multiple `interpretation` blocks clash on same type | Isabelle locales are named; Lean typeclasses are keyed by type | Use a `structure` bundle or a `Type` wrapper synonym for secondary locale interpretations |
