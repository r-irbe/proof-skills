# Template_Lyapunov -- Discrete Lyapunov Energy Contraction and GPU Iteration Bounds

Use this template for **convergence and termination proofs**: proving that an iterative algorithm,
GPU kernel loop, power iteration solver (e.g. HippoRAG / Personalized PageRank), or discrete dynamical
system strictly terminates within an explicit, finite iteration bound.

Common patterns: non-negative integer Lyapunov energy function, per-iteration decay lower bound
$\delta > 0$, induction over step indices, and ceiling division floor bounds solved via `Nat.div_add_mod`.

## Main results
* `lyapunov_finite_convergence` -- Energy strictly decreasing by $\delta > 0$ hits 0 within $n$ steps when $n \cdot \delta \ge v_0$
* `ceil_div_mul_ge` -- Euclidean ceiling division arithmetic lemma: $((v_0 + \delta - 1) / \delta) \cdot \delta \ge v_0$
* `gpu_iteration_bound_sound` -- Soundness of loop upper bound $n = (v_0 + \delta - 1) / \delta$ guaranteeing complete convergence

## Implementation notes
- Discrete energy must be represented as a non-negative integer (`Nat`), avoiding floating-point rounding ambiguities.
- In Lean 4 standard library, non-linear division is an uninterpreted function in `omega`.
- To prove ceiling division bounds in Presburger arithmetic, instantiate `Nat.div_add_mod` ($m = n \cdot (m / n) + m \% n$) and `Nat.mod_lt` ($m \% n < n$).
- Inductive hypothesis steps must rewrite $(t + 1) \cdot \delta$ to $t \cdot \delta + \delta$ via `Nat.succ_mul` before invoking `omega`.

## References
* Hendrik W. Lenstra Jr., *Integer Programming with a Fixed Number of Variables*, Math. Operations Res., 1983
* William Pugh, *The Omega test: a fast and practical integer programming algorithm for dependence analysis*, Supercomputing 1991
* Hassan K. Khalil, *Nonlinear Systems*, Prentice Hall, 2002

## Tags
template, lyapunov, convergence, termination, gpu-bound, power-iteration, omega, div-mod

```lean
import Init

set_option autoImplicit false

namespace Foundations.Lyapunov

structure State where
  residue : Nat
  deriving DecidableEq, Repr

def lyapunov (s : State) : Nat := s.residue

theorem lyapunov_finite_convergence
    (trajectory : Nat -> State) (n : Nat) (delta : Nat) (_h_delta : delta > 0)
    (h_decay : forall t, t < n -> lyapunov (trajectory (t + 1)) + delta <= lyapunov (trajectory t))
    (h_bound : n * delta >= lyapunov (trajectory 0)) :
    lyapunov (trajectory n) = 0 := by
  have h_le : forall t, t <= n -> lyapunov (trajectory t) + t * delta <= lyapunov (trajectory 0) := by
    intro t
    induction t with
    | zero =>
      intro _
      omega
    | succ t ih =>
      intro ht
      have ht_lt : t < n := by omega
      have hstep := h_decay t ht_lt
      have hprev := ih (by omega)
      have h_mul : (t + 1) * delta = t * delta + delta := Nat.succ_mul t delta
      rw [h_mul]
      omega
  have h_final := h_le n (Nat.le_refl n)
  omega

theorem ceil_div_mul_ge (v0 delta : Nat) (h_delta : delta > 0) :
    ((v0 + delta - 1) / delta) * delta >= v0 := by
  have h_div := Nat.div_add_mod (v0 + delta - 1) delta
  have h_mod := Nat.mod_lt (v0 + delta - 1) h_delta
  have h_comm : ((v0 + delta - 1) / delta) * delta = delta * ((v0 + delta - 1) / delta) := Nat.mul_comm _ _
  rw [h_comm]
  omega

theorem gpu_iteration_bound_sound
    (trajectory : Nat -> State) (v0 delta : Nat) (h_delta : delta > 0)
    (h_init : lyapunov (trajectory 0) = v0)
    (h_decay : forall t, t < (v0 + delta - 1) / delta ->
      lyapunov (trajectory (t + 1)) + delta <= lyapunov (trajectory t)) :
    lyapunov (trajectory ((v0 + delta - 1) / delta)) = 0 := by
  have h_bound : ((v0 + delta - 1) / delta) * delta >= lyapunov (trajectory 0) := by
    rw [h_init]
    exact ceil_div_mul_ge v0 delta h_delta
  exact lyapunov_finite_convergence trajectory ((v0 + delta - 1) / delta) delta h_delta h_decay h_bound

end Foundations.Lyapunov
```
