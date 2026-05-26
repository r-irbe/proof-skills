# Lean 4 Template Reference

This directory contains **12 best-practice template files** for Lean 4 module
development (validated against Lean v4.28.0 + Mathlib v4.28.0 + cslib).

Use these as copy-paste starting points for new modules and as a reference for
patterns, pitfalls, and performance tips. Pair with the [Lean 4 Proof
Strategy](../references/lean4-proof-strategy.md) and [Lean 4 Tactic
Hierarchy](../references/lean4-tactic-hierarchy.md) guides.

> **Format note.** The templates are distributed as Markdown (`.md`) with
> embedded ` ```lean ` code blocks rather than as standalone `.lean` source.
> Lake therefore never tries to compile them, eliminating the risk of someone
> treating a template as a real module. To regenerate the Markdown from a
> revised `.lean` source, run `python3 scripts/lean/templates_to_md.py`
> (see [`scripts/lean/`](../scripts/lean/)).

---

## Template Navigator

| File | Use for | DAG Layer | Key tactics |
|------|---------|-----------|-------------|
| [`Template_Foundation.md`](./Template_Foundation.md) | Types, structures, inductive enums, decidable predicates | Layer 0 | `decide`, `grind`, `@[simp]`, `@[ext]` |
| [`Template_Arithmetic.md`](./Template_Arithmetic.md) | Nat/Int arithmetic, scaled thresholds, simplex constraints | Layer 0–1 | `grind`, `omega`, `norm_num`, `push_cast` |
| [`Template_Analysis.md`](./Template_Analysis.md) | Real analysis, continuity, Lipschitz, `Real.sqrt` | Layer 1–2 | `positivity`, `fun_prop`, `linarith`, `calc` |
| [`Template_Dynamics.md`](./Template_Dynamics.md) | Lyapunov stability, Markov chains, contraction mappings | Layer 2–3 | `ContractingWith`, `NNReal`, `linarith` |
| [`Template_Automation.md`](./Template_Automation.md) | `@[grind]` bridge lemmas, custom tactics, `@[simp]` sets | Layer 0 | `macro`, `elab_rules`, `Qq`, `register_grind_attr` |
| [`Template_Application.md`](./Template_Application.md) | Multi-layer theorem composition, pipeline models | Layer 2–3 | `simp only [...]`, `grind`, cross-module `have` |
| [`Template_Index.md`](./Template_Index.md) | Umbrella re-export modules | Layer 4 | `export`, `assert_not_exists` |
| [`Template_Lakefile.md`](./Template_Lakefile.md) | Lake build configuration, CI setup | N/A | Lake DSL |
| [`Template_ProofStrategy.md`](./Template_ProofStrategy.md) | Proof methodology, tactic hierarchy, finding lemmas, debugging | N/A | N/A |
| [`Template_Verification.md`](./Template_Verification.md) | Verification completeness, axiom auditing, testing | N/A | N/A |
| [`Template_Refactoring.md`](./Template_Refactoring.md) | Module splitting, DAG management, import organization | N/A | N/A |
| [`Template_Performance.md`](./Template_Performance.md) | Memory, parallelism, build optimization, tactic speed | N/A | N/A |

---

## Reference Templates

Templates 9–12 (`ProofStrategy`, `Verification`, `Refactoring`, `Performance`)
are **methodology guides**, not module starters. They do not correspond to any
specific module or DAG layer. Use them as checklists and reference material
alongside the module-starter templates (1–8).

---

## Quick-Start Patterns

### Starting a new leaf module
1. Copy `Template_Foundation.md`
2. Rename namespace `MyProject.MyModule` → `YourProject.YourModule`
3. Replace example types (`MyRecord`, `MyPhase`, `myFunc`) with your domain types
4. Add `assert_not_exists Real` at end if no analysis imports

### Starting a new arithmetic module
1. Copy `Template_Arithmetic.md`
2. Define your scale constants (`×100` or `×1000`)
3. Prove simplex constraints with `@[grind]` + `grind`
4. Add `by decide` unit tests for all threshold values

### Starting a new analysis module
1. Copy `Template_Analysis.md`
2. Import only the Mathlib analysis files you need
3. Use `positivity` for non-negativity, `fun_prop` for continuity
4. Avoid `nlinarith` on `Real.sqrt` — use `Real.sqrt_le_sqrt` + `linarith`

### Starting a new dynamics module
1. Copy `Template_Dynamics.md`
2. Choose your state space type (custom struct or `EuclideanSpace ℝ (Fin n)`)
3. Define Lyapunov function as `NNReal`-valued
4. Use `ContractingWith K f` for contraction mapping theorems

### Adding automation / bridge lemmas
1. Copy `Template_Automation.md`
2. Choose the right `@[grind]` variant for each lemma
3. Register `register_grind_attr myproject_grind` for project-specific tagging
4. Use `macro` for simple tactic abbreviations, `elab_rules` for complex ones

---

## Tactic Hierarchy Reference

See [`references/lean4-tactic-hierarchy.md`](../references/lean4-tactic-hierarchy.md)
for the full priority order. Quick summary:

```
rfl → decide/norm_num → native_decide → grind → omega → linarith
    → simp only [...] → aesop → nlinarith → ring/field_simp → bare simp
```

**Principle**: always try the fastest tactic first. Use `grind` as the primary
general-purpose tactic (not `omega`, which is more limited).

---

## `@[grind]` Variant Quick Reference

| Variant | When to use | Example |
|---------|-------------|---------|
| `@[grind =]` | Equational rewrites (like `@[simp]` for grind) | `a * 0 = 0` |
| `@[grind →]` | Forward implication: if P holds, add Q | `h : a ≤ b ⊢ a / c ≤ b / c` |
| `@[grind ←]` | Backward from conclusion | `⊢ v / 100 ≤ 1 ← h : v ≤ 100` |
| `@[grind norm]` | Normalization pre-processing (**v4.28**) | Canonical form simplification |
| `@[grind unfold]` | Always unfold in preprocessing (**v4.28**) | Transparent definition |

**v4.28 features**: `register_grind_attr`, `grind_pattern`, `grind +locals`, `grind +suggestions`.

> **Note on `first_par`**: The parser exists in v4.28.0 but the tactic is **NOT YET IMPLEMENTED** — it errors with "has not been implemented". Use sequential `first | tac1 | tac2 | tac3` until a future Lean version enables it.

---

## DAG Layer Rule (reminder)

```
Layer 3 (top)   →   imports from Layers 0–2
Layer 2         →   imports from Layers 0–1
Layer 1         →   imports from Layer 0
Layer 0 (leaf)  →   imports nothing project-local (only Mathlib / cslib)
```

A module at Layer N may only import modules at Layer ≤ N−1. Use
`assert_not_exists` to enforce this at the type level. See
[`references/lean4-module-dependency-guide.md`](../references/lean4-module-dependency-guide.md)
for the full discussion.

---

## Module Size Guidelines

| Lines | Action |
|-------|--------|
| < 500 | Ideal for leaf (Layer 0) modules |
| 500–2000 | Acceptable for any layer |
| 2000–2500 | Consider splitting |
| > 2500 | **Must split** into `.Core` + `.Lemmas` + `.Main` |
| > 3000 | **Bad**: causes full recompilation on every edit |

---

## Common Pitfalls (from all templates)

| Pitfall | Fix |
|---------|-----|
| `nlinarith` on `Real.sqrt` goals | Use `Real.sqrt_le_sqrt` + `linarith` |
| Bare `simp` in finished proofs | Use `simp only [lemma1, lemma2]` |
| `set_option maxHeartbeats 0` globally | Set per-theorem with `set_option maxHeartbeats N in` |
| Missing `@[ext]` on structures | Add `@[ext]` to every record-like structure |
| `import Mathlib.Analysis.*` in leaf modules | Use narrow imports |
| `open Namespace` at module top in index | Use `export Namespace (name1 name2)` |
| Mixing ×100 and ×1000 scales without casts | Define named scale constants + cast lemmas |
| DAG layer cycle | Use `#import_path SomeDecl` (v4.28, takes declaration names not module names) to trace; refactor |
| `native_decide` in mathlib PRs | Use `decide` (kernel-checkable); `native_decide` is not |

---

## Performance Tips Summary

1. **`lake exe cache get`** before first build — saves hours of Mathlib compilation
2. **`lake build -j $(nproc)`** — parallel build using all CPU cores
3. **Narrow imports** — import specific Mathlib files, not `Mathlib.Tactic`
4. **Module splitting** — files > 2500 lines invalidate build cache for all importers
5. **`#count_heartbeats`** — measure before setting `maxHeartbeats`
6. **`lake shake`** (v4.28) — remove unused imports that inflate compile times
7. **`@[grind]` over repeated hints** — register once, use everywhere
8. **`native_decide` for large finite checks** — much faster than `decide`, but not kernel-checkable

See `Template_Performance.md` for in-depth performance tuning.

---

## See Also

- [`references/mathlib4-conventions.md`](../references/mathlib4-conventions.md) — naming, file headers, capitalization
- [`references/lean4-module-dependency-guide.md`](../references/lean4-module-dependency-guide.md) — DAG enforcement, splitting workflow
- [`references/lean4-proof-strategy.md`](../references/lean4-proof-strategy.md) — one-step-at-a-time, error priority, hardest case first
- [`references/lean4-tactic-hierarchy.md`](../references/lean4-tactic-hierarchy.md) — full tactic priority table
- [`scripts/lean/`](../scripts/lean/) — runnable enforcement scripts (axiom audit, import hygiene, etc.)
