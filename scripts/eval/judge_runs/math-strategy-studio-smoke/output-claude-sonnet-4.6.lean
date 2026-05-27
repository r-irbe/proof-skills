In finite dimensions, every linear map T: ℝⁿ → ℝⁿ satisfies the rank-nullity theorem: dim(ker T) + dim(im T) = n, which follows because ℝⁿ splits as ker T ⊕ (ker T)⊥ and T restricted to (ker T)⊥ is injective.

To prove the analogous result for a closed, densely defined Fredholm operator T: X → Y between Banach spaces—namely that ind(T) = dim(ker T) - dim(coker T) is finite and stable—plan the proof as follows.

Step 1 (analogue of complement): Use the closed range theorem and the fact that ker T is finite-dimensional to produce a closed complement X = ker T ⊕ X₁ (finite-dimensional subspaces are always complemented).

Step 2 (analogue of restriction being bijective): T|_{X₁}: X₁ → im T is a continuous bijection between Banach spaces; by the open mapping theorem it has a bounded inverse, so im T is closed, giving the exact analogue of the finite-dimensional isomorphism.

Step 3 (analogue of rank-nullity): Write Y = im T ⊕ Y₁ where dim Y₁ = dim coker T < ∞ (again, finite-dimensional subspaces complement), so X ≅ ker T ⊕ X₁ and Y ≅ im T ⊕ Y₁, and the index is the "signed dimension surplus" dim ker T - dim Y₁.

Step 4 (stability): Perturb T by a compact operator K; in finite dimensions adding any operator preserves rank-nullity up to exact cancellation, and here the same holds because K maps the unit ball to a precompact set, so K|_{X₁} cannot "fill" the cokernel asymptotically—formalize via the fact that (T+K)|_{X₁} is still Fredholm by Atkinson's theorem.

The guiding analogy is: finite rank ↔ compact, basis ↔ Schauder basis/Hahn-Banach selection, and the open mapping theorem replaces the trivially-true invertibility of a square matrix restricted to its row space.