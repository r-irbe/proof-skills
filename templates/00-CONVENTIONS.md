# `00-CONVENTIONS.md` -- Cross-Template Lean 4 Module Conventions (v3)

> **Status**: v3 canonical standard (`proof-skills` v0.4.0).
> Every template in [`core/`](core/), [`workflow/`](workflow/), and [`packs/`](packs/) inherits the conventions on this page.

---

## 1. Mandatory File Preamble & Hygiene Gates

Every Lean 4 module begins with an SPDX license header, explicit narrow imports, and `set_option autoImplicit false`:

```lean
/-
Copyright (c) <YEAR> <Project> Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
-/
import <Project>.<Layer>.<UpstreamDefs>
-- Never `import Mathlib` umbrella; import narrow capability modules only.
-- Note: `∑` and `∏` binders are root-scoped in modern Lean 4 / Mathlib4;
-- do NOT add vestigial `open scoped BigOperators` unless `𝔼` notation is used.

set_option autoImplicit false

/-!
# `<Project>.<Path>` -- <Human-Readable Module Title>

<One-paragraph mathematical & architectural summary.>

## Abstraction-Concrete Duality Contract
- **Specification surface (`Prop`)**: <abstract algebraic / order / topological interface>
- **Executable / WHNF surface (`def` / `@[csimp]`)**: <concrete monomorphic carrier, if any>

## References
- <Paper section / ADR / Blueprint label>
-/
```

---

## 2. Interactive `lean-lsp` MCP-First Proving Protocol

1. **Zero `trace_state` File Pollution**: Never edit `.lean` files just to print goal states or run blind batch `lake build` loops during interactive proving. Query live goals via `lean_goal(target: "tactic" | "term" | "altproof")` and errors via `lean_diagnostics`.
2. **Singleton Language Server**: Attach all editors and MCP tools through `tools/lean-serve-broker/` (`CONV-LEAN-SERVE-SINGLETON`); never spawn competing `lake serve` daemons.
3. **Pre-Proof Counterexample Screening**: Run `lean_counterexample_search` (`@counterexample-first-proving`) and check static `FIDELITY-04` (`Nat` subtraction truncation `a - b` when `a < b`) before investing >10 tactic steps.
4. **Canonical Tactic Dispatch & `@[grind]` Tagging**:
   - Dispatch order: `rfl` / `sair_decide` -> `simp only [...]` -> `omega` / `linarith` / `positivity` -> `ring` / `abel` -> `grind` / `aesop` -> structured `have` / `calc` / `induction`.
   - Annotate clean equational and forward-chaining lemmas with `@[grind =]` / `@[grind ->]` where reusable; never leave bare non-terminal `simp`.

---

## 3. The Abstraction-Concrete Duality (`@[csimp]` Twin Architecture)

Across all modules (`Template_Theorem`, `Template_DataModule`, `Template_ComputableTwin_Csimp`, `Template_KernelWHNF_SAIR`):

1. **Abstract in `Prop` Specifications (Where Concreteness Adds Friction)**:
   - State theorems over minimal algebraic/order/lattice/metric interfaces (`Monoid`, `CommRing`, `PartialOrder`, `Fin n -> α`, `List α`) rather than fixed-arity parameters (`a0 a1 a2 a3`, `FIDELITY-08`) or raw bit-packed words.
2. **Concrete in Computable Definitions & Kernel Witnesses (Where Abstractions Cost WHNF / Codegen)**:
   - Eliminate polymorphic `ite`/`Decidable` dictionaries (`SAIR-LAW-08` -> `Bool.rec`), `WellFounded.fix`/`brecOn` (`SAIR-LAW-06` -> structural `Nat.rec`), nested `Prod` boxing (`SAIR-LAW-09` -> flat `structure` or CPS), and `Prop` witnesses inside runtime cones (`SAIR-LAW-22`).
   - Connect the two layers via `@[csimp] theorem specFn_eq_fastFn : @specFn = @fastFn` (`SAIR-LAW-07`).

---

## 4. Scoped Unicode & Trust-Base Invariants (`INV-001`)

- **Valid UTF-8 Lean 4 Mathematical Symbols**: Standard mathematical operators (`∀`, `∃`, `≤`, `≥`, `≠`, `→`, `↔`, `∑`, `∏`, `⊗`, `∈`, `⊆`, Greek/subscripts `α`, `β`, `ℝ`, `ℕ`, `ℤ`, `ℚ`) are idiomatic and encouraged in Lean 4 and Markdown math exposition.
- **Banned Typographic Punctuation & Invisible Characters**: Curly quotes, en/em dashes (`--` in ASCII instead), horizontal ellipsis (`...` instead), NBSP (`\u00A0`), zero-width characters, and bidi overrides are strictly banned across all files.
- **3-Axiom Kernel Lockdown**: Exported theorems must depend on at most `[propext, Classical.choice, Quot.sound]` (`@lean-verification-gate`). Avoid `native_decide` and `bv_decide` whenever `Lean.ofReduceBool` / `Lean.trustCompiler` is disallowed; use `sair_decide` (`examples/Template_SairDecide.lean`).

---

## 5. Unified Module Section Skeleton

```lean
namespace <Project>.<Module>

/-! ### §1 Variables & Abstract Interfaces -/
/-! ### §2 Definitions & `@[csimp]` Computable Twins -/
/-! ### §3 Helper Lemmas (`private` by default) -/
/-! ### §4 Main Public Theorems & Non-Vacuity Witnesses -/

end <Project>.<Module>
```

## 6. Host-Repository Override Slot

Downstream repositories place project-specific deltas (such as fixed-point scaling conventions or paper anchor formats) in `<host>/skills-overrides/templates/Template_<Name>.md` linking back to `templates/core/Template_<Name>.md` or `templates/workflow/Template_<Name>.md` without duplicating generic prose.
