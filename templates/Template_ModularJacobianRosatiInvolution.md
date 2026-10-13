# Template_ModularJacobianRosatiInvolution - Modular Jacobian Rosati Involution Bounds

Use this template for **Modular Jacobian Rosati involution**, **canonical principal polarizations**,
**positivity of trace pairing**, and **bounding stochastic circulation in confidence cascades**.

## Main results
* `<ModularJacobianRosatiInvolutionDatum>` - datum (tracePairing, involutionCeiling, polarizationConductor, involutionTolerance, scaleWeight)
* `<modularJacobianRosatiInvolutionDefect>` - defect between involution ceiling and observed trace pairing
* `<normalizedModularJacobianRosatiInvolutionRatio>` - normalized ratio of trace pairing to involution ceiling
* `<modularJacobianRosatiInvolutionSlack>` - involution slack relative to tolerance threshold
* `<modularJacobianRosatiInvolutionEnergy>` - quadratic Modular Jacobian Rosati involution energy scaling with scale weight and polarization conductor
* `<IsStableModularJacobianRosatiInvolution>` - stability predicate: trace pairing strictly below involution ceiling
* `<modularJacobianRosatiInvolutionDefect_pos_of_isStable>` - stability implies positive involution defect
* `<normalizedModularJacobianRosatiInvolutionRatio_lt_one_of_isStable>` - stability implies normalized ratio strictly less than 1
* `<modularJacobianRosatiInvolutionEnergy_pos>` - Modular Jacobian Rosati involution energy is strictly positive
* `<modularJacobianRosatiInvolution_reconstruction_identity>` - defect + tracePairing = ceiling
* `<modularJacobianRosatiInvolutionSlack_pos_of_lt_tolerance>` - slack is positive when trace pairing is below tolerance
* `<modularJacobianRosatiInvolution_capacity_scaled_nonneg>` - capacity scaled nonnegativity
* `<modularJacobianRosatiInvolution_stability_preserved_under_shrink>` - stability preserved under positive trace pairing reduction
* `<modularJacobianRosatiInvolutionEnergy_monotone_of_weight_le>` - energy is monotonic in scale weight
* `<modularJacobianRosatiInvolution_tolerance_slack_add_identity>` - tolerance slack add identity
* `<modularJacobianRosatiInvolutionDefect_monotone_of_pairing_le>` - defect is monotonic in trace pairing reduction
* `<modularJacobianRosatiInvolution_adjoint_positivity>` - trace pairing under canonical principal polarization is positive
* `<modularJacobianRosatiInvolution_circulation_contraction>` - scaling by factor c with 0 < c < 1 strictly reduces trace pairing

## References
* FLT: `StochasticCCV/Core/ModularJacobianRosatiInvolution.lean`
* Shimura, G. (1971), *Introduction to the Arithmetic Theory of Automorphic Functions*, Princeton University Press.
* Milne, J. S. (1986), *Abelian Varieties*, in Arithmetic Geometry, Springer-Verlag, 103-150.
* Mumford, D. (1970), *Abelian Varieties*, Oxford University Press.

## Tags
template, modular-jacobian, rosati-involution, principal-polarization, trace-pairing, stochastic-ccv, circulation-contraction
