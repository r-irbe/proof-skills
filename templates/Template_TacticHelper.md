# Template_TacticHelper.md — v2 reusable tactic / automation Lean module

> **Status:** v2 production template (extracted from
> `_v2-proposals/proof-templates-v2.md §3`).
> Use this in **any** Lean 4 + Mathlib project that maintains a
> *centralised tactic-helper module* — i.e., a single file that other
> modules import for shared automation (`@[grind]` lemmas, custom
> tactics, decide ladders, bridge cast-lemmas, consolidation macros).
>
> Companion v1: [`Template_Automation.md`](./Template_Automation.md).

---

## 1. When to use this template

Apply `Template_TacticHelper` when a module:

* Is the **single, project-wide hub** for cross-cutting automation
  (`<Project>.Tactics`, `<Project>.Aesop`, `<Project>.Grind`).
* Imports `Mathlib.Tactic` — **this is the one exception** to the
  "no `import Mathlib.Tactic`" rule. Everyone else imports the
  helper module, not Mathlib.Tactic directly.
* Hosts ≥ 1 of: a custom `syntax`/`macro_rules` tactic, a
  `register_simp_attr` / `register_grind_attr`, a curated
  `@[grind]` bridge-lemma pack, or a consolidation `macro`.

**Do NOT use** for:

* Single-file `@[grind]` annotations on local lemmas → tag them in their
  source file directly.
* Per-skill automation (e.g., a tactic only used by one module) →
  define it inline in that module.

---

## 2. Customisation checklist

| Placeholder           | Decide                                                                  | Default                                                                       |
|-----------------------|-------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| `<Project>`           | Top-level namespace                                                     | Matches `package`                                                             |
| `<proj>`              | Lower-case short tactic prefix                                          | Pick a 3-6-letter project prefix; e.g. `myproj_decide`                        |
| Custom-tactic table   | List active and recently-deleted custom tactics                         | Initialize with one row; grow over time                                       |
| `register_simp_attr`  | Skip if you never need a whitelisted simp set                           | Keep if you have a custom `decide` ladder                                     |
| Bridge-lemma scale    | Match your project's `Nat` scale (see Template_DataModule §3)           | E.g. `×100`, `×10000`                                                          |
| Consolidation macros  | Survive iff ≥ 1 cross-module use after one full release/wave            | Tombstone unused macros — do not let them rot                                 |

---

## 3. Mandatory governance blocks (top of file)

A tactic-helper module must declare **policies** that downstream code
relies on.  Make these the first headings under `/-! ... -/`:

* **Key annotations** — list which `@[grind]` variants, `@[positivity]`,
  `@[aesop safe apply]`, `@[fun_prop]`, `@[simp]` lemmas this file
  exposes.
* **Custom-tactic status table** — every active custom tactic plus
  recently-deleted ones (tombstones).
* **`native_decide` policy** — explicitly state whether
  `native_decide` is allowed.  If banned, point at the replacement
  tactic and the CI script that enforces it.
* **Library comparison and rationale** — when to reach for `grind` vs
  `aesop` vs `omega` vs `polyrith`; when to author a new `Qq` tactic
  (default: never until you have a downstream consumer).
* **Proof-search strategy (when stuck)** — the ordered cheat-sheet for
  contributors stuck on a goal.

---

## 4. Full template

```lean
/-
Copyright (c) <YEAR> <Project>.
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

namespace <Project>.Tactics

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
    `def`s here only when bare `decide` fails to unfold them. -/
register_simp_attr <proj>_decide_unfold

/-- `<proj>_decide`: kernel-checked replacement for `native_decide`.
    Climbs three rungs:
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
-- §2  Bridge lemmas (e.g., scaled `Nat` ↔ ℝ)
-- =====================================================================

/-- ×100-scaled bound: `n ≤ 100 → (n : ℝ) / 100 ≤ 1`. -/
@[grind ←]
theorem nat100_to_real_le_one {n : Nat} (h : n ≤ 100) :
    (n : ℝ) / 100 ≤ 1 := by
  push_cast; linarith

/-- Cast-placement cheat-sheet:
    * `push_cast; ring`                       — Nat→Int equalities
    * `convert h using N <;> push_cast <;> omega`  — cast-placement misfires
    * `zify [bound]; simp only [Int.abs_eq_natAbs]; linarith`  — natAbs → Int
    * `le_div_iff₀ + exact_mod_cast`          — Int.ediv → ℝ.div
    Surface these as inline `-- PATTERN:` comments next to the relevant lemmas. -/

-- =====================================================================
-- §3  Reusable theorems (e.g. geometric decay)
-- =====================================================================

/-- Polymorphic geometric decay over any `CommSemiring`. -/
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
   * `skills/templates/Template_DataModule.md` — `@[grind]`-tagged carrier lemmas
   * `skills/references/lean4-tactic-hierarchy.md` — terminator priority
   * `<Project>/Tactics.lean` — canonical reference implementation
   * `<Project>/AGENT.md §"Proof Search Strategy"` — cast cheat-sheet
   * `scripts/lean/check-native-decide.sh` — CI enforcement
   * `scripts/lean/proof_quality.py` — heuristic quality audit
-/
```

---

## 5. Inline anti-patterns

```lean
-- ANTI-PATTERN: writing a Qq-based custom tactic before there is ≥ 1
-- downstream consumer.  Qq tactics are expensive to maintain and
-- frequently break across Lean/Mathlib bumps.  Wait for the consumer.

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

---

## 6. Worked 14-LOC example

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

---

## 7. What v2 adds over v1 (`Template_Automation.md`)

| Addition                                                                                                                  | Rationale                                                                                                  |
|---------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------|
| Custom-tactic status table with explicit deprecation/survival rule                                                        | Every project that builds a tactic library accumulates dead tactics; the table makes deletion routine.     |
| `native_decide` policy block                                                                                              | Codifies the most common kernel-soundness regression and links the CI script that enforces the ban.       |
| `decide +kernel` rung in the decide ladder                                                                                | Catches goals that `decide` misses but `kernel` can still discharge without `native_decide`.               |
| `register_simp_attr` pattern for whitelisted simp sets                                                                    | Lets you build a `<proj>_decide` rung 3 without contaminating the global `simp` set.                       |
| `@[grind .]` dotted-direction variant in the §0 catalog                                                                   | Documents the modern grind-annotation taxonomy (project-agnostic).                                         |
| Cast-placement cheat-sheet                                                                                                | Surfaces the four most common cast-error escape patterns.                                                  |
| Tag-measure-demote workflow                                                                                               | Codifies the lifecycle of a `@[grind]` lemma from authored to production.                                  |
| Removal of speculative `Qq` skeleton                                                                                      | "Don't write Qq until you have a consumer" is now an enforceable rule, not a speculative example.          |

---

## 8. See also

* [`Template_Theorem.md`](./Template_Theorem.md)
* [`Template_DataModule.md`](./Template_DataModule.md)
* [`Template_Bridge.md`](./Template_Bridge.md)
* [`../references/lean4-tactic-hierarchy.md`](../references/lean4-tactic-hierarchy.md)
