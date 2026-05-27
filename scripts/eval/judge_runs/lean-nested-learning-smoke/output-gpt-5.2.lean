Inner: θ' = θ - α ∇_θ L_train(θ); Outer: ϕ ← ϕ - β ∇_ϕ L_val(θ'(ϕ)) (differentiate through the inner step, optionally with stop-gradient/off-policy truncation).
