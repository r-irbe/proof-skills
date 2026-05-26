# Proof-Templates v2 — Project-Grounded Redesign

**Status:** proposal (no code edits yet — synthesis-ready).
**Inputs:** existing `skills/templates/Template_*.md`, ~40 KLOC Project corpus
(`Project/`), `Project/AGENT.md` (REC-031, Common Patterns, Domain Conventions),
`docs/tracking/{proof_quality,axiom_audit}.md`.
**Audience:** future template-synthesis pass that will overwrite
`skills/templates/Template_{Foundation,Analysis,Automation,Application}.md`
(and add a `Template_Bridge.md`).

## Template-name mapping

The four "conceptual" templates named in the brief do not exist verbatim. They
map onto the canonical 12-template set as follows; the v2 proposal keeps the
canonical names but treats them as the conceptual roles:

| Brief name              | Existing canonical file        | Role in the project                                      |
|-------------------------|--------------------------------|----------------------------------------------------|
| `Template_Theorem`      | `Template_Analysis.md`         | Proof-heavy modules (Banach, Lyapunov, Info-geom)  |
| `Template_DataModule`   | `Template_Foundation.md`       | Types, simplex structures, `Core.lean` files       |
| `Template_TacticHelper` | `Template_Automation.md`       | `Project.Tactics`, custom decide ladders, `@[grind]` |
| `Template_Bridge`       | *(none — to be added)*         | `Project/Bridges/*.lean` facades over upstream libs  |

`Template_Bridge.md` is a **new** template. The existing
`Template_Index.md`/`Template_Application.md` cover umbrella re-exports
and multi-layer composition, but neither captures the facade-over-upstream
pattern used in `Project/Bridges/`.

---

## 1. `Template_Theorem` (≈ `Template_Analysis.md`)

### 1.1 Current template gaps

| Gap                                                                                                                          | Why it matters                                                                                                                   |
|------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| **No file-doc top block convention.** The example header is a short prose blurb; Project uses `/-! # ... ## Sections ## Reference ## Change note -/` with explicit per-section TOC.                              | New theorem files in the project are routinely 600–2500 LOC; readers cannot navigate without a section table.                          |
| **No "paper-anchor" requirement.** Template lists abstract "Main results"; Project mandates `## Reference` pointing to `project-tufte.tex §...` and substrate pin (e.g., `pin 9491746`).                                                                                                          | `AGENT.md §"Paper Cross-References"` (line 240–250) makes this a hard rule.                                                      |
| **No "## Sections" table / `§N` numbering.** Project sections are physically demarcated with `-- ==…==  §N Title  -- ==…==` banners and re-described in `/-! ### §N ... -/`.                                                                                                                  | Required so that `git blame`-friendly section IDs survive splits and rewaves.                                                    |
| **`Real.sqrt` advice is correct but incomplete.** Template prescribes `Real.sqrt_le_sqrt + linarith`; the project's `hellinger_zero_iff_eq` (Information.lean L2405–2433) shows the *real* workhorse pattern: `sq_nonneg` + `le_antisymm` + `Real.sqrt_inj` for "sum of squares = 0 ⇒ each = 0". | Template misses the most common analysis-module shape (sum-of-squares case split).                                               |
| **No guidance on `linear_combination`.** Used heavily in `StochasticCCV/Core/Banach.lean` (e.g. L91, L132, L145, L159, L195) for closing ℚ-arithmetic simplex constraints — far cleaner than `nlinarith`.                                                                                  | Currently `linear_combination` is invisible in the template, despite being the simplex-arithmetic standard.                      |
| **No `## API exports` section.** Project proof modules end with `export NS (name1 name2)` blocks (`KLCore.lean` L92–93, L173–177).                                                                                                                                                          | Without it, downstream `Tests/*.lean` and bridges break when namespaces are restructured.                                        |
| **No "## See also" footer.** Skills, references, and sibling templates are unlinked.                                          | Forces readers to re-discover the rest of the skill ecosystem.                                                                  |
| **`set_option maxHeartbeats N in` example uses 800000 with `linarith`** — misleading, that goal needs no heartbeat bump.      | New users copy the option syntax onto trivial proofs.                                                                            |
| **No anti-pattern: bare `simp` in proof bodies** — exists in `Template_Application.md` but not in `Template_Analysis.md`, even though analysis proofs are the most simp-fragile.                                                                                                          | Project explicitly prefers `simp only [...]`.                                                                                      |

### 1.2 Project evidence

| File (LOC)                                                  | What it teaches                                                                                                                                                                |
|-------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Project/StochasticCCV/Information.lean` (2 513)              | Canonical heavy-theorem-file layout: copyright header → wave-batch banner → `namespace`-wrapped definitions → `end namespace` → big `/-! # Title ## §41…§53 -/` TOC. Demonstrates the §-banner section style and inline `-- W##-B##` change notes (L21–28, L74–80, L2351–2383). |
| `Project/StochasticCCV/Core/Banach.lean` (833)                | Theorem-heavy module with `private` helper lemmas, `linear_combination` (L91, L145, L159, L195), Birkhoff/Doeblin disambiguation prose (L31–50), and `TODO(W3-B7-A3, mathlib PR #38758)` cross-references (L289–300). Shows that template should encourage *disambiguation* prose at the top.        |
| `Project/LyapunovStability/Discrete.lean` (46)                | The **other** valid shape: a 46-LOC sibling-skeleton intentionally kept tiny, with paper anchor (Lyapunov 1907, Khalil 2002) and substrate pin in the file-doc block. Proves "small theorem module" is a first-class shape, not a degenerate one.                                                  |
| `Project/StochasticCCV/Information/KLCore.lean` (177)         | Shows the **`namespace` + `export`** discipline: definitions inside `namespace Project.Information.KL`, then `export Project.Information.KL (klDivergenceCCVR ... fisherMetric_invariant_under_diffeo_reparam)` at end (L92–93, L173–177).                                                              |
| `Project/CCVGating/CCVE/Tangent.lean` (625)                   | Uses `/- Remark: ... -/` blocks (L141–190) for *intent prose without theorems*, replacing former placeholder theorems. Pattern to encourage when a section is "epistemic" rather than provable.                                                                                                    |

### 1.3 Proposed v2 template

```lean
/-
Copyright (c) 2025 <Project> Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: <Project> Contributors
SPDX-License-Identifier: Apache-2.0
-/

import <Project>.<Foundation>.<DependencySubmodule>
import Mathlib.Analysis.<SpecificFile>
-- One Mathlib import per logical capability; never `import Mathlib`.

-- =====================================================================
-- W##-B##-a# <SHORT-CHANGE-TAG> (e.g., W34-B2-a4 mathlib-lift)
-- Source: docs/refactor/wave-##/<plan-file>.md §<section>
-- Critic amendments (if any) and one-line rationale.
-- =====================================================================

set_option autoImplicit false

/-!
# <Project>.<Path> — <Human Title>

<One-paragraph summary: what is proved here, why this layer.>

## Sections

* §<N>    <title>           [<paper-label / T-id, if any>]
* §<N+1>  <title>
* ...

## Substrate (pin <SHA-7>)

* `Mathlib.<File>` — `<lemma family used>`
* `<Project>.<DependencyModule>` — `<types/lemmas relied on>`

## Reference

* `<paper>.tex` §"<Section name>" and §"<Other section>"
* `report/<chapter>.tex` §<N>–§<M> catalogue of theorem labels

## Change note

<Why this file was added/split/renumbered. Cross-reference any prior
wave that produced it. Disambiguate from any siblings or near-namesakes
(e.g., "Doeblin vs Birkhoff–von Neumann vs Birkhoff ergodic — see L31–50
of Banach.lean for the convention").>
-/

namespace <Project>.<Path>

-- ## Variables

variable
  {α : Type*}            -- carrier type (often `ℝ` here)
  (f : α → α)            -- map / dynamics
  (K : ℝ≥0) (hK : K < 1) -- contraction rate
  -- Group with comments; keep order stable across rewaves.

-- ## Definitions

/-- <Concept name>: <one-line characterisation>.

    <Optional second paragraph: design choice, scope, boundary
    conventions (e.g., "Lean's `Real.log 0 = 0` and `x / 0 = 0`
    give a total extension; information-theoretic properties require
    interior hypotheses").>

    Substrate: `Mathlib.<File>.<lemma>`.
-/
noncomputable def <name> (x : α) : ℝ :=
  <expression>

-- ## Main statements
-- (One `-- ============== §N <Title> ============== ` banner per section.)

-- ==================================================
-- §1  <Section title>  [<T-id if applicable>]
-- ==================================================

/-! ### §1 <Section title>

<Multi-paragraph section docstring. Include:
 - what the section proves (one sentence per theorem),
 - which paper claim it discharges,
 - any boundary / domain caveats,
 - any cross-references to sibling sections.> -/

/-- **<Theorem title>** [<paper T-id>]. <Statement in words>.

    <Proof-strategy paragraph: "Proved via X applied to Y; final step
    closes with `linarith` on the assembled bounds.">
-/
theorem <snake_case_name> (h : <Hyp>) : <Goal> := by
  -- One-step-at-a-time per AGENT.md §"Proof Strategy".
  <tac1>
  <tac2>
  -- Close with the lowest-cost terminator that works:
  -- rfl → decide → norm_num → grind → omega → linarith → nlinarith → calc.
  linarith [<explicit hypothesis hints>]

-- ## Proofs (helper lemmas)

/-- Weighted triangle inequality used by §1.  `private` because it leaks
    set-arithmetic and should not pollute the public API. -/
private theorem <helper_name> (a b : ℚ) (hx : 0 ≤ x) :
    |a * x + b * y| ≤ |a| * x + |b| * y := by
  calc |a * x + b * y|
      ≤ |a * x| + |b * y|        := abs_add_le _ _
    _ = |a| * x + |b| * y         := by
        rw [abs_mul, abs_of_nonneg hx, abs_mul, abs_of_nonneg hy]

end <Project>.<Path>

-- ## API exports
-- Re-export the proven symbols at the parent namespace so downstream
-- consumers (Tests, Bridges) do not need to know the internal namespace.
export <Project>.<Path>
  (<main_def_1> <main_def_2>
   <main_theorem_1> <main_theorem_2>)

/- ## See also
   * `skills/templates/Template_DataModule.md` — for the underlying simplex types
   * `skills/templates/Template_TacticHelper.md` — for `@[grind]` bridge lemmas this file relies on
   * `skills/references/lean4-tactic-hierarchy.md` — terminator priority order
   * `skills/skills/lean-math-analysis/SKILL.md` — Mathlib analysis API cards
   * `Project/AGENT.md §"Common Patterns and Pitfalls"` — Nat-scaled vs ℝ bridge patterns
-/
```

**Inline anti-patterns to surface (with one-line rationale):**

```lean
-- ANTI-PATTERN: `nlinarith` on `Real.sqrt` goals.  nlinarith cannot model
-- transcendentals; prefer `Real.sqrt_le_sqrt` + `linarith`, OR the
-- "sum of squares = 0 ⇒ each = 0" pattern from §1.3 evidence (sq_nonneg +
-- le_antisymm + Real.sqrt_inj).  See Information.lean L2405–2433.

-- ANTI-PATTERN: bare `simp` in a finished proof.  Use `simp only [name₁, name₂]`.
-- AGENT.md §"Hard Constraints" treats simp-fragility as a CI risk.

-- ANTI-PATTERN: `set_option maxHeartbeats N` *globally*.  Always scope with
-- `set_option maxHeartbeats N in theorem ...`.  Measure first with
-- `#count_heartbeats`.

-- ANTI-PATTERN: `native_decide` in a proof body.  Banned in the project (Tactics.lean
-- L46–51).  Use the `proj_decide` ladder (decide → decide +kernel
-- → simp only [proj_decide_unfold]; decide) or a structured proof.

-- ANTI-PATTERN: `noncomputable section` wrapping more than the noncomputable
-- defs.  Per REC-031, every noncomputable instance is audited; wrapping
-- computable defs hides them from the audit.
```

**Worked 12-LOC example (compactly demonstrates the shape):**

```lean
namespace MyProj.MyAnalysis

/-- **Sum-of-squares case split**: if `(a)² + (b)² = 0` over ℝ then both vanish. -/
theorem sq_pair_zero_iff {a b : ℝ} : a ^ 2 + b ^ 2 = 0 ↔ a = 0 ∧ b = 0 := by
  refine ⟨fun h => ?_, fun ⟨ha, hb⟩ => by simp [ha, hb]⟩
  have ha : a ^ 2 = 0 := le_antisymm (by linarith [sq_nonneg b]) (sq_nonneg _)
  have hb : b ^ 2 = 0 := le_antisymm (by linarith [sq_nonneg a]) (sq_nonneg _)
  exact ⟨pow_eq_zero_iff two_ne_zero |>.mp ha, pow_eq_zero_iff two_ne_zero |>.mp hb⟩

end MyProj.MyAnalysis
export MyProj.MyAnalysis (sq_pair_zero_iff)
```

### 1.4 Diff vs current `Template_Analysis.md`

* **Add:** file-doc top block (`/-! # Title ## Sections ## Substrate ## Reference ## Change note -/`), wave/batch banner, `## Variables`/`## Definitions`/`## Main statements`/`## Proofs`/`## API exports`/`## See also` skeleton, `linear_combination` example, sum-of-squares pattern, `private`-helper convention, explicit `native_decide` ban, `noncomputable section` warning.
* **Remove/demote:** `set_option maxHeartbeats 800000 in` example (trivial goal — misleading); §10 `bound_tac` (vapor — only prose, no payload); §14 noncomputable-scoping block (move guidance to `## See also → AGENT.md REC-031`).
* **Refactor:** §1–§14 prose collapsed into the unified `## Definitions`/`## Main statements`/`## Proofs` skeleton; one §-banner per logical section, not per technique.
* **Rename rationale:** keep filename `Template_Analysis.md`, but state at the top "Use for proof-heavy modules ('Theorem' modules)".

---

## 2. `Template_DataModule` (≈ `Template_Foundation.md`)

### 2.1 Current template gaps

| Gap                                                                                                                                                                                                                                          | Why it matters                                                                                                                                                |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **No simplex-structure pattern.** the project's `CCVQ`, `CCVR`, `CCVRE` (3- and 4-component simplices) are *the* data-module shape; template only shows `MyRecord {score100, threshold, isValid}`.                                                | Every new domain-data module in the project is a simplex structure with `hSimplex : r + s + k (+ e) = 1` and `hr, hs, hk (, he) : 0 ≤ ·`. Missing this pattern means the template doesn't match how Project actually defines data. |
| **No "auto-constructor `@[simp]` pack" pattern.** `KLCore.lean` L40–43 ships `@[simp] lemma uniformCCVRE_r : uniformCCVRE.r = 1/4 := rfl` × 4. The template shows projection `@[simp]` only on `mk`, not on *named* constructed instances.    | Without this, every `simp` that touches a named distribution stalls.                                                                                          |
| **No `noncomputable def`/`#eval` decision rule.** Template tells users to add `#eval` blocks but does not warn that simplex distributions over ℝ must be `noncomputable` and `#eval` won't work.                                              | REC-031 (AGENT.md L130–151) audits all 122 `noncomputable` instances; users need to know up-front when their def is forced noncomputable.                     |
| **No "scale convention" header block.** Project data modules consistently encode "what does ×100 mean" in the docstring (AGENT.md L173–186); template buries it in §2 prose.                                                                    | Required: every data module should state its scale (×1, ×100, ×1000, ×10000) at the top so consumers do not mix scales.                                       |
| **No "TODO upstream-PR / migration target" pattern.** Project data modules frequently carry `TODO(W3-B7-A3, mathlib PR #38758)` markers that record the planned mathlib migration (Banach.lean L289–300).                                       | Without a slot for this, the migration debt is invisible.                                                                                                     |
| **`Decidable` instance example uses `inferInstance` without showing the `decide_or_decidable_eq` pattern** Project uses (e.g., `interval_cases r <;> assumption` in `regime_exhaustion`).                                                       | Misses the most common finite-state decidability pattern.                                                                                                     |
| **Outdated: `#check_assertions` advice** — template says "in heavily-imported files this may produce a long list". the project's actual practice is to use it only in true leaf modules + after each `assert_not_exists`.                            | Sharpen the rule to "place `#check_assertions` only at the bottom of leaf modules where ≤ 5 assertions exist".                                                |

### 2.2 Project evidence

| File                                                          | What it teaches                                                                                                                                                                                                                                                                       |
|---------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Project/StochasticCCV/Core/Banach.lean` L71–104                | Canonical `CCVQ`/`CCVR` simplex structure: `@[ext]` + 4 hypothesis fields (`hSimplex`, `hr`, `hs`, `hk`) + `okdStepQ` with field-by-field construction + `@[simp]` projection lemmas (`okdStepQ_r/s/k`).                                                                              |
| `Project/StochasticCCV/Information/KLCore.lean` L20–43          | Canonical `CCVRE` (4-component) + `uniformCCVRE` named distribution + 4-pack `@[simp]` projections (`uniformCCVRE_r/s/k/e`). Shows that named distributions are first-class data and need their own `@[simp]` set.                                                                   |
| `Project/CCVGating/CCVE/Tangent.lean` L65–98                    | Showcases the `convexComb` / `convex_preserves_bounds` / `convex_bounded_simple` triad — three layers of decreasing abstraction for the same operation. Pattern: define general, prove bounded, expose simple specialisation.                                                          |
| `Project/CCVGating/CCVE/Tangent.lean` L118–137                  | `CCVE.permute_rske : CCVE → CCVE` shows the field-by-field constructor with `grind` discharging the simplex hypothesis. Template should surface this `⟨...⟩, by ...; grind⟩` pattern for in-place hypothesis discharge.                                                                |
| `Project/LyapunovStability/Discrete.lean`                       | The 46-LOC counter-example: a data module that is just `def IsLyapunovStable f xStar := Function.IsFixedPt f xStar` + one wrapper theorem. Proves that "data module" can be one-screen, and that the template should not force a §1–§14 skeleton.                                      |
| `Project/Tactics.lean` L164–170 (`simplex_component_le`)        | Demonstrates `@[grind .]` (note the dot — "default-direction" annotation). Current template only shows `@[grind]`, `@[grind =]`, `@[grind →]`, `@[grind ←]` — missing the dotted form.                                                                                                |

### 2.3 Proposed v2 template

```lean
/-
Copyright (c) 2025 <Project>.
Released under Apache 2.0 license.
-/

-- Narrow Mathlib imports only; no `import Mathlib.Tactic` in a leaf data module.
import Mathlib.Data.Nat.Defs
import Mathlib.Order.Basic
-- import Mathlib.Data.Real.Basic   -- only if simplex is real-valued

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
`<MyType>` on `<MathlibType>` via `<bridge-pattern>`.  Tracking:
`docs/refactor/<wave>/<plan>.md §<N>`.

## Reference
* `<paper>.tex` §"<Name>" (definition of `<Type>`)

## Tags
template, data-module, simplex, leaf, decidable, grind
-/

namespace <Project>.<Path>

-- ## Variables (rare in data modules; usually only needed by §4)

-- ## Definitions

/-- <One-line description of the simplex / record>.

    Fields are `Nat`-scaled `×<N>`; see `## Scale convention` above.
    All hypothesis fields (`hSimplex`, `h<field>_nonneg`, ...) are stored
    so that downstream `okdStep`-style operators can construct the result
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
    so callers must opt-in (matches the project's `uniformCCVRE` pattern). -/
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
   * `skills/templates/Template_Theorem.md` — for proof-heavy companion modules
   * `skills/templates/Template_Bridge.md` — for the `<Type>R` ↔ `<Type>` real bridge
   * `Project/StochasticCCV/Core/Banach.lean` (`CCVQ`, `CCVR`) — canonical examples
   * `Project/AGENT.md §"Scaled Integer Arithmetic"` — scale convention rationale
   * `docs/tracking/axiom_audit.md` — noncomputable audit rules (REC-031)
-/
```

**Anti-patterns to surface inline:**

```lean
-- ANTI-PATTERN: hiding the scale in the field name.  Use `r : Nat` with a
-- ## Scale convention header, NOT `r100 : Nat`/`r1000 : Nat` interleaved.
-- Mixed scales in one struct are a major source of cast errors.

-- ANTI-PATTERN: `noncomputable instance : Fintype <Type>` blocks `decide`.
-- See AGENT.md L144–151: prefer `Fintype.ofList`/`Fintype.ofEquiv` enumeration
-- when the underlying set is finite (~50 LOC refactor unlocks ∀-quantifier proofs).

-- ANTI-PATTERN: `import Mathlib.Tactic` in a data module.  Pulls in the full
-- tactic surface (≥ 30s compile penalty).  Import only what you need.

-- ANTI-PATTERN: structure with no `@[ext]`.  Breaks `ext` tactic for record
-- equality.  Always add `@[ext]` to record-like structures.

-- ANTI-PATTERN: `deriving Inhabited` "in case".  `Inhabited` ties you to a
-- distinguished default; only derive it when a downstream tactic (e.g. `inhabit`)
-- actually requires it.
```

**Worked 10-LOC example:**

```lean
namespace MyProj.Probability

@[ext] structure Coin where
  heads : Nat       -- ×100; heads ∈ [0, 100]
  hBound : heads ≤ 100
  deriving Repr, DecidableEq

def fair : Coin := ⟨50, by decide⟩
@[simp] theorem fair_heads : fair.heads = 50 := rfl
@[grind .] theorem heads_le_100 (c : Coin) : c.heads ≤ 100 := c.hBound
example : fair.heads = 50 := by decide

end MyProj.Probability
export MyProj.Probability (Coin fair)
```

### 2.4 Diff vs current `Template_Foundation.md`

* **Add:** simplex-structure pattern with `hSimplex` and per-field `h<f>` proofs; named-instance `@[simp]` pack convention; scale-convention header; migration-target TODO slot; `@[grind .]` dotted-direction syntax; `## API exports` block.
* **Remove:** §14 recursion/termination block (belongs in `Template_Foundation` only for *foundational* recursion; data modules rarely need it — move to a `Template_Recursion.md` cross-link).
* **Sharpen:** `#check_assertions` rule ("only in leaf modules with ≤ 5 assertions"); `assert_not_imported` reminder that it emits a *warning*, not an error (already in template — keep but elevate).
* **Refactor:** §1–§14 → §1–§5 + `## See also`. Data modules should rarely exceed ~150 LOC; template's 14-section skeleton encourages over-stuffing.

---

## 3. `Template_TacticHelper` (≈ `Template_Automation.md`)

### 3.1 Current template gaps

| Gap                                                                                                                                                                                                                                          | Why it matters                                                                                                                                  |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| **No "deprecation table" pattern.** `Project.Tactics` ships a *Custom-tactic status* table (L33–44) listing active vs. removed (`proj_*` family) tactics. The template has no slot for this.                                                | Every project that builds a tactic library accumulates dead tactics; without a table, contributors re-introduce them.                            |
| **`first_par` advice is partially outdated.** Template says "not yet implemented in v4.28.0"; OK, but does not record the *expected migration path* (swap `first` → `first_par` when available) or what counts as a "branch independence" check. | Sets the wrong expectation that this will "just work later".                                                                                     |
| **No `register_simp_attr` pattern.** Project uses `register_simp_attr proj_decide_unfold` (Tactics.lean L107) to maintain a *whitelisted simp set* gated to one tactic. The template covers `register_grind_attr` but not the simp analogue.    | Important for build-stable custom decide ladders that don't leak into general `simp`.                                                            |
| **No `decide +kernel` rung.** the project's `proj_decide` ladder (Tactics.lean L114–119) is `first | decide | decide +kernel | (simp only […]; decide)`. Template omits the `+kernel` rung.                                                       | `decide +kernel` is the canonical replacement for `native_decide` in kernel-checked proofs.                                                      |
| **No "0 cross-module uses ⇒ delete" rule.** Project deleted all 8 `proj_*` Qq tactics in W3-B9-A1 after observing zero cross-module use (Tactics.lean L40–44).                                                                                  | Without this rule, tactic libraries accrete dead code.                                                                                          |
| **`@[grind]` variant catalog missing the `.` (dotted) form.** Project uses `@[grind .]` for symmetric/bidirectional lemmas (Tactics.lean L164, L230, L429).                                                                                      | The dot is undocumented in the template; new users won't know it exists.                                                                         |
| **No "consolidation macro" guidance.** the project's `mono_corollaries` / `iterate_mono` / `bridge_chain` macros (L37) survived the deprecation pass because they had multi-module use; template doesn't articulate the survival rule.              | Encourages premature macro extraction.                                                                                                          |
| **No "native_decide audit" link.** the project's `scripts/check-native-decide.sh` enforces zero `native_decide` in proof bodies; template only mentions in passing.                                                                                  | Auditing must be discoverable from the template.                                                                                                |
| **`grind_lint`, `grind +suggestions` examples are present but not connected to a dev workflow.** the project's workflow is "tag → measure → demote": tag with `+suggestions`, measure with `#grind_lint check`, demote to `simp only` once stable. | Template lists features without prescribing how to use them in sequence.                                                                         |

### 3.2 Project evidence

| File / location                                                                  | What it teaches                                                                                                                                                                                       |
|----------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Project/Tactics.lean` L13–82 (file-level doc-comment)                              | Canonical tactic-module header: key annotations table, custom-tactic status table (with "active / removed / DELETED W3-B9-A1" rows), `native_decide` policy, library-comparison rationale, proof-search strategy ladder, references block.                                  |
| `Project/Tactics.lean` L85–119 (`proj_decide` ladder)                              | The full `register_simp_attr <X>_decide_unfold` + `syntax X : tactic` + `macro_rules ... first | decide | decide +kernel | (simp only […]; decide)` pattern. Replaces `native_decide` while keeping the trust base small.                                                    |
| `Project/Tactics.lean` L40–44 + L121–141                                            | Demonstrates the deprecation+deletion workflow: dead tactics are first removed from `macro_rules`, then the surrounding section is rewritten as a "(DELETED W3-B9-A1)" tombstone comment. Pattern preserves traceability.                                              |
| `Project/Tactics.lean` L164–243 (simplex/contraction bridge lemmas)                 | Shows `@[grind .]` (L164, L230, L429) and `@[grind →]` (L240) distinctions, plus the docstring style (4–6 lines: what + which downstream modules consume + dispatched-by tactic).                                                                                       |
| `Project/AGENT.md` L161–169 (Project-tuned cheat-sheet)                               | Concrete tactic-helper patterns to bake into the template: `push_cast; ring` for Nat→Int; `convert h using N <;> push_cast <;> omega`; `zify [bound]; simp only [Int.abs_eq_natAbs]; linarith`; `le_div_iff₀ + exact_mod_cast`. Template currently surfaces none of these. |

### 3.3 Proposed v2 template

```lean
/-
Copyright (c) 2025 <Project>.
Released under Apache 2.0 license.
-/

-- A tactic module DOES intentionally pull a broad tactic surface.
-- This is the one exception to "no `import Mathlib.Tactic`".
import Mathlib.Tactic
import Mathlib.Topology.MetricSpace.Contracting   -- for ContractingWith helpers
-- Add the specific Mathlib files your bridge lemmas reference.

set_option autoImplicit false

/-! # <Project>.Tactics — Reusable Automation and Bridge-Lemma Library

<One-paragraph rationale.  Include the count: "N bridge lemmas + M custom
tactics".  This file is the central tactic-helper module; everything else
in the project imports it.>

## Key annotations

- `@[ext]` on …
- `@[grind]`, `@[grind .]`, `@[grind →]`, `@[grind ←]`, `@[grind =]`,
  `@[grind norm]`, `@[grind unfold]` — see §0 for the full catalog.
- `@[positivity]`, `@[aesop safe apply]`, `@[fun_prop]` — registered
  extensions; see §6.

## Custom-tactic status table

| Tactic              | Cross-module uses | Status              |
|---------------------|-------------------|---------------------|
| `<proj>_decide`     | many              | active (vN)         |
| `mono_corollaries`  | many              | active (vN)         |
| `iterate_mono`      | many              | active (vN)         |
| (former) `foo_qq`   | 0                 | **DELETED v(N-1)**  |
| (former) `bar_qq`   | 0                 | **DELETED v(N-1)**  |

**Survival rule.**  A custom tactic is retained iff (a) it has ≥ 1
cross-module use in the latest census **or** (b) it is documented as
"intended for downstream consumers (planned wave W##)".  Tactics with 0
cross-module uses after one full wave are deleted; the tombstone is
recorded as `-- (DELETED W##-B##) Removed deprecated <name>`.

## `native_decide` policy

`native_decide` is **banned in proof bodies**.  It is compiler-trusted,
not kernel-checked, and inflates the axiom audit.  Use the
`<proj>_decide` ladder (§1) or a structured proof.  Enforced by
`scripts/lean/check-native-decide.sh`.

## Library comparison and rationale

- `Qq`: keep transitively via Mathlib; do *not* author new Qq tactics
  without ≥ 1 prospective downstream consumer (see Survival rule).
- `Batteries`: transitive via Mathlib.
- `Aesop`: prefer `grind` for arithmetic / SAT-shape goals; reserve
  `aesop` for structural induction on inductive types.

## Proof-search strategy (when stuck)

1. `rfl` → `decide` → `norm_num` → `omega`
2. `grind [<hint-lemma>]`
3. `simp only [<lemma-list>]` followed by `linarith` / `omega`
4. `aesop` (structural / case splits)
5. Loogle / LeanSearch / Reservoir
6. Ask the council (`skills/skills/lean-review-council/SKILL.md`)
-/

-- =====================================================================
-- §0  `@[grind]` variant catalog
-- =====================================================================

/-- The seven `@[grind]` annotations and when to use each.

    | Annotation         | Use for                                            |
    |--------------------|----------------------------------------------------|
    | `@[grind]`         | General hint (no direction)                        |
    | `@[grind .]`       | Symmetric/bidirectional (default-direction marker) |
    | `@[grind =]`       | Equational rewrite (LHS → RHS)                     |
    | `@[grind →]`       | Forward: if hyp matches, add conclusion to ctx     |
    | `@[grind ←]`       | Backward: fire when goal matches conclusion        |
    | `@[grind norm]`    | Normalisation pre-processing (v4.28+)              |
    | `@[grind unfold]`  | Always-unfold in pre-processing (v4.28+)           | -/

-- =====================================================================
-- §1  Custom decide ladder  (replaces `native_decide`)
-- =====================================================================

/-- Whitelisted simp set used by `<proj>_decide` rung 3.  Tag concrete
    `def`s here (e.g. domain-specific helpers) only when bare `decide`
    fails to unfold them. -/
register_simp_attr <proj>_decide_unfold

/-- `<proj>_decide`: kernel-checked replacement for `native_decide`.
    Climbs three rungs (per `docs/refactor/playbooks/native-decide/00-OVERVIEW.md`):
    1. plain `decide`,
    2. `decide +kernel`,
    3. `simp only [<proj>_decide_unfold]; decide`.
    No `native_decide` fallback — exceeding rung 3 means a structured
    proof is required. -/
syntax "<proj>_decide" : tactic
macro_rules
  | `(tactic| <proj>_decide) => `(tactic|
      first
        | decide
        | decide +kernel
        | (simp only [<proj>_decide_unfold]; decide))

-- =====================================================================
-- §2  Bridge lemmas (Nat ×100 ↔ ℝ)
-- =====================================================================

/-- ×100-scaled bound: `n ≤ 100 → (n : ℝ) / 100 ≤ 1`. -/
@[grind ←]
theorem nat100_to_real_le_one {n : Nat} (h : n ≤ 100) :
    (n : ℝ) / 100 ≤ 1 := by
  push_cast; linarith

/-- Cast-placement cheat-sheet (per AGENT.md L161–169):
    * `push_cast; ring`                       — Nat→Int equalities
    * `convert h using N <;> push_cast <;> omega`  — cast-placement misfires
    * `zify [bound]; simp only [Int.abs_eq_natAbs]; linarith`  — natAbs → Int
    * `le_div_iff₀ + exact_mod_cast`          — Int.ediv → ℝ.div
    Surface these as inline `-- PATTERN:` comments next to the relevant lemmas. -/

-- =====================================================================
-- §3  Reusable theorems (geometric decay, regime exhaustion, simplex)
-- =====================================================================

/-- Polymorphic geometric decay over any `CommSemiring`.  Used in:
    LyapunovStability, AgenticSafety, ReinforcementLearning. -/
theorem geometric_decay {α : Type*} [CommSemiring α] {f : ℕ → α} {c : α}
    (h_step : ∀ n, f (n + 1) = c * f n) :
    ∀ n, f n = c ^ n * f 0 := by
  intro n
  induction n with
  | zero => simp
  | succ k ih => rw [h_step, ih]; ring

-- =====================================================================
-- §4  Consolidation macros (survive when ≥ 1 cross-module use)
-- =====================================================================

/-- `<proj>_mono_corollaries`: discharges the standard pack of
    monotonicity corollaries that fall out of a single base ≤-lemma.
    Survives by Survival rule (≥ 3 cross-module uses). -/
macro "<proj>_mono_corollaries" : tactic => `(tactic|
  first
    | (constructor <;> linarith)
    | (refine ⟨?_, ?_, ?_⟩ <;> linarith))

-- =====================================================================
-- §5  Dev workflow: tag → measure → demote
-- =====================================================================

/-! ### Tactic-helper development workflow

1. **Tag**: write the proof with `grind +suggestions` (or `grind?`) to
   discover which lemmas grind wants.
2. **Measure**: run `#grind_lint check` to detect redundant or looping
   `@[grind]` lemmas. Run `#count_heartbeats` to baseline.
3. **Demote**: once the lemma set is stable, replace `grind` with
   `simp only [<explicit list>]` + `linarith`/`omega` in *finished*
   proofs to insulate against future Mathlib `@[simp]` churn.

`first_par` (Lean v4.28.0): syntax parses, tactic **not implemented**.
When implemented, mechanical swap `first` → `first_par`; until then,
keep branches order-independent so the swap is safe. -/

end <Project>.Tactics

/- ## See also
   * `skills/templates/Template_Theorem.md` — proof-heavy consumers
   * `skills/templates/Template_DataModule.md` — `@[grind]`-tagged simplex lemmas
   * `skills/references/lean4-tactic-hierarchy.md` — terminator priority
   * `Project/Tactics.lean` — canonical reference implementation (~2 200 LOC)
   * `Project/AGENT.md §"Proof Search Strategy (Project-specific)"` — cast cheat-sheet
   * `scripts/lean/check-native-decide.sh` — CI enforcement
   * `scripts/lean/proof_quality.py` — heuristic quality audit
-/
```

**Anti-patterns to surface inline:**

```lean
-- ANTI-PATTERN: writing a Qq-based custom tactic before there is ≥ 1
-- downstream consumer.  the project's 8-tactic `proj_*` Qq family was deleted
-- in W3-B9-A1 after zero cross-module use (Tactics.lean L40–44).

-- ANTI-PATTERN: `@[grind]` on every helper "in case".  `grind_lint check`
-- will flag the duplicates; the looping ones will silently slow every
-- downstream `grind` call.  Tag only what is consumed.

-- ANTI-PATTERN: `@[simp]` with no LHS-complexity discipline.  Every
-- `@[simp]` lemma must satisfy: LHS strictly "larger" than RHS, terminates,
-- orthogonal LHS patterns within the file.  Run `simp?` to verify normal forms.

-- ANTI-PATTERN: `@[aesop safe apply]` on a lemma with side conditions.
-- Aesop will loop trying to discharge them.  Use `unsafe 50% apply` or
-- attach the side conditions as `@[aesop norm]` instead.

-- ANTI-PATTERN: leaving a custom macro alive after it loses its consumers.
-- One full wave of zero cross-module use ⇒ delete + tombstone comment.
```

**Worked 14-LOC example:**

```lean
namespace MyProj.Tactics

register_simp_attr myproj_decide_unfold

/-- Decide ladder: kernel-checkable, no native_decide. -/
syntax "myproj_decide" : tactic
macro_rules
  | `(tactic| myproj_decide) => `(tactic|
      first
        | decide
        | decide +kernel
        | (simp only [myproj_decide_unfold]; decide))

@[grind ←] theorem nat100_le_one {n : Nat} (h : n ≤ 100) :
    (n : ℝ) / 100 ≤ 1 := by push_cast; linarith

end MyProj.Tactics
```

### 3.4 Diff vs current `Template_Automation.md`

* **Add:** custom-tactic status table, deprecation/survival rule, `native_decide` policy block, `decide +kernel` rung, `register_simp_attr` pattern, `@[grind .]` dotted variant, Project cast cheat-sheet (`push_cast; ring`, `convert ... using N`, `zify [bound]`, `le_div_iff₀`), tag-measure-demote workflow.
* **Remove:** §3 grind-pattern speculative example (no working Project consumer); §6 `@[positivity]` extension stub (highly advanced, deserves its own skill — link out); §10 `Qq`-meta-programming skeleton (encourages premature Qq use — replace with the **don't write Qq until ≥ 1 consumer** rule).
* **Sharpen:** `first_par` block (one paragraph: parses-only, swap when implemented, branch-independence requirement); §11 `grind?` / `grind +suggestions` block (collapse into §5 dev workflow).
* **Re-order:** §0 grind catalog → §1 decide ladder → §2 bridge lemmas → §3 reusable theorems → §4 consolidation macros → §5 dev workflow. Front-loads the everyday-needed material.

---

## 4. `Template_Bridge` (NEW)

### 4.1 Current template gaps

No existing template covers the **Project/Bridges/** pattern: a thin façade module
that re-exports symbols from an upstream library (Cslib, Mathlib, future
Pantograph/TensorLib) under the project's own namespace, optionally adding
project-local primitives for gaps in the upstream API.

`Template_Index.md` and `Template_Application.md` are adjacent but not the
same shape:

| Template                | Re-exports from           | Adds new defs?      | Has substrate pin?  | Has bridge-local primitives? |
|-------------------------|---------------------------|---------------------|---------------------|------------------------------|
| `Template_Index`        | sibling project modules   | no                  | no                  | no                           |
| `Template_Application`  | sibling project modules   | yes                 | no                  | no                           |
| **`Template_Bridge`**   | **upstream third-party**  | yes (project-local) | **yes (SHA-pinned)**| **yes (gap-fillers)**        |

### 4.2 Project evidence

| File                                                | What it teaches                                                                                                                                                                                                                                                                                                                                                |
|-----------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Project/Bridges/CslibInferenceSystem.lean` (46 LOC)  | Canonical bridge: file-doc with pin provenance (`cslib pin : 6be5d165…`, `toolchain : v4.30.0-rc2`), narrow `import Cslib.Foundations.Logic.InferenceSystem`, `abbrev` aliases under `Project.Bridges.CslibInferenceSystem`, `_root_.Cslib.Logic.InferenceSystem` explicit pathing, one bridge-local `Admissible` primitive (no upstream equivalent at the pin), small `mono`/`false` API. |
| `Project/Bridges/CslibLTS.lean` (48 LOC)              | The "pure facade" form: only `abbrev` aliases, no bridge-local primitives. Notably uses nested `namespace Project / namespace Bridges / namespace CslibLTS` instead of dotted form — both forms are valid; the template should pick the dotted form as canonical for grep-friendliness.                                                                            |
| `Project/Bridges/InfoGeom_FractalGeom_Sketch.lean`    | The "sketch" form: bridge that does not yet re-export anything, only documents the *intended* upstream once it stabilises. Pattern: stub files are first-class.                                                                                                                                                                                                |
| `Project/StochasticCCV/Core/Banach.lean` L52–58, L289–300 | "Embedded bridge": when a full file is too heavy, an inline `### CCVR predicate (W3-X3 / PR #38758)` block + `TODO(W3-B7-A3, mathlib PR #38758)` marker records the migration target. Same pattern, scoped to a section instead of a file.                                                                                                                  |
| `Project/AGENT.md` L42–48 (skills/scripts table)      | The `bridge_validator.py` script enforces bridge-module hygiene (cross-module import validation). Template must reference it.                                                                                                                                                                                                                                  |

### 4.3 Proposed v2 template

```lean
/-
Copyright (c) <YEAR> <Project> Authors. All rights reserved.
Released under Apache 2.0 license.

# <Project>.Bridges.<UpstreamName> — facade over `<UpstreamLib>.<Path>`

<One-paragraph statement of purpose.  Bridges exist for one of three reasons:
 1. **Naming**: project consumers want `<Project>.Bridges.X` not `Upstream.X`.
 2. **Stability**: insulate consumers from upstream renames.
 3. **Gap-filling**: provide a project-local primitive that the upstream
    lacks at the current pin.>

## Pin provenance

- Wave    : W##-B##-a# (<short-tag>)
- <upstream-lib> pin  : <40-char SHA>   (`lakefile.lean:<line>`)
- mathlib pin          : <40-char SHA>
- toolchain            : leanprover/lean4:v4.##.#-<channel>

## Bridge namespace probe

Document the **exact** upstream FQN here so future readers do not chase
phantom symbols.  Example:

> Upstream symbol is `Cslib.Logic.InferenceSystem`
> (NOT `cslib.InferenceSystem`, NOT `Cslib.InferenceSystem`).
> Class is two-sorted on tag `S` + judgment carrier `α`.

## Re-export surface

| Local name        | Upstream FQN                                  | Notes                          |
|-------------------|-----------------------------------------------|--------------------------------|
| `System`          | `Cslib.Logic.InferenceSystem`                 | `abbrev`, two-sorted           |
| `DerivableIn`     | `Cslib.Logic.InferenceSystem.DerivableIn`     | `abbrev`                       |
| `Admissible`      | *bridge-local*                                | upstream lacks at this pin     |

## Migration target

When upstream lands `<expected-PR>` (tracking
`docs/refactor/<wave>/<plan>.md §<N>`), delete the bridge-local
`Admissible` block and re-export the upstream version.
-/

import <UpstreamLib>.<NarrowPath>
-- Import the *narrowest* upstream file possible.  Pulling
-- `import Cslib` (umbrella) defeats the bridge's stability purpose.

set_option autoImplicit false

namespace <Project>.Bridges.<UpstreamName>
-- Canonical form: dotted `namespace`.  Avoid nested `namespace`
-- blocks (`namespace A / namespace B`) — they make grep harder.

universe u v

-- ## Re-exports (`abbrev` form, with explicit `_root_.` upstream paths)

abbrev System (S : Type u) (α : Type u) : Type _ :=
  _root_.<UpstreamLib>.<Path>.<UpstreamType> S α

abbrev DerivableIn (S : Type u) {α : Type u}
    [_root_.<UpstreamLib>.<Path>.<UpstreamType> S α] (a : α) : Prop :=
  _root_.<UpstreamLib>.<Path>.<UpstreamType>.DerivableIn S a

-- ## Bridge-local primitives (only when upstream lacks them)

/-- Bridge-local <X> (no upstream `<X>` primitive at pin `<SHA-7>`).
    Tracking the upstream proposal:
    https://github.com/<owner>/<repo>/pull/<NNN>. -/
def Admissible (S : Type u) {α : Type u}
    [_root_.<UpstreamLib>.<Path>.<UpstreamType> S α] (R : α → Prop) : Prop :=
  ∀ a, R a → DerivableIn S a

-- ## Minimal API for the bridge-local primitive
-- Keep this tiny: monotonicity, trivial-case, and any one or two
-- lemmas downstream actively consumes.  Avoid building a full theory
-- inside a bridge — that belongs in a Theorem module.

theorem Admissible.mono {S : Type u} {α : Type u}
    [_root_.<UpstreamLib>.<Path>.<UpstreamType> S α] {R R' : α → Prop}
    (hRR' : ∀ a, R' a → R a) (hR : Admissible S R) : Admissible S R' :=
  fun a hRa => hR a (hRR' a hRa)

theorem Admissible.false {S : Type u} {α : Type u}
    [_root_.<UpstreamLib>.<Path>.<UpstreamType> S α] :
    Admissible S (fun _ : α => False) :=
  fun _ h => absurd h (fun h => h)

end <Project>.Bridges.<UpstreamName>

/- ## See also
   * `skills/templates/Template_Theorem.md` — for proof-heavy modules that
     should consume *only* the bridge, never the upstream directly
   * `skills/scripts/lean/bridge_validator.py` — CI check that downstream
     modules import via the bridge, not the upstream directly
   * `Project/Bridges/CslibInferenceSystem.lean` — canonical 46-LOC example
   * `Project/Bridges/CslibLTS.lean` — pure-facade variant (no bridge-locals)
-/
```

**Anti-patterns to surface inline:**

```lean
-- ANTI-PATTERN: `export` from a bridge module.  Bridges are namespace-locked
-- on purpose — consumers must write `Project.Bridges.X.Foo` so that the
-- import graph is auditable.  Use `abbrev`, not `export`.

-- ANTI-PATTERN: importing the upstream umbrella (`import Cslib`,
-- `import Mathlib`).  Defeats the stability purpose.  Pin to the narrowest
-- upstream file that supplies the symbols you re-export.

-- ANTI-PATTERN: building a full theory on top of a bridge-local primitive.
-- If `Admissible` grows past ~5 lemmas, promote it to a Theorem module that
-- *imports* the bridge.  Bridges should stay ≤ ~60 LOC.

-- ANTI-PATTERN: bypassing the bridge from a consumer module.
-- `scripts/lean/bridge_validator.py` will catch direct upstream imports.

-- ANTI-PATTERN: forgetting the upstream SHA pin block.  Without it, a
-- silent upstream rename will appear as "missing symbol" at a future
-- toolchain bump and there will be no record of what we last verified.
```

**Worked 12-LOC example:**

```lean
namespace MyProj.Bridges.MathlibPartialOrder

universe u

/-- Re-export Mathlib's `PartialOrder` under the project namespace, pinned to
    Mathlib SHA <SHA-7>. -/
abbrev PartialOrder (α : Type u) : Type u := _root_.PartialOrder α

/-- Bridge-local convenience: pull `le_refl` to a fully-qualified form so that
    project-side proofs can write `MyProj.Bridges.MathlibPartialOrder.refl x`. -/
theorem refl {α : Type u} [PartialOrder α] (x : α) : x ≤ x := le_refl x

end MyProj.Bridges.MathlibPartialOrder
```

### 4.4 Diff vs current templates

This is a **new** template; no prior file to diff against. The deltas vs. the
two closest neighbours are:

* **vs. `Template_Index.md`** — `Template_Index` re-exports *sibling project*
  modules; `Template_Bridge` re-exports *third-party upstream* modules. Bridge
  adds SHA pin, FQN-disambiguation block, and bridge-local primitives.
* **vs. `Template_Application.md`** — `Template_Application` composes
  intra-project modules into theorems; `Template_Bridge` does not prove
  theorems beyond ≤ 5 monotonicity/triviality lemmas about bridge-local
  primitives. A bridge that ships > ~60 LOC of theorem content should be
  split: bridge stays minimal, theorems move to a Theorem-template file.

---

## 5. Cross-template recommendations

These shared conventions emerged from all four redesigns and belong in a new
`templates/README.md` section (or an updated `00-CONVENTIONS.md`):

### 5.1 Mandatory file-doc top block (every template)

```lean
/-
Copyright (c) <YEAR> <Project> Authors.  Released under Apache 2.0.
-/

-- =====================================================================
-- W##-B##-a# <SHORT-CHANGE-TAG>                       (only if applicable)
-- Source: docs/refactor/wave-##/<plan>.md §<section>
-- =====================================================================

import …
set_option autoImplicit false

/-!
# <Project>.<Path> — <Human Title>

<one-paragraph summary>

## Sections        (skip for ≤ 60-LOC files)
## Substrate       (pin <SHA-7>) — only when third-party deps matter
## Reference       (paper anchor — REQUIRED in the project proof modules)
## Change note     (why this file exists / why it was split / renamed)
## Tags            (lowercase, comma-separated, for grep)
-/
```

The wave/batch banner is **project-specific** but the slot exists in every
template; downstream projects can use any change-tracking scheme.

### 5.2 Unified section skeleton

Every template should expose the same H2 skeleton so that a reader can
context-switch between files without re-learning structure:

```
## Variables
## Definitions
## Main statements
## Proofs                    (helper lemmas; `private` by default)
## API exports               (terminating `export Namespace (names…)`)
## See also                  (footer block, plain comment)
```

Data modules and bridges may omit `## Proofs` if empty. Theorem modules may
omit `## Variables` if no shared hypotheses are factored out. **Never** omit
`## API exports` or `## See also`.

### 5.3 Theorem-doc structure

```lean
/-- **<Theorem title>** [<paper T-id, if any>]. <one-sentence statement>.

    <one-paragraph proof strategy: which Mathlib lemma family, which
     terminator, which @[grind] hints>.

    Substrate: `<Mathlib.File>.<lemma>`.   (optional, for analysis lemmas)
-/
theorem <snake_case_name> … := …
```

Citations to `project-tufte.tex` use `[T<chapter>.<idx>]`. Citations to upstream
PRs use `(<repo> PR #<NNN>)`.

### 5.4 Proof comment style

* `-- PATTERN: <name>` for reusable proof patterns (search-friendly).
* `-- PITFALL: <symptom>` for known-bad approaches (search-friendly).
* `-- LOOGLE: #loogle <query>` for the search that finds the relevant lemma.
* `-- TODO(<wave-tag>, <upstream-ref>): <action>` for tracked debt.
* `-- (DELETED W##-B##) Removed deprecated <name>` for tombstones — keep these forever; they prevent re-introduction.

### 5.5 Anti-patterns to repeat in every template

A short "checklist of pitfalls" near the bottom of every template, all
borrowed from one canonical source list:

| Anti-pattern                                                                | Fix                                                                                              |
|-----------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|
| `import Mathlib` or `import Mathlib.Tactic` in non-tactic modules           | Narrow to the specific Mathlib file(s) you use                                                   |
| Bare `simp` in finished proofs                                              | `simp only [<explicit list>]`                                                                    |
| `set_option maxHeartbeats N` globally                                       | Scope with `set_option maxHeartbeats N in theorem …`                                             |
| `native_decide` in a proof body                                             | `<proj>_decide` ladder, or a structured proof                                                    |
| `nlinarith` on `Real.sqrt` goals                                            | `Real.sqrt_le_sqrt` + `linarith`, or sum-of-squares case split                                   |
| `noncomputable section` around computable defs                              | Scope `noncomputable` per-definition                                                             |
| Custom Qq-tactic with no cross-module consumer                              | Don't write it; use `grind`/`linarith` directly until ≥ 1 consumer exists                        |
| `@[simp]` lemma without LHS-complexity discipline                           | Verify with `simp?`; ensure LHS strictly larger, terminating, orthogonal                         |
| Missing `@[ext]` on a record-like structure                                 | Add `@[ext]` so `ext` works                                                                      |
| Bridge module re-exporting upstream via `export` instead of `abbrev`        | Use `abbrev` to preserve namespace-locking                                                       |
| Bridge module importing the upstream umbrella                               | Pin to the narrowest upstream file                                                               |
| Data module without a `## Scale convention` header (Nat ×100, ×1000, etc.)  | Always state the scale at the top                                                                |

### 5.6 Module-size signal table (already in `README.md`, but elevate)

Promote the table from `README.md` L129–137 into each template's "## Module
checklist" so the splitting trigger is one-click visible:

| LOC          | Action                                                                            |
|--------------|-----------------------------------------------------------------------------------|
| < 500        | Ideal for leaf / data / bridge modules                                            |
| 500 – 2 000  | Acceptable for any layer                                                          |
| 2 000 – 2 500| Consider splitting (`StochasticCCV/Information.lean` is 2 513 — at the edge)      |
| > 2 500      | Must split into `.Core` + `.Lemmas` + `.Main` (see `Template_Application.md` §7) |
| > 3 000      | Bad: forces full recompilation of every importer on every edit                    |

### 5.7 Cross-template See-Also matrix (link consistency)

Each template's `## See also` footer should link to the other three plus the
shared references. Suggested matrix:

|                       | Theorem | DataModule | TacticHelper | Bridge | Refs                                   |
|-----------------------|:-------:|:----------:|:------------:|:------:|----------------------------------------|
| `Template_Theorem`    |    —    |     ✓      |      ✓       |   ✓    | `lean4-tactic-hierarchy`, `lean-math-analysis` |
| `Template_DataModule` |    ✓    |     —      |      ✓       |   ✓    | `mathlib4-conventions`, `axiom_audit`         |
| `Template_TacticHelper`|   ✓    |     ✓      |      —       |        | `lean4-tactic-hierarchy`, `check-native-decide.sh` |
| `Template_Bridge`     |    ✓    |     ✓      |              |   —    | `bridge_validator.py`, `lean4-module-dependency-guide` |

### 5.8 Generation pipeline

The current convention `Template_*.md` is generated from `Template_*.lean`
sources via `scripts/lean/templates_to_md.py`. v2 should keep this — the
proposal above shows the **Markdown** layout; the synthesis pass needs to
write the `.lean` source so that the `.md` regenerates with the same shape.
Recommended source convention: each H2 (`##`) section in the `.md` corresponds
to a top-level `-- ============== <Title> ============== ` banner in the
`.lean`; the `templates_to_md.py` script should be updated (or already
supports) emitting the H2 from the banner.

---

## 6. Implementation order (for the synthesis pass)

1. **Land the cross-template conventions** (§5) first as
   `templates/00-CONVENTIONS.md` so each template can link to it.
2. **Rewrite the three existing templates** in place: `Template_Analysis.md`
   (→ "Theorem"), `Template_Foundation.md` (→ "DataModule"),
   `Template_Automation.md` (→ "TacticHelper"). Keep filenames stable; add a
   one-line "Use this for …-style modules" subtitle.
3. **Add `Template_Bridge.md`** as a new file; update `templates/README.md`
   navigator with a "DAG Layer: N/A (façade)" row.
4. **Regenerate `.md` from `.lean`** via `templates_to_md.py`; confirm the
   H2-from-banner pipeline still works.
5. **Cross-link** the four templates per §5.7 matrix, and add a
   `## See also → Template_Theorem.md` line in any pre-existing skill files
   that previously linked only to `Template_Analysis.md`.

---

*End of proposal. No code changes yet — this document is the input for the
synthesis pass that will overwrite the `.lean` template sources.*
