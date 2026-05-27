The linearity property of conditional expectation states that for random variables X and Y defined on a probability space (Ω, F_full, P), and for a sub-sigma-algebra F, and for constants a, b in R:

E[aX + bY | F] = aE[X | F] + bE[Y | F]   almost surely.

This holds whenever X and Y are integrable, meaning E[|X|] < ∞ and E[|Y|] < ∞.

To prove this, recall that E[X | F] is defined as the unique (up to a.s. equivalence) F-measurable random variable Z such that for every A in F, the integral of Z over A equals the integral of X over A: ∫_A Z dP = ∫_A X dP.

For the linear combination, define Z = aE[X | F] + bE[Y | F]. This Z is F-measurable because it is a linear combination of F-measurable functions. For any A in F:

∫_A Z dP = ∫_A [aE[X | F] + bE[Y | F]] dP = a ∫_A E[X | F] dP + b ∫_A E[Y | F] dP.

By the defining property of conditional expectation applied to X and Y respectively:

= a ∫_A X dP + b ∫_A Y dP = ∫_A (aX + bY) dP.

Since Z is F-measurable and satisfies the integral identity for every A in F, by uniqueness of conditional expectation, Z = E[aX + bY | F] almost surely. This completes the proof.

The linearity extends to finite sums: E[∑_{i=1}^n a_i X_i | F] = ∑_{i=1}^n a_i E[X_i | F] a.s., provided each X_i is integrable.

For countably infinite sums, additional conditions are needed. If X_n are non-negative, monotone convergence for conditional expectation gives E[∑_{n=1}^∞ X_n | F] = ∑_{n=1}^∞ E[X_n | F] a.s. For general sequences, dominated convergence or uniform integrability suffices.

Linearity interacts cleanly with other properties. Combined with the tower property E[E[X | F_1] | F_2] = E[X | F_2] when F_2 ⊆ F_1, and with the fact that E[X | F] = X when X is F-measurable, the three properties together characterize conditional expectation as a projection operator on L^2(Ω, F_full, P) onto the closed subspace L^2(Ω, F, P).

In the L^2 sense, conditional expectation is the orthogonal projection: E[X | F] is the element of L^2(Ω, F, P) closest to X in mean-square distance. Linearity of projections in Hilbert space is the geometric underpinning of the linearity property.

A special case: if c is F-measurable and bounded, then E[cX | F] = c E[X | F] a.s. This is the pull-out property, also called the taking-out-what-is-known rule. It follows because cE[X | F] is F-measurable and for any A in F, ∫_A c E[X | F] dP = ∫_A cX dP by properties of conditional expectation and the measurability of c with respect to F.

Linearity also implies E[X - E[X | F] | F] = 0 a.s., meaning the residual is orthogonal to all F-measurable functions in the L^2 sense, reinforcing the projection interpretation.
