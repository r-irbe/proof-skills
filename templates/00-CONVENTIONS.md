# 00-CONVENTIONS.md — Cross-template Lean 4 module conventions

> **Status:** v2 production document (extracted from
> `_v2-proposals/proof-templates-v2.md §5` and
> `_v2-proposals/all-templates.md`).
> Every `Template_*.md` in this folder assumes the conventions on this
> page.  Read this first.  Each template then specialises for its
> module shape (Theorem / DataModule / TacticHelper / Bridge / …).

---

## 1. Mandatory file-doc top block (every Lean module)

Every module in a serious Lean 4 project ships exactly this preamble:

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
## Reference       (paper / ADR / RFC anchor — REQUIRED for proof modules)
## Change note     (why this file exists / why it was split / renamed)
## Tags            (lowercase, comma-separated, for grep)
-/
```

* **Apache-2.0** is the Mathlib-compatible default; downstream `reuse
  lint` reads the SPDX line.
* **`set_option autoImplicit false`** is mandatory; autoimplicits
  produce subtle universe / elaboration bugs that the compiler will not
  diagnose.
* The wave/batch banner is **project-specific** but the *slot* exists in
  every template.  Downstream projects can use any change-tracking
  scheme (issue id, ADR id, PR number).

---

## 2. Unified section skeleton

Every Lean source file in the corpus exposes the same H2 skeleton
inside its `namespace`/`end namespace` block so a reader can
context-switch between files without re-learning structure:

```
## Variables                       -- shared `variable {α : Type*}` declarations
## Definitions                     -- `def`, `noncomputable def`, `structure`, `inductive`
## Main statements                 -- top-level public theorems, one `--- §N Title ---` banner per section
## Proofs                          -- helper lemmas; `private` by default
## API exports                     -- terminating `export Namespace (names…)` block
## See also                        -- footer block, plain `/- ... -/` comment with links
```

| Module shape   | May omit `## Variables` | May omit `## Proofs` | May omit `## Main statements` | **Must keep**             |
|----------------|:-----------------------:|:--------------------:|:-----------------------------:|---------------------------|
| Theorem        |  ✓ if no shared vars    |                      |                               | `## API exports`, `## See also` |
| DataModule     |       ✓                 |     ✓ if empty       |     ✓ (light here)            | `## API exports`, `## See also` |
| TacticHelper   |       ✓                 |                      |                               | `## API exports`, `## See also` |
| Bridge         |       ✓                 |   ✓ if pure facade   |     ✓                         | `## See also`                  |

**Never** omit `## See also` — it is the discoverability glue.

---

## 3. Theorem-doc structure

Every public theorem starts with a `/-- ... -/` docstring in this
shape:

```lean
/-- **<Theorem title>** [<paper T-id, if any>]. <one-sentence statement>.

    <one-paragraph proof strategy: which Mathlib lemma family, which
     terminator, which @[grind] hints>.

    Substrate: `<Mathlib.File>.<lemma>`.   (optional, for analysis lemmas)
-/
theorem <snake_case_name> … := …
```

**Citation conventions** (adopt a project-local convention; this is a
sample):

| Source                       | Citation form              |
|------------------------------|----------------------------|
| Project paper / spec         | `[T<chapter>.<idx>]` (e.g. `[T7.12]`) |
| Upstream PR                  | `(<repo> PR #<NNN>)`       |
| ADR / decision doc           | `[ADR-<NNN>]`              |
| Issue / ticket               | `(#<NNN>)`                 |
| Textbook                     | `(Author Year §N)`         |

---

## 4. Proof comment style (search-friendly tags)

Use these comment tags consistently — they are grep targets across the
corpus:

| Tag                                            | Meaning                                                                |
|------------------------------------------------|------------------------------------------------------------------------|
| `-- PATTERN: <name>`                           | Reusable proof pattern (e.g. `-- PATTERN: sum-of-squares case split`) |
| `-- PITFALL: <symptom>`                        | Known-bad approach to warn future readers away                         |
| `-- LOOGLE: #loogle <query>`                   | The Loogle search that found the relevant lemma                        |
| `-- LEANSEARCH: <query>`                       | Equivalent for LeanSearch                                              |
| `-- TODO(<change-tag>, <upstream-ref>): <action>` | Tracked debt (e.g. `TODO(W3-B7, mathlib PR #38758): retire bridge`) |
| `-- (DELETED <tag>) Removed deprecated <name>` | Tombstone — **keep these forever**; they prevent re-introduction       |
| `-- FIXME(<owner>): <action>`                  | Personal unblocked TODO — should not survive into main                 |
| `-- SAFETY: <invariant>`                       | Critical invariant the surrounding code assumes                        |

---

## 5. Anti-patterns to repeat in every template

The canonical checklist of pitfalls.  Each `Template_*.md` lists the
subset that applies; this table is the master.

| Anti-pattern                                                                | Fix                                                                                              |
|-----------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|
| `import Mathlib` or `import Mathlib.Tactic` in non-tactic modules           | Narrow to the specific Mathlib file(s) you use                                                   |
| Bare `simp` in finished proofs                                              | `simp only [<explicit list>]`                                                                    |
| `set_option maxHeartbeats N` globally                                       | Scope with `set_option maxHeartbeats N in theorem …`                                             |
| `native_decide` in a proof body                                             | `<proj>_decide` ladder (`decide → decide +kernel → simp only […]; decide`), or a structured proof |
| `nlinarith` on `Real.sqrt` / `Real.log` / `Real.exp` goals                  | `Real.sqrt_le_sqrt` + `linarith`, or sum-of-squares case split (`sq_nonneg` + `le_antisymm`)     |
| `noncomputable section` around computable defs                              | Scope `noncomputable` per-definition                                                             |
| Custom `Qq`-tactic with no cross-module consumer                            | Don't write it; use `grind`/`linarith` directly until ≥ 1 consumer exists                        |
| `@[simp]` lemma without LHS-complexity discipline                           | Verify with `simp?`; ensure LHS strictly larger, terminating, orthogonal                         |
| `@[aesop safe apply]` on a lemma with side conditions                       | Use `unsafe 50% apply` or attach side conditions as `@[aesop norm]`                              |
| `@[grind]` on every helper "in case"                                        | Tag only what is consumed; run `#grind_lint check` to catch loops                                |
| Missing `@[ext]` on a record-like structure                                 | Add `@[ext]` so `ext` works                                                                      |
| Bridge module re-exporting upstream via `export` instead of `abbrev`        | Use `abbrev` to preserve namespace-locking                                                       |
| Bridge module importing the upstream umbrella (`import Mathlib`)            | Pin to the narrowest upstream file                                                               |
| Data module without a `## Scale convention` header (Nat ×100, ×1000, etc.)  | Always state the scale at the top                                                                |
| `autoImplicit true` (the default)                                           | Always `set_option autoImplicit false` at top of file                                            |
| `deriving Inhabited` "in case"                                              | Derive only when a downstream tactic actually requires it                                        |

---

## 6. Module-size signal table

Use this as the splitting trigger.  Promote it into each template's
"Module checklist" so the rule is visible at a glance.

| LOC          | Action                                                                            |
|--------------|-----------------------------------------------------------------------------------|
| < 500        | Ideal for leaf / data / bridge modules                                            |
| 500 – 2 000  | Acceptable for any layer                                                          |
| 2 000 – 2 500| Consider splitting; mature corpora regularly hit this ceiling                     |
| > 2 500      | **Must split** into `.Core` + `.Lemmas` + `.Main` (Application template §7)       |
| > 3 000      | Bad: forces full recompilation of every importer on every edit                    |

---

## 7. Cross-template See-Also matrix

Each `Template_*.md`'s `## See also` footer should link to its
siblings according to this matrix.  Keeps the discoverability graph
connected.

|                         | Theorem | DataModule | TacticHelper | Bridge | Refs                                              |
|-------------------------|:-------:|:----------:|:------------:|:------:|---------------------------------------------------|
| `Template_Theorem`      |    —    |     ✓      |      ✓       |   ✓    | `lean4-tactic-hierarchy`, `lean-math-analysis`    |
| `Template_DataModule`   |    ✓    |     —      |      ✓       |   ✓    | `mathlib4-conventions`, `axiom_audit`             |
| `Template_TacticHelper` |    ✓    |     ✓      |      —       |        | `lean4-tactic-hierarchy`, `check-native-decide.sh`|
| `Template_Bridge`       |    ✓    |     ✓      |              |   —    | `bridge_validator.py`, `lean4-module-dependency-guide` |

---

## 8. Choosing a template (decision tree)

Use this flowchart when authoring a new Lean module:

```
Is the module re-exporting third-party (Mathlib / Cslib / Batteries) symbols?
├─ Yes → Template_Bridge.md
└─ No
   └─ Is the module ONE central tactic-helper module (custom syntax / decide ladder / cross-cutting @[grind] pack)?
      ├─ Yes → Template_TacticHelper.md
      └─ No
         └─ Does the module prove ≥ 2 publicly-cited theorems?
            ├─ Yes → Template_Theorem.md
            └─ No → Template_DataModule.md  (carrier-type + minimal API)
```

Special-case templates (existing v1, not yet recast as v2):

* `Template_Application.md` — composing intra-project modules into a multi-layer theorem chain.
* `Template_Index.md` — pure intra-project re-export façade.
* `Template_Arithmetic.md` — heavy arithmetic shape (`omega`, `linarith`, `norm_num`).
* `Template_Dynamics.md` — dynamical-systems shape (Lyapunov, Banach, fixed point).
* `Template_ProofStrategy.md` — long-running proof-strategy scratchpad.
* `Template_Refactoring.md` — mid-refactor file with both old and new shape.
* `Template_Verification.md` — verification-suite / property-test shape.
* `Template_Performance.md` — performance-tuning shape (`#count_heartbeats`, profile guards).
* `Template_Lakefile.md` — `lakefile.lean` / `lakefile.toml` shape.

---

## 9. Project-specific overrides

Projects with conventions that *differ* from this canonical set should
add a top-level `AGENT.md` (or `skills-overrides/AGENT.md` per the
dispatch precedence in [`../AGENT.md` §3.1](../AGENT.md)) that records
the delta.  Common override slots:

* **Scale convention** — what does ×100 mean for *your* domain?
* **Custom-tactic prefix** — your project's `<proj>_decide`, `<proj>_mono_corollaries`, …
* **Paper / spec anchor format** — your `[T<chapter>.<idx>]` analogue.
* **Wave/batch tag scheme** — your `W##-B##-a#` analogue (issue id, ADR id, …).
* **Cast cheat-sheet** — the `push_cast; ring`/`convert ... using N` family tuned to your numeric types.

The overrides layer **does not change the template files**; it
annotates them with project-specific defaults so a contributor reading
both can see "in this project, `<Project>` = `MyProj`, `<proj>` =
`mp`, paper anchor is `[T<chapter>.<idx>]`".

---

## 10. Generation pipeline (optional)

Some projects generate the `.md` template files from `.lean` source
templates via a build script (`scripts/lean/templates_to_md.py` or
similar).  This page is **markdown-authored** and survives without the
generator, but if you adopt the generator, the convention is:

* Each H2 (`##`) section in the `.md` corresponds to a top-level
  `-- ============== <Title> ============== ` banner in the `.lean`.
* The generator emits the H2 from the banner; manual edits to the `.md`
  must be backported to the `.lean` source.

This is optional — the templates work fine as hand-authored Markdown.

---

## 11. See also

* [`README.md`](./README.md) — template navigator and DAG-layer table
* [`Template_Theorem.md`](./Template_Theorem.md) — proof-heavy modules
* [`Template_DataModule.md`](./Template_DataModule.md) — carrier-type modules
* [`Template_TacticHelper.md`](./Template_TacticHelper.md) — automation hub
* [`Template_Bridge.md`](./Template_Bridge.md) — upstream-facade modules
* [`../AGENT.md`](../AGENT.md) — skill-dispatch precedence and project-override layer
