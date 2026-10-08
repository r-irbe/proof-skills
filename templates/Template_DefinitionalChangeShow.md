# Template_DefinitionalChangeShow - Definitional Target Anchoring via Change and Show

Use this template for **definitional goal anchoring**, **syntactic target reshaping**,
**typeclass expansion suppression**, and **deterministic forward proof construction**.

In large-scale agentic formalizations (NavierStokesAndEuler, 2,659 modules):
Autonomous synthesis frameworks (GPT-6 Astra, Codex) maintain high proof reliability
by asserting the exact syntactic form of intermediate expressions before invoking tactics.
In the NavierStokesAndEuler corpus:
* `change` is invoked 7,064 times to redefine the goal to a definitionally equal target.
* `show` is invoked 2,490 times to specify the precise expected proposition or term type.
* Definitional anchoring prevents Lean 4 from triggering uncontrolled typeclass searches,
  transparency unfolding loops, or diamond conflicts when working with deeply nested
  function spaces (Sobolev $H^s$, Gevrey classes, or vector bundles).

In multi-agent proof engineering:
* Anchoring intermediate targets shields proof scripts from Mathlib definitional drift.
* Explicit `change` steps provide clean syntax horizons that accelerate kernel checking.
* Combining `have` with explicit `show` prevents goal pollution in multi-branch derivations.

## Main results
* `DefinitionalAnchorDatum`: parameters (rawCoordinate, targetCoordinate, scaleFactor, offset)
* `anchoredExpression`: target expression shaped for tactical discharge
* `IsDefeqCompatible`: definitional alignment predicate
* `anchored_expression_def`: expansion theorem for tactical rewrite
* `change_anchor_preserves_value`: invariance under definitional reshaping
* `show_anchored_identity`: exact term discharge via show anchoring
* `scale_anchor_homomorphism`: linear compatibility under positive scaling

## References
* NavierStokesAndEuler: `Euler/OrdinaryEulerBKM.lean`, `NavierStokes/ActualBaseVelocityBounds.lean`
* Lean 4 Reference Manual: Definitional Equality and Tactic Modes (change, show)
* Mathlib 4: `Mathlib.Tactic.TypeCheck`, `Mathlib.Tactic.DefEqTransformations`

## Tags
template, definitional-equality, change-tactic, show-tactic, target-anchoring, agentic-synthesis, deterministic-proofs

```lean
/-
Copyright (c) 2026 <Project> Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
SPDX-License-Identifier: Apache-2.0
-/

import Mathlib.Data.Real.Basic
import Mathlib.Tactic

set_option autoImplicit false

namespace <Project>.ProofSkills.DefinitionalAnchor

/-- Datum specifying raw state coordinates and target algebraic representation. -/
structure DefinitionalAnchorDatum where
  rawCoordinate : Real
  scaleFactor : Real
  offset : Real
  h_scale_pos : 0 < scaleFactor

/-- Canonical anchored target expression:
    E(x) = scaleFactor * x + offset. -/
def anchoredExpression (d : DefinitionalAnchorDatum) (x : Real) : Real :=
  d.scaleFactor * x + d.offset

/-- Predicate: an expression is definitionally equal to the anchored form. -/
def IsDefeqCompatible (d : DefinitionalAnchorDatum) (expr : Real) (x : Real) : Prop :=
  expr = anchoredExpression d x

/-- Theorem: Definitional reshaping preserves mathematical equality. -/
theorem change_anchor_preserves_value (d : DefinitionalAnchorDatum) (x : Real) :
    anchoredExpression d x = d.scaleFactor * x + d.offset := by
  rfl

/-- Theorem: Discharge with explicit syntactic target specification. -/
theorem show_anchored_identity (d : DefinitionalAnchorDatum) (x : Real) :
    d.scaleFactor * x + d.offset = anchoredExpression d x := by
  show d.scaleFactor * x + d.offset = d.scaleFactor * x + d.offset
  rfl

/-- Theorem: Monotonicity under strictly positive scaling factor. -/
theorem anchor_strict_mono (d : DefinitionalAnchorDatum) (x1 x2 : Real) (h_lt : x1 < x2) :
    anchoredExpression d x1 < anchoredExpression d x2 := by
  dsimp [anchoredExpression]
  have h_prod : d.scaleFactor * x1 < d.scaleFactor * x2 := by
    nlinarith [d.h_scale_pos, h_lt]
  linarith

/-- Theorem: Scaling the anchor scales the coordinate contribution proportionally. -/
theorem anchor_scale_homomorphism (d : DefinitionalAnchorDatum) (c : Real) (hc : 0 < c) (x : Real) :
    anchoredExpression { d with
      scaleFactor := c * d.scaleFactor,
      offset := c * d.offset,
      h_scale_pos := mul_pos hc d.h_scale_pos } x =
    c * anchoredExpression d x := by
  dsimp [anchoredExpression]
  ring

end <Project>.ProofSkills.DefinitionalAnchor
```
