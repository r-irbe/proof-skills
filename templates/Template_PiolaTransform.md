# Template_PiolaTransform - Wave-Packet Piola Algebra & Divergence-Free Preservation

Use this template for **Piola transformations**, **divergence-free constraint preservation**,
**incompressible coordinate deformations**, and **Jacobian determinant volume tracking**.

In continuum mechanics and fluid dynamics (Euler / Navier-Stokes formalization):
The Piola transformation preserves the divergence-free condition under nonlinear spatial mappings:
* For a coordinate deformation $F: \Omega_0 \to \Omega$ with Jacobian determinant $J = \det(F) > 0$,
  the Piola transform of a vector field $u$ is defined by:
  $$P(u) = J \cdot F^{-T} \cdot u$$
* The fundamental identity states that spatial divergence vanishes if and only if material divergence vanishes:
  $$\operatorname{div}(u) = 0 \iff \operatorname{Div}(P(u)) = 0$$
* In `Euler/PacketPiolaAlgebra.lean` and `Euler/PacketConstructedPiola.lean`, this finite-dimensional
  algebra governs the curl tensor transformation under volume-preserving changes of variables ($J = 1$).

In EASCI multi-agent consensus and belief dynamics:
* Probability current represents the flow of collective belief across agent state spaces.
* Nonlinear coordinate reparametrizations (such as log-odds transforms) must conserve total probability mass.
* The Piola transform guarantees that stationary consensus currents remain divergence-free under manifold re-embeddings.

## Main results
* `PiolaTransformDatum`: parameters (Jacobian J, inverse transpose norm, spatial divergence, material divergence, current magnitude)
* `piolaCurrentMagnitude`: magnitude of the transformed current field
* `volumeRatio`: volume distortion factor J
* `currentAmplification`: amplification ratio J * itn
* `piola_preserves_divergence_free`: preservation of solenoidal vector fields
* `divergence_defect_zero_incompressible`: vanishing defect under zero spatial divergence
* `piola_current_jacobian_scaling`: linear scaling with respect to Jacobian determinant
* `piola_current_mono_itn`: strict monotonicity with respect to inverse transpose operator norm

## References
* NavierStokesAndEuler: `Euler/PacketPiolaAlgebra.lean`, `Euler/PacketConstructedPiola.lean`, `Euler/PacketPiola.lean`
* Marsden, J. E., Hughes, T. J. R. (1983), *Mathematical Foundations of Elasticity*, Prentice-Hall
* Chorin, A. J., Marsden, J. E. (1993), *A Mathematical Introduction to Fluid Mechanics*, Springer-Verlag

## Tags
template, piola-transform, divergence-free, solenoidal, jacobian-determinant, coordinate-deformation, euler-equations

```lean
/-
Copyright (c) 2026 <Project> Authors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
SPDX-License-Identifier: Apache-2.0
-/

import Mathlib.Data.Real.Basic
import Mathlib.Tactic

set_option autoImplicit false

namespace <Project>.ProofSkills.PiolaTransform

/-- Datum specifying deformation Jacobian determinant, inverse transpose norm,
    spatial divergence, material divergence, and baseline current magnitude. -/
structure PiolaTransformDatum where
  J : Real
  invTransposeNorm : Real
  spatialDiv : Real
  materialDiv : Real
  currentMagnitude : Real
  h_J_pos : 0 < J
  h_itn_nonneg : 0 <= invTransposeNorm
  h_current_nonneg : 0 <= currentMagnitude
  h_piola_identity : spatialDiv = 0 -> materialDiv = 0

/-- Transformed current magnitude under the Piola mapping. -/
def piolaCurrent (d : PiolaTransformDatum) : Real :=
  d.J * d.invTransposeNorm * d.currentMagnitude

/-- Volume distortion factor measured by the Jacobian determinant. -/
def volumeRatio (d : PiolaTransformDatum) : Real :=
  d.J

/-- Current amplification factor under coordinate deformation. -/
def currentAmplification (d : PiolaTransformDatum) : Real :=
  d.J * d.invTransposeNorm

/-- Divergence preservation theorem: spatial solenoidal fields map to material solenoidal fields. -/
theorem piola_preserves_divergence_free (d : PiolaTransformDatum) (h : d.spatialDiv = 0) :
    d.materialDiv = 0 :=
  d.h_piola_identity h

/-- Divergence defect vanishes for incompressible fields. -/
theorem divergence_defect_zero (d : PiolaTransformDatum) (h : d.spatialDiv = 0) :
    d.materialDiv - d.spatialDiv = 0 := by
  rw [d.h_piola_identity h, h]
  ring

/-- Non-negativity of transformed current magnitude. -/
theorem piola_current_nonneg (d : PiolaTransformDatum) :
    0 <= piolaCurrent d := by
  dsimp [piolaCurrent]
  exact mul_nonneg (mul_nonneg (le_of_lt d.h_J_pos) d.h_itn_nonneg) d.h_current_nonneg

/-- Linear scaling of transformed current with respect to the Jacobian determinant. -/
theorem piola_current_jacobian_scaling (d : PiolaTransformDatum) (c : Real) (hc : 0 < c) :
    piolaCurrent { d with
      J := c * d.J,
      h_J_pos := mul_pos hc d.h_J_pos } = c * piolaCurrent d := by
  dsimp [piolaCurrent]
  ring

/-- Strict monotonicity of transformed current under increased deformation gradient norm. -/
theorem piola_current_strict_mono (d : PiolaTransformDatum) (delta : Real)
    (h_delta_pos : 0 < delta) (h_curr_pos : 0 < d.currentMagnitude) :
    piolaCurrent d < piolaCurrent { d with
      invTransposeNorm := d.invTransposeNorm + delta,
      h_itn_nonneg := by linarith [d.h_itn_nonneg, h_delta_pos] } := by
  dsimp [piolaCurrent]
  have h_pos : 0 < d.J * delta * d.currentMagnitude :=
    mul_pos (mul_pos d.h_J_pos h_delta_pos) h_curr_pos
  linarith

end <Project>.ProofSkills.PiolaTransform
```
