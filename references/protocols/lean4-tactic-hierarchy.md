# Lean 4 Unified Tactic Hierarchy (`v0.5.0` / Lean `v4.34.1`)

> Canonical priority order when choosing a tactic or superoptimizer for a Lean 4 goal.
> Project-agnostic. Pair with [`lean4-proof-strategy.md`](./lean4-proof-strategy.md) and [`../../templates/core/Template_AltProofTactics.md`](../../templates/core/Template_AltProofTactics.md).

When a goal is not immediately obvious, evaluate tactics in this deterministic cost-and-soundness order:
**`rfl` -> `bv_decide` / `decide +kernel` / `kernel_decide` / `norm_num` / `ring` -> `omega` / `linarith` / `nlinarith` / `positivity` -> `grind` / `eqsat_rw` -> `simp only [...]` -> `backchain` -> `aesop`**.

| Rung | Tactic / Term Macro | Domain & Guarantees |
|---:|---|---|
| 1 | `rfl` / `eval_nat%` / `preunfold%` / `swar_unroll%` | Zero-overhead definitional WHNF reduction and kernel compile-time term superoptimizers (`AltProof.Core`). |
| 2 | `bv_decide` / `decide +kernel` / `kernel_decide` | Kernel-verified finite bitvector and decidable propositions. **NEVER use `native_decide`** (`Lean.ofReduceBool` is banned by `GT-30/31`). |
| 3 | `norm_num` / `ring` / `field_simp` | Concrete numeric normalization, polynomial ring identities, and denominator clearing (`Q`/`R`). |
| 4 | `omega` / `linarith` / `positivity` / `nlinarith` | Domain-specific linear (`Nat`/`Int`/`Q`/`R`), sign (`0 <= e`, `0 < e`), and quadratic/Lyapunov arithmetic. |
| 5 | `grind` / `grind_close` / `eqsat_rw [rules]` (`egg_rw`) | E-graph congruence closure (`Lean 4.34.1` `grind`) and AltProof bounded equality-saturation bidirectional rewriting (`AltProof.Core`). |
| 6 | `simp only [lemmas]` / `sum_congr_ring` / `calc_ring_sum` / `finset_nonneg` / `finset_mono` / `gcongr_pos` | Explicit non-cyclic equational and `Finset.sum` congruence/monotonicity closers (`AltProof.Tactics`). |
| 7 | `backchain` / `contra_direct` | Bounded depth-first Core `MetaM` backward rule chaining (zero Mathlib dependency) and classical contraposition (`AltProof.Core`). |
| 8 | `aesop` / `alt_proof` / `elegance?` / `bfs_elegance?` | Best-first rule search and AltProof multi-route elegance/length superoptimization (`AltProof.Tactics`; replace `aesop?` with its explicit script). |

---

## Strict `native_decide` Ban (`GT-30` / `GT-31`)

`native_decide` compiles Lean expressions to native code outside the trusted kernel and injects `Lean.ofReduceBool` into `#print axioms`. Under `GUARDRAILS.md` (`GT-30/31`) and `lean-rules` (`rule-lean-no-native-decide`), `native_decide` is **banned in proof bodies**. Replace it with:
1. `rfl` paired with a `@[csimp]` computable twin (`Template_ComputableTwin_Csimp.md`),
2. `bv_decide` for fixed-width `BitVec` goals,
3. `decide +kernel` or `kernel_decide` (`first | rfl | decide +kernel | omega`), or
4. `norm_num` for concrete arithmetic constants.

---

## `@[grind]` Variant Quick Reference (Lean `v4.34.1`)

| Variant | When to use | Example |
|---------|-------------|---------|
| `@[grind =]` | Equational rewrites in congruence closure | `a * 0 = 0` |
| `@[grind ->]` | Forward implication trigger | `h : a <= b |- a / c <= b / c` |
| `@[grind <-]` | Backward goal-driven trigger | `|- v / 100 <= 1 <- h : v <= 100` |
| `@[grind norm]` | Normalization pre-processing | Canonical form simplification |
| `@[grind unfold]` | Eager unfolding in E-graph preprocessing | Transparent helper definition |

---

## Common Cast & Equality Saturation Patterns

| Pattern | Use case |
|---|---|
| `push_cast; ring` | `Nat -> Int` polynomial equalities |
| `eqsat_rw [h1, h2]` (`egg_rw`) | Bidirectional associative/commutative equality saturation up to fuel bound |
| `sum_congr_ring` / `calc_ring_sum` | Pointwise `Finset.sum` ring equalities |
| `zify [h_le]; omega` | Guarded `Nat.sub` to `Int` linear arithmetic |
| `nlinarith [sq_nonneg X, sq_nonneg Y]` | Nonlinear quadratic/Lyapunov bounds |

---

## Empirical Industrial Hierarchy (FLT 29,511-Theorem Census)

Telemetry across 29,511 theorems confirms that scalable Lean 4 libraries rely on monotonic forward context expansion and explicit rewrites:
1. `have` / `haveI` (89,669 uses)
2. `rw` / `rwa` (82,130 uses)
3. `exact` (45,244 uses)
4. `simp only` (25,758 uses)
5. `obtain` (19,704 uses)
6. `change` / `show` (8,889 uses)
7. `omega` / `linarith` / `ring` (7,821 uses)
