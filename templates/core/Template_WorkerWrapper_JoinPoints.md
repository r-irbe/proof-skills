# `Template_WorkerWrapper_JoinPoints.md` -- Worker/Wrapper, Join Points & Defunctionalized CPS Template

> **Status**: Canonical template (`@lean-proof-refactor`, aligned with `KERNEL-LAW-01`, `KERNEL-LAW-04`, `KERNEL-LAW-06`, `KERNEL-LAW-20`, `KERNEL-LAW-25`).

---

## 1. When to Use This Template

Use `Template_WorkerWrapper_JoinPoints` whenever:
1. A recursive algorithm or state machine receives structured records or typeclasses that cause repeated projection overhead in loops.
2. Branches in a step function duplicate large subterms, causing AST explosion and losing DAG sharing in the Lean 4 kernel.
3. Higher-order continuations or lambdas create allocation and substitution overhead during kernel WHNF evaluation.

---

## 2. Canonical Structure

```lean
set_option autoImplicit false

namespace WorkerWrapperTemplate

/-! ### 1. Defunctionalized Continuations -/

inductive Cont where
  | done : Cont
  | next : Nat -> Cont -> Cont
  deriving Repr, DecidableEq

def applyCont : Cont -> Nat -> Nat
  | .done, acc => acc
  | .next step k, acc => applyCont k (acc + step)

/-! ### 2. Unboxed Worker with Join Point -/

/--
Inner worker:
* Pure unboxed scalar arguments (< 2^63).
* Join point factoring common continuation logic.
-/
def loopWorker (fuel : Nat) (stepVal : Nat) (acc : Nat) : Nat :=
  @Nat.rec (fun _ => Nat -> Nat)
    (fun a => a)
    (fun _ loop a =>
      -- Factored Join Point
      let joinPoint := fun nextA => loop (nextA + 1)
      if a % 2 == 0 then
        joinPoint (a + stepVal)
      else
        joinPoint a)
    fuel
    acc

/-! ### 3. Outer Wrapper -/

structure ProblemConfig where
  fuel : Nat
  step : Nat
  seed : Nat

/-- Outer wrapper unpacking config. -/
@[inline] def solveProblem (cfg : ProblemConfig) : Nat :=
  loopWorker cfg.fuel cfg.step cfg.seed

end WorkerWrapperTemplate
```

---

## 3. Quality Verification Checklist

- [ ] Inner worker takes only primitive unboxed scalars (`Nat < 2^63`).
- [ ] No structure allocations, pairs, or tuples occur inside the recursive recursor step.
- [ ] Join points are applied in tail position across all branch arms.
- [ ] Continuations are first-order inductive datatypes.
