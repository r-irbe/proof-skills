---
name: "lean-proof-repair-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-proof-repair-handbook.md."
generated_from: "references/handbooks/lean-proof-repair-handbook.md"
skill_ref: "skills/lean-proof-repair/SKILL.md"
---

# `lean-proof-repair` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-proof-repair-handbook.md`](../handbooks/lean-proof-repair-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Renamed Mathlib lemma in `rw [old_name]` | `unknown identifier 'old_name'` | Query `lean_search(query: "<LHS> = <RHS>", source: "loogle")` -> replace with `rw [new_name]` |
| Non-terminal `simp` drifted after bump | `unsolved goals` after `simp; exact h` | Replace bare `simp` with `simp only [explicit_lemmas]` + `omega` / `ring` |
| `omega` fails on `Nat` subtraction after refactor | `omega could not prove the goal` with `a - b` | Add `have h_le : b <= a := by ...` before `omega`, or `zify [h_le] at *` |
| `fun_induction` / `induction` binder mismatch | `too many variable names provided` | Call `lean_lookup_symbol` on recursor/function and update `| caseName x y ih =>` binders |
| Typeclass diamond after new import | `failed to synthesize` or `type mismatch` on instances | Pin instance explicitly via `haveI : Class T := instName` or `convert thm using 1` |
| `ext` peels too many or too few layers | `unsolved goals` after `ext x` | Replace unbounded `ext` with explicit `funext x` or `apply Set.ext; intro x` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Locate replacement for deprecated/renamed lemma | `lean_search(query: "...", source: "loogle")` | Search by type signature rather than old substring name |
| Bridge minor definitional or cast mismatch between `h` and goal | `convert h using 1` (or `exact_mod_cast h`) | Bounds congruence depth to 1 so subgoals remain tiny |
| Recover broken `rw` caused by implicit argument change | `erw [lemma]` temporarily to diagnose, then `rw [lemma (x := val)]` | Never leave bare `erw` in final repaired code if explicit binder works |
| Freeze fragile `simp` call against future Mathlib drift | `simp only [lem1, lem2]` | Eliminates global `[simp]` set perturbations |
| Re-align shifted ring/linear expression | `ring_nf` or `linarith [h1, h2]` | Replaces brittle multi-step `rw [add_assoc, add_comm]` chains |
| Check if upstream `def` change made theorem false | `lean_counterexample_search(strategy: "dense")` | Run immediately if 3 repair attempts fail |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| `unknown identifier 'Foo.bar'` | Mathlib rename or split module import | Run `lean_search(query: "bar", source: "code")`; update identifier and `import` header |
| `simp made no progress` | Target lemma removed from `@[simp]` or LHS already in normal form | Delete redundant `simp` or pass explicit `simp only [target_lemma]` |
| `application type mismatch` | Argument order or implicitness `{x}` vs `(x)` changed upstream | Inspect signature with `lean_lookup_symbol`; use `@lemma` or named `(x := ...)` |
| `motive is not type correct` | Dependent index in `rw` or `cases` generalized improperly | Replace `cases e` with `rcases h : e with ...` or `generalize hx : e = x` |
| `maximum recursion depth / deterministic timeout` | Typeclass diamond or looping `[simp]` lemma introduced by new import | Switch `simp` to `simp only [...]` and check `synthInstance.maxHeartbeats` |
