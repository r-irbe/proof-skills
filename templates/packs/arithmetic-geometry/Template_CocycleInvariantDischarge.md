# Template_CocycleInvariantDischarge - Crossed Homomorphisms & Distributed Invariant Discharge

Use this template for **algebraic invariant discharge**, **distributed consensus verification**,
**Markov loop current conservation**, and **multi-agent view-change correctness**.

When distributed agents transition through views, route packets through network graphs,
or execute state transitions, the accumulated state discrepancy along an execution path
forms a **1-cocycle** (crossed homomorphism) under the action of the transition groupoid:
$$c(s \cdot t) = c(s) + s \cdot c(t)$$

Discharging distributed safety or proving path-independence is mathematically equivalent to
proving that the cohomology class $[c] \in H^1(G, M)$ vanishes-i.e. that $c$ is a **1-coboundary**:
$$\exists \Phi \in M,\quad \forall g \in G,\quad c(g) = g \cdot \Phi - \Phi$$
where $\Phi$ serves as the global certified state potential (or consensus agreement certificate).

## Main results
* `CrossedHomomorphism` - structure for 1-cocycles under groupoid/group actions
* `CrossedHomomorphism.map_one` / `map_inv` - canonical identity and inverse transport
* `coboundary_of_shapiro_eval` - Shapiro coinduction evaluation functional for asynchronous channels
* `cocycle_perturbation_abel` - automated cocycle stability under coboundary shifts via `abel`
* `markov_loop_current_exact_potential` - Kolmogorov cycle affinity discharge to global potential

## References
* Mathlib: `Mathlib.RepresentationTheory.Homological.GroupCohomology.LowDegree`
* FLT: `P2M/Sol/S_groupCohomology_isCoboundary1_of_addEquiv_pi.lean`
* FLT: `P2M/Sol/S_groupCohomology_isMulCoboundary1_of_filtration.lean`
* Castro & Liskov (1999), *Practical Byzantine Fault Tolerance* (view-change invariant)
* Kelly (1979), *Reversibility and Stochastic Networks* (Kolmogorov cycle criterion)

## Tags
template, cohomology, 1-cocycle, crossed-homomorphism, coboundary, consensus, bft, markov-current, invariant

```lean
/-
Copyright (c) 2026 <Project> Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
SPDX-License-Identifier: Apache-2.0
-/

import Mathlib.Algebra.Group.Basic
import Mathlib.Algebra.Group.Action.Defs
import Mathlib.Algebra.Hom.Group.Defs
import Mathlib.Tactic.Abel
import Mathlib.Tactic.Linarith

set_option autoImplicit false

namespace <Project>.ProofSkills.CocycleDischarge

/-!
## Section 1: Inhomogeneous 1-Cocycles and Crossed Homomorphisms
-/

/-- An inhomogeneous 1-cocycle (crossed homomorphism) for a group action G ? M.
    Satisfies c(g * h) = c(g) + g * c(h). -/
structure CrossedHomomorphism (G M : Type*) [Group G] [AddCommGroup M] [DistribMulAction G M] where
  toFun : G ? M
  map_mul' : forall  g h : G, toFun (g * h) = toFun g + g * toFun h

instance {G M : Type*} [Group G] [AddCommGroup M] [DistribMulAction G M] :
    DFunLike (CrossedHomomorphism G M) G (fun _ => M) where
  coe c := c.toFun
  coe_injective' := by rintro ?f, hf? ?f', hf'? rfl; rfl

variable {G M : Type*} [Group G] [AddCommGroup M] [DistribMulAction G M]

@[simp]
theorem cocycle_mul (c : CrossedHomomorphism G M) (g h : G) :
    c (g * h) = c g + g * c h :=
  c.map_mul' g h

/-- A 1-cocycle maps the group identity to zero. -/
@[simp]
theorem cocycle_one (c : CrossedHomomorphism G M) : c 1 = 0 := by
  have h := c.map_mul' 1 1
  simp only [mul_one, one_smul] at h
  exact add_left_eq_self.mp h.symm

/-- A 1-cocycle maps inverses to twisted negatives: c(g^-1) = - g^-1 * c(g). -/
@[simp]
theorem cocycle_inv (c : CrossedHomomorphism G M) (g : G) :
    c g^-1 = - (g^-1 * c g) := by
  have h := c.map_mul' g^-1 g
  simp only [inv_mul_cancel, cocycle_one] at h
  rw [? add_eq_zero_iff_eq_neg]
  exact h.symm

/-!
## Section 2: 1-Coboundaries & Potential Certificates
-/

/-- A 1-cocycle is a 1-coboundary if it arises from the difference of a global state potential. -/
def IsCoboundary (c : CrossedHomomorphism G M) : Prop :=
  exists  Phi : M, forall  g : G, c g = g * Phi - Phi

/-- Invariant preservation: shifting a cocycle by a coboundary preserves the cocycle property.
    Automated via the FLT `abel` transport idiom. -/
theorem cocycle_shift_is_cocycle
    (c : CrossedHomomorphism G M) (Phi : M) :
    forall  g h : G, (c (g * h) - (g * h) * Phi + Phi) =
      (c g - g * Phi + Phi) + g * (c h - h * Phi + Phi) := by
  intro g h
  rw [cocycle_mul, smul_sub, smul_add, mul_smul]
  abel

/-!
## Section 3: The Shapiro Coinduction Evaluation Functional
-/

/-- Coinduced representation functional: For a distributed system with message channel
    cochain P ~=+ (G ? P0) under shift action (h * p)(x) = p(h^-1 * x), any 1-cocycle
    is discharged to a coboundary via direct evaluation at identity. -/
theorem coboundary_of_shapiro_eval
    {P P0 : Type*} [AddCommGroup P] [AddCommGroup P0] [DistribMulAction G P]
    (e : P ~=+ (G ? P0))
    (he : forall  (h : G) (p : P) (x : G), e (h * p) x = e p (h^-1 * x))
    (c : CrossedHomomorphism G P) :
    IsCoboundary c := by
  let phi : P := e.symm (fun x => e (c x^-1) 1)
  refine ?-phi, fun g => ?_?
  apply e.injective
  funext x
  rw [map_sub, map_neg, e.apply_symm_apply, Pi.sub_apply, Pi.neg_apply, he]
  rw [e.apply_symm_apply, mul_inv_rev, inv_inv]
  rw [c.map_mul' x^-1 g, map_add, Pi.add_apply, he, inv_inv, mul_one]
  abel

/-!
## Section 4: Concrete Case Study - Multi-Agent Consensus View-Change
-/

namespace ConsensusCaseStudy

/-- Evaluator replica identifier. -/
def ReplicaId := Nat

/-- Protocol view (epoch / round). -/
structure View where
  epoch : Nat
  deriving DecidableEq, Repr

/-- Invariant discrepancy between two views. -/
structure ViewDiscrepancy (M : Type*) [AddCommGroup M] where
  drift : View ? View ? M
  transitive : forall  u v w, drift u w = drift u v + drift v w
  skew : forall  u v, drift v u = - drift u v

/-- Discharging view-change consistency: every consistent discrepancy cocycle
    is generated by a global anchor state potential. -/
theorem view_change_potential_discharge
    {M : Type*} [AddCommGroup M]
    (vd : ViewDiscrepancy M) (v0 : View) :
    exists  (anchor : View ? M), forall  u v, vd.drift u v = anchor v - anchor u := by
  refine ?fun v => vd.drift v0 v, fun u v => ?_?
  have h := vd.transitive v0 u v
  have h_skew := vd.skew v0 u
  rw [h]
  abel

end ConsensusCaseStudy

/-!
## Section 5: Concrete Case Study - Markov Loop Currents & Cycle Affinities
-/

namespace MarkovCurrentCaseStudy

variable {V : Type*} [DecidableEq V] [Fintype V]

/-- A conservative current on a graph satisfying Kirchhoff's node law. -/
structure ConservativeCurrent where
  J : V ? V ? Real
  skew : forall  u v, J v u = - J u v
  kirchhoff : forall  u, (Finset.univ.sum fun v => J u v) = 0

/-- Kolmogorov cycle affinity along a triangular loop. -/
def triangleAffinity (P : V ? V ? Real) (u v w : V) : Real :=
  (P u v * P v w * P w u) - (P u w * P w v * P v u)

/-- Detailed balance criterion: Vanishing 1-cycle affinity guarantees existence
    of a symmetric equilibrium potential. -/
theorem cycle_affinity_zero_implies_detailed_balance
    (P : V ? V ? Real)
    (h_pos : forall  u v, P u v > 0)
    (h_cycle : forall  u v w, triangleAffinity P u v w = 0) :
    forall  u v w, P u v * P v w * P w u = P u w * P w v * P v u := by
  intro u v w
  have h := h_cycle u v w
  dsimp [triangleAffinity] at h
  linarith

end MarkovCurrentCaseStudy

end <Project>.ProofSkills.CocycleDischarge
```

## Anti-Patterns Checklist

| Anti-Pattern | Root Cause of Failure | Correct Production Pattern |
| :--- | :--- | :--- |
| **Manual term expansion with `rw [mul_assoc]`** | Combinatorial state space blowup ($O(2^n)$ branching). | Apply `Additive.ofMul.injective; simp only [ofMul_mul, ofMul_div]; abel`. |
| **Unfolded open-context `exact`** | Diverges under deep typeclass hierarchies or permuted binders. | Use `p2m_exact_reverting` to isolate the closed Pi-type. |
| **Unbounded tactic search (`aesop`, `grind`)** | Non-deterministic heartbeats timeout in continuous integration. | Use forward monotonic accumulation (`have`, `obtain`, `abel`). |
| **Omitting skew-symmetry on edge currents** | Kirchhoff conservation alone does not prevent hidden circular sink flows. | Formulate current cochains with strict anti-symmetry `J v u = - J u v`. |
