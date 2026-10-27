---
name: "rocq-proof-adapter-handbook"
description: "Reference handbook for @rocq-proof-adapter with Goal-Shape Templates, SSReflect-to-Lean4 Phrasebook, and Error-to-Fix Table."
extracted_from: "skills/rocq-proof-adapter/SKILL.md"
---

# Rocq / Coq & MathComp Proof Adapter Handbook

Comprehensive guide for porting Rocq/Coq (SSReflect, Mathematical Components, MathComp-Analysis, Ltac2, Equations) into Lean 4 + Mathlib4.

## Goal-Shape Templates (templates)

| Rocq / MathComp Source Pattern | Concordance ID | Lean 4 Target Template |
| :--- | :--- | :--- |
| `move=> x /andP [h1 h2] /eqP ->` | `CONC-02-BOOLEAN-REFLECTION` | `rintro x ⟨h1, h2⟩ rfl` |
| `elim: n m => [| n ih] m //=` | `CONC-01-CASE-INDUCTION` | `induction n generalizing m with \| zero => simp \| succ n ih => ...` |
| `\sum_(i < n \| P i) F i` | `CONC-17-BIG-OPERATORS-FINSET` | `∑ i : Fin n with P i, F i` |
| `(bigD1 j) //= ... exchange_big` | `CONC-17-BIG-OPERATORS-FINSET` | `Finset.add_sum_erase` / `Finset.sum_comm` |
| `apply/setP => x; rewrite !inE` | `CONC-19-EXTENSIONALITY-CONGRUENCE` | `ext x; simp only [Set.mem_...]` |
| `Equations f (x : A) : B by wf (m x) lt` | `CONC-15-WELL-FOUNDED-RECURSION` | `def f (x : A) : B := ... termination_by m x decreasing_by omega` |

## Intent-to-Tactic Phrasebook (phrasebook)

| SSReflect / Coq Tactic | Lean 4 Equivalent | Translation Notes |
| :--- | :--- | :--- |
| `move: x y => h1 h2` | `revert x y; intro h1 h2` (or `generalize`) | SSReflect `:` generalizes/reverts; `=>` introduces |
| `case: (boolP P) => hP` | `by_cases hP : P` | Replaces boolean excluded middle with `by_cases` |
| `apply/contraT => /negP h` | `by_contra! h` | Classical contradiction + `push_neg` |
| `have [w hw] : exists x, P x` | `have ⟨w, hw⟩ : ∃ x, P x := ...` | Forward existential introduction |
| `wlog: x y / x <= y` | `wlog hxy : x <= y generalizing x y` | Mathlib `wlog` tactic matches SSReflect `wlog` |
| `by lia` / `by lra` / `by nra` | `by omega` / `by linarith` / `by nlinarith` | Micromega linear/nonlinear solvers |
| `rewrite -/foo` (fold definition) | `change ...` or `rw [<- foo_def]` | Prefer `change` over fragile inverse unfolding |
| `near=> n` (MathComp-Analysis) | `filter_upwards with n hn` | Filter eventuality discharge (`CONC-20`) |

## Error-to-Fix Table (errors)

| Porting Issue | Root Cause (Rocq vs Lean 4) | Deterministic Fix |
| :--- | :--- | :--- |
| `m - n == 0` translated literally to `m - n = 0` | MathComp defines `m <= n` as `m - n == 0` in `ssrnat` | Translate `m <= n` to native `m <= n` (`LE.le`) so `omega` and `linarith` recognize it |
| Missing `reflect` views (`/eqP`, `/andP`, `/orP`) | MathComp puts propositions in `bool`; Lean 4 puts logical connectives in `Prop` with `[Decidable]` | Drop `/eqP`, `/andP`, `/orP` views and destructure `Prop` connectives directly with `rcases`; use `decide` for closed `Bool` goals |
| `f =1 g` (extensional equality) clutter | Coq core lacks `funext`, so MathComp uses `=1` | Replace `f =1 g` with standard `f = g` and prove via `funext x` (`ext x`) |
| `ord_max` / `'I_n` emptiness condition | MathComp `'I_n` is empty when `n = 0`; `ord_max` takes `'I_n.+1` | Map `'I_n` to `Fin n` and `'I_n.+1` to `Fin (n + 1)` (`Fin.last n`) |
| `HB.instance` canonical projection mismatch | MathComp keys instances on projections; Lean keys on types | Define `instance : Ring T := ...` on the carrier type `T` (or a `Type` wrapper synonym) |
