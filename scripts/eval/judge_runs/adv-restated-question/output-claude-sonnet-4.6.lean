Use Bayesian reasoning: assign prior probabilities to each hypothesis, then update them using likelihood ratios for each piece of evidence, even when evidence conflicts.

For each hypothesis H and evidence E, compute P(H|E) ∝ P(E|H) × P(H). Conflicting evidence means some pieces raise the likelihood of H while others lower it — multiply all likelihood ratios together; the product is your posterior weight.

When evidence directly contradicts across hypotheses, favor the hypothesis that best explains the most evidence with the fewest ad-hoc assumptions (Occam's razor as a prior regularizer). Assign lower weight to hypotheses that require dismissing consistent, high-quality evidence to survive.

Practically: score each hypothesis by summing log-likelihood ratios across all evidence items — log P(E_i|H) − log P(E_i|¬H). Higher total score wins. This penalizes hypotheses that predict evidence you didn't see and rewards those that predicted what you did.

Where evidence quality varies, weight each term by your confidence in that evidence before summing. Unreliable or contaminated evidence gets down-weighted, not ignored entirely.

If two hypotheses reach near-equal scores, the correct move is to defer judgment and seek discriminating evidence — a test whose outcome strongly favors one hypothesis and is nearly impossible under the other.
