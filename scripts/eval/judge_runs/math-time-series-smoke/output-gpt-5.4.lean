For a 200-point series, first difference or detrend if needed so the series is stationary, since ARMA order selection only makes sense on a stationary series.
With only 200 observations, keep the search small—typically p, q ∈ {0,1,2,3}, and rarely above 4 unless there is very strong evidence.
Use the ACF/PACF only to narrow candidates: a PACF that cuts off suggests AR(p), an ACF that cuts off suggests MA(q), and gradual decay in both suggests mixed ARMA.
Then fit a grid of candidate ARMA(p,q) models and compare AICc or BIC; with n=200, BIC is often preferred if you want a more conservative choice, while AICc is good for predictive accuracy.
Reject models whose residuals still show autocorrelation by checking the residual ACF and a Ljung–Box test.
Also require stable, invertible parameter estimates and reasonable standard errors.
Choose the simplest model that has near-minimum information criterion and passes diagnostics, rather than automatically taking the simplest model that has near-minimum AICc/BIC.
In practice for 200 points, the selected model is often something low-order like ARMA(1,1), AR(1), AR(2), or MA(1).
