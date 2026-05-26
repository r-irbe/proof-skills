# Mathlib4 Coding Conventions — Comprehensive Reference

> Compiled from examination of the [Mathlib4 source code](https://github.com/leanprover-community/mathlib4),
> the official [Style Guide](https://leanprover-community.github.io/contribute/style.html),
> and the [Naming Conventions](https://leanprover-community.github.io/contribute/naming.html).

---

## 1. File & Module Structure

### 1.1 File Names
- Files use **`UpperCamelCase.lean`** (e.g., `Contracting.lean`, `SpecialFunctions/Pow/Real.lean`).
- Rare exceptions for specifically lower-cased objects (e.g., `lp.lean` for ℓ_p space).

### 1.2 File Header Format
Every file begins with a copyright block, then `module`, then imports:

```lean
/-
Copyright (c) 2019 Rohan Mitta. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Rohan Mitta, Kevin Buzzard, Alistair Tucker, Johannes Hölzl, Yury Kudryashov
-/
module

public import Mathlib.Analysis.SpecificLimits.Basic
public import Mathlib.Data.Setoid.Basic

import Mathlib.Topology.MetricSpace.Lipschitz
```
*Source: `Mathlib/Topology/MetricSpace/Contracting.lean`*

Rules:
- `Authors:` (plural even for one author), comma-separated, no trailing period, no `and`.
- `module` on its own line after the header.
- Blank line, then `public import`s grouped together.
- Blank line, then regular `import`s grouped together.
- Keep imports **alphabetical** within each block.

### 1.3 Module Docstrings
Immediately after imports, a `/-! ... -/` block:

```lean
/-!
# Contracting maps

A Lipschitz continuous self-map with Lipschitz constant `K < 1` is called a *contracting map*.
In this file we prove the Banach fixed point theorem, some explicit estimates on the rate
of convergence, and some properties of the map sending a contracting map to its fixed point.

## Main definitions

* `ContractingWith K f` : a Lipschitz continuous self-map with `K < 1`;
* `efixedPoint` : given a contracting map `f` on a complete emetric space ...
* `fixedPoint` : the unique fixed point of a contracting map ...

## Tags

contracting map, fixed point, Banach fixed point theorem
-/
```
*Source: `Mathlib/Topology/MetricSpace/Contracting.lean`*

Required sections in module docstrings:
- **`# Title`** — file title
- **Summary** — what the file contains
- **`## Main definitions`** and/or **`## Main results`** — backtick-quoted declaration names with descriptions
- **`## Notation`** — if custom notation is introduced
- **`## References`** — literature citations
- **`## Tags`** — comma-separated searchable tags

### 1.4 Directory Organization
Mathlib is organized into a deep hierarchy reflecting mathematical structure:
```
Mathlib/
├── Algebra/           # Algebraic structures
├── Analysis/          # Real/complex analysis
│   ├── Normed/Group/  # Normed groups
│   └── SpecialFunctions/
├── Data/              # Data structures (Nat, List, etc.)
├── Order/             # Order theory, lattices, filters
├── Tactic/            # Custom tactics
│   ├── Positivity/    # @[positivity] extensions
│   ├── FunProp/       # @[fun_prop] framework
│   └── Abel.lean      # Single-file tactics
└── Topology/          # Topological spaces, metric spaces
```

---

## 2. Naming Conventions

### 2.1 Capitalization Rules

| What | Style | Example |
|------|-------|---------|
| Theorem/lemma names (terms of `Prop`) | `snake_case` | `mul_comm`, `succ_ne_zero` |
| Types, structures, classes (`Prop`/`Type`/`Sort`) | `UpperCamelCase` | `ContractingWith`, `IsFixedPt` |
| Functions (named by return type) | follows return type | `toFun` (returns `Type`), `map_one'` (returns `Prop`) |
| All other terms | `lowerCamelCase` | `efixedPoint`, `fixedPoint` |
| UpperCamelCase in snake_case context | `lowerCamelCase` | `MonoidHom.toOneHom_injective` |
| Acronyms | grouped upper/lower | `LE`, `le_iff_lt_or_eq` |

*Source: [Naming conventions — Capitalization](https://leanprover-community.github.io/contribute/naming.html)*

### 2.2 Prop-Valued Classes
- **Nouns** → prefix with `Is`: `IsTopologicalRing`, `IsComplete`
- **Adjectives** → no prefix needed: `Normal`, `Nonempty`

### 2.3 Symbol Dictionary (Key Entries)

| Symbol | Name in theorems |
|--------|-----------------|
| `∨` | `or` |
| `∧` | `and` |
| `→` | `of` / `imp` (conclusion first) |
| `↔` | `iff` |
| `¬` | `not` |
| `∃` | `exists` |
| `∀` | `all` / `forall` |
| `=` | `eq` (often omitted) |
| `≠` | `ne` |
| `∈` | `mem` |
| `∪` | `union` |
| `∩` | `inter` |
| `⋃` | `iUnion` / `biUnion` |
| `<` | `lt` / `gt` |
| `≤` | `le` / `ge` |
| `+` | `add` |
| `*` | `mul` |
| `⁻¹` | `inv` |
| `∣` | `dvd` |
| `⊔` | `sup` |
| `⊓` | `inf` |
| `⊥` | `bot` |
| `⊤` | `top` |

### 2.4 Theorem Naming Patterns

**Descriptive names** — describe the conclusion:
```lean
theorem succ_ne_zero ...
theorem mul_zero ...
theorem mul_one ...
```

**Hypotheses with `of`** — hypotheses listed in order after `of`:
```lean
theorem lt_of_succ_le ...
theorem lt_of_le_of_ne ...
theorem add_lt_add_of_lt_of_le ...
```
The pattern `C_of_A_of_B` matches `A → B → C`.

**Abbreviations**: `pos` = `zero_lt`, `neg` = `lt_zero`, `nonneg` = `zero_le`, `nonpos` = `le_zero`:
```lean
theorem mul_pos ...
theorem mul_nonpos_of_nonneg_of_nonpos ...
```

**Left/right variants**:
```lean
theorem add_le_add_left ...
theorem add_le_add_right ...
```

**`le`/`lt` vs `ge`/`gt`**: Use `le`/`lt` for first occurrence; use `ge`/`gt` when arguments are swapped:
```lean
theorem lt_iff_le_not_ge ...
theorem Eq.ge {a b} (h : a = b) : b ≤ a  -- ge matches swapped order
```

### 2.5 Structural Lemma Naming

| Pattern | Name | Example |
|---------|------|---------|
| `(∀ x, f x = g x) → f = g` | `.ext` (with `@[ext]`) | `TopologicalSpace.ext` |
| `f = g ↔ ∀ x, f x = g x` | `.ext_iff` | |
| `Injective f` | `f_injective` | |
| `f x = f y ↔ x = y` | `f_inj` | |
| `a ≤ b → f a ≤ f b` | `f_mono` | |
| `Monotone f` | `f_monotone` | |
| `StrictMono f` | `f_strictMono` | |

### 2.6 Dot Notation & Namespaces
```lean
namespace ContractingWith

theorem toLipschitzWith (hf : ContractingWith K f) : LipschitzWith K f := hf.2

-- Enables: hf.toLipschitzWith
-- Also: hf.dist_le_mul, hf.fixedPoint_isFixedPt, etc.
```
*Source: `Mathlib/Topology/MetricSpace/Contracting.lean`*

### 2.7 Unexpanded vs Expanded Function Forms
```lean
-- Unexpanded (uses Pi.mul):
theorem Continuous.mul (hf : Continuous f) (hg : Continuous g) : Continuous (f * g)

-- Expanded (uses fun):
theorem Continuous.fun_mul (hf : Continuous f) (hg : Continuous g) :
    Continuous fun x ↦ f x * g x
```
Both should be tagged `@[fun_prop]`.

### 2.8 Spelling
- **American English** in declaration names: `factorization`, `Localization`, `FiberBundle`
- Documentation may use other common English spellings.

---

## 3. Import Conventions

### 3.1 Narrow Imports
Import only what you need. Prefer specific module paths over broad parent modules:
```lean
-- Good:
import Mathlib.Analysis.SpecificLimits.Basic
import Mathlib.Topology.MetricSpace.Lipschitz

-- Bad:
import Mathlib.Analysis
import Mathlib.Topology
```

### 3.2 `public import` vs `import`
- `public import` — re-exports the module to downstream consumers
- `import` — private dependency

### 3.3 `assert_not_exists`
Used to enforce that a module does NOT transitively import certain declarations, keeping the dependency graph lean:
```lean
assert_not_exists Field TwoSidedIdeal
```
*Source: `Mathlib/Data/ZMod/Aut.lean`*

This is placed at the **end** of the file and acts as a compile-time assertion that the named declarations were never imported.

---

## 4. Variable, Section & Namespace Patterns

### 4.1 Variable Conventions

| Variable | Convention |
|----------|-----------|
| `u`, `v`, `w` | universes |
| `α`, `β`, `γ` | generic types |
| `a`, `b`, `c` | propositions |
| `x`, `y`, `z` | elements of a generic type |
| `h`, `h₁`, `h₂` | hypotheses/assumptions |
| `p`, `q`, `r` | predicates and relations |
| `s`, `t` | lists or sets |
| `m`, `n`, `k` | natural numbers |
| `i`, `j`, `k` | integers |
| `G` | group |
| `R` | ring |
| `K`, `𝕜` | field |
| `E` | vector space |

### 4.2 Section & Namespace Structure
```lean
@[expose] public section

open NNReal Topology ENNReal Filter Function

variable {α : Type*}

namespace ContractingWith

variable [EMetricSpace α] {K : ℝ≥0} {f : α → α}

open EMetric Set

-- theorems here...

section
variable [CompleteSpace α]

-- theorems requiring completeness...

end

end ContractingWith
```
*Source: `Mathlib/Topology/MetricSpace/Contracting.lean`*

Key patterns:
- **`namespace`** wraps related definitions and provides dot notation.
- **`section`/`end`** scopes `variable` declarations without creating a namespace.
- **`open`** placed right after namespace/section headers.
- **`variable`** uses `{implicit}` for typeclass-inferable args, `(explicit)` for user-provided args.
- **No indentation** inside namespace/section blocks.
- Nested `section` for additional hypotheses (e.g., `[CompleteSpace α]`).
- `include`/`variable ... in` to scope variables to specific declarations.

### 4.3 `variable (f) in` Pattern
```lean
variable (f) in
/-- The unique fixed point of a contracting map ... -/
noncomputable def fixedPoint : α :=
  efixedPoint f hf _ (edist_ne_top (Classical.choice ‹Nonempty α›) _)
```
The `variable (f) in` makes `f` explicit for just that one declaration.

---

## 5. Attribute Usage Patterns

### 5.1 `@[simp]` — Simplification Lemmas
Used on lemmas that should be applied automatically by the `simp` tactic:
```lean
@[simp]
theorem nodupKeys_nil : @NodupKeys α β [] :=
  Pairwise.nil

@[simp]
theorem nodupKeys_cons {s : Sigma β} {l : List (Sigma β)} :
    NodupKeys (s :: l) ↔ s.1 ∉ l.keys ∧ NodupKeys l := by simp [keys, NodupKeys]
```
*Source: `Mathlib/Data/List/Sigma.lean`*

Priority variants: `@[simp 1100]`, `@[simp default + 1]`.

**Terminal `simp` policy**: Terminal `simp` calls (that close a goal) should generally **not** be squeezed. Squeezed `simp` is fragile to renames and drowns key info in noise. Non-terminal `simp` should be squeezed.

### 5.2 `@[ext]` — Extensionality
```lean
@[ext]
lemma ext {X Y : Lat} {f g : X ⟶ Y} (w : ∀ x : X, f x = g x) : f = g :=
  ConcreteCategory.hom_ext _ _ w
```
*Source: `Mathlib/Order/Category/Lat.lean`*

Can also be placed on structures to auto-generate extensionality lemmas:
```lean
@[ext]
structure Hom (X Y : Lat.{u}) where
  private mk ::
  hom' : LatticeHom X Y
```

### 5.3 `@[measurability]` — Measurability Lemmas
```lean
@[measurability]
theorem Finset.measurable_sup' {ι : Type*} {s : Finset ι} (hs : s.Nonempty) {f : ι → δ → α}
    (hf : ∀ n ∈ s, Measurable (f n)) : Measurable (s.sup' hs f) :=
  Finset.sup'_induction hs _ (fun _f hf _g hg => hf.sup hg) fun n hn => hf n hn
```
*Source: `Mathlib/MeasureTheory/Order/Lattice.lean`*

### 5.4 `@[fun_prop]` — Function Property Automation
```lean
@[fun_prop]
theorem Measurable.const_sup (hf : Measurable f) (c : M) :
    Measurable fun x => c ⊔ f x :=
  (measurable_const_sup c).comp hf
```
*Source: `Mathlib/MeasureTheory/Order/Lattice.lean`*

Solves goals of the form `P f` by decomposing `f` into compositions.

### 5.5 `@[positivity]` — Positivity Extensions
```lean
@[positivity ite _ _ _]
def evalIte : PositivityExt where eval {u α} zα pα e := do ...

@[positivity min _ _]
def evalMin : PositivityExt where eval {u α} zα pα e := do ...

@[positivity _ + _]
def evalAdd : PositivityExt where eval {u α} zα pα e := do ...
```
*Source: `Mathlib/Tactic/Positivity/Basic.lean`*

Registered via pattern matching on expression structure.

### 5.6 `@[continuity]` — Continuity Lemmas
Similar pattern to `@[measurability]` for `Continuous` predicates.

### 5.7 `@[to_additive]` — Multiplicative/Additive Duality
```lean
@[to_additive]
theorem dist_eq_norm_inv_mul ...

@[to_additive (attr := simp)]   -- combines with @[simp]
theorem inseparable_one_iff_norm ...
```
*Source: `Mathlib/Analysis/Normed/Group/Basic.lean`*

### 5.8 `@[deprecated]` — Graceful Deprecation
```lean
@[deprecated (since := "YYYY-MM-DD")]
alias old_name := new_name

@[deprecated "Use ... instead" (since := "YYYY-MM-DD")]
theorem example_thm ...
```

---

## 6. Docstring Conventions

### 6.1 Module Docstrings: `/-! ... -/`
Used for section headers, file documentation, and separators within a file:
```lean
/-!
# (Semi)normed groups: basic theory
-/
```
*Source: `Mathlib/Analysis/Normed/Group/Basic.lean`*

Also used as **section separators** within a file (not just at the top).

### 6.2 Declaration Docstrings: `/-- ... -/`
```lean
/-- A map is said to be `ContractingWith K`, if `K < 1` and `f` is `LipschitzWith K`. -/
def ContractingWith [EMetricSpace α] (K : ℝ≥0) (f : α → α) :=
  K < 1 ∧ LipschitzWith K f

/-- Let `x` be a point of a complete emetric space. Suppose that `f` is a contracting map,
and `edist x (f x) ≠ ∞`. Then `efixedPoint` is the unique fixed point of `f`
in `Metric.eball x ∞`. -/
noncomputable def efixedPoint ...
```
*Source: `Mathlib/Topology/MetricSpace/Contracting.lean`*

Rules:
- Subsequent lines of multi-line docstrings are **not** indented.
- Use backticks for inline code references.
- Every **structure field** must have a docstring.

### 6.3 Comments
- `/-! -/` for module docs and section headers (auto-included in generated docs)
- `/- -/` for technical comments, TODOs, implementation notes
- `--` for short inline comments

---

## 7. Proof Style

### 7.1 Tactic Mode
The preferred style for non-trivial proofs. `by` goes on the **same line** as `:=`, never on a line by itself:

```lean
theorem exists_fixedPoint (hf : ContractingWith K f) (x : α) (hx : edist x (f x) ≠ ∞) :
    ∃ y, IsFixedPt f y ∧ Tendsto (fun n ↦ f^[n] x) atTop (𝓝 y) ∧
      ∀ n : ℕ, edist (f^[n] x) y ≤ edist x (f x) * (K : ℝ≥0∞) ^ n / (1 - K) := by
  ...
```

### 7.2 Term Mode
Used for simple proofs:
```lean
theorem toLipschitzWith (hf : ContractingWith K f) : LipschitzWith K f := hf.2

theorem one_sub_K_ne_zero (hf : ContractingWith K f) : (1 : ℝ≥0∞) - K ≠ 0 :=
  ne_of_gt hf.one_sub_K_pos'

theorem restrict (hf : ContractingWith K f) {s : Set α} (hs : MapsTo f s s) :
    ContractingWith K (hs.restrict f s s) :=
  ⟨hf.1, fun x y ↦ hf.2 x y⟩
```
*Source: `Mathlib/Topology/MetricSpace/Contracting.lean`*

### 7.3 `calc` Blocks
Align relation symbols; `_` placeholders left-justified:
```lean
theorem edist_inequality (hf : ContractingWith K f) {x y} (h : edist x y ≠ ∞) :
    edist x y ≤ (edist x (f x) + edist y (f y)) / (1 - K) :=
  suffices edist x y ≤ edist x (f x) + edist y (f y) + K * edist x y by
    rwa [ENNReal.le_div_iff_mul_le ...]
  calc
    edist x y ≤ edist x (f x) + edist (f x) (f y) + edist (f y) y := edist_triangle4 _ _ _ _
    _ = edist x (f x) + edist y (f y) + edist (f x) (f y) := by rw [edist_comm y, add_right_comm]
    _ ≤ edist x (f x) + edist y (f y) + K * edist x y := add_le_add le_rfl (hf.2 _ _)
```
*Source: `Mathlib/Topology/MetricSpace/Contracting.lean`*

### 7.4 Focusing Dots
New subgoals use `·` (not indented relative to `by`):
```lean
theorem ... := by
  refine ⟨y, y.2, Subtype.ext_iff.1 hfy, ?_, fun n ↦ ?_⟩
  · convert (continuous_subtype_val.tendsto _).comp h_tendsto
    simp only [...]
  · convert hle n
    rw [MapsTo.iterate_restrict]
    rfl
```

### 7.5 Mixing Term and Tactic Mode
```lean
theorem ... : IsUnit (↑u * a) ↔ IsUnit a :=
  Iff.intro
    (fun ⟨v, hv⟩ => by
      have : IsUnit (↑u⁻¹ * (↑u * a)) := by exists u⁻¹ * v; rw [← hv, Units.val_mul]
      rwa [← mul_assoc, Units.inv_mul, one_mul] at this)
    u.isUnit.mul
```

### 7.6 Formatting Rules
- **Line length**: max 100 characters.
- **Indent**: 2 spaces for proof body; 4 spaces for continuation of theorem statement.
- **Spaces**: around `:`, `:=`, and infix operators.
- Put `:=` before a line break, not at the start of next line.
- **No empty lines** inside declarations (linter-enforced).
- **No `λ`**: use `fun` keyword exclusively.
- **`↦` preferred** over `=>` in lambdas (printed by pretty printer).
- **`<|`** preferred over `$`; use to avoid deep parenthesization.
- One tactic per line (short related sequences may use `;`).

---

## 8. Instance & Structure Conventions

### 8.1 `where` Syntax
```lean
instance instOrderBot : OrderBot ℕ where
  bot := 0
  bot_le := Nat.zero_le
```

### 8.2 Structure Field Docstrings
Every field must have a docstring:
```lean
structure PrincipalSeg {α β : Type*} (r : α → α → Prop) (s : β → β → Prop) extends r ↪r s where
  /-- The supremum of the principal segment -/
  top : β
  /-- The image of the order embedding is the set of elements `b` such that `s b top` -/
  down' : ∀ b, s b top ↔ ∃ a, toRelEmbedding a = b
```

### 8.3 Hypotheses Left of Colon
Prefer explicit arguments over universal quantifiers:
```lean
-- Preferred:
example (n : ℝ) (h : 1 < n) : 0 < n := by linarith

-- Avoid:
example (n : ℝ) : 1 < n → 0 < n := fun h ↦ by linarith
```

### 8.4 Explicit Types
All argument types and return types should be explicit:
```lean
-- Good:
def GoodStatement (n : ℕ) : Prop := ∃ k : ℕ, n + k = 3

-- Bad:
def BadStatement (n) := ∃ k, n + k = 3
```

---

## 9. Transparency & API Design

| Keyword | Transparency | Usage |
|---------|-------------|-------|
| `def` | semireducible (default) | Most definitions |
| `abbrev` | reducible + inline | Definitional abbreviations |
| `structure` | opaque wrapper | Type synonyms, sealed APIs |
| `irreducible_def` | kernel-irreducible | Only with documented profiling need |

- Default is `semireducible` — don't use `abbrev` without good reason.
- Avoid `erw`/`rfl` after `simp`/`rw` — indicates missing API lemmas.

---

## 10. Normal Forms

- Settle on one canonical form for equivalent statements.
- Register `@[simp]` lemmas to convert to the normal form.
- Special case for `⊥`/`⊤`:
  - Use `x ≠ ⊥` in **assumptions** (easier to provide).
  - Use `⊥ < x` in **conclusions** (more powerful result).

---

## 11. Tactic Extension Registration

### Environment Extensions
```lean
structure FunPropDecl where
  funPropName : Name
  path : Array DiscrTree.Key
  funArgId : Nat

initialize funPropDeclsExt : FunPropDeclsExt ←
  registerSimpleScopedEnvExtension { ... }
```
*Source: `Mathlib/Tactic/FunProp/Decl.lean`*

### Tactic Attribute Pattern
```lean
@[positivity ite _ _ _]
def evalIte : PositivityExt where eval {u α} zα pα e := do
  ...
```
*Source: `Mathlib/Tactic/Positivity/Basic.lean`*

Pattern: `@[tactic_name pattern]` registers a handler that matches expression structure.

---

## 12. Performance Conventions

- Benchmark PRs that add classes, instances, `@[simp]` lemmas, or change imports.
- Comment `!bench` on PRs to trigger CI benchmarking.
- Non-terminal `simp` calls should be squeezed (use `simp?`).
- Terminal `simp` calls should generally **not** be squeezed.

---

## Summary of Key Differences from General Lean 4

| Convention | Mathlib | General Lean 4 |
|-----------|---------|----------------|
| Naming | Strict snake_case/CamelCase rules | Flexible |
| Module docstrings | Required with Main results section | Optional |
| Structure fields | Must have docstrings | Optional |
| `fun` vs `λ` | `fun` only, `λ` forbidden | Both valid |
| `↦` vs `=>` | `↦` preferred | `=>` common |
| `<|` vs `$` | `<|` only, `$` forbidden | Both valid |
| Line length | 100 chars max | No enforced limit |
| Empty lines in proofs | Forbidden (linter) | Allowed |
| Terminal simp | Not squeezed | N/A |
| Import style | Narrow, specific paths | Any |
| `assert_not_exists` | Used to enforce import boundaries | Rare |
| Types explicit | All argument/return types stated | Type inference common |
