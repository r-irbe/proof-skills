A prose claim in a paper typically mixes rhetorical hedging, scope qualifiers, and implicit assumptions into a single sentence. To extract a formalizable hypothesis you must strip each layer systematically.

First, identify the core predicate. Every prose claim has a subject, a relation, and an object. Isolate these three. "Heavy social media use causes anxiety in adolescents" decomposes into subject=social media use (quantified as heavy), relation=causes, object=anxiety, population=adolescents.

Second, convert vague quantifiers to measurable ones. "Heavy" must become an operational threshold: daily use exceeding two hours, or a continuous variable measured in hours per day. "Anxiety" must become a measured construct: GAD-7 score, or a binary threshold on that scale. Every term that cannot be plugged into a data column is not yet formalized.

Third, make the causal or associative claim explicit. Authors often conflate correlation, association, and causation. Decide which the claim actually asserts. If it says "causes," the formal hypothesis requires a directed graph or a potential-outcomes framing: for unit i, Y_i(T=1) > Y_i(T=0) in expectation. If it says "associated with," the formal hypothesis is a conditional dependence: P(Y | X) ≠ P(Y).

Fourth, state the null hypothesis. Formalization requires a falsifiable null. For the causal version: E[Y_i(1) - Y_i(0)] = 0. For the associative version: the partial correlation between X and Y conditioning on covariates Z equals zero.

Fifth, specify the population and the sampling frame. The prose often says "adolescents" but the formal hypothesis must state whether this means all adolescents globally, a specific age band (13–17), a specific cultural context, or a convenience sample. The hypothesis is only as general as the population it refers to.

Sixth, identify moderators implied by the prose. Authors often embed moderating claims inside the main assertion. "Especially in girls" or "particularly under stress" signals an interaction term: H: β_interaction ≠ 0 in the model Y = α + β_1 X + β_2 M + β_3 (X·M) + ε.

Seventh, identify mediators if the claim is mechanistic. "Social media causes anxiety by reducing sleep" implies a mediation chain. Formalize this as two sub-hypotheses: H1: X → M (social media reduces sleep), H2: M → Y controlling for X (sleep reduction increases anxiety). The total effect decomposes into direct and indirect paths.

Eighth, specify the statistical model family. The same conceptual hypothesis can be tested with OLS, logistic regression, a mixed-effects model, or a structural equation model. Choosing the wrong family is a specification error. Match the model to the outcome type: continuous outcomes, count data, ordinal data, and survival data each require a different link function.

Ninth, state the effect size minimum that would count as substantively meaningful. A hypothesis is not just about direction but magnitude. "We hypothesize that daily social media use is positively associated with GAD-7 scores with a standardized beta of at least 0.10" is a stronger, more useful formalization than merely asserting a positive sign.

Tenth, write out the formal statement in logical notation or regression equation form. For the running example: H: β_1 > 0 in GAD-7_i = α + β_1·(hours_per_day_i) + β_2·age_i + β_3·sex_i + ε_i, where ε ~ N(0, σ²), estimated on a sample of adolescents aged 13–17. This is now testable, replicable, and falsifiable, which is the complete definition of a formalized hypothesis.
