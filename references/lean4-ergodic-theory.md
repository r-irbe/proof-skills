---
title: "Ergodic theory cheat-sheet (Lean 4 / Mathlib4)"
status: reference
source: extracted from `lean-math-stochastic §Part 5`
owners: lean-math-stochastic
date: 2026-05-27
---

# Ergodic theory cheat-sheet

Reference for Birkhoff's ergodic theorem, mixing rates, and the
"time-average = space-average" identity as it appears in Lean 4 /
Mathlib4.  Extracted from the slim of `lean-math-stochastic`.

## 1. Birkhoff's ergodic theorem

For an ergodic, measure-preserving transformation `T : Ω → Ω` and an
integrable observable `f : Ω → ℝ`:

```
(1 / n) · Σ_{k=0}^{n-1} f(T^k x)  →  ∫ f dμ   μ-a.e.
```

### 1.1 Project relevance

The long-run average of the quality / risk observable equals its
expected value under the stationary distribution.  This is what
justifies using stationary-distribution analysis to assess long-run
pipeline behaviour rather than simulating the iteration.

### 1.2 Mathlib API entry-points

```lean
import Mathlib.Dynamics.BirkhoffSum.Average
-- BirkhoffSum.birkhoffSum, BirkhoffAverage.birkhoffAverage
-- Ergodic.birkhoffAverage_ae_tendsto  (the headline a.s. convergence)

import Mathlib.Dynamics.Ergodic.Ergodic
-- Ergodic, PreErgodic, IsErgodic (predicate vs structure variants vary by pin)
```

Pin-drift warning: Mathlib has renamed the ergodic predicates more
than once.  Check `Mathlib/Dynamics/Ergodic/Ergodic.lean` at your
current pin before quoting a lemma name.

## 2. Mixing

For any measurable `A, B`:

```
μ(A ∩ T⁻ⁿ B)  →  μ(A) · μ(B)   as n → ∞
```

### 2.1 Mixing rate

For Markov chains, **mixing rate = spectral gap**.  The project
`StochasticCCV` modules cite this equality whenever they bound a
convergence-to-equilibrium rate from a spectral-gap hypothesis.

### 2.2 Practical Lean handle

In most project proofs, you do NOT prove mixing from scratch — you
bundle "this chain has a spectral gap" and consume the consequence
via the existing `okdStep_L1_contraction` and friends in
`references/lean4-contraction-catalog.md §4`.

## 3. Common pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| `IsFiniteMeasure` missing | `μ.average f` rejects the type | Add `[IsFiniteMeasure μ]`; auto-gives `[SigmaFinite μ]` |
| `Ergodic` vs `PreErgodic` confusion | "expected `PreErgodic`, got `Ergodic`" | Mathlib has split the two — pick by which hypotheses you actually have |
| Off-by-one in Birkhoff sum | `range n` vs `range (n+1)` | Use `BirkhoffSum.birkhoffSum`; do not hand-roll |
| Trying to prove mixing | proofs balloon | Cite the spectral-gap result instead |

## 4. See also

- `references/lean4-contraction-catalog.md` — the contraction / spectral-gap
  bridge that handles the "consequence" half of mixing-rate arguments.
- `references/lean4-time-series-patterns.md` — the discrete-iterate twin
  of this file (autocorrelation ↔ Birkhoff average).
- `Template_Measure.md` — broader measure-theory module starter
  including ergodic / Birkhoff scaffolding.
