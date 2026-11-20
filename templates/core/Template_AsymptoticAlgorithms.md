# `Template_AsymptoticAlgorithms.md` -- Classical Algorithmic Breakthroughs Template

> **Status**: Canonical template (`@lean-math-discrete`, aligned with `KERNEL-LAW-01`, `KERNEL-LAW-11`, `KERNEL-LAW-17`, `KERNEL-LAW-29`).

---

## 1. When to Use This Template

Use `Template_AsymptoticAlgorithms` whenever:
1. Polynomial operations (GCD, resultants, discriminants) encounter explosive integer coefficient growth.
2. Sparse matrix permanent or bipartite matching can be factored into irreducible components.
3. Prime counting or arithmetic functions must eliminate static precomputed lookup tables in favor of dynamic mathematical sieves.

---

## 2. Canonical Structure

```lean
set_option autoImplicit false

namespace AsymptoticTemplate

/-! ### 1. Subresultant Exact Division -/

def subresultantDiv (prem : Nat) (g h delta : Nat) : Nat :=
  let div := g * (h ^ delta)
  if div == 0 then 0 else prem / div

/-! ### 2. Block Factorization -/

def blockProduct (subresults : List Nat) : Nat :=
  subresults.foldl (· * ·) 1

/-! ### 3. Dynamic Legendre Step -/

def phiStep (x pa phiA phiQuot : Nat) : Nat :=
  if x < pa * pa then
    x -- pruned base case
  else
    phiA - phiQuot

end AsymptoticTemplate
```

---

## 3. Quality Verification Checklist

- [ ] Zero static precomputed seed tables or hardcoded lookup lists.
- [ ] Subresultant pseudo-remainders are divided by exact scaling factors over integers.
- [ ] Reducible matrices are decomposed into diagonal blocks prior to evaluation.
- [ ] Adheres strictly to Anti-Gating (`KERNEL-LAW-29`): scales smoothly across all input regimes.
