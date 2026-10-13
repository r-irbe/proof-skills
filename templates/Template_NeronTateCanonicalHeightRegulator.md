# Template_NeronTateCanonicalHeightRegulator - Neron-Tate Canonical Height Regulator & Gram Determinant Bounds

Use this template for **Neron-Tate canonical heights**, **Gram regulators**,
**height bilinear pairings**, and **stochastic confidence cascade variance bounds**.

In arithmetic geometry and Fermat's Last Theorem / modular curves:
The Neron-Tate canonical height h_NT : E(Q) -> Real is the unique quadratic form that differs from the
naive Weil height by a bounded function and satisfies:
  h_NT(m * P) = m^2 * h_NT(P)
for all m in Integer and P in E(Q). Extending to the Mordell-Weil group modulo torsion E(Q)/E(Q)_tors,
the height pairing:
  <P, Q>_{NT} = (h_NT(P + Q) - h_NT(P) - h_NT(Q)) / 2
is symmetric, bilinear, and positive-definite. The Gram determinant det(<P_i, P_j>_{NT}) defines
the regulator Reg(E/Q), which measures the covolume of the Mordell-Weil lattice in Euclidean space.
In the Birch and Swinnerton-Dyer formula and Wiles' modularity proof, the non-vanishing of the regulator
certifies the non-degeneracy of the rational point lattice and bounds the global height capacity.

In stochastic consensus and Markov non-equilibrium networks:
* The canonical height acts as a quadratic Lyapunov energy bounding the variance of belief states.
* Gram regulators measure the volumetric dispersion of distributed agent confidence profiles.
* The regulator defect quantifies the stability margin before encountering divergence cascades.
* Normalized height ratios provide contractive decay guarantees across consensus iterations.

## Main results
* `<NeronTateCanonicalHeightDatum>` - datum (canonicalHeightNorm, regulatorCapacity, gramDeterminant, heightTolerance, scaleWeight)
* `<neronTateRegulatorDefect>` - defect between regulator capacity ceiling and observed canonical height norm
* `<normalizedNeronTateRegulatorRatio>` - normalized ratio of observed canonical height norm to regulator capacity
* `<neronTateRegulatorSlack>` - slack between tolerance threshold and observed canonical height norm
* `<neronTateRegulatorEnergy>` - quadratic energy scaling with Gram determinant and scale weight
* `<IsStableNeronTateRegulator>` - predicate: observed canonical height norm strictly below regulator capacity
* `<IsAdmissibleNeronTateRegulator>` - predicate: observed canonical height norm within tolerance threshold
* `<IsContractiveNeronTateRegulator>` - predicate: normalized height ratio strictly less than 1
* `<neronTateRegulatorDefect_pos_of_stable>` - defect is strictly positive for stable heights
* `<neronTateRegulatorSlack_nonneg_of_admissible>` - slack is non-negative for admissible heights
* `<normalizedNeronTateRegulatorRatio_pos>` - normalized ratio is strictly positive
* `<normalizedNeronTateRegulatorRatio_lt_one_of_stable>` - normalized ratio is strictly less than 1 for stable heights
* `<isContractiveNeronTateRegulator_iff_stable>` - stability is equivalent to contractive height ratio
* `<neronTateRegulatorEnergy_pos>` - quadratic regulator energy is strictly positive
* `<neronTateRegulatorDefect_anti_mono>` - increasing height norm strictly decreases defect
* `<natNeronTateRegulatorDefect>` - integer-scaled representation of height defect
* `<natNeronTateRegulatorDefect_nonneg>` - integer-scaled defect is non-negative when capacity exceeds norm
* `<natNeronTateRegulatorDefect_pos>` - integer-scaled defect is strictly positive for strict bounds
* `<neronTateRegulatorDefect_contraction_gain>` - contraction factor strictly increases height defect

## References
* FLT: `StochasticCCV/Core/NeronTateCanonicalHeightRegulator.lean`
* Neron, A. (1965), *Quasi-fonctions et hauteurs sur les varietes abeliennes*, Ann. of Math. (2) 82, 249-331.
* Tate, J. (1965), *On the conjectures of Birch and Swinnerton-Dyer and a geometric analog*, Seminaire Bourbaki 18 (306), 415-440.
* Silverman, J. H. (2009), *The Arithmetic of Elliptic Curves*, Graduate Texts in Mathematics 106, Springer.

## Tags
template, neron-tate, canonical-height, regulator, gram-determinant, mordell-weil, bsd-conjecture
