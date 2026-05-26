# Template_DataModule.md — v2 data / carrier-type Lean module

> **Status:** v2 production template (extracted from
> `_v2-proposals/proof-templates-v2.md §2`).
> Use this in **any** Lean 4 + Mathlib project for *leaf* modules whose
> primary purpose is **defining a data type** (structure, inductive,
> record, or fintype enumeration) and the minimum decidability + `simp`
> API that downstream proofs need.
>
> Companion v1: [`Template_Foundation.md`](./Template_Foundation.md).

---

## 1. When to use this template

Apply `Template_DataModule` when a module:

* Defines **one carrier type** (`structure`, `inductive`, `abbrev`)
  plus its closest API (`mk`-field `@[simp]` lemmas, decidability
  predicates, one or two `@[grind]` bridge lemmas).
* Will be **imported by ≥ 2 sibling modules** (proof modules,
  tactic helpers, applications).
* Sits at **Layer-0 / Layer-1** of the build graph — i.e., should
  **not** import `Mathlib.Tactic` or heavy analysis files.

**Do NOT use** for:

* Modules that prove substantive theorems → use [`Template_Theorem.md`](./Template_Theorem.md).
* Modules that compose data types into bigger theorems →
  use [`Template_Application.md`](./Template_Application.md).
* Modules whose sole purpose is re-exporting →
  use [`Template_Index.md`](./Template_Index.md) or [`Template_Bridge.md`](./Template_Bridge.md).

---

## 2. Customisation checklist

| Placeholder            | Decide                                                                | Common defaults                                                          |
|------------------------|-----------------------------------------------------------------------|--------------------------------------------------------------------------|
| `<Project>`            | Top-level namespace                                                   | Matches `package` in `lakefile.lean`                                     |
| `<Path>`               | Dotted module path under `<Project>/`                                 | E.g. `Probability.Coin`                                                  |
| `<Type>`               | The carrier name (`PascalCase`)                                       | E.g. `Coin`, `Simplex3`, `Outcome`                                        |
| Field set              | Pick a **representative scale** (see §3)                              | Project-wide convention; document in `<Project>/AGENT.md`                |
| `<wave-tag>` (optional)| Your change-tracking tag                                              | Drop the line if no waveplan                                             |
| `<Mathlib.Path>` migration target | A specific upstream PR or future Mathlib namespace          | Drop the TODO if no migration planned                                    |

### 3. Scale convention (when to use scaled `Nat`)

A common pattern in formally-verified projects is to represent
probabilities or fractions as **scaled `Nat`** rather than `Rat` /
`Real`, because `Nat` arithmetic supports `decide` (and avoids
`noncomputable`).

| Scale          | Means                       | Use when                                              |
|----------------|-----------------------------|-------------------------------------------------------|
| `×100`         | Percent (basis: 100)        | Coarse probabilities (`r : Nat`, `r ≤ 100`)           |
| `×10000`       | Basis points (basis: 10⁴)   | Financial-style rates, 4-decimal precision            |
| `×2^N`         | Binary scale                | Bit-precision arithmetic, hardware models             |
| (none — `Rat`) | Exact rationals             | When `decide` is not required                          |
| (none — `ℝ`)   | Reals                       | Continuous analysis (use the proof-template instead)  |

**Hard rule.** Mixing scales in one struct is a top source of cast
errors.  If a field is `×100` and another is `×10000`, **split into two
structs** with a bridge.

---

## 4. Mandatory file-doc top block

```lean
/-
Copyright (c) <YEAR> <Project> Authors.  Released under Apache 2.0.
-/
```

The `## Scale convention` heading is mandatory whenever any field is
scaled-`Nat`.

---

## 5. Full template

```lean
/-
Copyright (c) <YEAR> <Project>.
Released under Apache 2.0 license.
-/

-- Narrow Mathlib imports only; no `import Mathlib.Tactic` in a leaf data module.
import Mathlib.Data.Nat.Defs
import Mathlib.Order.Basic
-- import Mathlib.Data.Real.Basic   -- only if the type is real-valued

set_option autoImplicit false

/-!
# <Project>.<Path> — <Title> (data module)

<One-paragraph summary.>

## Scale convention
* `<field1> : Nat` is `<field1>_real * 100` (i.e., `0 ≤ <field1> ≤ 100`)
* `<field2> : Nat` is `<field2>_real * 10000`
* Real-valued analogue lives in `<Project>.<Path>R`; bridge in
  `<Project>.<Path>.Bridge` (see `## See also`).

## Sections
* §1  Core types
* §2  Constructor `@[simp]` pack
* §3  Decidable predicates
* §4  `@[grind]` bridge lemmas
* §5  Unit-test `by decide` block

## Migration target
TODO(<wave-tag>, mathlib PR #<NNN>): once `<Mathlib.Path>` lands, re-anchor
`<Type>` on `<MathlibType>` via `<bridge-pattern>`.  Tracking:
`docs/<your-tracking-path>`.

## Reference
* `<paper>.tex` §"<Name>" *(or your ADR / spec / RFC link)*

## Tags
template, data-module, leaf, decidable, grind
-/

namespace <Project>.<Path>

-- ## Variables (rare in data modules; usually only needed by §4)

-- ## Definitions

/-- <One-line description of the simplex / record>.

    Fields are `Nat`-scaled `×<N>`; see `## Scale convention` above.
    All hypothesis fields (`hSimplex`, `h<field>_nonneg`, ...) are stored
    so that downstream operators can construct the result
    without re-proving membership. -/
@[ext]
structure <Type> where
  r        : Nat       -- ×100
  s        : Nat       -- ×100
  k        : Nat       -- ×100
  hSimplex : r + s + k = 100
  deriving Repr, DecidableEq
  -- Add `deriving Inhabited, Hashable` only when actually needed downstream.

/-- Canonical "uniform" instance.  Provided as a `def`, not an `instance`,
    so callers must opt-in. -/
def uniform : <Type> :=
  ⟨33, 33, 34, by decide⟩  -- prefer `by decide` over `by norm_num` for Nat.

-- ## Main statements / API surface
-- (Light here; heavy theorems belong in the Theorem template.)

-- ============================================================
-- §2  Constructor `@[simp]` pack
-- ============================================================

/-- Field projection of `mk`.  Required so `simp` can normalise
    field accesses through the constructor. -/
@[simp] theorem r_mk (r s k : Nat) (h : r + s + k = 100) :
    (<Type>.mk r s k h).r = r := rfl
@[simp] theorem s_mk (r s k : Nat) (h : r + s + k = 100) :
    (<Type>.mk r s k h).s = s := rfl
@[simp] theorem k_mk (r s k : Nat) (h : r + s + k = 100) :
    (<Type>.mk r s k h).k = k := rfl

/-- Named-instance projection pack.  Mirror this 3-pack for every
    *named* `<Type>` instance (uniform, peaked, balanced, ...). -/
@[simp] theorem uniform_r : uniform.r = 33 := rfl
@[simp] theorem uniform_s : uniform.s = 33 := rfl
@[simp] theorem uniform_k : uniform.k = 34 := rfl

-- ============================================================
-- §3  Decidable predicates  (Bool-valued at leaf level)
-- ============================================================

/-- Bool-valued gate predicate; lifts to `Prop` only when needed. -/
def passes (x : <Type>) : Bool := 30 ≤ x.r && 30 ≤ x.s

-- ============================================================
-- §4  `@[grind]` bridge lemmas
-- ============================================================

/-- Component bound: on the ×100 simplex, every coordinate ≤ 100.
    Tagged `@[grind .]` ("default direction") so grind picks it up
    in either orientation. -/
@[grind .]
theorem component_le (x : <Type>) : x.r ≤ 100 ∧ x.s ≤ 100 ∧ x.k ≤ 100 := by
  have h := x.hSimplex; grind

-- ============================================================
-- §5  `by decide` smoke tests
-- ============================================================

example : passes uniform = true := by decide
example : passes ⟨10, 10, 80, by decide⟩ = false := by decide

end <Project>.<Path>

-- ## API exports
-- Re-export so consumers `import <Project>.<Path>` and use unqualified names.
export <Project>.<Path> (<Type> uniform passes component_le)

-- ## Leaf-module guards (only in true Layer-0 files)
-- Hard guard: fail compile if `Real` snuck in transitively.
-- assert_not_exists Real
-- Soft guard: warn if a heavy analysis file was imported.
-- assert_not_imported Mathlib.Analysis.SpecialFunctions.Sqrt

/- ## See also
   * `skills/templates/Template_Theorem.md` — proof-heavy companions
   * `skills/templates/Template_Bridge.md` — `<Type>R` ↔ `<Type>` real bridge
   * `<Project>/AGENT.md §"Scaled Integer Arithmetic"` — scale-convention rationale
-/
```

---

## 6. Inline anti-patterns

```lean
-- ANTI-PATTERN: hiding the scale in the field name.  Use `r : Nat` with a
-- `## Scale convention` header, NOT `r100 : Nat`/`r1000 : Nat` interleaved.
-- Mixed scales in one struct are a major source of cast errors.

-- ANTI-PATTERN: `noncomputable instance : Fintype <Type>` blocks `decide`.
-- Prefer `Fintype.ofList`/`Fintype.ofEquiv` enumeration when the underlying
-- set is finite (~50 LOC refactor unlocks ∀-quantifier proofs).

-- ANTI-PATTERN: `import Mathlib.Tactic` in a data module.  Pulls in the full
-- tactic surface (≥ 30s compile penalty).  Import only what you need.

-- ANTI-PATTERN: structure with no `@[ext]`.  Breaks `ext` tactic for record
-- equality.  Always add `@[ext]` to record-like structures.

-- ANTI-PATTERN: `deriving Inhabited` "in case".  `Inhabited` ties you to a
-- distinguished default; only derive it when a downstream tactic (e.g.
-- `inhabit`) actually requires it.
```

---

## 7. Worked 10-LOC example

```lean
namespace MyProj.Probability

@[ext] structure Coin where
  heads  : Nat                 -- ×100; heads ∈ [0, 100]
  hBound : heads ≤ 100
  deriving Repr, DecidableEq

def fair : Coin := ⟨50, by decide⟩
@[simp] theorem fair_heads : fair.heads = 50 := rfl
@[grind .] theorem heads_le_100 (c : Coin) : c.heads ≤ 100 := c.hBound
example : fair.heads = 50 := by decide

end MyProj.Probability
export MyProj.Probability (Coin fair)
```

---

## 8. What v2 adds over v1 (`Template_Foundation.md`)

| Addition                                                              | Rationale                                                                                                |
|-----------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| Simplex-structure pattern with stored `hSimplex` + per-field proofs   | Downstream operators don't have to re-prove membership; eliminates a whole class of redundant lemmas.    |
| Named-instance `@[simp]` pack convention                              | Makes `simp` unfold named instances symmetrically with `mk`-built ones.                                  |
| Scale-convention header (mandatory when scaled-`Nat`)                 | Forces author to record the multiplier so readers and tooling can detect cast errors.                    |
| Migration-target TODO slot                                            | Signals when a leaf module is provisional pending an upstream Mathlib change.                            |
| `@[grind .]` dotted-direction syntax                                  | Matches the modern grind annotation catalog; symmetric/bidirectional default.                            |
| `## API exports` block                                                | Lets consumers import the data module and write unqualified names.                                       |
| Hard-removal of `§14 recursion/termination`                           | Recursion belongs in a Recursion template, not in every leaf data module.                                |

---

## 9. See also

* [`Template_Theorem.md`](./Template_Theorem.md) — proof-heavy companion
* [`Template_TacticHelper.md`](./Template_TacticHelper.md) — where to put cross-cutting `@[grind]` bridge lemmas
* [`Template_Bridge.md`](./Template_Bridge.md) — `Nat`-scaled ↔ `ℝ` bridge between leaf and analytic modules
