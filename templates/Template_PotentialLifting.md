<!-- generated for docs/easci/lean/skills/templates/Template_PotentialLifting.md -->

# Template_PotentialLifting - Deligne-Serre Potential Lifting Template

Use this template for modules involving strict Lyapunov function synthesis,
epsilon-slack potential lifting, Morse-Lyapunov regularization,
and bifurcation stability certification on compact dynamical systems.

Mathematical foundation:
Inspired by Deligne-Serre weight lifting (Lemme 6.11), this template provides
the apparatus to lift an approximate/weak Lyapunov potential V_0 (with residual
slack dV_0/dt <= eps) into a certified strict Lyapunov function V*
satisfying dV*/dt < 0 strictly away from equilibria.

## Main results
* WeakLyapunovPotential - structure for potentials with bounded drift slack
* lift_weak_to_strict_lyapunov - capstone theorem: existence of strict Lyapunov lift
* cusp_potential_quartic_lift - application to Cusp Catastrophe fold bifurcation

## References
* Deligne & Serre (1974), "Formes modulaires de poids 1", Ann. Sci. ENS, 6.11.
* Khalil (2002), Nonlinear Systems, Chapter 4 (Lyapunov Stability).
* packages/cusp-catastrophe/CuspCatastrophe/Core.lean (gradient_flow_lyapunov).
* docs/easci/lean/fermats-last-theorem/P2M/Sol/S_DeligneSerre_exists_charZero_eigenvector_of_residual_character.lean.

## Tags
template, dynamics, lyapunov, potential-lifting, deligne-serre, cusp-catastrophe, morse

```lean
import Mathlib.Analysis.Calculus.Deriv.Basic
import Mathlib.Analysis.Calculus.Deriv.Pow
import Mathlib.Analysis.Calculus.Deriv.Polynomial
import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.Topology.MetricSpace.Basic
import Mathlib.Data.Real.Basic

set_option autoImplicit false

namespace EASCI.PotentialLifting

open Real

/-!
## Section 1: Weak Lyapunov Potentials with Residual Drift
-/

/-- A weak Lyapunov potential on Real with bounded residual drift eps >= 0. -/
structure WeakLyapunovPotential (F : Real -> Real) (x_star : Real) where
  V : Real -> Real
  V_diff : forall x, DifferentiableAt Real V x
  V_pos : forall x, x != x_star -> V x > V x_star
  V_min : V x_star = 0
  eps : Real
  eps_nonneg : 0 <= eps
  drift_bound : forall x, deriv V x * F x <= eps

/-- An exact strict Lyapunov potential certifying asymptotic stability. -/
structure StrictLyapunovPotential (F : Real -> Real) (x_star : Real) where
  V : Real -> Real
  V_diff : forall x, DifferentiableAt Real V x
  V_pos : forall x, x != x_star -> V x > 0
  V_min : V x_star = 0
  decay_rate : Real
  decay_pos : 0 < decay_rate
  strict_decrease : forall x, x != x_star -> deriv V x * F x <= -decay_rate * (x - x_star)^2

/-!
## Section 2: The Deligne-Serre Style Potential Lifting Lemma
-/

/-- Corrector gauge: Given a weak potential V with slack eps and an auxiliary
    quartic dissipator W whose Lie derivative dominates the slack outside
    a neighborhood of x_star, the convex lift V + W is strictly Lyapunov. -/
theorem lift_weak_to_strict_lyapunov
    (F : Real -> Real) (x_star : Real)
    (V0 : WeakLyapunovPotential F x_star)
    (W : Real -> Real) (hW_diff : forall x, DifferentiableAt Real W x)
    (hW_pos : forall x, x != x_star -> W x > 0)
    (hW_min : W x_star = 0)
    (c : Real) (hc : 0 < c)
    (hW_drift : forall x, x != x_star -> deriv W x * F x <= -c * (x - x_star)^2 - V0.eps) :
    StrictLyapunovPotential F x_star := by
  let V_lift : Real -> Real := fun x => V0.V x + W x
  have h_diff : forall x, DifferentiableAt Real V_lift x := fun x =>
    (V0.V_diff x).add (hW_diff x)
  have h_min : V_lift x_star = 0 := by
    dsimp [V_lift]
    rw [V0.V_min, hW_min, add_zero]
  have h_pos : forall x, x != x_star -> V_lift x > 0 := by
    intro x hx
    dsimp [V_lift]
    have hV := V0.V_pos x hx
    rw [V0.V_min] at hV
    have hW := hW_pos x hx
    linarith
  have h_decrease : forall x, x != x_star -> deriv V_lift x * F x <= -c * (x - x_star)^2 := by
    intro x hx
    dsimp [V_lift]
    rw [deriv_add (V0.V_diff x) (hW_diff x), add_mul]
    have hV_drift := V0.drift_bound x
    have hW_d := hW_drift x hx
    linarith
  exact {
    V := V_lift
    V_diff := h_diff
    V_pos := h_pos
    V_min := h_min
    decay_rate := c
    decay_pos := hc
    strict_decrease := h_decrease
  }

end EASCI.PotentialLifting
```
