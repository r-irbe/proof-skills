# Lean 4 Tactic Hierarchy

> Recommended priority order when choosing a tactic for an unfamiliar goal.
> Project-agnostic. Pair with [`lean4-proof-strategy.md`](./lean4-proof-strategy.md).

When a goal is not immediately obvious, try tactics in this priority order.
Faster tactics first; specialized closers before general search.

| # | Tactic | When to use |
|---|---|---|
| 1 | `grind` | Mixed goals: LIA + equality + ring + case-splitting. Subsumes a large fraction of `omega` and `linarith` calls. Use `grind?` to get a reproducible script. |
| 2 | `omega` | Pure Nat/Int linear arithmetic (simplex bounds, threshold comparisons). Faster than `grind` for single-domain goals. |
| 3 | `norm_num` | Concrete numeric evaluation (`(100 : ℝ) > 0`, `200/100 = 2`). |
| 4 | `simp only [lemmas]` | Definitional unfolding, named lemma rewrites. Prefer `simp only` over bare `simp` in finished proofs. |
| 5 | `nlinarith [sq_nonneg ...]` | Nonlinear ℝ arithmetic (Lyapunov bounds, contraction rates). `grind` does NOT replace this. |
| 6 | `linarith` | Simple ℝ/ℚ linear arithmetic (convex combinations, rate bounds). Keep where `grind` is overkill. |
| 7 | `ring` | Polynomial identities. |
| 8 | `positivity` | Goals of form `0 ≤ e` or `0 < e`. Often replaces small `nlinarith` calls. |
| 9 | `field_simp` | Clearing denominators in division proofs. Essential for ℚ/ℝ. |
| 10 | `decide` / `native_decide` | Concrete finite evaluations (enum cases, small computations). NOT replaceable by `grind`. Prefer `decide` over `native_decide` for kernel-checkability. |
| 11 | `convert ... using N` | When goals match up to Nat→Int cast placement. Follow with `push_cast; omega`. |
| 12 | `push_cast` / `norm_cast` / `zify` | Cast normalization: `↑(a-b:Nat) → ↑a-↑b` (needs subtraction bound). |
| 13 | `aesop` | General-purpose (last resort — slow on large goals). Use `aesop?` to get a script. |

**Principle:** always try the fastest tactic first. Use `grind` as the primary
general-purpose tactic; reach for `omega` / `linarith` / `nlinarith` only when
`grind` does not close the goal.

---

## `@[grind]` Variant Quick Reference

| Variant | When to use | Example |
|---------|-------------|---------|
| `@[grind =]` | Equational rewrites (like `@[simp]` for grind) | `a * 0 = 0` |
| `@[grind →]` | Forward implication: if P holds, add Q | `h : a ≤ b ⊢ a / c ≤ b / c` |
| `@[grind ←]` | Backward from conclusion | `⊢ v / 100 ≤ 1 ← h : v ≤ 100` |
| `@[grind norm]` | Normalization pre-processing (v4.28+) | Canonical form simplification |
| `@[grind unfold]` | Always unfold in preprocessing (v4.28+) | Transparent definition |

**v4.28 features:** `register_grind_attr`, `grind_pattern`, `grind +locals`,
`grind +suggestions`.

> **Note on `first_par`:** the parser exists in Lean v4.28.0 but the tactic
> is **NOT YET IMPLEMENTED** — it errors with "has not been implemented".
> Use sequential `first | tac1 | tac2 | tac3` until a future Lean version
> enables it.

---

## Common Cast Patterns

| Pattern | Use case |
|---|---|
| `push_cast; ring` | Nat→Int equalities (unfold `set` vars with `rw [hX_def]` first) |
| `convert h using N <;> push_cast <;> omega` | Cast-placement mismatches |
| `zify [bound]; simp only [Int.abs_eq_natAbs]; linarith` | natAbs→Int bridging |
| `le_div_iff₀; exact_mod_cast` | `Int.ediv → ℝ.div` bridging |
| `nlinarith [sq_nonneg X, sq_nonneg Y]` | Quadratic Lyapunov bounds |

---

## When You Should Reach for `aesop`/`grind` vs Manual Steps

- Prefer manual steps when:
  - The proof structure is illustrative (textbook proof, paper §X.Y).
  - You are debugging — a manual proof has a known shape.
  - You want a small, reviewable proof term.

- Reach for `aesop`/`grind` when:
  - The goal is purely "obvious from the available hypotheses".
  - You have a strong `@[simp]` / `@[grind]` set in scope.
  - You will save the suggested script (`aesop?` / `grind?`) and replace the
    search call with the explicit tactics.
