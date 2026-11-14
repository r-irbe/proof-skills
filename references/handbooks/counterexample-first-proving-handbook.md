---
name: counterexample-first-proving-handbook
description: Reference handbook for @counterexample-first-proving (Plausible property-based
  testing, Galois-pruned boundary witness search, and pre-proof conjecture falsification).
extracted_from: skills/counterexample-first-proving/SKILL.md
---

# Counterexample-First Proving & Conjecture Falsification Handbook

> **Scope**: Pre-proof conjecture screening via `lean_counterexample_search`, `Plausible` (`SampleableExt`, `Shrinkable`), boundary-witness enumeration (`0`, `1`, `Nat` subtraction underflow `a < b`), and small-model falsification before allocating interactive tactic effort.
> **Encoding**: Scoped Unicode policy (`typographic-free` by default) per `INV-001`.

---

## 1. Quick-Lookup Indexing Tables (`mathcomp-skills` Three-Entry-Point Pattern)

### Table 1: Goal-Shape-First (`templates` Entry Point)

| Goal / Term Shape | Falsification Strategy | Canonical Probe / Tactic |
| :--- | :--- | :--- |
| Universal arithmetic claim `∀ a b : Nat, P a b` | Galois boundary sweep (`0, 1, 2`, `a < b` truncation) | `lean_counterexample_search(strategy: "dense")` or `#eval` over `List.product [0,1,2,3] [0,1,2,3]` |
| Conditional inequality `h : f x ≤ g x ⊢ p x ≤ q x` | Boundary equality & sign-flip witness probe | Test `x = 0`, negative `x`, and degenerate zero-denominator / zero-weight inputs |
| List / Finset invariant `∀ xs : List α, P xs` | Small-length enumeration (`[]`, `[x]`, `[x, x]`, `[x, y]`) | `plausible` tactic with `SampleableExt` or bounded `Decidable` check on `Fin 3` |
| Matrix / graph property `∀ G : SimpleGraph (Fin n), ...` | Small-order canonical graphs (`n = 0, 1, 2, 3`, disconnected, self-loop) | Evaluate decidable witness predicate on `n ≤ 4` before attempting induction |
| Fixed-width bitvector identity `∀ x y : BitVec w, ...` | Small-width instantiation (`w = 1, 2, 4, 8`) + `MSB` sign boundary | Instantiate `w := 4` with `decide +kernel` or run `bv_decide` in scratch probe |

### Table 2: Intent-First (`phrasebook` Entry Point)

| User / Engineer Intent | Recommended Tool / Pattern | Actionable Recipe |
| :--- | :--- | :--- |
| "Check if a new theorem statement is actually true before proving" | `lean_counterexample_search` | Run `lean_counterexample_search(filePath, theoremName, strategy: "dense")` in isolated scratch |
| "Detect hidden `Nat` subtraction truncation (`a - b = 0` when `a < b`)" | Boundary witness `(a := 0, b := 1)` + static `lean-analyzer` | Test `a < b` inputs; add explicit `(h : b ≤ a)` guard or lift statement to `Int` |
| "Test a non-decidable `Real` statement on concrete rationals" | Rational specialization (`ℚ` / scaled `Nat`) | Specialize `ℝ` parameters to `ℚ` values `0, 1, -1, 1/2` and evaluate via `norm_num` |
| "Distinguish a false theorem from a missing precondition" | Minimal counterexample shrinking | Shrink witness via `Shrinkable`, inspect violated edge case, and escalate precondition to `specifier` |

### Table 3: Error / Bottleneck-First (`errors` Entry Point)

| Symptom / Failure Mode | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| `plausible` reports `Unable to synthesize SampleableExt` | Custom `structure` or abstract type lacks generator instance | Specialize type variable `α := Fin 3` or `Int` in a scratch `example`, or derive `SampleableExt` |
| `plausible` finds counterexample `a = 0, b = 1` on `a - b + b = a` | Unguarded `Nat.sub` truncates at zero (`FIDELITY-04`) | Escalate to `specifier` to add hypothesis `h : b ≤ a` or restate over `Int` |
| Prover spends >15 tactic steps stuck on an induction step | Induction hypothesis is strictly weaker than true invariant or theorem is false | Run `lean_counterexample_search` on the current subgoal state before continuing manual tactics |
| `Decidable` synthesis fails on existential `∃ y, P x y` | Unbounded existential quantifier is not computationally enumerable | Bound witness domain (`∃ y ∈ Finset.range B, P x y`) for finite testing |

---

## 2. Standard Pre-Proof Falsification Protocol

1. **Static Vacuity & Truncation Pass**: Run `lean_diagnostics` (`lean-analyzer` WASM) to flag `FIDELITY-04` (`NatSubTruncation`) and `NatDivModByZero` before any dynamic sampling.
2. **Boundary Witness Sweep**: Test `{0, 1, 2, maxBound}` and degenerate structures (`∅`, singleton, duplicate elements).
3. **Property-Based Shrinking**: Invoke `lean_counterexample_search` (isolated scratch copy; zero source pollution).
4. **Escalation Contract**: When a counterexample witness `w` is confirmed (`¬ P w`), Prover MUST NOT silently weaken the theorem signature; record `w` in the handoff packet and return to `specifier`.
