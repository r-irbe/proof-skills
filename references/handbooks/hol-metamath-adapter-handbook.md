---
name: hol-metamath-adapter-handbook
description: Reference handbook for @hol-metamath-adapter with Goal-Shape Templates,
  HOL-Light/Metamath-to-Lean4 Phrasebook, and Error-to-Fix Table.
extracted_from: skills/hol-metamath-adapter/SKILL.md
---

# HOL Light & Metamath (`set.mm`) Proof Adapter Handbook

Complete guide for translating HOL Light (`.ml`) tactical proofs and Metamath (`set.mm`) ZFC theorems into idiomatic Lean 4 + Mathlib4.

## Goal-Shape Templates (templates)

| HOL Light / Metamath Source Pattern | Concordance ID | Lean 4 Target Template |
| :--- | :--- | :--- |
| HOL Light `SUBGOAL_THEN \`P\` ASSUME_TAC THENL [t1; t2]` | `CONC-02-FORWARD-HAVE-OBTAIN` | `have hP : P := by t1` followed by `t2` |
| HOL Light `INDUCT_TAC THENL [base; step]` | `CONC-01-CASE-INDUCTION` | `induction n with \| zero => base \| succ n ih => step` |
| HOL Light `CONV_TAC WORD_BLAST` / `WORD_ARITH_TAC` | `CONC-18-BITVEC-SWAR-DECISION` | `by bv_decide` / `by bv_omega` |
| Metamath `3eqtri` / `eqletr` / `lelttr` chain | `CONC-06-CALCULATION-BLOCKS` | `calc a = b := ... _ <= c := ... _ < d := ...` |
| Metamath `uzind` on `k e. ( Z>= ` M )` | `CONC-01-CASE-INDUCTION` | `induction k, hk using Int.le_induction` (or `Nat.le_induction`) |
| Metamath `G e. Grp , B = ( Base ` G ) , .+ = ( +g ` G )` | `CONC-04-TYPECLASS-TOWERS` | `variable {G : Type*} [Group G]` |

## Intent-to-Tactic Phrasebook (phrasebook)

| HOL Light / Metamath Tactic | Lean 4 Equivalent | Notes |
| :--- | :--- | :--- |
| `MESON_TAC[th1; th2]` / `METIS_TAC` | `aesop` / `grind [th1, th2]` | First-order resolution (`CONC-05`) |
| `ARITH_TAC` / `INT_ARITH_TAC` | `omega` | Linear `Nat`/`Int` arithmetic (`CONC-13`) |
| `REAL_ARITH_TAC` / `REAL_RING` / `REAL_FIELD` | `linarith` / `ring` / `field_simp; ring` | Real linear, polynomial, and field solvers (`CONC-13`, `CONC-14`) |
| `REWRITE_TAC[FUN_EQ_THM; EXTENSION]` | `ext x` | Function and set extensionality (`CONC-19`) |
| Metamath `syl` / `mpd` / `pm2.*` chains | `tauto` / `aesop` | Propositional & syllogistic deduction (`CONC-05`) |
| Metamath `sqge0` / `mulge0` / `addge0` / `expgt0` | `positivity` | Non-negativity and strict positivity (`CONC-13`) |
| Metamath `decadd` / `decmul` / `prmo` | `norm_num` / `decide` | Arithmetic & primality evaluation (`CONC-02`) |
| Metamath `fsum` over `( M ... N )` | `∑ k ∈ Finset.Icc M N, f k` | Closed integer interval sum (`CONC-17`) |

## Error-to-Fix Table (errors)

| Porting Bug / Error | Foundational Cause (HOL / Metamath vs Lean 4) | Deterministic Fix |
| :--- | :--- | :--- |
| Silent arithmetic bug on `m - n` from `set.mm` | In `set.mm`, `N c_ Z c_ C` so `m - n` is true integer subtraction; Lean `Nat.sub` truncates to `0` when `m < n` | Use `Int` (`(m : Int) - n`) or `zify [h_le]` with explicit `n <= m` hypothesis |
| Off-by-one in `nsum (0..n) f` vs `Finset.range n` | HOL Light `(0..n)` has `n + 1` elements (`[0, n]`); `Finset.range n` has `n` elements (`[0, n)`) | Map `(0..n)` to `Finset.range (n + 1)` or `Finset.Iic n` |
| Punctured limit mismatch on `(f --> l) (at a)` | HOL Light `at a` excludes `a` (`0 < dist(x,a) < e`) | Translate `at a` to `𝓝[≠] a` (`nhdsWithin a {a}^c`) in Mathlib (`CONC-20`) |
| `REAL_FIELD` fails to translate directly to `ring` | `REAL_FIELD` clears denominators automatically | Run `field_simp [h_nonzero]` before `ring` in Lean 4 |
| `new_type_definition` non-emptiness obligation | Every HOL Light type must be non-empty | Provide `[Nonempty α]` or `Inhabited` witness when lifting subtypes |

---

## 2. Structural Translation Architecture: HOL Light & Metamath -> Lean 4

### 2.1Foundational Carrier & Partial-Function Alignment
Both HOL Light and Metamath (`set.mm`) encode partial operations as total functions with convention defaults that occasionally differ from Lean 4 / Mathlib4:
1. **Number Hierarchy (`set.mm` `ℕ ⊆ ℤ ⊆ ℝ ⊆ ℂ` vs Lean 4 Distinct Types)**:
   - In `set.mm`, `A - B` on `A, B ∈ ℕ₀` is **true complex/integer subtraction**, NOT truncating `Nat.sub`! Translating `( M - N )` literally to `(m : Nat) - n` introduces `FIDELITY-04` soundness bugs whenever `m < n`. Always translate `set.mm` subtraction over `ℕ₀` or `ℤ≥` either to `(m : Int) - (n : Int)` or guard with `(h : n ≤ m)` and verify via `@counterexample-first-proving`.
2. **Interval & Big-Operator Endpoints**:
   - HOL Light `nsum (m..n) f` and Metamath `( M ... N )` are **closed** intervals `[m, n]` (empty when `n < m`). Map them to `Finset.Icc m n` (never `Finset.range n`, which is `[0, n)`).
3. **Topological & Analytic Filters (`CONC-20`)**:
   - HOL Light `(f --> l) (at a)` and `(f --> l) sequentially` map to `Filter.Tendsto f (nhdsWithin a {a}^c) (nhds l)` and `Filter.Tendsto f Filter.atTop (nhds l)`.

### 2.2 Idiomatic Tactical De-Compilation (`THENL` / RPN Stacks -> Structured Lean 4)
Do not transliterate raw HOL Light `THEN` chains or 80-step Metamath RPN syllogisms (`syl`, `mp2b`, `eqtr4i`) line-by-line:
1. **Slice at Forward Milestones**: Convert `SUBGOAL_THEN` and Metamath intermediate labeled steps (`$p` lemmas / internal deduction checkpoints) into explicit typed `have h_step : ... := by ...` claims.
2. **Collapse Equational & Inequality Chains into `calc`**: Any chain of `3eqtri`, `eqtrd`, `letrd`, `ltlerd` in `set.mm` or `TRANS` convs in HOL Light becomes a single readable `calc` block where each step is closed by `rw`, `ring`, `linarith`, or `gcongr`.
3. **Replace `MESON_TAC` / `ARITH_TAC`**: Map first-order `MESON_TAC [lem1; lem2]` to `grind [lem1, lem2]` or `aesop`, and linear `ARITH_TAC` / `INT_ARITH_TAC` to `omega`.

```lean
-- Metamath `uzind` + `fsum` port idiom in Lean 4:
theorem sum_icc_linear (m n : Int) (hmn : m ≤ n) :
    (∑ k ∈ Finset.Icc m n, (2 * k + 1)) = (n + 1) ^ 2 - m ^ 2 := by
  induction n, hmn using Int.le_induction with
  | base => simp; ring
  | succ k hmk ih =>
    rw [Finset.sum_Icc_succ_top (by omega), ih]
    ring
```

## 3. Verification & Handoffs
- Run `lean_search(query: "<CONC-ID>", source: "concordance")` to resolve dialect mappings, screen statements with `lean_counterexample_search`, and verify strict 3-axiom compliance (`#print axioms`) via `@lean-verification-gate`.
