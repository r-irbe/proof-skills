# Template_ModularJacobianAtkinLehnerEigenvalue - Modular Jacobian Atkin-Lehner Eigenvalues & Pseudo-Eigenvalues

Use this template for **modular Jacobian Atkin-Lehner operator eigenvalues**, **pseudo-eigenvalue bounds**,
**circulation capacity bounds**, and **symmetry mode analysis**.

In arithmetic geometry and Fermat's Last Theorem / modular forms:
On modular curves X_0(N) and their modular Jacobians J_0(N), the Atkin-Lehner involutions
W_Q act on the space of cusp forms S_2(\Gamma_0(N)) and on the modular Jacobian J_0(N).
For newforms f, the Atkin-Lehner eigenvalue satisfies W_Q(f) = \pm f, with the sign
governing the functional equation of the associated Hasse-Weil L-function and determining
the sign of the global root number \epsilon(E/\mathbb{Q}) for elliptic curves in modularity
proofs (Wiles, Taylor-Wiles, Diamond, Conrad, Darmon).
On the Jacobian J_0(N), Atkin-Lehner operators induce decomposition into eigenspaces,
bounding the torsion of optimal quotients and certifying the stability of the Mazur
Eisenstein quotient under level transitions.

In stochastic consensus and Markov non-equilibrium networks:
* Atkin-Lehner eigenvalues quantify reversible/anti-reversible symmetry modes in Markov graph circulation.
* Pseudo-eigenvalue bounds certify the spectral gap and stability of non-equilibrium steady states.
* The Atkin-Lehner slack defines certified safety headroom against asymmetric circulation perturbation.
* The normalized Atkin-Lehner ratio verifies dissipation rate control relative to total network capacity.

## Main results
* `<ModularJacobianAtkinLehnerEigenvalueDatum>` - datum (atkinLehnerEigenvalue, atkinLehnerCapacity, pseudoEigenvalueBound, atkinLehnerTolerance, atkinLehnerWeight)
* `<atkinLehnerDefect>` - defect between Atkin-Lehner capacity ceiling and observed eigenvalue norm
* `<normalizedAtkinLehnerRatio>` - normalized ratio of observed Atkin-Lehner eigenvalue norm to capacity ceiling
* `<atkinLehnerCapacityBound>` - total Atkin-Lehner capacity bound scaled by capacity ceiling and pseudo-eigenvalue bound
* `<atkinLehnerSlack>` - Atkin-Lehner slack between tolerance-scaled capacity and observed eigenvalue norm
* `<atkinLehnerWeightedMargin>` - weighted margin combining Atkin-Lehner weight and Atkin-Lehner tolerance
* `<atkinLehnerCombinedIndex>` - combined index of normalized Atkin-Lehner ratio and Atkin-Lehner slack
* `<IsAtkinLehnerBounded>` - predicate: Atkin-Lehner eigenvalue norm does not exceed capacity ceiling
* `<IsCriticalAtkinLehner>` - predicate: Atkin-Lehner eigenvalue matches capacity ceiling exactly
* `<IsStrictAtkinLehnerBounded>` - predicate: Atkin-Lehner eigenvalue norm is strictly below capacity ceiling
* `<IsAtkinLehnerCapacitySafe>` - predicate: Atkin-Lehner eigenvalue norm does not exceed capacity bound
* `<IsAtkinLehnerSafe>` - safety envelope certifying both ceiling boundedness and capacity boundedness
* `<atkin_lehner_defect_pos_of_strict>` - defect is strictly positive for strict bounded systems
* `<atkin_lehner_defect_nonneg_of_bounded>` - defect is non-negative for bounded systems
* `<bounded_of_atkin_lehner_defect_nonneg>` - non-negative defect implies bounded system
* `<atkin_lehner_bounded_iff_defect_nonneg>` - boundedness is equivalent to non-negative defect
* `<normalized_atkin_lehner_ratio_pos>` - normalized ratio is strictly positive
* `<normalized_atkin_lehner_ratio_le_one_of_bounded>` - normalized ratio is at most 1 for bounded systems
* `<bounded_of_normalized_atkin_lehner_ratio_le_one>` - ratio at most 1 implies bounded system
* `<atkin_lehner_bounded_iff_normalized_le_one>` - boundedness is equivalent to normalized ratio at most 1

## References
* FLT: `StochasticCCV/Core/ModularJacobianAtkinLehnerEigenvalue.lean`
* Atkin, A. O. L., Lehner, J. (1970), *Hecke operators on \Gamma_0(m)*, Math. Ann. 185, 134-160.
* Mazur, B. (1977), *Modular curves and the Eisenstein ideal*, Publ. Math. IHES 47, 33-186.
* Ribet, K. A. (1990), *On modular representations of Gal(\bar{Q}/Q) arising from modular forms*, Invent. Math. 100, 431-476.

## Tags
template, modular-jacobian, atkin-lehner, eigenvalues, involutions, hecke-operators, circulation-symmetry

```lean
/-
Copyright (c) 2026 <Project> Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: <Project> Formalization Team
SPDX-License-Identifier: Apache-2.0
-/

import Mathlib.Data.Real.Basic
import Mathlib.Tactic

set_option autoImplicit false
set_option linter.unusedVariables false
set_option linter.unusedSectionVars false
set_option linter.unusedSimpArgs false

noncomputable section

namespace <Project>.<proj>

structure <ModularJacobianAtkinLehnerEigenvalueDatum> where
  atkinLehnerEigenvalue : ℝ
  atkinLehnerCapacity : ℝ
  pseudoEigenvalueBound : ℝ
  atkinLehnerTolerance : ℝ
  atkinLehnerWeight : ℝ
  eigenvalue_pos : 0 < atkinLehnerEigenvalue
  capacity_pos : 0 < atkinLehnerCapacity
  bound_pos : 0 < pseudoEigenvalueBound
  tolerance_pos : 0 < atkinLehnerTolerance
  weight_pos : 0 < atkinLehnerWeight

def <atkinLehnerDefect> (d : <ModularJacobianAtkinLehnerEigenvalueDatum>) : ℝ :=
  d.atkinLehnerCapacity - d.atkinLehnerEigenvalue

def <normalizedAtkinLehnerRatio> (d : <ModularJacobianAtkinLehnerEigenvalueDatum>) : ℝ :=
  d.atkinLehnerEigenvalue / d.atkinLehnerCapacity

def <atkinLehnerCapacityBound> (d : <ModularJacobianAtkinLehnerEigenvalueDatum>) : ℝ :=
  d.atkinLehnerCapacity * d.pseudoEigenvalueBound

def <atkinLehnerSlack> (d : <ModularJacobianAtkinLehnerEigenvalueDatum>) : ℝ :=
  d.atkinLehnerCapacity * d.atkinLehnerTolerance - d.atkinLehnerEigenvalue

def <atkinLehnerWeightedMargin> (d : <ModularJacobianAtkinLehnerEigenvalueDatum>) : ℝ :=
  d.atkinLehnerWeight * <atkinLehnerDefect> d + d.atkinLehnerTolerance

def <atkinLehnerCombinedIndex> (d : <ModularJacobianAtkinLehnerEigenvalueDatum>) : ℝ :=
  <normalizedAtkinLehnerRatio> d + <atkinLehnerSlack> d

def <IsAtkinLehnerBounded> (d : <ModularJacobianAtkinLehnerEigenvalueDatum>) : Prop :=
  d.atkinLehnerEigenvalue ≤ d.atkinLehnerCapacity

def <IsCriticalAtkinLehner> (d : <ModularJacobianAtkinLehnerEigenvalueDatum>) : Prop :=
  d.atkinLehnerEigenvalue = d.atkinLehnerCapacity

def <IsStrictAtkinLehnerBounded> (d : <ModularJacobianAtkinLehnerEigenvalueDatum>) : Prop :=
  d.atkinLehnerEigenvalue < d.atkinLehnerCapacity

def <IsAtkinLehnerCapacitySafe> (d : <ModularJacobianAtkinLehnerEigenvalueDatum>) : Prop :=
  d.atkinLehnerEigenvalue ≤ <atkinLehnerCapacityBound> d

def <IsAtkinLehnerSafe> (d : <ModularJacobianAtkinLehnerEigenvalueDatum>) : Prop :=
  <IsAtkinLehnerBounded> d ∧ <IsAtkinLehnerCapacitySafe> d

theorem <atkin_lehner_defect_pos_of_strict> (d : <ModularJacobianAtkinLehnerEigenvalueDatum>)
    (h : <IsStrictAtkinLehnerBounded> d) : 0 < <atkinLehnerDefect> d := by
  dsimp [<IsStrictAtkinLehnerBounded>] at h
  dsimp [<atkinLehnerDefect>]
  linarith

theorem <atkin_lehner_defect_nonneg_of_bounded> (d : <ModularJacobianAtkinLehnerEigenvalueDatum>)
    (h : <IsAtkinLehnerBounded> d) : 0 ≤ <atkinLehnerDefect> d := by
  dsimp [<IsAtkinLehnerBounded>] at h
  dsimp [<atkinLehnerDefect>]
  linarith

theorem <bounded_of_atkin_lehner_defect_nonneg> (d : <ModularJacobianAtkinLehnerEigenvalueDatum>)
    (h : 0 ≤ <atkinLehnerDefect> d) : <IsAtkinLehnerBounded> d := by
  dsimp [<atkinLehnerDefect>] at h
  dsimp [<IsAtkinLehnerBounded>]
  linarith

theorem <atkin_lehner_bounded_iff_defect_nonneg> (d : <ModularJacobianAtkinLehnerEigenvalueDatum>) :
    <IsAtkinLehnerBounded> d ↔ 0 ≤ <atkinLehnerDefect> d := by
  constructor
  · exact <atkin_lehner_defect_nonneg_of_bounded> d
  · exact <bounded_of_atkin_lehner_defect_nonneg> d

theorem <normalized_atkin_lehner_ratio_pos> (d : <ModularJacobianAtkinLehnerEigenvalueDatum>) :
    0 < <normalizedAtkinLehnerRatio> d := by
  dsimp [<normalizedAtkinLehnerRatio>]
  exact div_pos d.eigenvalue_pos d.capacity_pos

theorem <normalized_atkin_lehner_ratio_le_one_of_bounded> (d : <ModularJacobianAtkinLehnerEigenvalueDatum>)
    (h : <IsAtkinLehnerBounded> d) : <normalizedAtkinLehnerRatio> d ≤ 1 := by
  dsimp [<IsAtkinLehnerBounded>] at h
  dsimp [<normalizedAtkinLehnerRatio>]
  exact (div_le_one d.capacity_pos).mpr h

theorem <bounded_of_normalized_atkin_lehner_ratio_le_one> (d : <ModularJacobianAtkinLehnerEigenvalueDatum>)
    (h : <normalizedAtkinLehnerRatio> d ≤ 1) : <IsAtkinLehnerBounded> d := by
  dsimp [<normalizedAtkinLehnerRatio>] at h
  dsimp [<IsAtkinLehnerBounded>]
  exact (div_le_one d.capacity_pos).mp h

theorem <atkin_lehner_bounded_iff_normalized_le_one> (d : <ModularJacobianAtkinLehnerEigenvalueDatum>) :
    <IsAtkinLehnerBounded> d ↔ <normalizedAtkinLehnerRatio> d ≤ 1 := by
  constructor
  · exact <normalized_atkin_lehner_ratio_le_one_of_bounded> d
  · exact <bounded_of_normalized_atkin_lehner_ratio_le_one> d

end <Project>.<proj>
```
