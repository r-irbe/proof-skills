Cholesky decomposition requires Σ to be symmetric positive definite. Check the leading principal minors:

Minor 1: det([1]) = 1 > 0. Good.
Minor 2: det([[1,2],[2,1]]) = (1)(1) − (2)(2) = 1 − 4 = −3 < 0.

Since the second leading minor is negative, Σ is indefinite (eigenvalues are 3 and −1). The Cholesky decomposition does not exist for this matrix. No real lower-triangular L satisfying L L^T = Σ exists.
