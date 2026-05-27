With only 200 observations, use a parsimonious search and cap orders at p,q ≤ 2 or 3.
Fit candidate ARMA(p,q) models on that small grid, compare AICc or BIC, and keep the smallest model whose residual ACF looks like white noise and whose parameters are stable/significant.
As a practical default starting point, ARMA(1,1) is the first model to test because it captures both short-memory AR and MA behavior without overfitting.
