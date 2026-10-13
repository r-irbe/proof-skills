# Template_HeegnerPointRegulatorHeight - Heegner Point Canonical Heights and Gross-Zagier Regulator Bounds

Use this template for **Heegner point canonical heights**, **Gross-Zagier formulas**,
**central L-derivative pairings**, and **variance bounds on stochastic confidence cascades**.

## Main results
* `<HeegnerPointRegulatorDatum>` - datum (heegnerHeightNorm, regulatorThreshold, grossZagierConstant, heightTolerance, discriminantWeight)
* `<heegnerRegulatorDefect>` - defect between regulator threshold and observed Heegner height norm
* `<normalizedHeegnerRegulatorRatio>` - normalized ratio of observed Heegner height norm to regulator threshold
* `<heegnerRegulatorSlack>` - slack between tolerance threshold and observed Heegner height norm
* `<heegnerRegulatorEnergy>` - quadratic energy scaling with Gross-Zagier constant and discriminant weight
* `<IsStableHeegnerRegulator>` - predicate: observed Heegner height norm strictly below regulator threshold
* `<IsAdmissibleHeegnerRegulator>` - predicate: observed Heegner height norm within tolerance threshold
* `<IsContractiveHeegnerRegulator>` - predicate: normalized Heegner height ratio strictly less than 1
* `<heegnerRegulatorDefect_pos_of_stable>` - defect is strictly positive for stable Heegner regulators
* `<heegnerRegulatorSlack_nonneg_of_admissible>` - slack is non-negative for admissible Heegner regulators
* `<normalizedHeegnerRegulatorRatio_pos>` - normalized ratio is strictly positive
* `<normalizedHeegnerRegulatorRatio_lt_one_of_stable>` - normalized ratio is strictly less than 1 for stable regulators
* `<isContractiveHeegnerRegulator_iff_stable>` - stability is equivalent to contractive Heegner height ratio
* `<heegnerRegulatorEnergy_pos>` - quadratic regulator energy is strictly positive
* `<heegnerRegulatorDefect_anti_mono>` - increasing height norm strictly decreases defect
* `<natHeegnerRegulatorDefect>` - integer-scaled representation of Heegner defect
* `<natHeegnerRegulatorDefect_nonneg>` - integer-scaled defect is non-negative when threshold exceeds norm
* `<natHeegnerRegulatorDefect_pos>` - integer-scaled defect is strictly positive for strict bounds
* `<heegnerRegulatorDefect_contraction_gain>` - contraction factor strictly increases Heegner defect

## References
* FLT: `StochasticCCV/Core/HeegnerPointRegulatorHeight.lean`
* Gross, B., Zagier, D. (1986), *Heegner points and derivatives of L-series*, Invent. Math. 84, 225-320.

## Tags
template, heegner-point, gross-zagier, canonical-height, regulator, central-derivative, rankin-selberg
