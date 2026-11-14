# Template_NeronTateCanonicalHeightRegulator - Neron-Tate Canonical Height Regulator and Gram Determinant Bounds

Use this template for **Neron-Tate canonical heights**, **Gram regulators**,
**bilinear height pairings**, and **variance bounds on stochastic confidence cascades**.

## Main results
* `<NeronTateCanonicalHeightDatum>` - datum (canonicalHeightNorm, regulatorCapacity, gramDeterminant, heightTolerance, scaleWeight)
* `<neronTateHeightDefect>` - defect between regulator capacity and observed canonical height norm
* `<normalizedNeronTateHeightRatio>` - normalized ratio of observed canonical height norm to regulator capacity
* `<neronTateHeightSlack>` - slack between tolerance threshold and observed canonical height norm
* `<neronTateRegulatorEnergy>` - quadratic energy scaling with Gram determinant and scale weight
* `<IsStableNeronTateHeight>` - predicate: observed canonical height norm strictly below regulator capacity
* `<IsAdmissibleNeronTateHeight>` - predicate: observed canonical height norm within tolerance threshold
* `<IsContractiveNeronTateHeight>` - predicate: normalized height ratio strictly less than 1
* `<neronTateHeightDefect_pos_of_stable>` - defect is strictly positive for stable height norms
* `<neronTateHeightSlack_nonneg_of_admissible>` - slack is non-negative for admissible heights
* `<normalizedNeronTateHeightRatio_pos>` - normalized ratio is strictly positive
* `<normalizedNeronTateHeightRatio_lt_one_of_stable>` - normalized ratio is strictly less than 1 for stable heights
* `<isContractiveNeronTateHeight_iff_stable>` - stability is equivalent to contractive height ratio
* `<neronTateRegulatorEnergy_pos>` - quadratic regulator energy is strictly positive
* `<neronTateHeightDefect_anti_mono>` - increasing height norm strictly decreases defect
* `<natNeronTateHeightDefect>` - integer-scaled representation of height defect
* `<natNeronTateHeightDefect_nonneg>` - integer-scaled defect is non-negative when capacity exceeds norm
* `<natNeronTateHeightDefect_pos>` - integer-scaled defect is strictly positive for strict bounds
* `<neronTateHeightDefect_contraction_gain>` - contraction factor strictly increases height defect

## References
* FLT: `StochasticCCV/Core/NeronTateCanonicalHeightRegulator.lean`
* Neron, A. (1965), *Quasi-fonctions et hauteurs sur les varietes abeliennes*, Ann. of Math. 82, 249-331.

## Tags
template, neron-tate, canonical-height, gram-determinant, regulator, mordell-weil, bilinear-pairing
