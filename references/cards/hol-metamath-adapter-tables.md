---
name: "hol-metamath-adapter-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/hol-metamath-adapter-handbook.md."
generated_from: "references/handbooks/hol-metamath-adapter-handbook.md"
skill_ref: "skills/hol-metamath-adapter/SKILL.md"
---

# `hol-metamath-adapter` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/hol-metamath-adapter-handbook.md`](../handbooks/hol-metamath-adapter-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| HOL Light `SUBGOAL_THEN \`P\` ASSUME_TAC THENL [t1; t2]` | `CONC-02-FORWARD-HAVE-OBTAIN` | `have hP : P := by t1` followed by `t2` |
| HOL Light `INDUCT_TAC THENL [base; step]` | `CONC-01-CASE-INDUCTION` | `induction n with | zero => base | succ n ih => step` |
| HOL Light `CONV_TAC WORD_BLAST` / `WORD_ARITH_TAC` | `CONC-18-BITVEC-SWAR-DECISION` | `by bv_decide` / `by bv_omega` |
| Metamath `3eqtri` / `eqletr` / `lelttr` chain | `CONC-06-CALCULATION-BLOCKS` | `calc a = b := ... _ <= c := ... _ < d := ...` |
| Metamath `uzind` on `k e. ( Z>= ` M )` | `CONC-01-CASE-INDUCTION` | `induction k, hk using Int.le_induction` (or `Nat.le_induction`) |
| Metamath `G e. Grp , B = ( Base ` G ) , .+ = ( +g ` G )` | `CONC-04-TYPECLASS-TOWERS` | `variable {G : Type*} [Group G]` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| `MESON_TAC[th1; th2]` / `METIS_TAC` | `aesop` / `grind [th1, th2]` | First-order resolution (`CONC-05`) |
| `ARITH_TAC` / `INT_ARITH_TAC` | `omega` | Linear `Nat`/`Int` arithmetic (`CONC-13`) |
| `REAL_ARITH_TAC` / `REAL_RING` / `REAL_FIELD` | `linarith` / `ring` / `field_simp; ring` | Real linear, polynomial, and field solvers (`CONC-13`, `CONC-14`) |
| `REWRITE_TAC[FUN_EQ_THM; EXTENSION]` | `ext x` | Function and set extensionality (`CONC-19`) |
| Metamath `syl` / `mpd` / `pm2.*` chains | `tauto` / `aesop` | Propositional & syllogistic deduction (`CONC-05`) |
| Metamath `sqge0` / `mulge0` / `addge0` / `expgt0` | `positivity` | Non-negativity and strict positivity (`CONC-13`) |
| Metamath `decadd` / `decmul` / `prmo` | `norm_num` / `decide` | Arithmetic & primality evaluation (`CONC-02`) |
| Metamath `fsum` over `( M ... N )` | `sum k in Finset.Icc M N, f k` | Closed integer interval sum (`CONC-17`) |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Silent arithmetic bug on `m - n` from `set.mm` | In `set.mm`, `N c_ Z c_ C` so `m - n` is true integer subtraction; Lean `Nat.sub` truncates to `0` when `m < n` | Use `Int` (`(m : Int) - n`) or `zify [h_le]` with explicit `n <= m` hypothesis |
| Off-by-one in `nsum (0..n) f` vs `Finset.range n` | HOL Light `(0..n)` has `n + 1` elements (`[0, n]`); `Finset.range n` has `n` elements (`[0, n)`) | Map `(0..n)` to `Finset.range (n + 1)` or `Finset.Iic n` |
| Punctured limit mismatch on `(f --> l) (at a)` | HOL Light `at a` excludes `a` (`0 < dist(x,a) < e`) | Translate `at a` to `[!=] a` (`nhdsWithin a {a}`) in Mathlib (`CONC-20`) |
| `REAL_FIELD` fails to translate directly to `ring` | `REAL_FIELD` clears denominators automatically | Run `field_simp [h_nonzero]` before `ring` in Lean 4 |
| `new_type_definition` non-emptiness obligation | Every HOL Light type must be non-empty | Provide `[Nonempty ]` or `Inhabited` witness when lifting subtypes |
