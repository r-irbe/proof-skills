Given theorem: "For all integers n > 1, if n is not divisible by any prime p ≤ √n, then n is prime."

**Preconditions (hypotheses):**
1. n ∈ ℤ, n > 1
2. ∀ prime p: p ≤ √n → p ∤ n

**Conclusion:**
n is prime (n has no divisors other than 1 and itself).

**Traceability anchor:**
`THM-PRIMALITY-TRIAL-DIVISION-001` — links this statement to its proof obligation in a verification artifact (e.g., Coq lemma `prime_of_no_small_factor`, Isabelle/HOL `prime_nat_iff`, or a requirements doc section §3.2.1). The anchor is a stable, unique identifier that survives refactoring, maps the theorem to upstream requirements (e.g., REQ-CRYPTO-42), downstream proofs, and any dependent lemmas, enabling full bidirectional traceability in a formal verification or safety assurance context.