---
name: "isabelle-isar-adapter-handbook"
description: "Reference handbook for @isabelle-isar-adapter with Goal-Shape Templates, Isar-to-Lean4 Phrasebook, and Error-to-Fix Table."
extracted_from: "skills/isabelle-isar-adapter/SKILL.md"
---

# Isabelle/HOL & Isar Proof Adapter Handbook

Complete guide for translating Isabelle/HOL (`.thy`), Isar structured proofs, Archive of Formal Proofs (AFP) developments, and `HOL-Analysis` / `HOL-Probability` into Lean 4 + Mathlib4.

## Goal-Shape Templates (templates)

| Isabelle / Isar Source Pattern | Concordance ID | Lean 4 Target Template |
| :--- | :--- | :--- |
| `fix x assume h: "P x" show "Q x"` | `CONC-02-FORWARD-HAVE-OBTAIN` | `intro x h; ...` |
| `obtain y where hy: "R x y" using h` | `CONC-10-SUBTYPES-SIGMA` | `obtain ⟨y, hy⟩ := h` |
| `have "a = b" ... also have "... < c" ... finally` | `CONC-06-CALCULATION-BLOCKS` | `calc a = b := by ... _ < c := by ...` |
| `proof (induct n arbitrary: m rule: nat.induct)` | `CONC-01-CASE-INDUCTION` | `induction n generalizing m with \| zero => ... \| succ n ih => ...` |
| `function f ... termination by (relation "measure g")` | `CONC-15-WELL-FOUNDED-RECURSION` | `def f ... termination_by g x decreasing_by omega` + `fun_induction f` |
| `integral⇧N M f` / `LINT x:M. f x` / `AE x in M. P x` | `CONC-16-MEASURE-INTEGRATION-BOCHNER` | `∫⁻ x, f x ∂μ` / `∫ x, f x ∂μ` / `∀ᵐ x ∂μ, P x` |

## Intent-to-Tactic Phrasebook (phrasebook)

| Isabelle Tactic / Method | Lean 4 Equivalent | Notes |
| :--- | :--- | :--- |
| `by simp` / `by (simp only: thms)` | `by simp` / `by simp only [thms]` | Prefer `simp only [...]` for non-terminal steps |
| `by auto` / `by fastforce` / `by blast` | `by aesop` / `by grind` / `by tauto` | Tableau & rewrite automation (`CONC-05`) |
| `by metis thms` / `sledgehammer` | `by grind [thms]` / `exact?` / `aesop` | Reconstruct Sledgehammer premise lists via `grind` or `have` |
| `by linarith` / `by presburger` / `by algebra` | `by linarith` / `by omega` / `by ring` | Arithmetic decision procedures (`CONC-13`) |
| `by (simp add: field_simps)` | `field_simp; ring` | Clears non-zero denominators (`CONC-14`) |
| `by word_bitwise` / `by unat_arith` | `by bv_decide` / `by bv_omega` | Fixed-width machine words (`CONC-18`) |
| `proof (rule ccontr) assume "¬ P"` | `by_contra! h` | Classical contradiction + `push_neg` (`CONC-11`) |
| `eventually_mono` (`∀⇩F x in F. P x`) | `filter_upwards [h1, h2] with x hx1 hx2` | Filter eventualities (`CONC-20`) |

## Error-to-Fix Table (errors)

| Porting Pitfall / Error | Semantic Delta (Isabelle vs Lean 4) | Deterministic Fix |
| :--- | :--- | :--- |
| Limit / derivative proof fails at `x = a` | Isabelle `at a` is the *punctured* filter `𝓝[≠] a`; `nhds a` is unpunctured `𝓝 a` | Map Isabelle `(f ⤏ l) (at a)` to `Tendsto f (𝓝[≠] a) (𝓝 l)` and `(f ⤏ l) (nhds a)` to `Tendsto f (𝓝 a) (𝓝 l)` |
| `(∑x∈A. f x)` lacks `Finset` in Lean | Isabelle `sum` takes `'a set` and returns `0` if `infinite A` | Either type `A : Finset α` with `∑ x ∈ A, f x` or use `∑ᶠ x ∈ A, f x` (`finsum`) |
| Type variable `'a` assumed non-empty | Every HOL type `'a` is inhabited (`∃ x :: 'a. True`); Lean `Type u` can be empty | Add `[Nonempty α]` or `[Inhabited α]` when a proof uses `SOME x. True` (`Classical.arbitrary`) |
| `space M` carrier membership hypotheses `x ∈ space M` | Isabelle `measure` carries a subset `space M ⊆ UNIV` | Drop `x ∈ space M` when `M` is a measure on the type `α`, or restrict via `Measure.restrict μ s` |
| Multiple `interpretation` blocks clash on same type | Isabelle locales are named; Lean typeclasses are keyed by type | Use a `structure` bundle or a `Type` wrapper synonym for secondary locale interpretations |
