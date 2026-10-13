# Template_GrossZagierHeegnerEulerSystem - Gross-Zagier Heegner Point Euler Systems and Norm-Compatibility Bounds

Use this template for **Heegner point Euler systems**, **Gross-Zagier theorems**,
**ring class field norm compatibility**, and **variance bounds on stochastic confidence cascades**.

## Main results
* `<GrossZagierEulerSystemDatum>` - datum (eulerSystemNorm, capacityThreshold, traceFactor, eulerTolerance, scaleWeight)
* `<grossZagierEulerDefect>` - defect between capacity threshold and observed Euler system norm
* `<normalizedGrossZagierEulerRatio>` - normalized ratio of observed Euler system norm to capacity threshold
* `<grossZagierEulerSlack>` - slack between tolerance threshold and observed Euler system norm
* `<grossZagierEulerEnergy>` - quadratic energy scaling with trace compatibility factor and scale weight
* `<IsStableGrossZagierEuler>` - predicate: observed Euler system norm strictly below capacity threshold
* `<IsAdmissibleGrossZagierEuler>` - predicate: observed Euler system norm within tolerance threshold
* `<IsContractiveGrossZagierEuler>` - predicate: normalized Euler system ratio strictly less than 1
* `<grossZagierEulerDefect_pos_of_stable>` - defect is strictly positive for stable Euler systems
* `<grossZagierEulerSlack_nonneg_of_admissible>` - slack is non-negative for admissible Euler systems
* `<normalizedGrossZagierEulerRatio_pos>` - normalized ratio is strictly positive
* `<normalizedGrossZagierEulerRatio_lt_one_of_stable>` - normalized ratio is strictly less than 1 for stable systems
* `<isContractiveGrossZagierEuler_iff_stable>` - stability is equivalent to contractive Euler ratio
* `<grossZagierEulerEnergy_pos>` - quadratic regulator energy is strictly positive
* `<grossZagierEulerDefect_anti_mono>` - increasing norm strictly decreases defect
* `<natGrossZagierEulerDefect>` - integer-scaled representation of Euler defect
* `<natGrossZagierEulerDefect_nonneg>` - integer-scaled defect is non-negative when threshold exceeds norm
* `<natGrossZagierEulerDefect_pos>` - integer-scaled defect is strictly positive for strict bounds
* `<grossZagierEulerDefect_contraction_gain>` - contraction factor strictly increases Euler defect

## References
* FLT: `StochasticCCV/Core/GrossZagierHeegnerEulerSystem.lean`
* Gross, B., Zagier, D. (1986), *Heegner points and derivatives of L-series*, Invent. Math. 84, 225-320.
* Kolyvagin, V. A. (1990), *Euler systems*, The Grothendieck Festschrift, Vol. II, 435-483.

## Tags
template, heegner-point, gross-zagier, euler-system, kolyvagin, selmer-annihilation, norm-compatibility
