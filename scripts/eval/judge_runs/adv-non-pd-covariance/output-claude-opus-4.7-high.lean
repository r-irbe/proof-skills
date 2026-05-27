The matrix Σ = [[1, 2], [2, 1]] is not positive definite (its eigenvalues are 3 and −1), so a real Cholesky decomposition L with L Lᵀ = Σ does not exist.

Verification: for L = [[a,0],[b,c]], L Lᵀ requires a² = 1, ab = 2, b² + c² = 1. From a = 1, b = 2, giving c² = 1 − 4 = −3, which has no real solution.

If complex entries are allowed, one valid factor is
L = [[1, 0], [2, i√3]],
which satisfies L Lᵀ = [[1, 2], [2, 1]] (note: this is the symmetric LLᵀ factorization, not the Hermitian L Lᴴ form, since Σ is indefinite).
