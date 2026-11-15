# AltProof v0.5.0 -- Equality Saturation, Core SolveByElim, SAIR Superoptimizers, and Elegance Meta-Tactics

`AltProof` (`v0.5.0`) is a two-layer Lean 4 meta-tactic and compile-time superoptimization package from [`proof-skills`](https://github.com/r-irbe/proof-skills):

- **Layer 1 (`AltProof.Core` -- `import Lean` only, 0 Mathlib, 0 Rust FFI)**:
  - **20-Route Advisor & Two-Axis Cost Ranker** (`routeTable`, `GoalFeatures`, `computeCostX10`).
  - **`eqsat_rw` / `egg_rw`**: Pure-Lean bidirectional equality & congruence saturation (`congrArg`, `congrFun`, `Eq.trans`, `Eq.symm`) in `MetaM` reconstructing kernel-checked proof terms with `[propext, Classical.choice, Quot.sound]` hygiene and zero Cargo/FFI dependencies.
  - **`backchain`**: Curated bounded depth-first backchaining wrapper over core Lean's `Lean.Elab.Tactic.SolveByElim` (`solve_by_elim`).
  - **`grind_close`**: Bounded e-graph congruence closure and E-matching closer backed by core Lean's `grind`.
  - **`contra_direct`**: Constructive negation, `Bool`, and `Decidable` normalizer eliminating `Classical.choice` leakage from `split`/`by_cases`.
  - **`sair_decide`**: Strict 3-rung kernel-clean decision macro (`rfl | decide +kernel | omega`) with zero `Lean.ofReduceBool`.
  - **`eval_nat%`, `preunfold%`, `swar_unroll%`**: SAIR elaboration-time superoptimizers folding closed `Nat`/`Bool` subterms to raw `Expr.lit (.natVal v)` (`nat_lit`), unrolling static trip-count loops, and hash-consing DAGs via `Lean.ShareCommon.shareCommon` with zero `Lean.*` constants in exported terms.
- **Layer 2 (`AltProof.Tactics` -- Mathlib4 BigOperators & Speculative Search)**:
  - **`sum_congr_ring` & `calc_ring_sum`**: One-step `Finset.sum` linear combination, double-sum commutation (`Finset.sum_comm`), and pointwise ring congruence closers.
  - **`finset_nonneg`, `finset_mono`, & `gcongr_pos`**: Automated `Finset.sum` non-negativity, monotonicity, and structural `gcongr` side-goal closers with universal hypothesis specialization (`specializePointwiseHyps`).
  - **`alt_proof`, `elegance?`, & `bfs_elegance?`**: Speculative `withoutModifyingState` closer cascade and depth-`<= 3` Best-First Search emitting `TryThis.addSuggestion` code actions ranked by `IO.getNumHeartbeats` and `computeCostX10`.

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
| `eqsat_rw` / `egg_rw` | `Core` | Bidirectional equational & congruence saturation where `simp` loops or stalls. | Meet-in-the-middle `MetaM` saturation (`congrArg`, `congrFun`, `Eq.trans`, `Eq.symm`) + `grind` fallback. |
| `backchain` | `Core` | Bounded Horn-clause / implication / conjunction backchaining without `aesop`. | `Lean.Elab.Tactic.SolveByElim` (`solve_by_elim (maxDepth := 6)`). |
| `grind_close` | `Core` | Core e-graph congruence closure & E-matching closer. | `(grind; done)` with optional `[params]`. |
| `contra_direct` | `Core` | Constructive boolean/negation normalizer avoiding `Classical.choice`. | `Bool.and_eq_true`, `decide_eq_true_eq`, `absurd` + `decide +kernel` / `omega`. |
| `sair_decide` | `Core` | 3-axiom contest-clean decidable/Presburger closer (`0` `Lean.ofReduceBool`). | `first \| rfl \| decide +kernel \| omega`. |
| `eval_nat% t` | `Core` | Compile-time closed `Nat` constant folding to raw `nat_lit`. | Pure `MetaM` evaluator emitting `mkRawNatLit v` (`0` `Lean.*` exports). |
| `preunfold% [d, ...] t` | `Core` | Compile-time helper unfolding, closed-branch pruning, and DAG sharing. | Beta/zeta/proj reduction + `Bool.rec` pruning + `ShareCommon.shareCommon`. |
| `swar_unroll% k b s` | `Core` | Compile-time static loop unrolling (`0 .. k-1`) for SWAR kernels. | Iterated `preunfoldExprWith` + `ShareCommon.shareCommon`. |
| `sum_congr_ring` | `Tactics` | Normalizes `Finset.sum` linear combinations and pointwise ring equalities. | `Finset.sum_add_distrib`, `sum_sub_distrib`, `mul_sum`, `sum_mul`, `Finset.sum_congr`. |
| `calc_ring_sum` | `Tactics` | Multi-step swapped double-sum (`Finset.sum_comm`) and scalar ring closer. | `Finset.sum_comm` + `sum_congr_ring` + `ring`. |
| `finset_nonneg` | `Tactics` | Discharges `0 <= sum i in s, f i` (including nested double sums). | `Finset.sum_nonneg` + `specializePointwiseHyps` + `positivity`/`linarith`/`solve_by_elim`. |
| `finset_mono` | `Tactics` | Discharges `sum i in s, f i <= sum i in s, g i` (including nested double sums). | `Finset.sum_le_sum` + `specializePointwiseHyps` + `gcongr_pos`/`linarith`/`solve_by_elim`. |
| `gcongr_pos` | `Tactics` | Structural monotonicity congruence closing positivity/linear side-goals. | `gcongr <;> first \| rfl \| assumption \| positivity \| linarith \| nlinarith \| omega`. |
| `alt_proof` | `Tactics` | Automated 20-step fast reduction cascade across core and Mathlib goals. | Ordered `first` cascade from `rfl` through `eqsat_rw`, `backchain`, `sum_congr_ring`, `grind_close`, `aesop`. |
| `elegance?` / `bfs_elegance?` | `Tactics` | Speculative AST-guided 20-route advisor + depth-`<= 3` BFS explorer. | `withoutModifyingState` + `IO.getNumHeartbeats` + `computeCostX10` + `TryThis.addSuggestion`. |

---

## Python Companion CLI (`lean-altproof`)

The companion zero-dependency Python analysis package lives in `scripts/lean/altproof/`:

```bash
pip install -e scripts/lean/altproof
altproof routes
altproof detect-v4 path/to/File.lean
altproof dispatch --goal "|- 0 <= Finset.sum s (fun i => (f i)^2)"
```

## License

Apache-2.0
