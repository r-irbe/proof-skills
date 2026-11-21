---
name: lean-asymptotic-algorithms-handbook
description: Reference handbook for classical mathematical and algorithmic breakthroughs (Subresultant PRS, Dulmage-Mendelsohn Permanent, Meissel-Lehmer Sieves, and Schedule Folding) in Lean 4.
extracted_from: skills/lean-asymptotic-algorithms/SKILL.md
---

# Classical Algorithmic Breakthroughs Handbook (Lean 4)

## Overview & Mathematical Literature Foundations

Algorithmic breakthroughs from classical mathematics provide asymptotic speedups that transcend low-level micro-optimizations. This handbook codifies four deep algorithmic paradigms:
1. **Subresultant Polynomial Remainder Sequences (PRS)** (Knuth *TAOCP* Vol 2 §4.6.1; Collins 1967; Brown & Traub 1971; Ducos 2000): Eliminates exponential coefficient growth in polynomial GCD and univariate polynomial discriminants.
2. **Dulmage-Mendelsohn Matrix Decomposition & Permanent Evaluation** (Dulmage & Mendelsohn 1958; Brualdi & Ryser 1991; Scott & Tůma 2023): Decomposes sparse 0-1 bipartite graphs into irreducible diagonal blocks, factoring permanent computation $\operatorname{perm}(A) = \prod \operatorname{perm}(A_i)$ and pruning non-matching edges.
3. **Dynamic Meissel-Lehmer & Möbius Hyperbola Sieves** (Deleglise & Rivat 1996; Lagarias, Miller, Odlyzko 1985; Helfgott & Thompson 2023): Computes prime counting $\pi(x)$ in $O(x^{2/3} \log^{-2} x)$ and Mertens function $M(x) = \sum_{k \le x} \mu(k)$ in $O(x^{2/3} \log^{1/3} x)$ dynamically, completely eliminating static seed lookup tables (`KERNEL-LAW-17`, `KERNEL-LAW-29`).
4. **Courtois-Naik-Song Hash Schedule Folding** (Courtois, Naik, Song 2014): Eliminates message schedule zero words and algebraically pre-fuses initial vectors in fixed-padding cryptographic sequences.

---

## 1. Subresultant Polynomial Remainder Sequences (Knuth TAOCP Vol 2 §4.6.1)

In Euclidean polynomial remainder sequences over $\mathbb{Z}[x]$, computing $R_{i+1} = \operatorname{prem}(R_{i-1}, R_i)$ causes exponential growth in the bit-length of coefficients: coefficients grow as $2^{2^k}$.

The subresultant algorithm divides the pseudo-remainder by a precisely chosen integer factor derived from Habicht's theorem:
$$R_{i+1} = \frac{\operatorname{prem}(R_{i-1}, R_i)}{-g_i \cdot h_i^{\delta_i}}$$
Where $\delta_i = \deg(R_{i-1}) - \deg(R_i)$, $g_i$ is the leading coefficient of $R_i$, and $h_i$ tracks the nominal subresultant scale factor:
$$h_i = \frac{g_i^{\delta_{i-1}}}{h_{i-1}^{\delta_{i-1} - 1}}$$

This division is **strictly exact over $\mathbb{Z}$**, bounding coefficient growth polynomially and allowing kernel-reducible polynomial discriminant evaluation without fractions.

---

## 2. Dulmage-Mendelsohn Decomposition for Matrix Permanents

Computing the permanent of an $n \times n$ matrix is $\#\mathbf{P}$-complete ($O(n 2^n)$ via Ryser/Glynn). For sparse 0-1 matrices:
1. **Edge Pruning**: Compute a maximum bipartite matching via Hopcroft-Karp. Any edge $(i, j)$ not belonging to any maximum matching contributes exactly zero to $\operatorname{perm}(A)$ and can be pruned immediately.
2. **Block Factorization**: The strongly connected components (SCCs) of the alternating graph partition the matrix into irreducible diagonal blocks $A_1, A_2, \dots, A_k$:
   $$\operatorname{perm}(A) = \prod_{i=1}^{k} \operatorname{perm}(A_i)$$
Evaluating $k$ smaller blocks of dimension $n_i < n$ yields exponential instruction-count reductions.

---

## 3. Dynamic Meissel-Lehmer & Möbius Sieves (Zero Static Tables)

To satisfy **Anti-Gating (`KERNEL-LAW-29`)** and eliminate static seed tables, prime counting $\pi(x)$ and Mertens sums $M(x)$ are computed dynamically:

### Legendre $\phi(x, a)$ Pruning
$$\phi(x, a) = \phi(x, a - 1) - \phi(x / p_a, a - 1)$$
With dynamic base-case pruning:
- If $a = 0$, $\phi(x, 0) = \lfloor x \rfloor$.
- If $x < p_a^2$, $\phi(x, a) = \pi(x) - a + 1$.

### Dynamic Wheel Sieve (mod 30)
Generates primes dynamically up to $\sqrt{x}$ using an 8-spoke wheel:
$$\text{Spokes} = \{1, 7, 11, 13, 17, 19, 23, 29\}$$
Consumes $O(\sqrt{x})$ space, achieving asymptotic scaling across all input regimes without precomputed tables.

---

## Canonical Lean 4 Implementation Exemplar

```lean
set_option autoImplicit false

namespace AsymptoticBreakthroughs

/-! ### 1. Subresultant PRS Scaling -/

/-- Exact integer division step for Subresultant PRS. -/
def subresultantStep (prem : Nat) (g h delta : Nat) : Nat :=
  let divisor := g * (h ^ delta)
  if divisor == 0 then 0 else prem / divisor

/-! ### 2. Dulmage-Mendelsohn Factorization -/

/-- Factors permanent across irreducible diagonal blocks. -/
def factorPermanent (blockPerms : List (Nat -> Nat)) (sizes : List Nat) : Nat :=
  blockPerms.zip sizes |>.foldl (fun acc (p, s) => acc * p s) 1

/-! ### 3. Dynamic Legendre Phi Tree with Pruning -/

def phiRec (x a : Nat) (primes : Nat -> Nat) (piTable : Nat -> Nat) : Nat :=
  match a with
  | 0 => x
  | a' + 1 =>
      let pa := primes a
      if x < pa * pa then
        piTable x - a + 1
      else
        phiRec x a' primes piTable - phiRec (x / pa) a' primes piTable

end AsymptoticBreakthroughs
```

---

## Goal-Shape Templates (templates)

| Goal Shape | Target Typeclass / Lemma | Proof Template |
| :--- | :--- | :--- |
| Univariate polynomial discriminant in `Int[x]` | `Subresultant PRS Algorithm` | `subresultantPRS p (deriv p) 1 1` |
| Sparse matrix permanent `perm(A)` | `Dulmage-Mendelsohn Factorization` | `perm(A) = prod (perm(A_i))` |
| Prime count `pi(x)` without seed tables | `Dynamic Meissel-Lehmer Tree` | `pi(x) = phi(x, a) + a - 1 - P2(x, a)` |
| Prefix sum of Mobius `M(x)` | `Deleglise-Rivat Hyperbola Sieve` | `M(x) = sum_{k <= u} mu(k) + dynamic_hyperbola` |
| Fixed padding hash schedule | `Courtois-Naik-Song Schedule Folding` | `w16 = sigma0(w1) + w0; fold_zero_words` |

## Intent-to-Tactic Phrasebook (phrasebook)

| Mathematical Intent | Lean 4 / Mathlib Tactic | Notes |
| :--- | :--- | :--- |
| Compute polynomial GCD without coefficient explosion | `Ducos Subresultant PRS` | Exactly divides pseudo-remainder by `g * h^delta` |
| Factor reducible sparse matrix | `Hopcroft-Karp + SCC decomposition` | Prunes non-matching zero-edges and factors permanent |
| Evaluate `phi(x, a)` dynamically | `Legendre tree with square-root cutoff` | Prunes branches when `x < p_a^2` to bound recursion depth |
| Fold zero-word message schedule | `Algebraic simplification` | Simplifies words `w_9..w_14 = 0` out of recurrence equations |

## Error-to-Fix Table (errors)

| Error / Symptom | Root Cause | Fix |
| :--- | :--- | :--- |
| Integer coefficient overflow in polynomial PRS | Standard Euclidean pseudo-division blows up coefficients | Divide by Collins-Brown-Traub factor `g * h^delta` on each step |
| Exponential state explosion in permanent | Dense evaluation of reducible matrix | Apply Dulmage-Mendelsohn decomposition to split into smaller diagonal blocks |
| Memory exhaustion in prime sieve | Static table or naive sieve allocates `O(x)` memory | Use segmented dynamic wheel sieve running in `O(sqrt(x))` space |
| Range-gated fallback triggered | Artificial contest band threshold | Replace band dispatch with single dynamic algorithm scaling for all `n` |
