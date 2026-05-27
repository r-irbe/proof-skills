For ẋ = f(x) with equilibrium x = 0 (i.e., f(0) = 0), pick a candidate V: U → ℝ on a neighborhood U of 0 that is C¹, positive definite (V(0)=0, V(x)>0 for x≠0), and compute V̇(x) = ∇V(x)·f(x). If V̇(x) ≤ 0 on U, the origin is Lyapunov stable; if V̇(x) < 0 for x ≠ 0, it is asymptotically stable.

Example: ẋ₁ = −x₁ + x₁x₂², ẋ₂ = −x₂ − x₁²x₂. Take V(x) = ½(x₁² + x₂²), positive definite and radially unbounded. Then V̇ = x₁ẋ₁ + x₂ẋ₂ = −x₁² + x₁²x₂² − x₂² − x₁²x₂² = −(x₁² + x₂²) = −2V < 0 for x ≠ 0.

Hence V̇ is negative definite on ℝ², so the origin is globally asymptotically stable by Lyapunov's direct method.