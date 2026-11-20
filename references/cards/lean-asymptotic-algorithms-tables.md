---
name: "lean-asymptotic-algorithms-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-asymptotic-algorithms-handbook.md."
generated_from: "references/handbooks/lean-asymptotic-algorithms-handbook.md"
skill_ref: "skills/lean-math-discrete/SKILL.md"
---

# `lean-asymptotic-algorithms` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-asymptotic-algorithms-handbook.md`](../handbooks/lean-asymptotic-algorithms-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Univariate polynomial discriminant in `Int[x]` | `Subresultant PRS Algorithm` | `subresultantPRS p (deriv p) 1 1` |
| Sparse matrix permanent `perm(A)` | `Dulmage-Mendelsohn Factorization` | `perm(A) = prod (perm(A_i))` |
| Prime count `pi(x)` without seed tables | `Dynamic Meissel-Lehmer Tree` | `pi(x) = phi(x, a) + a - 1 - P2(x, a)` |
| Prefix sum of Mobius `M(x)` | `Deleglise-Rivat Hyperbola Sieve` | `M(x) = sum_{k <= u} mu(k) + dynamic_hyperbola` |
| Fixed padding hash schedule | `Courtois-Naik-Song Schedule Folding` | `w16 = sigma0(w1) + w0; fold_zero_words` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Compute polynomial GCD without coefficient explosion | `Ducos Subresultant PRS` | Exactly divides pseudo-remainder by `g * h^delta` |
| Factor reducible sparse matrix | `Hopcroft-Karp + SCC decomposition` | Prunes non-matching zero-edges and factors permanent |
| Evaluate `phi(x, a)` dynamically | `Legendre tree with square-root cutoff` | Prunes branches when `x < p_a^2` to bound recursion depth |
| Fold zero-word message schedule | `Algebraic simplification` | Simplifies words `w_9..w_14 = 0` out of recurrence equations |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Integer coefficient overflow in polynomial PRS | Standard Euclidean pseudo-division blows up coefficients | Divide by Collins-Brown-Traub factor `g * h^delta` on each step |
| Exponential state explosion in permanent | Dense evaluation of reducible matrix | Apply Dulmage-Mendelsohn decomposition to split into smaller diagonal blocks |
| Memory exhaustion in prime sieve | Static table or naive sieve allocates `O(x)` memory | Use segmented dynamic wheel sieve running in `O(sqrt(x))` space |
| Range-gated fallback triggered | Artificial contest band threshold | Replace band dispatch with single dynamic algorithm scaling for all `n` |
