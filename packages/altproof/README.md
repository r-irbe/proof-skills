# AltProof -- Speculative Alternative-Proof & Elegance Meta-Tactics for Lean 4

`AltProof` is a standalone Lean 4 + Mathlib4 meta-tactic package and AST feature-guided
route explorer from [`proof-skills`](https://github.com/r-irbe/proof-skills). It provides:

1. **Goal AST & Local Context Feature Detector (`GoalFeatures`, `extractGoalFeatures`)**:
   Inspects the active `MVarId` target `Expr` and non-implementation local context
   declarations to classify `Finset.sum`, `abs`/`norm`/`dist`, `ite`/`dite`/`decide`,
   negation/contradiction, `Nat`/`Int` arithmetic, `WellFounded.fix`, and `BitVec` shapes.
2. **Two-Axis Cost Ranker (`computeCostX10`, `TwoAxisScore`)**:
   Combines the B1 `extraction-outranks` reader-elegance metric with machine-side
   kernel/elaborator heartbeat cost (`IO.getNumHeartbeats`).
3. **Finite-Sum & Automated Reduction Tactics (`sum_congr_ring`, `finset_nonneg`, `finset_mono`, `alt_proof`)**:
   One-step normalization and pointwise discharge for `Finset.sum` linear combinations,
   non-negativity, monotonicity, and standard arithmetic/algebraic goals.
4. **Speculative In-Kernel Route & BFS Explorer (`elegance?`, `bfs_elegance?`)**:
   Filters the 11-route table (`routeTable`) by `GoalFeatures` relevance, probes single-step
   and bounded depth-`<= 3` Best-First Search (`tryBfsCandidateClosers`) closers inside
   `withoutModifyingState`, ranks succeeding closers by `computeCostX10`, and emits
   clickable `TryThis.addSuggestion` code actions.

---

## Installation

### Option 1: Lake Git Dependency (Subdirectory)

Add `altproof` to your `lakefile.lean`:

```lean
require altproof from git
  "https://github.com/r-irbe/proof-skills.git" @ "main" / "packages/altproof"
```

Or in `lakefile.toml`:

```toml
[[require]]
name = "altproof"
git = "https://github.com/r-irbe/proof-skills.git"
rev = "main"
subDir = "packages/altproof"
```

Then import and open the tactics in your Lean 4 files:

```lean
import AltProof

open AltProof
-- or `open AltProof.Tactics`
```

### Option 2: Direct Single-File Copy (Vendor-In)

`AltProof/Tactics.lean` is self-contained (requiring only `Mathlib.Tactic`,
`Mathlib.Algebra.BigOperators.Group.Finset.Basic`, and
`Mathlib.Algebra.BigOperators.Ring.Finset`). You can copy
`packages/altproof/AltProof/Tactics.lean` directly into your project tree.

---

## Tactic Reference Table

| Tactic | Purpose | Primary Mechanism |
| :--- | :--- | :--- |
| `sum_congr_ring` | Normalizes `Finset.sum` linear combinations (`a * sum f +/- b * sum g`) and closes pointwise ring equalities. | `Finset.sum_add_distrib`, `Finset.sum_sub_distrib`, `Finset.mul_sum`, `Finset.sum_mul`, and `Finset.sum_congr rfl (fun _ _ => by ring)`. |
| `finset_nonneg` | Discharges `0 <= sum i in s, f i` (including nested double sums). | `Finset.sum_nonneg` + `specializePointwiseHyps` + `positivity`, `linarith`, `nlinarith`, `omega`, `solve_by_elim`, recursive `finset_nonneg`, or `aesop`. |
| `finset_mono` | Discharges `sum i in s, f i <= sum i in s, g i` (including nested double sums). | `Finset.sum_le_sum` + `specializePointwiseHyps` + `linarith`, `nlinarith`, `omega`, `positivity`, `gcongr`, `solve_by_elim`, recursive `finset_mono`, or `aesop`. |
| `alt_proof` | Automated fast reduction cascade across decidable, Presburger, ring, and finite-sum goals. | Ordered `first` cascade: `rfl`, `assumption`, `bv_decide`, `decide`, `omega`, `ring`, `sum_congr_ring`, `finset_nonneg`, `finset_mono`, `positivity`, `linarith`, `nlinarith`, `norm_num`, `aesop`. |
| `elegance?` | Speculative AST-guided route advisor and single-step + depth-`<= 3` BFS closer probe. | Extracts `GoalFeatures`, filters `routeTable`, probes candidates in `withoutModifyingState` with `IO.getNumHeartbeats`, and emits `TryThis.addSuggestion`. |
| `bfs_elegance?` | Explicit bounded depth-`<= 3` in-kernel Best-First Search (`Proposal 9C`). | Probes structural decomposition prefixes (`intros; alt_proof`, `constructor <;> alt_proof`, `push_neg; alt_proof`, `intros; sum_congr_ring`) in `withoutModifyingState`. |

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
