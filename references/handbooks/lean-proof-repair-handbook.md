---
name: lean-proof-repair-handbook
description: Reference handbook for @lean-proof-repair with Goal-Shape Templates,
  Intent-to-Tactic Phrasebook, and Error-to-Fix Table.
extracted_from: skills/lean-proof-repair/SKILL.md
---

# Lean 4 Proof Repair Handbook

Systematic methodology for repairing broken Lean 4 proofs across toolchain upgrades (`v4.x` bumps), Mathlib API migrations, and internal definition refactors while preserving theorem signatures byte-for-byte.

## Goal-Shape Templates (templates)

| Goal / Breakage Shape | Diagnostic Signature | Repair Template |
| :--- | :--- | :--- |
| Renamed Mathlib lemma in `rw [old_name]` | `unknown identifier 'old_name'` | Query `lean_search(query: "<LHS> = <RHS>", source: "loogle")` -> replace with `rw [new_name]` |
| Non-terminal `simp` drifted after bump | `unsolved goals` after `simp; exact h` | Replace bare `simp` with `simp only [explicit_lemmas]` + `omega` / `ring` |
| `omega` fails on `Nat` subtraction after refactor | `omega could not prove the goal` with `a - b` | Add `have h_le : b <= a := by ...` before `omega`, or `zify [h_le] at *` |
| `fun_induction` / `induction` binder mismatch | `too many variable names provided` | Call `lean_lookup_symbol` on recursor/function and update `\| caseName x y ih =>` binders |
| Typeclass diamond after new import | `failed to synthesize` or `type mismatch` on instances | Pin instance explicitly via `haveI : Class T := instName` or `convert thm using 1` |
| `ext` peels too many or too few layers | `unsolved goals` after `ext x` | Replace unbounded `ext` with explicit `funext x` or `apply Set.ext; intro x` |

## Intent-to-Tactic Phrasebook (phrasebook)

| Repair Intent | Canonical Tactic / MCP Action | Notes |
| :--- | :--- | :--- |
| Locate replacement for deprecated/renamed lemma | `lean_search(query: "...", source: "loogle")` | Search by type signature rather than old substring name |
| Bridge minor definitional or cast mismatch between `h` and goal | `convert h using 1` (or `exact_mod_cast h`) | Bounds congruence depth to 1 so subgoals remain tiny |
| Recover broken `rw` caused by implicit argument change | `erw [lemma]` temporarily to diagnose, then `rw [lemma (x := val)]` | Never leave bare `erw` in final repaired code if explicit binder works |
| Freeze fragile `simp` call against future Mathlib drift | `simp only [lem1, lem2]` | Eliminates global `[simp]` set perturbations |
| Re-align shifted ring/linear expression | `ring_nf` or `linarith [h1, h2]` | Replaces brittle multi-step `rw [add_assoc, add_comm]` chains |
| Check if upstream `def` change made theorem false | `lean_counterexample_search(strategy: "dense")` | Run immediately if 3 repair attempts fail |

## Error-to-Fix Table (errors)

| Compiler / LSP Error | Root Cause | Deterministic Fix |
| :--- | :--- | :--- |
| `unknown identifier 'Foo.bar'` | Mathlib rename or split module import | Run `lean_search(query: "bar", source: "code")`; update identifier and `import` header |
| `simp made no progress` | Target lemma removed from `@[simp]` or LHS already in normal form | Delete redundant `simp` or pass explicit `simp only [target_lemma]` |
| `application type mismatch` | Argument order or implicitness `{x}` vs `(x)` changed upstream | Inspect signature with `lean_lookup_symbol`; use `@lemma` or named `(x := ...)` |
| `motive is not type correct` | Dependent index in `rw` or `cases` generalized improperly | Replace `cases e` with `rcases h : e with ...` or `generalize hx : e = x` |
| `maximum recursion depth / deterministic timeout` | Typeclass diamond or looping `[simp]` lemma introduced by new import | Switch `simp` to `simp only [...]` and check `synthInstance.maxHeartbeats` |

---

## 2. Pin-Drift & Toolchain Upgrade Playbook (`v4.x` -> `v4.34.1+`)

When bumping `lean-toolchain` and `lake-manifest.json` across a multi-hundred-module corpus, repair breakages in topological DAG order (Layer 0 -> top) using seven deterministic patterns:

1. **Identifier & Module Split Resolution**:
   - Never guess renamed Mathlib lemma names from memory. Query `lean_search(query: "<type pattern>", source: "loogle")` or `lean_search(query: "<old stem>", source: "code")` against the local `.lake/packages/mathlib` checkout.
   - Common modern Mathlib4 patterns: zero-divisor lemmas carry `₀` suffixes (`div_le_div_iff₀`, `div_lt_iff₀`), camelCase big-operator names (`tendsto_finsetSum`, `continuous_finsetSum`), and root-scoped `∑`/`∏` binders (delete vestigial `open scoped BigOperators` unless `𝔼` is used).
2. **`simp` Drift Quarantine (`simp` -> `simp only [...]`)**:
   - Upstream `@[simp]` additions/removals change intermediate normal forms. On the **old** working pin (if accessible) run `simp?` to freeze `simp only [...]`; on the **new** pin inspect `lean_goal` before and after `simp`, peel off the drifted rewrite, and close algebra/order residuals with `ring`, `linarith`, or `omega`.
3. **`rw` Auto-`rfl` & Transparency Shifts**:
   - Recent Lean 4 versions tighten `rw` transparency or close goals earlier when `rw` triggers automatic `rfl` (causing `no goals to be solved` on the next tactic!). Delete trailing redundant `rfl` steps, or replace `rw [lem]` on non-reducible type synonyms (`Matrix`, `Subtype` aliases) with `simp only [lem]` + `exact`.
4. **Binder & Implicitness Shifts (`intro` / `induction ... generalizing`)**:
   - Inspect exact binder order via `lean_goal(target: "tactic")`: implicit `{a b}` binders inside unfolded definitions (`Convex`, `Tendsto`) shift positional `intro` names silently, and `induction k generalizing j` already introduces `j` in each arm (remove duplicate `intro j`).
5. **Decidability & Classical Instance Drift**:
   - If an `if c then ... else ...` expression fails instance synthesis after an import trim, add `open Classical in` locally on `Prop` branches (or switch computational branches to `Bool` + `cond`).

## 3. Hard Repair Invariants & Handoffs
- **Signature Immutability**: Never weaken or alter a theorem's statement to make a broken proof compile! If an upstream definition genuinely changed semantics, halt and escalate to `specifier`.
- **Zero `sorry` / Zero `native_decide` Escapes**: Never patch a broken proof with `sorry` or `native_decide`.
- **Handoffs**: Predecessors: `lean-dependency-management`, `lean-bisect`. Successors: `lean-proof-review`, `lean-verification-gate`.
