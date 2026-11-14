---
name: "rocq-proof-adapter-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/rocq-proof-adapter-handbook.md."
generated_from: "references/handbooks/rocq-proof-adapter-handbook.md"
skill_ref: "skills/rocq-proof-adapter/SKILL.md"
---

# `rocq-proof-adapter` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/rocq-proof-adapter-handbook.md`](../handbooks/rocq-proof-adapter-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| `move=> x /andP [h1 h2] /eqP ->` | `CONC-02-BOOLEAN-REFLECTION` | `rintro x h1, h2 rfl` |
| `elim: n m => [ | n ih] m //=` | `CONC-01-CASE-INDUCTION` |
| `\sum_(i < n | P i) F i` | `CONC-17-BIG-OPERATORS-FINSET` | `sum i : Fin n with P i, F i` |
| `(bigD1 j) //= ... exchange_big` | `CONC-17-BIG-OPERATORS-FINSET` | `Finset.add_sum_erase` / `Finset.sum_comm` |
| `apply/setP => x; rewrite !inE` | `CONC-19-EXTENSIONALITY-CONGRUENCE` | `ext x; simp only [Set.mem_...]` |
| `Equations f (x : A) : B by wf (m x) lt` | `CONC-15-WELL-FOUNDED-RECURSION` | `def f (x : A) : B := ... termination_by m x decreasing_by omega` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| `move: x y => h1 h2` | `revert x y; intro h1 h2` (or `generalize`) | SSReflect `:` generalizes/reverts; `=>` introduces |
| `case: (boolP P) => hP` | `by_cases hP : P` | Replaces boolean excluded middle with `by_cases` |
| `apply/contraT => /negP h` | `by_contra! h` | Classical contradiction + `push_neg` |
| `have [w hw] : exists x, P x` | `have w, hw : exists  x, P x := ...` | Forward existential introduction |
| `wlog: x y / x <= y` | `wlog hxy : x <= y generalizing x y` | Mathlib `wlog` tactic matches SSReflect `wlog` |
| `by lia` / `by lra` / `by nra` | `by omega` / `by linarith` / `by nlinarith` | Micromega linear/nonlinear solvers |
| `rewrite -/foo` (fold definition) | `change ...` or `rw [<- foo_def]` | Prefer `change` over fragile inverse unfolding |
| `near=> n` (MathComp-Analysis) | `filter_upwards with n hn` | Filter eventuality discharge (`CONC-20`) |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| `m - n == 0` translated literally to `m - n = 0` | MathComp defines `m <= n` as `m - n == 0` in `ssrnat` | Translate `m <= n` to native `m <= n` (`LE.le`) so `omega` and `linarith` recognize it |
| Missing `reflect` views (`/eqP`, `/andP`, `/orP`) | MathComp puts propositions in `bool`; Lean 4 puts logical connectives in `Prop` with `[Decidable]` | Drop `/eqP`, `/andP`, `/orP` views and destructure `Prop` connectives directly with `rcases`; use `decide` for closed `Bool` goals |
| `f =1 g` (extensional equality) clutter | Coq core lacks `funext`, so MathComp uses `=1` | Replace `f =1 g` with standard `f = g` and prove via `funext x` (`ext x`) |
| `ord_max` / `'I_n` emptiness condition | MathComp `'I_n` is empty when `n = 0`; `ord_max` takes `'I_n.+1` | Map `'I_n` to `Fin n` and `'I_n.+1` to `Fin (n + 1)` (`Fin.last n`) |
| `HB.instance` canonical projection mismatch | MathComp keys instances on projections; Lean keys on types | Define `instance : Ring T := ...` on the carrier type `T` (or a `Type` wrapper synonym) |
