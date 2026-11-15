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

---

## 3. Worked Patterns & Scratch-Harness Idioms

### 3.1 Galois-Pruned Boundary Grid Before Random Fuzzing
Random generators rarely hit exact equality planes (`a + b = c`), zero-divisors, or `Nat` subtraction truncation corners (`a < b`). Always probe the deterministic Galois boundary lattice first:
- **`Nat` / `UInt64`**: `{0, 1, 2, k - 1, k, k + 1}` and pairs with `a = 0, b = 1` (`0 - 1 = 0`).
- **Lists / Sequences**: `[]`, `[0]`, `[0, 0]` (duplicate elements break injectivity/nodup assumptions), and `[1, 0]` (unsorted order).
- **Graphs / Relations**: empty graph (`0` vertices), isolated vertex, self-loop, 2-cycle (non-DAG), and disconnected two-component graph.

```lean
-- Ephemeral scratch probe (NEVER commit into library modules):
section ScratchFalsify
def checkClaim (a b : Nat) : Bool :=
  decide ((a - b) + b = a)

-- Immediately exposes (0, 1) -> false without invoking heavy tactics!
#eval (List.range 4).flatMap fun a =>
  (List.range 4).filterMap fun b =>
    if checkClaim a b then none else some (a, b)
end ScratchFalsify
```

### 3.2 Testing Non-Decidable `Real` / Topological Conjectures via Rational Specialization
When a theorem quantifies over `[Field K]` or `Real`, `Plausible` cannot directly decide equality on arbitrary reals. Specialize the statement in a scratch block to `Rat` (`ℚ`) or `Fin n -> Rat` over `{ -2, -1, -1/2, 0, 1/2, 1, 2 }`:
1. If the specialized `ℚ` claim fails on `(-1/2, 1)`, the universal `ℝ` theorem is refuted immediately (since `ℚ` embeds into `ℝ` preserving ring and order operations).
2. If the specialized claim holds on all rational witnesses up to denominator 4, inspect whether completeness (`sSup`, `Tendsto`) or positivity (`0 < x`) was omitted from hypotheses.

### 3.3 Mid-Proof Subgoal Falsification Rule (10-Step Cutoff)
Whenever an `induction`, `rw`, or `cases` step leaves an open subgoal that resists closure for more than 10 tactic steps:
1. Extract the current subgoal context and target via `lean_goal(filePath, line, col, target="filtered")`.
2. Form a standalone scratch lemma from that subgoal and run `lean_counterexample_search(strategy="dense")`.
3. Over 40% of stuck induction steps in practice stem from an **under-strengthened induction hypothesis** (where the subgoal is literally false for general `ih` inputs even though the top-level theorem is true!). Shrinking pinpoints the missing invariant term immediately.

## 4. Pitfalls, Recovery & Handoffs
- **Never commit `#eval` or `plausible` calls** into production library files; keep falsification strictly in `lean_counterexample_search` or untracked scratch probes.
- **Vacuous Precondition Trap**: If `Plausible` reports "gave up after 100 discarded samples", your hypotheses `h1 ∧ h2` may be mutually inconsistent (`FIDELITY-01` vacuity)! Construct a positive witness (`example : ∃ x, Precond x`) before proving `Precond x → Concl x`.
- **Handoffs**: Predecessors: `lean-specification`, `lean-proof`. Successors: `lean-specification` (on counterexample `w`), `lean-proof` (once falsification passes clean).
