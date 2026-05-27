Consider the system ẋ = f(x) with equilibrium at x* = 0. Choose a candidate Lyapunov function V: ℝⁿ → ℝ satisfying: (1) V(0) = 0, (2) V(x) > 0 for all x ≠ 0 in some neighborhood U of the origin (positive definite), and (3) V̇(x) = ∇V(x)·f(x) ≤ 0 for all x ∈ U (negative semi-definite along trajectories).

**Example:** ẋ₁ = -x₁ + x₁x₂, ẋ₂ = -x₂. Take V(x) = x₁² + x₂², which is positive definite.

Compute V̇ = 2x₁(-x₁ + x₁x₂) + 2x₂(-x₂) = -2x₁² + 2x₁²x₂ - 2x₂² = -2x₁²(1 - x₂) - 2x₂².

In the region |x₂| < 1, we have (1 - x₂) > 0, so V̇ < 0 (actually negative definite there), proving asymptotic stability by Lyapunov's theorem.

**Theorem (Lyapunov Stability):** If V is positive definite and V̇ is negative semi-definite on U, then x* = 0 is stable (Lyapunov sense); if V̇ is negative definite, it is asymptotically stable. The key insight is that V̇ ≤ 0 means trajectories cannot escape level sets {x : V(x) = c}, confining motion near the equilibrium. The method is constructive but finding V requires physical intuition or sum-of-squares techniques; energy functions (kinetic + potential) are natural candidates for mechanical systems.