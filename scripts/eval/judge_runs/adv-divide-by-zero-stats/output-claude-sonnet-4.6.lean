The Pearson correlation is **undefined (NaN)**.

The formula is r = cov(X,Y) / (σ_X · σ_Y). Y = [7,7,7,7,7] is a constant, so σ_Y = 0. The denominator is zero, making the expression undefined — division by zero. No linear relationship can be quantified when one variable has no variance. NumPy confirms this with a RuntimeWarning and returns NaN.
