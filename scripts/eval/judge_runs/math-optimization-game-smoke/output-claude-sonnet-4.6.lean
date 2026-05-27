In a two-player zero-sum game with m×n payoff matrix A, the row player (maximizer) chooses mixed strategy p ∈ ℝᵐ and the column player (minimizer) chooses q ∈ ℝⁿ. The Nash equilibrium value v = maxₚ minᵢ (Aᵀp)ᵢ = minᵧ maxᵢ (Aq)ᵢ by the minimax theorem.

Row player's LP (primal): maximize v subject to Aᵀp ≥ v·1, p ≥ 0, 1ᵀp = 1.

Column player's LP (dual): minimize u subject to Aq ≤ u·1, q ≥ 0, 1ᵀq = 1.

Strong duality guarantees both LPs share the same optimal value v* (the game value). Shift A by a constant if needed to ensure v* > 0 before solving, then subtract it back.