---
name: "itp-cross-porting-handbook"
description: "Reference handbook for @itp-cross-porting covering CONC-01..20 across Lean 4, Rocq, Isabelle/HOL, HOL Light, Agda, and Metamath."
extracted_from: "skills/itp-cross-porting/SKILL.md"
---

# Cross-ITP Proof Porting Handbook (`CONC-01..20`)

Canonical guide for translating definitions, specifications, and proofs between Lean 4 and Rocq/MathComp, Isabelle/HOL, HOL Light, Agda, and Metamath (`vendor/itp-ontology/cross-itp-concordance.v1.json` and `references/dialects/{lean4,rocq,isabelle,hol_light,agda,metamath}.json`).

## Goal-Shape Templates (templates)

| Source Prover & Construct | Concordance ID | Lean 4 Target Template |
| :--- | :--- | :--- |
| Agda `begin a ≡⟨ h1 ⟩ b ≤⟨ h2 ⟩ c ∎` | `CONC-06-CALCULATION-BLOCKS` | `calc a = b := h1 _ <= c := h2` |
| Agda `Σ[ x ∈ A ] P x` (propositional `P`) | `CONC-10-SUBTYPES-SIGMA` | `{x : A // P x}` with `@[ext]` via `Subtype.ext` |
| Agda `solve n (\ x y -> lhs := rhs) refl` | `CONC-13-LINEAR-NONLINEAR-ARITHMETIC` | `by ring` (or `by omega` for linear `Nat`/`Int`) |
| Agda Cubical `data _/_ (A : Type) R` | `CONC-07-QUOTIENTS-SETOIDS` | `Quotient s` + `Quotient.lift` / `Quotient.inductionOn` |
| Foreign `at x` punctured limit (`Isabelle` / `HOL Light`) | `CONC-20-FILTERS-TOPOLOGICAL-LIMITS` | `Tendsto f (𝓝[≠] x) (𝓝 l)` (NOT unpunctured `𝓝 x`) |
| Foreign fixed-width word blast (`word_bitwise` / `WORD_BLAST`) | `CONC-18-BITVEC-SWAR-DECISION` | `by bv_decide` (or `by bv_omega`) |

## Intent-to-Tactic Phrasebook (phrasebook)

| Porting Intent | Source Idiom | Lean 4 Idiom (`lean-lsp`) |
| :--- | :--- | :--- |
| Look up cross-prover tactic equivalence | Any foreign tactic | `lean_search(query: "<tactic or CONC-ID>", source: "concordance")` |
| Port Agda structural recursion with `Acc _<_ x` | `go x (acc rs)` | Drop `Acc` parameter; add `termination_by measure x` + `decreasing_by omega` |
| Port Setoid pointwise equality `f ≗ g` (`--without-K`) | `∀ x → f x ≡ g x` | Prove `f = g` directly via `funext x` (`Quot.sound` provides `funext` in Lean 4) |
| Port foreign finite sum (`\sum`, `∑x∈A`, `nsum`) | `CONC-17-BIG-OPERATORS-FINSET` | `∑ x ∈ s, f x` over `Finset α` with `Finset.sum_bij` / `Finset.sum_comm` |
| Port Lebesgue / Bochner integral (`LINT`, `\int[mu]`) | `CONC-16-MEASURE-INTEGRATION-BOCHNER` | `∫ x in s, f x ∂μ` (Bochner) or `∫⁻ x, f x ∂μ` (`ENNReal`) + `by measurability` |
| Port classical postulate (`em : ExcludedMiddle`) | Explicit module postulate | Remove parameter; use `by_cases h : P` or `by_contra! h` |

## Error-to-Fix Table (errors)

| Porting Defect / Error | Foundational Cause | Fix |
| :--- | :--- | :--- |
| False theorem after porting `a - b` on naturals | Source (`Metamath` `N c_ C`) uses untruncated subtraction; Lean `Nat.sub` truncates at `0` | Cast to `Int` (`(a : Int) - b`) or add precondition `h : b <= a` before `omega` |
| Limit theorem fails at `x` (`Tendsto f (𝓝 x)`) | Source (`Isabelle` / `HOL Light`) `at x` excludes `x` (`0 < dist y x`) | Replace `𝓝 x` with punctured neighborhood `𝓝[≠] x` (`nhdsWithin x {x}ᶜ`) |
| `failed to synthesize Decidable` on ported boolean reflection | Source uses `bool` predicate where Lean uses `Prop` | Add `open Classical in` locally or bridge via `decide` with `[DecidablePred P]` |
| Universe mismatch `Type u` vs `Set` when porting Agda `Set₁` | Agda `Set` is `Type 0` whereas Mathlib `Set α` is `α -> Prop` | Map Agda `Set` (universe) to `Type*` and Agda `Pred A l` to `Set A` |
| Division-by-zero discrepancy (`a / 0 = 0`) | Source guards `b != 0` implicitly in partial domain | Add explicit `(hb : b != 0)` hypothesis and discharge via `field_simp [hb]; ring` |
