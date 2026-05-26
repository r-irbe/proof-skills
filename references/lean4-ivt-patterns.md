---
title: "IVT (Intermediate Value Theorem) patterns in Lean 4 / Mathlib"
status: reference
source: extracted from `lean-math-analysis §8.2`, `lean-math-dynamical §Part 8`, `lean-math-stochastic §8.4`
owners: lean-math-convergence, lean-math-stochastic
date: 2026-05-27
---

# IVT patterns in Lean 4 / Mathlib

A canonical reference for the **intermediate-value theorem** as it lives
in Mathlib, the bracketing pattern used to prove root existence, and
typical project applications (sign-change in catastrophe-theory cubics,
equilibrium existence for Markov chains).  Every consumer skill that
needs an IVT bracket should link here rather than restate the lemma.

## 1. The canonical Mathlib incantation

```lean
-- Import: Mathlib.Topology.Order.IntermediateValue
-- Key theorem: IsPreconnected.intermediate_value₂

-- For continuous f : ℝ → ℝ with f a ≤ 0 ≤ f b (with hab : a ≤ b):
isPreconnected_Icc.intermediate_value₂
  (left_mem_Icc.mpr hab) (right_mem_Icc.mpr hab)
  hf.continuousOn continuous_const.continuousOn
  (le_of_lt ha) (le_of_lt hb)
-- → ∃ c ∈ Set.Icc a b, f c = 0
```

## 2. Alternative API entry-points

```lean
-- intermediate_value_uIcc : Set.uIcc (unordered interval) variant
-- intermediate_value_Icc  : gives Set.Icc (f a) (f b) ⊆ f '' Set.Icc a b
--                          (use this when you want a value, not just existence)
```

`intermediate_value_Icc` is the right choice when the surrounding proof
already has a specific target value `y ∈ Set.Icc (f a) (f b)`.
`IsPreconnected.intermediate_value₂` is the right choice when you only
need *some* zero of `f - g`.

## 3. Project application — `asymmetric_three_roots_ivt`

Sign analysis for the cusp polynomial `x³ - 3x + 1 = 0`, on the
intervals `[a, b]` with `a = -3`, `b = 1`:

```lean
-- f(-2) = -8 + 6 + 1 = -1 < 0
-- f(-1) = -1 + 3 + 1 =  3 > 0  → root in (-2, -1)
-- f( 0) =           1 > 0
-- f( 1) = 1 - 3 + 1 = -1 < 0   → root in (0, 1)
-- f( 2) = 8 - 6 + 1 =  3 > 0   → root in (1, 2)
```

The three brackets each feed one `IsPreconnected.intermediate_value₂`
invocation; the `three_distinct_roots` statement then unions the
witnesses with `Distinct.of_lt`.

## 4. Polynomial continuity (the usual prerequisite)

```lean
-- Polynomial functions are continuous; `fun_prop` closes the goal.
example (a b : ℝ) : Continuous (fun x : ℝ => x^3 + a*x + b) := by fun_prop

-- Manually: continuous_pow + Continuous.mul + Continuous.add
```

## 5. Common pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Forgetting `hab : a ≤ b` | "could not unify Icc" | Add the explicit `le` hypothesis |
| Pre-rotated sign hypotheses | "expected `≤ 0`, got `0 ≤`" | Use `neg_le_neg_iff` to flip |
| `f` not continuous on the closed interval | `intermediate_value` fails | Discharge with `Continuous.continuousOn hf` |
| Searching for `IVT` by name | symbol not found | Mathlib uses `intermediate_value_*` and `IsPreconnected.intermediate_value_*` |

## 6. Where the canonical block was duplicated before this extraction

| Location | Lines (pre-extraction) |
|---|---|
| `skills/lean-math-analysis §8.2` | ~12 |
| `skills/lean-math-dynamical §Part 8` | ~20 |
| `skills/lean-math-stochastic §8.4` | ~10 |

All three now `See also`-link this file.
