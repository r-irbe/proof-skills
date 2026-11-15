---
name: isabelle-isar-adapter-handbook
description: Reference handbook for @isabelle-isar-adapter with Goal-Shape Templates,
  Isar-to-Lean4 Phrasebook, and Error-to-Fix Table.
extracted_from: skills/isabelle-isar-adapter/SKILL.md
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
| `(∑x∈A. f x)` lacks `Finset` in Lean | Isabelle `sum` takes `'a set` and returns `0` if `infinite A` | Either type `A : Finset α` with `∑ x ∈ A, f x` or use `∑^f x ∈ A, f x` (`finsum`) |
| Type variable `'a` assumed non-empty | Every HOL type `'a` is inhabited (`∃ x :: 'a. True`); Lean `Type u` can be empty | Add `[Nonempty α]` or `[Inhabited α]` when a proof uses `SOME x. True` (`Classical.arbitrary`) |
| `space M` carrier membership hypotheses `x ∈ space M` | Isabelle `measure` carries a subset `space M ⊆ UNIV` | Drop `x ∈ space M` when `M` is a measure on the type `α`, or restrict via `Measure.restrict μ s` |
| Multiple `interpretation` blocks clash on same type | Isabelle locales are named; Lean typeclasses are keyed by type | Use a `structure` bundle or a `Type` wrapper synonym for secondary locale interpretations |

---

## 2. Structural Translation Architecture: Isabelle/Isar -> Lean 4

### 2.1 Mapping Isabelle `locale` & `sublocale` Hierarchies (`CONC-04`)
Isabelle locales (`locale group_hom = G: group G + H: group H for G H + fixes f assumes ...`) bundle parameters and assumptions by name, whereas Mathlib4 uses **unbundled typeclasses on carrier types** plus morphism structures (`MonoidHom`, `G →* H`):
1. **Standard Algebraic / Topological Locales**: Map directly to Mathlib4 typeclasses (`[Group G]`, `[TopologicalSpace X]`, `[MeasureSpace Ω]`) rather than defining bespoke `structure` records, so Mathlib's global lemma library applies automatically.
2. **Multi-Instance / Parametric Domain Locales**: When an AFP development instantiates the *same* locale twice on the same carrier type `(ℝ, op₁)` and `(ℝ, op₂)`, translate the locale as an explicit Lean `structure MyLocale (α : Type*)` (bundled record) or a `Type` wrapper synonym (`def DualCarrier (α : Type*) := α`) to avoid typeclass coherence diamonds.

### 2.2 Translating Structured Isar Proofs (`fix-assume-show` & `also-finally`)
Isar declarative blocks map almost 1-to-1 onto idiomatic Lean 4 structured proofs:
- `fix x assume h: "P x" have h1: "Q x" by ... show "R x" by ...` -> `intro x h; have h1 : Q x := by ...; show R x; ...`
- `have "a = b" by ... also have "... ≤ c" by ... finally show "a ≤ c" .` -> `calc a = b := by ... \n  _ ≤ c := by ...`
- `proof (cases "P x") case True ... case False ... qed` -> `by_cases h : P x` with focused `·` branches.
- **Sledgehammer Reconstruction**: When porting `by (metis lem1 lem2 lem3)`, try `by grind [lem1, lem2, lem3]` first; if higher-order unification is involved, decompose into one `have` step plus `aesop` or `linarith`.

### 2.3 Quotients (`lift_definition` / `transfer`) & `HOL-Analysis` Filters
1. **`lift_definition` & `transfer`**: Map `quotient_type 'a q = "'a" / "R"` to `Quotient setoidR`, `lift_definition` to `Quotient.lift` / `Quotient.lift₂` (proving compatibility), and `by transfer` proofs on universal goals to `induction x using Quotient.inductionOn`.
2. **Filter & Measure Conventions (`CONC-16`, `CONC-20`)**:
   - Isabelle `(f ⤏ l) (at a within S)` -> `Tendsto f (𝓝[S \ {a}] a) (𝓝 l)` (note `at a within S` excludes `a`!).
   - Isabelle `AE x in M. P x` -> `∀ᵐ x ∂μ, P x` (`Filter.Eventually P (MeasureTheory.ae μ)`), manipulated via `filter_upwards [h1, h2] with x hx1 hx2`.

## 3. Pitfalls & Handoffs
- Always check emptiness assumptions (`[Nonempty α]`) when porting theorems that invoke Hilbert's choice `SOME x. P x` (`Classical.epsilon`).
- **Handoffs**: Predecessors: `itp-cross-porting`, `lean-specification`. Successors: `lean-proof-review`, `lean-verification-gate`.
