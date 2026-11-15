---
name: lean-proof-refactor-handbook
description: Reference handbook for @lean-proof-refactor.
extracted_from: skills/lean-proof-refactor/SKILL.md
---

# Lean Proof Refactoring & Abstraction-Concrete Duality Handbook

> **Scope**: Post-hoc proof slimming (`CUT / CONSIDERED-NEGATIVE / DEFER`), helper-lemma extraction, the **`WAVE-13 G1` Abstraction-Concrete Duality Cost Law**, `@[csimp]` computable twins, statement-level `Real`-coupling generalization (`abstraction-safe` vs `nat-mixed` vs `real-specific`), and AltProof 3-tier tactic automation.
> **Encoding**: Scoped Unicode policy (`typographic-free` by default) per `INV-001`.

---

## Quick-Lookup Indexing Tables (`mathcomp-skills` Three-Entry-Point Pattern)

### Table 1: Goal-Shape-First (`templates` Entry Point)

| Goal / Term Shape | Primary Tactic / Pattern | Canonical Recipe / Notes |
| :--- | :--- | :--- |
| Proof `> 50 LOC` with repeated sub-block | `CUT` -> private/module helper lemma | Extract only when reusable (`>= 2` call sites or clean conceptual invariant) |
| Concrete coordinate/`Real` proof using only ring/order ops | Statement-level mixin generalization | Generalize `[CommRing R] [LinearOrder R] [IsOrderedRing R]`; keep `Real` theorem as 1-line corollary |
| Slow `Prop`-friendly `specFn` vs fast monomorphic `fastFn` | `@[csimp] theorem specFn_eq_fastFn` (`SAIR-LAW-07`) | Keep `specFn` clean for proofs; route LCNF execution & `rw` to `fastFn` |
| Parametric hot kernel step (`1,600x..3,345x` WHNF penalty) | `WAVE-13 G1` `rfl`-bridged Duality | Specialize hot `def` to raw unboxed `Nat`; prove parametric lemma in cold section; bridge via `rfl` |
| Verbose `Finset.sum` linearity or monotonicity block | `sum_congr_ring` / `finset_mono` / `finset_nonneg` | Collapse 15-40 line `Finset.sum` proofs to 1-line AltProof combinators |

### Table 2: Intent-First (`phrasebook` Entry Point)

| User / Engineer Intent | Recommended Tool / Idiom | Actionable Recipe |
| :--- | :--- | :--- |
| Slim a long proof corpus without regressions | `scripts/lean/proof_quality.py` + `CUT / CONSIDERED-NEGATIVE / DEFER` | Preserve public theorem signatures byte-for-byte; gate every batch on `0` warnings/errors |
| Eliminate single-use helper bloat ("bundle effect") | `CONSIDERED-NEGATIVE` adjudication | Do not split linear single-use glue that merely relocates line count |
| Audit which `Real`-typed theorems can be generalized | `python3 -m altproof.coupling_scanner` | Classify into `abstraction-safe` (algebraic/order), `nat-mixed`, or `real-specific` (`exp`/`log`/`nhds`) |
| Share proof structure across multiple concrete bit/SWAR kernels | `WAVE-13 G1` Cold Parametric Theorem + `rfl` Bridge | Prove once over `(step : State -> State)`; instantiate on concrete `fastStep` at `<= 1%` WHNF cost |

### Table 3: Error / Bottleneck-First (`errors` Entry Point)

| Symptom / Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Extracted helper requires 9+ awkward context variables | Cut boundary sliced mid-tactic state | Widen cut to a natural mathematical invariant or mark `CONSIDERED-NEGATIVE` |
| Generalizing a hot `def` slowed `rfl`/`decide` by `> 1,000x` | `WAVE-13 G1`: dictionary/closure dispatch inside hot `@Nat.rec` | Revert hot `def` to concrete monomorphic `Nat.*` ops; move polymorphism strictly to cold `theorem` layer |
| Public theorem signature changed during refactor | Hard API boundary violation | Revert signature edit; add generalized lemma alongside and prove original signature via 1-liner |
| Commute-diagram lift increased total LOC on tiny state | Commute pattern overhead (`<= 5` state ops) | Apply Commute diagram lifts only above the `> 20` state-operation threshold |

---

## 1. Core Refactoring Campaign Workflow (`CUT / CONSIDERED-NEGATIVE / DEFER`)

1. **Find** -- Scan the corpus for long or branch-heavy proofs:
   `python3 scripts/lean/proof_quality.py --lean-dir <dir> --output <report.md>`
   (measures line count, branch points, and tactic anti-patterns). Wrap defaults via `lean-project.toml`; never fork the scanner per repo.
2. **Adjudicate each finding** against one test: *can a generic block be named once and called in `>= 2` places (or isolate a standalone mathematical concept)?*
   - **`CUT`** -- Extract the shared, more general lemma.
   - **`CONSIDERED-NEGATIVE`** -- Single-use glue where splitting only relocates lines (the negative bundle effect); record the reason in the ledger so future waves do not re-litigate it.
   - **`DEFER`** -- Threshold-sitting proofs (`~50` lines, `<= 2` branches) deferred to a dedicated cleanup window.
3. **Extract** -- State the extracted lemma at its natural algebraic/order generality (`Finset`, `CommRing`, `PartialOrder`), prove it independently, and reduce each caller to a 1-3 line bridge.
4. **Gate** -- Full `lake build` (`0` errors, `0` warnings), axiom-closure verification, and `proof_quality.py` delta check (`before -> after`).

---

## 2. The Abstraction-Concrete Duality & `WAVE-13 G1` Cost Law

A foundational principle across mathematical libraries, kernel-verified algorithms, and hardware codegen: **use abstractions where concreteness adds proof friction, and be concrete where abstractions add kernel WHNF or hardware overhead.**

1. **`WAVE-13 G1` Empirical Cost Asymmetry**:
   - **Hot Computation Cone (`def`)**: Parameterizing a recursive kernel step over typeclasses (`[Semiring R]`), higher-order closures, or configuration records incurs a **`1,600x .. 3,345x` WHNF instruction penalty** because `type_checker.cpp` must unfold dictionary projections and allocate closures at every `@Nat.rec` step instead of folding raw C++/GMP `nat_lit` primitives.
   - **Cold Proof Cone (`theorem`)**: Proving theorems over an abstract parametric specification `specLoop (step : alpha -> alpha)` and bridging to the monomorphic concrete implementation `fastLoop` via a definitional equality bridge:
     ```lean
     theorem fastLoop_eq_specLoop (n x : Nat) :
         fastLoop n x = specLoop concreteStep n x := rfl
     ```
     costs **`<= 1%` kernel overhead** (`0` runtime WHNF penalty on `fastLoop`) while allowing one abstract proof to serve arbitrarily many concrete instantiations!
2. **Statement-Level Coupling Classification (`altproof.coupling_scanner`)**:
   - **`abstraction-safe`**: Mentions `Real` only through `+`, `-`, `*`, `<=`, `Finset.sum`, or `Matrix` -- generalize to `[CommRing R] [LinearOrder R] [IsOrderedRing R]`.
   - **`nat-mixed`**: Bridges discrete `Nat` / scaled-integer invariants to `Real` -- keep a clean cast boundary (`exact_mod_cast`, `push_cast`).
   - **`real-specific`**: Uses completeness, transcendental functions (`exp`, `log`, `sqrt`, `sin`), filters (`Tendsto`, `nhds`), derivatives, or measure theory -- keep on `Real` / topological spaces.
3. ** Dual-Path `@[csimp]` Bridge (`Template_ComputableTwin_Csimp.md`)**:
   - Pair `def specFn` (clean structural induction for proofs) with `def fastFn` (tail-recursive / SWAR / `BitVec` / hardware-extractable) via `@[csimp] theorem specFn_eq_fastFn : @specFn = @fastFn`.

---

## 3. AltProof 3-Tier Tactic Slimming & Advisor

Combine structural extraction with the 3-tier AltProof pipeline ([`Template_AltProofTactics.md`](../../templates/core/Template_AltProofTactics.md)):

1. **Tier 1 (Live Lean 4 Meta-Tactics in `packages/altproof/`)**:
   - `sum_congr_ring`: normalizes `Finset.sum` linearity (`sum_add_distrib`, `sum_sub_distrib`, `mul_sum`, `sum_mul`, `sum_neg_distrib`) and closes pointwise equalities via `Finset.sum_congr rfl` + `ring`.
   - `finset_mono`: discharges `Finset.sum s f <= Finset.sum s g` via `Finset.sum_le_sum`, automatic hypothesis specialization, and ordered-ring closers (`gcongr`, `linarith`, `positivity`, `omega`).
   - `finset_nonneg`: discharges `0 <= Finset.sum s f` via `Finset.sum_nonneg` + positivity/linear closers.
   - `sair_decide`: strict 3-rung kernel-clean closer (`first | rfl | decide +kernel | omega`) free of `Lean.ofReduceBool`.
   - `elegance?` / `alt_proof`: speculative search (`withoutModifyingState`) across ranked closers emitting `Try this: <tactic>`.
2. **Tier 2 (MCP Goal Advisor & Two-Axis Scorer)**:
   - Query `lean_goal(filePath, line, col, target="altproof")` or `lean_metrics(target, action="altproof")` for ranked tactic recommendations and two-axis elegance/kernel-cost dominance verdicts.

---

## 4. Pitfalls & Recovery

- **Do not fold `rw` + `simp only` blindly**: `rw` matches syntactic head constants at `reducible`/`implicit` transparency, whereas `simp only` simplifies bottom-up; collapsing a two-step rewrite can break downstream `nlinarith` atom matching.
- **Commute-diagram threshold (`> 20` ops)**: Commutative state-lifting diagrams pay off on large state machines (`> 20` transitions) but add net boilerplate on `<= 5`-op helpers.
- **Revert immediately on negative reuse**: If an extracted lemma has only 1 caller and increases file LOC + parameter plumbing, revert and log `CONSIDERED-NEGATIVE`.

## Handoffs

- **Predecessors:** `lean-proof` (initial green proof), `lean-corpus-audit` (long-proof census).
- **Successors:** `lean-sair-kernel-optimization` (hot WHNF / SWAR / codegen tuning), `lean-proof-review` (4-layer soundness & style audit).
