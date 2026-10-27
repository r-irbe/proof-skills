# Template_ModularJacobianTamagawa - Modular Jacobian Tamagawa Numbers & Neron Component Groups

Use this template for **modular Jacobian Tamagawa numbers**, **Neron component groups**,
**monodromy pairing bounds**, and **stochastic Markov flow current capacity envelopes**.

In arithmetic geometry and Fermat's Last Theorem / modular forms:
Let X_0(N) be a modular curve over a local field K with residue field k, and let J_0(N) be its modular Jacobian.
The Neron model represents the smooth group scheme over the ring of integers.
The special fiber decomposes into an identity component and a finite component group Phi = J_k / J_k^0.
By Grothendieck, Raynaud, and Mazur, the order c_p = #Phi(k) is the Tamagawa number of J_0(N) at p.
The Tamagawa number measures combinatorial and topological obstructions to smooth reduction, bounded
by the dual intersection graph of the special fiber of the modular curve.

In stochastic consensus and Markov flow networks:
* The Neron model separates continuous potential flow dynamics (within identity component basins)
  from discrete topological circulation cycles across network clusters (component group Phi).
* Tamagawa numbers represent discrete topological capacity invariants across network partitions.
* The component group ceiling bounds inter-cluster circulation drift, guaranteeing stable potential flow.

## Main results
* `<ModularJacobianNeronDatum>` - datum (neronComponentOrder, componentGroupCeiling, flowPotentialCapacity, neronTolerance, monodromyWeight)
* `<NeronDefect>` - defect between component group ceiling and observed Neron component order
* `<NormalizedNeronRatio>` - normalized ratio of component order to component group ceiling
* `<NeronCapacityBound>` - total capacity bound scaled by ceiling and flow potential capacity
* `<NeronSlack>` - slack between tolerance-scaled ceiling and observed component order
* `<WeightedNeronBound>` - monodromy-weighted Neron bound accounting for cluster graph topology
* `<IsNeronBounded>` - predicate: component order is bounded by component group ceiling
* `<IsConnectedNeron>` - predicate: Neron model has connected special fiber (order 1)
* `<IsNeronFlowSafe>` - predicate: observed component order is within certified tolerance envelope
* `<NeronDefectNonnegOfBounded>` - Neron defect is non-negative for bounded component groups
* `<NeronBoundedIffDefectNonneg>` - boundedness is equivalent to non-negative defect
* `<NormalizedNeronRatioNonneg>` - normalized Neron ratio is non-negative
* `<NormalizedNeronRatioLeOneOfBounded>` - normalized ratio is bounded by 1 for bounded systems
* `<NeronCapacityBoundPos>` - capacity bound is strictly positive
* `<NeronCapacityBoundNonneg>` - capacity bound is non-negative
* `<ConnectedNeronImpliesBounded>` - connected special fiber implies bounded system
* `<ConnectedNeronDefect>` - connected Neron defect equals ceiling minus 1
* `<ConnectedNeronRatio>` - connected Neron ratio equals 1 / ceiling
* `<NeronFlowSafeIffSlackNonneg>` - flow safety is equivalent to non-negative slack
* `<NeronSlackNonnegOfSafe>` - slack is non-negative for flow-safe systems
* `<NeronOrderReconstruction>` - component order reconstructed from ratio and ceiling
* `<WeightedNeronBoundPos>` - monodromy-weighted bound is strictly positive
* `<NeronCapacityScale>` - capacity bound scales non-negatively with positive scaling
* `<NeronCapacityMonotone>` - capacity bound is monotone in ceiling
* `<NeronDefectMonotone>` - defect is monotone in component order
* `<NeronSlackMonotoneTolerance>` - slack is monotone in tolerance parameter

## References
* FLT: `StochasticCCV/Core/ModularJacobianNeron.lean`
* Grothendieck, A. (1972), *SGA 7 I: Groupes de Monodromie en Geometrie Algebrique*, LNM 288, Springer.
* Raynaud, M. (1970), *Specialisation du foncteur de Picard*, Publ. Math. IHES 38, 27-76.
* Mazur, B. (1977), *Modular curves and the Eisenstein ideal*, Publ. Math. IHES 47, 33-186.

## Tags
template, modular-jacobian, neron-model, component-group, tamagawa-number, markov-flow, capacity-envelope

```lean
/-
Copyright (c) 2026 <Project> Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
SPDX-License-Identifier: Apache-2.0
-/

import Mathlib.Data.Real.Basic
import Mathlib.Tactic

set_option autoImplicit false
set_option linter.unusedVariables false
set_option linter.unusedSectionVars false
set_option linter.unusedSimpArgs false

noncomputable section

namespace <Namespace>

/-- Datum specifying modular Jacobian Neron component order, component group ceiling,
    flow potential capacity, tolerance, and monodromy weight. -/
structure <ModularJacobianNeronDatum> where
  neronComponentOrder : Real
  componentGroupCeiling : Real
  flowPotentialCapacity : Real
  neronTolerance : Real
  monodromyWeight : Real
  order_pos : 0 < neronComponentOrder
  ceiling_pos : 0 < componentGroupCeiling
  capacity_pos : 0 < flowPotentialCapacity
  tolerance_pos : 0 < neronTolerance
  weight_pos : 0 < monodromyWeight

/-- Defect between component group ceiling and observed Neron component order. -/
def <NeronDefect> (d : <ModularJacobianNeronDatum>) : Real :=
  d.componentGroupCeiling - d.neronComponentOrder

/-- Normalized ratio of Neron component order to component group ceiling. -/
def <NormalizedNeronRatio> (d : <ModularJacobianNeronDatum>) : Real :=
  d.neronComponentOrder / d.componentGroupCeiling

/-- Total Neron capacity bound scaled by component group ceiling and flow capacity. -/
def <NeronCapacityBound> (d : <ModularJacobianNeronDatum>) : Real :=
  d.componentGroupCeiling * d.flowPotentialCapacity

/-- Neron slack between tolerance-scaled ceiling and component order. -/
def <NeronSlack> (d : <ModularJacobianNeronDatum>) : Real :=
  d.componentGroupCeiling * d.neronTolerance - d.neronComponentOrder

/-- Monodromy-weighted Neron bound accounting for cluster graph topology. -/
def <WeightedNeronBound> (d : <ModularJacobianNeronDatum>) : Real :=
  d.componentGroupCeiling * (1 + d.monodromyWeight * d.neronTolerance)

/-- Predicate: Neron component order is bounded by component group ceiling. -/
def <IsNeronBounded> (d : <ModularJacobianNeronDatum>) : Prop :=
  d.neronComponentOrder <= d.componentGroupCeiling

/-- Predicate: Neron model has connected special fiber (order 1). -/
def <IsConnectedNeron> (d : <ModularJacobianNeronDatum>) : Prop :=
  d.neronComponentOrder = 1

/-- Predicate: observed component order is within certified tolerance envelope. -/
def <IsNeronFlowSafe> (d : <ModularJacobianNeronDatum>) : Prop :=
  d.neronComponentOrder <= d.componentGroupCeiling * d.neronTolerance

/-- Neron defect is non-negative for bounded component groups. -/
theorem <NeronDefectNonnegOfBounded> (d : <ModularJacobianNeronDatum>)
    (h : <IsNeronBounded> d) : 0 <= <NeronDefect> d := by
  dsimp [<NeronDefect>, <IsNeronBounded>] at *
  linarith

/-- Boundedness is equivalent to non-negative Neron defect. -/
theorem <NeronBoundedIffDefectNonneg> (d : <ModularJacobianNeronDatum>) :
    <IsNeronBounded> d <-> 0 <= <NeronDefect> d := by
  dsimp [<IsNeronBounded>, <NeronDefect>]
  constructor <;> intro h <;> linarith

/-- Normalized Neron ratio is non-negative. -/
theorem <NormalizedNeronRatioNonneg> (d : <ModularJacobianNeronDatum>) :
    0 <= <NormalizedNeronRatio> d := by
  dsimp [<NormalizedNeronRatio>]
  exact div_nonneg (le_of_lt d.order_pos) (le_of_lt d.ceiling_pos)

/-- Normalized Neron ratio is bounded by 1 for bounded systems. -/
theorem <NormalizedNeronRatioLeOneOfBounded> (d : <ModularJacobianNeronDatum>)
    (h : <IsNeronBounded> d) : <NormalizedNeronRatio> d <= 1 := by
  dsimp [<NormalizedNeronRatio>, <IsNeronBounded>] at *
  exact (div_le_one d.ceiling_pos).mpr h

/-- Neron capacity bound is strictly positive. -/
theorem <NeronCapacityBoundPos> (d : <ModularJacobianNeronDatum>) :
    0 < <NeronCapacityBound> d := by
  dsimp [<NeronCapacityBound>]
  exact mul_pos d.ceiling_pos d.capacity_pos

/-- Neron capacity bound is non-negative. -/
theorem <NeronCapacityBoundNonneg> (d : <ModularJacobianNeronDatum>) :
    0 <= <NeronCapacityBound> d :=
  le_of_lt (<NeronCapacityBoundPos> d)

/-- Connected Neron model implies bounded system when ceiling is at least 1. -/
theorem <ConnectedNeronImpliesBounded> (d : <ModularJacobianNeronDatum>)
    (h_conn : <IsConnectedNeron> d) (h_ge : 1 <= d.componentGroupCeiling) :
    <IsNeronBounded> d := by
  dsimp [<IsNeronBounded>, <IsConnectedNeron>] at *
  rw [h_conn]
  exact h_ge

/-- Connected Neron model defect equals ceiling minus 1. -/
theorem <ConnectedNeronDefect> (d : <ModularJacobianNeronDatum>)
    (h : <IsConnectedNeron> d) :
    <NeronDefect> d = d.componentGroupCeiling - 1 := by
  dsimp [<NeronDefect>, <IsConnectedNeron>] at *
  rw [h]

/-- Connected Neron model has normalized ratio 1 / ceiling. -/
theorem <ConnectedNeronRatio> (d : <ModularJacobianNeronDatum>)
    (h : <IsConnectedNeron> d) :
    <NormalizedNeronRatio> d = 1 / d.componentGroupCeiling := by
  dsimp [<NormalizedNeronRatio>, <IsConnectedNeron>] at *
  rw [h]

/-- Flow safety is equivalent to non-negative Neron slack. -/
theorem <NeronFlowSafeIffSlackNonneg> (d : <ModularJacobianNeronDatum>) :
    <IsNeronFlowSafe> d <-> 0 <= <NeronSlack> d := by
  dsimp [<IsNeronFlowSafe>, <NeronSlack>]
  constructor <;> intro h <;> linarith

/-- Slack is non-negative for flow-safe systems. -/
theorem <NeronSlackNonnegOfSafe> (d : <ModularJacobianNeronDatum>)
    (h : <IsNeronFlowSafe> d) : 0 <= <NeronSlack> d :=
  (<NeronFlowSafeIffSlackNonneg> d).mp h

/-- Component order reconstructed from normalized ratio and ceiling. -/
theorem <NeronOrderReconstruction> (d : <ModularJacobianNeronDatum>) :
    d.neronComponentOrder = <NormalizedNeronRatio> d * d.componentGroupCeiling := by
  dsimp [<NormalizedNeronRatio>]
  have hu : IsUnit d.componentGroupCeiling := (ne_of_gt d.ceiling_pos).isUnit
  exact (hu.div_mul_cancel d.neronComponentOrder).symm

/-- Monodromy-weighted Neron bound is strictly positive. -/
theorem <WeightedNeronBoundPos> (d : <ModularJacobianNeronDatum>) :
    0 < <WeightedNeronBound> d := by
  dsimp [<WeightedNeronBound>]
  have h_prod : 0 < d.monodromyWeight * d.neronTolerance :=
    mul_pos d.weight_pos d.tolerance_pos
  have h_sum : 0 < 1 + d.monodromyWeight * d.neronTolerance := by linarith
  exact mul_pos d.ceiling_pos h_sum

/-- Linear scaling of Neron capacity bound. -/
theorem <NeronCapacityScale> (d : <ModularJacobianNeronDatum>) (c : Real) (hc : 0 <= c) :
    0 <= c * <NeronCapacityBound> d :=
  mul_nonneg hc (<NeronCapacityBoundNonneg> d)

/-- Capacity bound is monotone in component group ceiling. -/
theorem <NeronCapacityMonotone> (d : <ModularJacobianNeronDatum>) (b : Real)
    (hb : d.componentGroupCeiling <= b) :
    <NeronCapacityBound> d <= b * d.flowPotentialCapacity := by
  dsimp [<NeronCapacityBound>]
  nlinarith [d.capacity_pos]

/-- Defect is monotone in lower bounds on component order. -/
theorem <NeronDefectMonotone> (d : <ModularJacobianNeronDatum>) (p : Real)
    (hp : p <= d.neronComponentOrder) :
    d.componentGroupCeiling - d.neronComponentOrder <= d.componentGroupCeiling - p := by
  linarith

/-- Slack is monotone in tolerance parameter. -/
theorem <NeronSlackMonotoneTolerance> (d : <ModularJacobianNeronDatum>) (t : Real)
    (ht : d.neronTolerance <= t) :
    <NeronSlack> d <= d.componentGroupCeiling * t - d.neronComponentOrder := by
  dsimp [<NeronSlack>]
  nlinarith [d.ceiling_pos]

end <Namespace>
```
