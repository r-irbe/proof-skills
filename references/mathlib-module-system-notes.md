# Mathlib module-system notes for porting proofs upstream

Learnings from porting normed-space / measure-theory lemmas to recent
Mathlib master (module system era). Each item cost a debugging round;
check them BEFORE porting, not after.

## 1. Notation does not propagate through non-public import links

Under the module system, syntax (notations) reaches a file only through
`public import` chains. A transitive semantic dependency is not enough:
if any link between your file and the notation's defining module is a
plain (non-public) import, the notation silently fails to parse
(`expected token` at the notation site).

**Rule**: a file using `‖x‖` needs `Mathlib.Analysis.Normed.Group.Basic`
in its own public imports even when every other import reaches it.
Probe missing-notation failures by importing the defining module
directly.

## 2. `Real`'s norm/abs instances are module-sealed

`‖x‖` (norm on `ℝ`) and `|x|` are not definitionally unifiable in files
outside the declaring module: the instances (`Real.instLE`, the norm
instance) do not delta-unfold ("definition is not exposed").  Consequences:

- `simpa`/`exact` cannot bridge `‖x‖ = |x|` even though
  `Real.norm_eq_abs` is `rfl`-class;
- corollaries that specialize a normed-space statement to `ℝ` must
  rewrite explicitly (`rw [Real.norm_eq_abs]`) inside a concretely
  typed `have`, not rely on defeq.

## 3. Positional application stops at an unassigned implicit binder

When the expected-type propagation leaves a later implicit binder
unassigned (e.g. `{n : ℕ}` feeding an `hn : 1 ≤ n` argument), positional
application fails with a pending-mvar mismatch.  Fix: pass the explicit
argument that determines the implicit (`... h' hn`), or annotate the
`have` with the full expected type so unification runs top-down.

## 4. Generated names are invisible to text search

`@[to_additive]` / `@[fun_prop]`-generated lemmas
(`Finset.measurable_sum` off `Finset.measurable_prod`) do not appear in
source grep.  Before concluding "mathlib lacks it", probe with
`#check @Name` on the additive/multiplicative twin.

## 5. Construct pointers (normed-space / measure-theory porting)

| Need | Construct |
|---|---|
| E-valued squeeze: `‖f n‖ ≤ a n → a n → 0 → f n → 0` | `squeeze_zero_norm'` (`Mathlib.Analysis.Normed.Group.Continuity`) |
| finite sums of measurables | `Finset.measurable_sum` (to_additive off `measurable_prod`) |
| scalar-action measurability | `Measurable.const_smul` (`[MeasurableConstSMul M X]`) |
| affine-contraction lemmas | none upstream (as of 2026-10) — `IsContractingWith`-shaped statements are open |
| geometric finite-sum bound | `geom_sum_mul_neg` (no direct `geom_range_le`) |

## 6. Header linter conventions

- Module docstring (`/-! ... -/`) must come BEFORE
  `@[expose] public section`.
- Unused `simp` arguments are linted; drop them.
- `set_option autoImplicit false` remains mandatory in ported files.
