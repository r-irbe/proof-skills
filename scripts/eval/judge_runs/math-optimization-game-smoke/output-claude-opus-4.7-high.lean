For a zero-sum game with payoff matrix A (rows = player 1's strategies, columns = player 2's), solve via LP. Player 1 (maximizer) finds mixed strategy x ≥ 0, 1ᵀx = 1 maximizing v s.t. Aᵀx ≥ v·1. Player 2 (minimizer) finds y ≥ 0, 1ᵀy = 1 minimizing w s.t. Ay ≤ w·1. By LP duality v = w (minimax theorem).

```python
import numpy as np
from scipy.optimize import linprog

def solve_zero_sum(A):
    m, n = A.shape
    c = np.zeros(n + 1); c[-1] = 1
    A_ub = np.hstack([A, -np.ones((m, 1))])
    b_ub = np.zeros(m)
    A_eq = np.zeros((1, n + 1)); A_eq[0, :n] = 1
    b_eq = [1]
    bounds = [(0, None)] * n + [(None, None)]
    res = linprog(c, A_ub, b_ub, A_eq, b_eq, bounds=bounds, method='highs')
    y, v = res.x[:n], res.x[-1]
    return v, y
```

Swap A → -Aᵀ (or flip signs/constraints) to recover x*.