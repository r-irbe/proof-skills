# Template_Theorem.md — v2 proof-heavy Lean module

> **Status:** v2 production template (extracted from
> `_v2-proposals/proof-templates-v2.md §1`).
> Use this in **any** Lean 4 + Mathlib project for modules whose primary
> purpose is *proving theorems* (as opposed to *defining data* or
> *building automation*).
>
> Companion v1: [`Template_Analysis.md`](./Template_Analysis.md) (kept for
> existing modules that follow the v1 shape).

---

## 1. When to use this template

Apply `Template_Theorem` when a module:

* Proves ≥ 2 theorems that **users will cite** from other modules.
* Has a clearly stateable formal claim per theorem (i.e., not an
  exploratory scratch file).
* Lives at any layer of the project — *foundations* (carrier types
  proved sound), *core* (the workhorse theorems), or *application*
  (the headline corollaries).
* Imports `Mathlib.Analysis.*`, `Mathlib.Topology.*`,
  `Mathlib.Probability.*`, or any analogous "proof-substrate" library.

**Do NOT use** for:

* Pure data-definition modules → use [`Template_DataModule.md`](./Template_DataModule.md).
* Tactic / automation modules → use [`Template_TacticHelper.md`](./Template_TacticHelper.md).
* Re-export façade modules → use [`Template_Bridge.md`](./Template_Bridge.md) or
  [`Template_Index.md`](./Template_Index.md).

---

## 2. Customisation checklist (do this before writing any theorem)

Walk this list **once per new file**.  Every `<placeholder>` in §4 maps to
exactly one of these decisions.

| Placeholder        | Decide                                                          | Project-conventional default                                                |
|--------------------|-----------------------------------------------------------------|-----------------------------------------------------------------------------|
| `<YEAR>`           | Calendar year of file creation                                  | `date +%Y`                                                                  |
| `<Project>`        | Top-level namespace (matches `lakefile.lean` `package` name)    | E.g. `MyProj`, `Foo`, `Acme`.                                               |
| `<Foundation>`     | Sub-namespace for type-level prerequisites                      | E.g. `Core`, `Basic`, `Foundation`                                          |
| `<Path>`           | Module path under `<Project>/` (dotted)                         | E.g. `Analysis.Convergence`                                                 |
| `<DependencySubmodule>` | Same-project upstream the file consumes                    | Any `<Project>.*` module already in the build graph                          |
| `<SpecificFile>`   | Narrow Mathlib file (NEVER `import Mathlib`)                    | E.g. `Mathlib.Analysis.SpecificLimits.Basic`                                |
| `W##-B##-a#`       | Your wave / batch tag (drop if no waveplan)                     | Use your own change-tracking scheme                                         |
| `<paper-label>` / `<T-id>` | External reference (paper section, ADR id, issue)       | Skip if no external doc                                                     |
| `<MyProj.Bridges.X>` | Replace with your bridge namespace                            | See [`Template_Bridge.md`](./Template_Bridge.md)                            |

For projects without waves: replace the wave/batch banner with a
plain `Source:` line citing the issue, ADR, or PR that motivated the file.

---

## 3. Mandatory file-doc top block (every theorem module)

```lean
/-
Copyright (c) <YEAR> <Project> Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: <Project> Contributors
SPDX-License-Identifier: Apache-2.0
-/
```

* **Apache-2.0 is the Mathlib-compatible default.** If your project ships
  under a different licence, keep the SPDX line accurate; downstream
  Mathlib-linker checks (and `reuse lint`) read it.
* **Authors line is mandatory.** Mathlib's `style-linter` enforces it.

---

## 4. Full template

The block below is the **production template** — copy verbatim, then
fill in placeholders per §2.

```lean
/-
Copyright (c) <YEAR> <Project> Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: <Project> Contributors
SPDX-License-Identifier: Apache-2.0
-/

import <Project>.<Foundation>.<DependencySubmodule>
import Mathlib.Analysis.<SpecificFile>
-- One Mathlib import per logical capability; never `import Mathlib`.

-- =====================================================================
-- W##-B##-a# <SHORT-CHANGE-TAG>  (or: "Source: issue #NNN" / ADR id)
-- One-line rationale: why this file exists at this layer.
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

* `<paper>.tex` §"<Section name>"  *(or any external authority)*
* `docs/<adr>.md` §<N>             *(or your ADR / decision-doc path)*

## Change note

<Why this file was added/split/renumbered.  Disambiguate from any siblings
or near-namesakes (e.g., "Doeblin vs Birkhoff–von Neumann vs Birkhoff
ergodic — see comment block at line N for the convention used here").>
-/

namespace <Project>.<Path>

-- ## Variables

variable
  {α : Type*}            -- carrier type (often `ℝ` for analysis)
  (f : α → α)            -- map / dynamics
  (K : ℝ≥0) (hK : K < 1) -- contraction rate, etc.
  -- Group with comments; keep order stable across refactors.

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
 - which external claim it discharges,
 - any boundary / domain caveats,
 - any cross-references to sibling sections.> -/

/-- **<Theorem title>** [<paper T-id>]. <Statement in words>.

    <Proof-strategy paragraph: "Proved via X applied to Y; final step
    closes with `linarith` on the assembled bounds.">
-/
theorem <snake_case_name> (h : <Hyp>) : <Goal> := by
  -- One-step-at-a-time per project proof discipline.
  <tac1>
  <tac2>
  -- Close with the lowest-cost terminator that works:
  -- rfl → decide → norm_num → grind → omega → linarith → nlinarith → calc.
  linarith [<explicit hypothesis hints>]

-- ## Proofs (helper lemmas)

/-- Weighted triangle inequality used by §1.  `private` because it leaks
    set-arithmetic and should not pollute the public API. -/
private theorem <helper_name> {x y : ℝ} (a b : ℚ) (hx : 0 ≤ x) (hy : 0 ≤ y) :
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
   * `skills/templates/Template_DataModule.md` — for the underlying carrier types
   * `skills/templates/Template_TacticHelper.md` — for `@[grind]` bridge lemmas
   * `skills/references/lean4-tactic-hierarchy.md` — terminator priority order
   * `skills/skills/lean-math-analysis/SKILL.md` — Mathlib analysis API cards
   * `<Project>/AGENT.md` — project-specific conventions
-/
```

---

## 5. Inline anti-patterns to surface (with one-line rationale)

Drop these comments next to the relevant code if you see the trap:

```lean
-- ANTI-PATTERN: `nlinarith` on `Real.sqrt` / transcendental goals.
-- nlinarith cannot model `sqrt`, `log`, `exp`. Prefer
-- `Real.sqrt_le_sqrt` + `linarith`, OR the "sum of squares = 0 ⇒
-- each = 0" pattern (`sq_nonneg + le_antisymm + pow_eq_zero_iff`).

-- ANTI-PATTERN: bare `simp` in a finished proof.  Use
-- `simp only [name₁, name₂]` so a future Mathlib `@[simp]` addition
-- cannot break the proof.

-- ANTI-PATTERN: `set_option maxHeartbeats N` *globally*.  Always scope
-- with `set_option maxHeartbeats N in theorem ...`.  Measure first with
-- `#count_heartbeats`.

-- ANTI-PATTERN: `native_decide` in a proof body.  It is compiler-trusted
-- (not kernel-checked) and inflates the axiom audit.  Use the project's
-- `<proj>_decide` ladder (decide → decide +kernel → simp+decide) or a
-- structured proof.

-- ANTI-PATTERN: `noncomputable section` wrapping more than the
-- noncomputable defs.  Wrapping computable defs hides them from
-- noncomputable-instance audits.
```

---

## 6. Worked 12-LOC example (compactly demonstrates the shape)

This is a **complete, generic** illustration — it compiles against pure
Mathlib without any project-specific dependencies.

```lean
namespace MyProj.Analysis.Squares

/-- **Sum-of-squares case split**: if `(a)² + (b)² = 0` over ℝ then both vanish. -/
theorem sq_pair_zero_iff {a b : ℝ} : a ^ 2 + b ^ 2 = 0 ↔ a = 0 ∧ b = 0 := by
  refine ⟨fun h => ?_, fun ⟨ha, hb⟩ => by simp [ha, hb]⟩
  have ha : a ^ 2 = 0 := le_antisymm (by linarith [sq_nonneg b]) (sq_nonneg _)
  have hb : b ^ 2 = 0 := le_antisymm (by linarith [sq_nonneg a]) (sq_nonneg _)
  exact ⟨pow_eq_zero_iff two_ne_zero |>.mp ha, pow_eq_zero_iff two_ne_zero |>.mp hb⟩

end MyProj.Analysis.Squares
export MyProj.Analysis.Squares (sq_pair_zero_iff)
```

---

## 7. What v2 adds over v1 (`Template_Analysis.md`)

| Addition                                                       | Rationale                                                                                              |
|----------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| File-doc top block (`/-! # … ## Sections ## Substrate … -/`)  | Forces the author to list sections, Mathlib substrate, references, and change-rationale up front.       |
| Wave/batch banner                                              | Connects the file to the plan that produced it; survives `git blame` better than commit-only metadata. |
| `## Variables` / `## Definitions` / `## Main statements` / `## Proofs` / `## API exports` / `## See also` skeleton | Uniform skeleton across the corpus; reviewers and tooling can locate sections without grep gymnastics.  |
| Explicit `native_decide` ban + `noncomputable section` warning | Codifies the two most common kernel-soundness regressions seen in mature corpora.                       |
| `private` helper convention                                    | Keeps `linarith`-shaped set-arithmetic lemmas out of the public API surface.                            |
| `linear_combination` + sum-of-squares pattern                  | Replaces ad-hoc `nlinarith` chains with documented closed-form patterns.                                |

---

## 8. See also

* [`Template_DataModule.md`](./Template_DataModule.md) — carrier types you'll cite from §"Substrate"
* [`Template_TacticHelper.md`](./Template_TacticHelper.md) — where to put reusable `@[grind]` bridge lemmas
* [`Template_Bridge.md`](./Template_Bridge.md) — for re-exporting upstream symbols
* [`../references/lean4-tactic-hierarchy.md`](../references/lean4-tactic-hierarchy.md) — terminator priority
* `<Project>/AGENT.md` — your project-specific conventions (cast cheat-sheet, naming, etc.)
