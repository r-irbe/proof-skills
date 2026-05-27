For a nonlinear system \(\dot x=f(x)\) with equilibrium \(x^\*=0\) (after shifting coordinates if needed), choose a \(C^1\) Lyapunov function \(V:\mathbb{R}^n\to\mathbb{R}\) such that \(V(0)=0\), \(V(x)>0\) for all \(x\neq 0\) near the origin, and \(\dot V(x)=\nabla V(x)\cdot f(x)\le 0\) in some neighborhood of \(0\).
Because \(V\) is positive definite, its sublevel sets \(\Omega_c=\{x:V(x)\le c\}\) are neighborhoods of the equilibrium for sufficiently small \(c>0\).
Because \(\dot V\le 0\), along any trajectory starting in \(\Omega_c\) we have \(V(x(t))\le V(x(0))\le c\) for all \(t\ge 0\), so the trajectory can never leave \(\Omega_c\).
Hence for every neighborhood of the origin, one can choose a smaller sublevel set contained in it, and every solution starting there remains in the larger neighborhood for all future time.
This is exactly Lyapunov stability of the equilibrium.
If in fact \(\dot V(x)<0\) for all \(x\neq 0\) nearby, then \(V\) strictly decreases and the equilibrium is asymptotically stable; if \(V\) is also radially unbounded, the conclusion is global.
As a standard example, for \(\dot x=-x^3\), take \(V(x)=\tfrac12 x^2\), then \(\dot V=x\dot x=-x^4\le 0\), so \(x=0\) is stable, and since \(\dot V<0\) for \(x\neq 0\), it is actually asymptotically stable.
