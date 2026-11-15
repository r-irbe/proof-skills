---
name: "itp-cross-porting-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/itp-cross-porting-handbook.md."
generated_from: "references/handbooks/itp-cross-porting-handbook.md"
skill_ref: "skills/itp-cross-porting/SKILL.md"
---

# `itp-cross-porting` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/itp-cross-porting-handbook.md`](../handbooks/itp-cross-porting-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Agda `begin a  h1  b <= h2  c ` | `CONC-06-CALCULATION-BLOCKS` | `calc a = b := h1 _ <= c := h2` |
| Agda `[ x in A ] P x` (propositional `P`) | `CONC-10-SUBTYPES-SIGMA` | `{x : A // P x}` with `@[ext]` via `Subtype.ext` |
| Agda `solve n (\ x y -> lhs := rhs) refl` | `CONC-13-LINEAR-NONLINEAR-ARITHMETIC` | `by ring` (or `by omega` for linear `Nat`/`Int`) |
| Agda Cubical `data _/_ (A : Type) R` | `CONC-07-QUOTIENTS-SETOIDS` | `Quotient s` + `Quotient.lift` / `Quotient.inductionOn` |
| Foreign `at x` punctured limit (`Isabelle` / `HOL Light`) | `CONC-20-FILTERS-TOPOLOGICAL-LIMITS` | `Tendsto f ([!=] x) ( l)` (NOT unpunctured ` x`) |
| Foreign fixed-width word blast (`word_bitwise` / `WORD_BLAST`) | `CONC-18-BITVEC-SWAR-DECISION` | `by bv_decide` (or `by bv_omega`) |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Look up cross-prover tactic equivalence | Any foreign tactic | `lean_search(query: "<tactic or CONC-ID>", source: "concordance")` |
| Port Agda structural recursion with `Acc _<_ x` | `go x (acc rs)` | Drop `Acc` parameter; add `termination_by measure x` + `decreasing_by omega` |
| Port Setoid pointwise equality `f  g` (`--without-K`) | `forall  x -> f x  g x` | Prove `f = g` directly via `funext x` (`Quot.sound` provides `funext` in Lean 4) |
| Port foreign finite sum (`\sum`, `sumxinA`, `nsum`) | `CONC-17-BIG-OPERATORS-FINSET` | `sum x in s, f x` over `Finset ` with `Finset.sum_bij` / `Finset.sum_comm` |
| Port Lebesgue / Bochner integral (`LINT`, `\int[mu]`) | `CONC-16-MEASURE-INTEGRATION-BOCHNER` | `int x in s, f x ` (Bochner) or `int x, f x ` (`ENNReal`) + `by measurability` |
| Port classical postulate (`em : ExcludedMiddle`) | Explicit module postulate | Remove parameter; use `by_cases h : P` or `by_contra! h` |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| False theorem after porting `a - b` on naturals | Source (`Metamath` `N c_ C`) uses untruncated subtraction; Lean `Nat.sub` truncates at `0` | Cast to `Int` (`(a : Int) - b`) or add precondition `h : b <= a` before `omega` |
| Limit theorem fails at `x` (`Tendsto f ( x)`) | Source (`Isabelle` / `HOL Light`) `at x` excludes `x` (`0 < dist y x`) | Replace ` x` with punctured neighborhood `[!=] x` (`nhdsWithin x {x}^c`) |
| `failed to synthesize Decidable` on ported boolean reflection | Source uses `bool` predicate where Lean uses `Prop` | Add `open Classical in` locally or bridge via `decide` with `[DecidablePred P]` |
| Universe mismatch `Type u` vs `Set` when porting Agda `Set` | Agda `Set` is `Type 0` whereas Mathlib `Set ` is ` -> Prop` | Map Agda `Set` (universe) to `Type*` and Agda `Pred A l` to `Set A` |
| Division-by-zero discrepancy (`a / 0 = 0`) | Source guards `b != 0` implicitly in partial domain | Add explicit `(hb : b != 0)` hypothesis and discharge via `field_simp [hb]; ring` |
