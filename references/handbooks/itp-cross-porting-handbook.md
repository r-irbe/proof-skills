---
name: itp-cross-porting-handbook
description: Reference handbook for @itp-cross-porting covering CONC-01..20 across
  Lean 4, Rocq, Isabelle/HOL, HOL Light, Agda, and Metamath.
extracted_from: skills/itp-cross-porting/SKILL.md
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
| Limit theorem fails at `x` (`Tendsto f (𝓝 x)`) | Source (`Isabelle` / `HOL Light`) `at x` excludes `x` (`0 < dist y x`) | Replace `𝓝 x` with punctured neighborhood `𝓝[≠] x` (`nhdsWithin x {x}^c`) |
| `failed to synthesize Decidable` on ported boolean reflection | Source uses `bool` predicate where Lean uses `Prop` | Add `open Classical in` locally or bridge via `decide` with `[DecidablePred P]` |
| Universe mismatch `Type u` vs `Set` when porting Agda `Set₁` | Agda `Set` is `Type 0` whereas Mathlib `Set α` is `α -> Prop` | Map Agda `Set` (universe) to `Type*` and Agda `Pred A l` to `Set A` |
| Division-by-zero discrepancy (`a / 0 = 0`) | Source guards `b != 0` implicitly in partial domain | Add explicit `(hb : b != 0)` hypothesis and discharge via `field_simp [hb]; ring` |

---

## 2. Four-Stage Cross-ITP Porting Protocol (`CONC-01..20`)

### Stage 1: Semantic Boundary Audit (Before Writing Any Proof)
Most cross-prover porting failures arise in **statement translation**, not tactic translation. Audit five semantic boundaries first:
1. **Totalized Edge Values**: Check `a - b` on `Nat` (`0` when `a < b` in Lean/Rocq/Isabelle, vs negative integer in Metamath `set.mm`), `a / 0` (`0` in Lean/Mathlib, unspecified in HOL/Isabelle `real` in older libraries), and `Nat.pow 0 0 = 1`.
2. **Carrier Non-Emptiness**: HOL Light and Isabelle/HOL types are guaranteed inhabited (`Nonempty α`); Lean 4, Rocq, and Agda types can be empty (`Empty`, `Fin 0`).
3. **Filter Puncturing (`CONC-20`)**: Verify whether `at a` / `within` includes or excludes the basepoint `a` (`𝓝 a` vs `𝓝[≠] a`).
4. **Axiomatic Footprint**: Agda `--without-K` / constructive Rocq proofs avoid `Classical.choice` and `propext`; ifconstructive purity is desired (`@lean-kernel-optimization` Route 9), avoid `by_cases` / `Classical.choose` when `Decidable` instances exist.
5. **Conjecture Falsification**: Run `lean_counterexample_search(strategy: "dense")` on every translated statement before porting its proof.

### Stage 2: Concordance Lookup (`CONC-01..20`)
Query `lean_search(query: "<concept or foreign tactic>", source: "concordance")` across the 20 canonical concordance classes:
- `CONC-01..06`: Induction/cases, forward `have`/`obtain`/boolean reflection, rewriting/congruence, typeclass/locale/HB hierarchies, tableau/SMT automation (`aesop`/`grind`), and `calc` chains.
- `CONC-07..12`: Quotients/setoids, lists/vectors, finite sets/maps, subtypes/`Sigma` types, classical contradiction, and inductive predicates.
- `CONC-13..20`: Linear/nonlinear arithmetic (`omega`/`linarith`/`ring`/`positivity`), field clearing (`field_simp`), well-founded recursion (`termination_by` + `fun_induction`), Bochner/Lebesgue integration, big operators (`∑`/`∏`), `BitVec`/SWAR decision (`bv_decide` / `decide +kernel`), extensionality (`ext`), and filters (`Tendsto` / `filter_upwards`).

### Stage 3: Modular Milestone Porting & Adapter Routing
Dispatch prover-specific syntax to the dedicated adapter skill when working from raw foreign scripts:
- **Rocq / Coq / SSReflect / MathComp**: `@rocq-proof-adapter`
- **Isabelle/HOL / Isar / AFP**: `@isabelle-isar-adapter`
- **HOL Light (`.ml`) / Metamath (`set.mm`)**: `@hol-metamath-adapter`
- **Agda / Cubical Agda**: Translate equational reasoning `≡⟨ ... ⟩` directly to `calc`, propositional `Σ` to `Subtype`, and `Acc` recursion to `termination_by`.

### Stage 4: Idiomatic MathlibAlignment & Axiom Verification
Refactor ported proofs so they use native Mathlib4 API lemmas rather than re-proving foreign prelude helpers, then run `@lean-proof-review` and `@lean-verification-gate` (`#print axioms`).
