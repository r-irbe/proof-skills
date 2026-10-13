# Template_GrossZagierKolyvaginDerivative - Gross-Zagier Kolyvagin Derivative Operators and Selmer Annihilation

Use this template for **Kolyvagin derivative operators**, **Gross-Zagier theorems**,
**Selmer group annihilation**, and **variance bounds on stochastic confidence cascades**.

## Main results
* `<GrossZagierKolyvaginDatum>` - datum (derivativeNorm, selmerBoundCeiling, eulerSystemRank, derivativeTolerance, scaleWeight)
* `<grossZagierKolyvaginDefect>` - defect between Selmer bound ceiling and observed derivative norm
* `<normalizedGrossZagierKolyvaginRatio>` - normalized ratio of observed derivative norm to Selmer bound ceiling
* `<grossZagierKolyvaginSlack>` - slack between tolerance threshold and observed derivative norm
* `<grossZagierKolyvaginEnergy>` - quadratic energy scaling with Euler system rank and scale weight
* `<IsStableGrossZagierKolyvagin>` - predicate: observed derivative norm strictly below Selmer bound ceiling
* `<IsAdmissibleGrossZagierKolyvagin>` - predicate: observed derivative norm within tolerance threshold
* `<IsContractiveGrossZagierKolyvagin>` - predicate: normalized derivative ratio strictly less than 1
* `<grossZagierKolyvaginDefect_pos_of_stable>` - defect is strictly positive for stable derivative systems
* `<grossZagierKolyvaginSlack_nonneg_of_admissible>` - slack is non-negative for admissible derivative systems
* `<normalizedGrossZagierKolyvaginRatio_pos>` - normalized ratio is strictly positive
* `<normalizedGrossZagierKolyvaginRatio_lt_one_of_stable>` - normalized ratio is strictly less than 1 for stable systems
* `<isContractiveGrossZagierKolyvagin_iff_stable>` - stability is equivalent to contractive derivative ratio
* `<grossZagierKolyvaginEnergy_pos>` - quadratic derivative energy is strictly positive
* `<grossZagierKolyvaginDefect_anti_mono>` - increasing norm strictly decreases defect
* `<natGrossZagierKolyvaginDefect>` - integer-scaled representation of derivative defect
* `<natGrossZagierKolyvaginDefect_nonneg>` - integer-scaled defect is non-negative when ceiling exceeds norm
* `<natGrossZagierKolyvaginDefect_pos>` - integer-scaled defect is strictly positive for strict bounds
* `<grossZagierKolyvaginDefect_contraction_gain>` - contraction factor strictly increases derivative defect

## References
* FLT: `StochasticCCV/Core/GrossZagierKolyvaginDerivative.lean`
* Gross, B., Zagier, D. (1986), *Heegner points and derivatives of L-series*, Invent. Math. 84, 225-320.
* Kolyvagin, V. A. (1990), *Euler systems*, The Grothendieck Festschrift, Vol. II, 435-483.
* Rubin, K. (2000), *Euler Systems*, Annals of Mathematics Studies 147, Princeton University Press.

## Tags
template, heegner-point, gross-zagier, kolyvagin-derivative, euler-system, selmer-annihilation, rank-one
