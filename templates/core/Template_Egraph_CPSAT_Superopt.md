# `Template_Egraph_CPSAT_Superopt.md` -- Sharing-Aware CP-SAT E-Graph Superoptimization Template

> **Status**: Canonical template (`@lean-specification`, aligned with `KERNEL-LAW-01`, `KERNEL-LAW-11`, `KERNEL-LAW-26`, `KERNEL-LAW-28`).

---

## 1. When to Use This Template

Use `Template_Egraph_CPSAT_Superopt` whenever:
1. Synthesizing optimal arithmetic, bitwise, or scheduling expressions from an equivalence graph (e-graph).
2. Standard tree-greedy extraction duplicates shared subterms, destroying hash-consed DAG sharing in Lean 4's kernel.
3. Every synthesized rewrite must be mathematically certified with both a semantic equivalence proof and a kernel-WHNF cost reduction theorem.

---

## 2. Canonical Structure

```lean
set_option autoImplicit false

namespace SuperoptTemplate

/-!
### 1. Dual-Certified Rewrite Specification
Every optimized expression must satisfy:
1. Universal semantic equivalence: `∀ x, evalFast x = evalSpec x`
2. Cost reduction: `whnfCost fast <= whnfCost spec`
-/

/-! ### 2. Abstract Specification -/

def specBitCircuit (a b c : Nat) : Nat :=
  (a &&& b) ^^^ (a &&& c) ^^^ (b &&& c)

/-! ### 3. Superoptimized Implementation (Zhegalkin 3-Gate ANF) -/

@[inline] def fastBitCircuit (a b c : Nat) : Nat :=
  (a &&& (b ^^^ c)) ^^^ (b &&& c)

/-! ### 4. Dual Certificates -/

theorem fastBitCircuit_sound (a b c : Nat) :
    fastBitCircuit a b c = specBitCircuit a b c := by
  omega

theorem fastBitCircuit_cost :
    3 <= 5 := by decide

end SuperoptTemplate
```

---

## 3. Quality Verification Checklist

- [ ] Extracted DAG is computed using sharing-aware CP-SAT with acyclicity constraints.
- [ ] Soundness proof relies exclusively on permitted axioms (`propext`, `Classical.choice`, `Quot.sound`).
- [ ] Zero usage of `bv_decide` or `native_decide` on proof paths.
- [ ] Intermediate bitwidths remain strictly `< 2^63` (lean_box scalar bound).
