Let θ be model parameters, φ meta-parameters (e.g., learning rate, initialization, or loss weighting). For each task τ sampled from p(T):

Inner step (adaptation on support set D_τ^s):
  θ_τ' = θ − α(φ) · ∇_θ L^s(θ; D_τ^s, φ)

Outer step (meta-update on query set D_τ^q):
  φ ← φ − β · ∇_φ Σ_τ L^q(θ_τ'(φ); D_τ^q)

The outer gradient backpropagates through the inner update, requiring a second-order derivative ∇_φ θ_τ' (or a first-order approximation as in FOMAML/Reptile). This is the MAML-style bilevel formulation: inner = task-specific SGD, outer = meta-SGD over the post-adaptation loss.