# AltProof -- Three-Layer Equality Saturation, Domain Closers, SAIR Superoptimizers, and Elegance Meta-Tactics

`AltProof` is a three-layer Lean 4 meta-tactic, production proof-closer, and compile-time superoptimization library shipped inside [`proof-skills`](https://github.com/r-irbe/proof-skills) until standalone external package promotion is warranted:

- **Layer 1 (`AltProof.Core` -- `import Lean` only, 0 Mathlib, 0 Rust FFI)**:
  - **20-Route Advisor & Two-Axis Cost Ranker** (`routeTable`, `GoalFeatures`, `computeCostX10`).
  - **`eqsat_rw` / `egg_rw`**: Pure-Lean bidirectional equality & congruence saturation (`congrArg`, `congrFun`, `Eq.trans`, `Eq.symm`) in `MetaM` reconstructing kernel-checked proof terms with `[propext, Classical.choice, Quot.sound]` hygiene and zero Cargo/FFI dependencies.
  - **`backchain`**: Curated bounded depth-first backchaining wrapper over core Lean's `Lean.Elab.Tactic.SolveByElim` (`solve_by_elim`).
  - **`grind_close`**: Bounded e-graph congruence closure and E-matching closer backed by core Lean's `grind`.
  - **`contra_direct`**: Constructive negation, `Bool`, and `Decidable` normalizer eliminating `Classical.choice` leakage from `split`/`by_cases`.
  - **`sair_decide`**: Strict 3-rung kernel-clean decision macro (`rfl | decide +kernel | omega`) with zero `Lean.ofReduceBool`.
  - **`eval_nat%`, `preunfold%`, `swar_unroll%`**: SAIR elaboration-time superoptimizers folding closed `Nat`/`Bool` subterms to raw `Expr.lit (.natVal v)` (`nat_lit`), unrolling static trip-count loops, and hash-consing DAGs via `Lean.ShareCommon.shareCommon` with zero `Lean.*` constants in exported terms.
- **Layer 2 (`AltProof.Closers` -- Production-Safe Mathlib4 Closers & Bridge Lemmas)**:
  - Lightweight, self-contained proof closers safe for production formalizations and standalone paper supplements (zero interactive advisor or route-table overhead):
  - **`sum_congr_ring` & `calc_ring_sum`**: One-step `Finset.sum` linear combination, separable double-sum factorization, swapped double-sum (`Finset.sum_comm`), and pointwise ring congruence closers.
  - **`finset_nonneg`, `finset_mono`, & `gcongr_pos`**: Automated `Finset.sum` non-negativity, monotonicity, and structural `gcongr` side-goal closers with universal hypothesis specialization (`specializePointwiseHyps`).
  - **`convex_comb`, `markov_row_sum`, & `matrix_pos`**: Convex-combination / simplex bounds, row-stochastic Markov kernel & Laplacian zero-row-sum normalization, and entrywise matrix non-negativity/positivity closers.
  - **`sup_norm_scale` & `deriv_quot_ring`**: Positive-homogeneous `Finset.sup'` scaling (`sup'_const_mul_of_nonneg`) and denominator-clearing quotient derivative / simplex-ratio ring normalization.
  - **Reusable Domain Bridges**: `fin_card_filter_Ico` (`Fin N` half-open slice cardinality), `natAbs_le_div_of_cast_abs_le` (`Int.natAbs` floor-division bound from real `|.|` inequality), and `zero_sum_vecMul_l1_le_of_entry_floor` (quantitative Doeblin entry-floor $\ell^1$ contraction on zero-sum vectors).
- **Layer 3 (`AltProof.Tactics` -- Speculative `alt_proof`, `elegance?`, & `bfs_elegance?` Explorers)**:
  - **`alt_proof`, `elegance?`, & `bfs_elegance?`**: Speculative `withoutModifyingState` closer cascade (including `grind_close`, `simp_all`, `norm_cast`, `push_cast; ring`, `field_simp; ring`, and all `AltProof.Closers`) and depth-`<= 3` Best-First Search emitting `TryThis.addSuggestion` code actions ranked by `IO.getNumHeartbeats` and `computeCostX10`.
  - **Goal scope**: `elegance?` and `bfs_elegance?` test whether a tactic closes the active goal and every subgoal it creates. The probes restore the caller's proof state. With sibling goals open, the suggested replacement uses `focus` to replay in the same scope.
  - **Continuous Tooling Rule**: During proving campaigns, harvest recurring multi-line algebraic, sum, norm, cast, or finite-domain proof patterns into `AltProof.Closers` and wire them into `elegance?` so every campaign leaves the shared closer library stronger.

---

## Installation

### Option 1: Lake Git Dependency (Subdirectory)

Add `altproof` to your `lakefile.lean` (pinned to Lean `v4.34.1`):

```lean
require altproof from git
  "https://github.com/r-irbe/proof-skills.git" @ "v0.5.0" / "packages/altproof"
```

Or in `lakefile.toml`:

```toml
[[require]]
name = "altproof"
git = "https://github.com/r-irbe/proof-skills.git"
rev = "v0.5.0"
subDir = "packages/altproof"
```

Then import either `AltProof.Core` (zero-Mathlib projects) or `AltProof` (full Mathlib projects):

```lean
import AltProof

open AltProof.Core AltProof.Tactics
```

### Option 2: Direct Single-File Copy (Core-Only or Mathlib)

- Copy `packages/altproof/AltProof/Core.lean` into any core-only (`import Lean`) project.
- Copy `templates/core/examples/Template_AltProofTactics.lean` for a single-file Mathlib4 drop-in.

---

## Tactic & Elaborator Reference Table

| Tactic / Elaborator | Layer | Purpose | Primary Mechanism |
| :--- | :--- | :--- | :--- |
| `eqsat_rw` / `egg_rw` | `Core` | Bidirectional equational & congruence saturation where `simp` loops or stalls. | Meet-in-the-middle `MetaM` saturation (`congrArg`, `congrFun`, `Eq.trans`, `Eq.symm`) (3-axiom clean). |
| `eqsat_rw_sair` / `eqsat_rw_kernel` | `Core` | Contest-safe (`no-grind`, 3-axiom) equational congruence closer. | Strictly pure-Lean `eqsat_rw` without invoking `grind` or `Lean.ofReduceBool`. |
| `backchain` | `Core` | Bounded Horn-clause / implication / conjunction backchaining without `aesop`. | `Lean.Elab.Tactic.SolveByElim` (`solve_by_elim (maxDepth := 6)`). |
| `grind_close` | `Core` | Core e-graph congruence closure & E-matching closer. | `(grind; done)` with optional `[params]`. |
| `contra_direct` | `Core` | Constructive boolean/negation normalizer avoiding `Classical.choice`. | `Bool.and_eq_true`, `decide_eq_true_eq`, `absurd` + `decide +kernel` / `omega`. |
| `sair_decide` | `Core` | 3-axiom contest-clean decidable/Presburger closer (`0` `Lean.ofReduceBool`). | `first \| rfl \| decide +kernel \| omega`. |
| `eval_nat% t` | `Core` | Compile-time closed `Nat` constant folding to raw `nat_lit`. | Pure `MetaM` evaluator emitting `mkRawNatLit v` (`0` `Lean.*` exports). |
| `preunfold% [d, ...] t` | `Core` | Compile-time helper unfolding, closed-branch pruning, and DAG sharing. | Beta/zeta/proj reduction + `Bool.rec` pruning + `ShareCommon.shareCommon`. |
| `swar_unroll% k b s` | `Core` | Compile-time static loop unrolling (`0 .. k-1`) for SWAR kernels. | Iterated `preunfoldExprWith` + `ShareCommon.shareCommon`. |
| `sum_congr_ring` | `Closers` | Normalizes `Finset.sum` linear combinations and pointwise ring equalities. | `Finset.sum_add_distrib`, `sum_sub_distrib`, `mul_sum`, `sum_mul`, `Finset.sum_congr`. |
| `calc_ring_sum` | `Closers` | Multi-step swapped double-sum (`Finset.sum_comm`) and scalar ring closer. | `Finset.sum_comm` + `sum_congr_ring` + `ring`. |
| `finset_nonneg` | `Closers` | Discharges `0 <= sum i in s, f i` (including nested double sums). | `Finset.sum_nonneg` + `specializePointwiseHyps` + `positivity`/`linarith`/`solve_by_elim`. |
| `finset_mono` | `Closers` | Discharges `sum i in s, f i <= sum i in s, g i` (including nested double sums). | `Finset.sum_le_sum` + `specializePointwiseHyps` + `gcongr_pos`/`linarith`/`solve_by_elim`. |
| `convex_comb` | `Closers` | Discharges convex-combination, affine-interpolation, and simplex bounds. | Conjunction unpacking + pairwise non-negative product synthesis + `nlinarith`/`ring`. |
| `markov_row_sum` | `Closers` | Discharges row-stochastic Markov kernel & Laplacian zero-row-sum identities. | `Matrix.vecMul`/`mulVec` unfolding + `Finset.sum_comm` + row-sum rewriting + `sum_congr_ring`. |
| `matrix_pos` | `Closers` | Discharges entrywise non-negativity/positivity of kernels and `Fin n` matrices. | `positivity` + `finset_nonneg` + `fin_cases` concrete fallback. |
| `sup_norm_scale` | `Closers` | Pulls `c >= 0` out of `Finset.sup'` and closes sup-norm scaling bounds. | `sup'_const_mul_of_nonneg` + `ring`/`linarith`/`gcongr_pos`. |
| `deriv_quot_ring` | `Closers` | Clears nonzero denominators in quotient derivative and simplex-ratio goals. | `div_add_div_same`/`div_sub_div_same` + `field_simp` + `ring`. |
| `gcongr_pos` | `Closers` | Structural monotonicity congruence closing positivity/linear side-goals. | `gcongr <;> first \| rfl \| assumption \| positivity \| linarith \| nlinarith \| omega`. |
| `alt_proof` | `Tactics` | Automated 24-step fast reduction cascade across core and Mathlib goals. | Ordered `first` cascade from `rfl` through `AltProof.Closers`, `eqsat_rw`, `backchain`, `aesop`. |
| `elegance?` / `bfs_elegance?` | `Tactics` | Speculative AST-guided 20-route advisor + depth-`<= 3` BFS explorer. | `withoutModifyingState` + `IO.getNumHeartbeats` + `computeCostX10` / `computeTwoAxisCostX10` + `TryThis.addSuggestion`. |
| `sair_elegance?` / `kernel_elegance?` | `Tactics` | 3-axiom contest-safe (`no-grind`) speculative closer advisor. | Filters out `grind_close`/`bv_decide`/`native_decide`; ranks `kernel_decide`, `eqsat_rw_sair`, and `AltProof.Closers`. |

---

## Python Companion CLI (`lean-altproof`)

The companion zero-dependency Python analysis package lives in `scripts/lean/altproof/`:

```bash
pip install -e scripts/lean/altproof
altproof routes
altproof detect-v4 path/to/File.lean
altproof dispatch --goal "|- 0 <= Finset.sum s (fun i => (f i)^2)"
altproof tree-shake MyProject.Concordance --output-dir /tmp/supplement --anonymize --verify-build --markdown
```

## License

Apache-2.0
