Let L = (SC, ≤) be a lattice of security classifications, where SC is a finite set of levels and ≤ is a partial order. Each subject s ∈ S has a clearance λ(s) ∈ SC and each object o ∈ O has a classification λ(o) ∈ SC. A state σ ⊆ S × O × {r, w, e, a} represents current accesses. The **simple security property** (no-read-up) states:

∀(s, o, r) ∈ σ : λ(o) ≤ λ(s)

i.e., subject s may hold read access to object o only if s's clearance dominates o's classification. A system is **secure** iff every reachable state σ satisfies this predicate for all read-access triples. In the multi-category lattice (Bell-LaPadula's original formulation), dominance is component-wise: (c₁, C₁) ≤ (c₂, C₂) iff c₁ ≤ c₂ ∧ C₁ ⊆ C₂, so both hierarchical level and compartment set must be dominated.