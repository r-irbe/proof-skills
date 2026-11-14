---
name: "counterexample-first-proving-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/counterexample-first-proving-handbook.md."
generated_from: "references/handbooks/counterexample-first-proving-handbook.md"
skill_ref: "skills/counterexample-first-proving/SKILL.md"
---

# `counterexample-first-proving` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/counterexample-first-proving-handbook.md`](../handbooks/counterexample-first-proving-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Universal arithmetic claim `forall  a b : Nat, P a b` | Galois boundary sweep (`0, 1, 2`, `a < b` truncation) | `lean_counterexample_search(strategy: "dense")` or `#eval` over `List.product [0,1,2,3] [0,1,2,3]` |
| Conditional inequality `h : f x <= g x  p x <= q x` | Boundary equality & sign-flip witness probe | Test `x = 0`, negative `x`, and degenerate zero-denominator / zero-weight inputs |
| List / Finset invariant `forall  xs : List , P xs` | Small-length enumeration (`[]`, `[x]`, `[x, x]`, `[x, y]`) | `plausible` tactic with `SampleableExt` or bounded `Decidable` check on `Fin 3` |
| Matrix / graph property `forall  G : SimpleGraph (Fin n), ...` | Small-order canonical graphs (`n = 0, 1, 2, 3`, disconnected, self-loop) | Evaluate decidable witness predicate on `n <= 4` before attempting induction |
| Fixed-width bitvector identity `forall  x y : BitVec w, ...` | Small-width instantiation (`w = 1, 2, 4, 8`) + `MSB` sign boundary | Instantiate `w := 4` with `decide +kernel` or run `bv_decide` in scratch probe |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| "Check if a new theorem statement is actually true before proving" | `lean_counterexample_search` | Run `lean_counterexample_search(filePath, theoremName, strategy: "dense")` in isolated scratch |
| "Detect hidden `Nat` subtraction truncation (`a - b = 0` when `a < b`)" | Boundary witness `(a := 0, b := 1)` + static `lean-analyzer` | Test `a < b` inputs; add explicit `(h : b <= a)` guard or lift statement to `Int` |
| "Test a non-decidable `Real` statement on concrete rationals" | Rational specialization (`` / scaled `Nat`) | Specialize `` parameters to `` values `0, 1, -1, 1/2` and evaluate via `norm_num` |
| "Distinguish a false theorem from a missing precondition" | Minimal counterexample shrinking | Shrink witness via `Shrinkable`, inspect violated edge case, and escalate precondition to `specifier` |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| `plausible` reports `Unable to synthesize SampleableExt` | Custom `structure` or abstract type lacks generator instance | Specialize type variable ` := Fin 3` or `Int` in a scratch `example`, or derive `SampleableExt` |
| `plausible` finds counterexample `a = 0, b = 1` on `a - b + b = a` | Unguarded `Nat.sub` truncates at zero (`FIDELITY-04`) | Escalate to `specifier` to add hypothesis `h : b <= a` or restate over `Int` |
| Prover spends >15 tactic steps stuck on an induction step | Induction hypothesis is strictly weaker than true invariant or theorem is false | Run `lean_counterexample_search` on the current subgoal state before continuing manual tactics |
| `Decidable` synthesis fails on existential `exists  y, P x y` | Unbounded existential quantifier is not computationally enumerable | Bound witness domain (`exists  y in Finset.range B, P x y`) for finite testing |
