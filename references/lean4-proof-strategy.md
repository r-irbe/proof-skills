# Lean 4 Proof Strategy

> Project-agnostic guide to writing, debugging, and cleaning up Lean 4 proofs.
> Distilled from working on a large formalization project. Pair with
> [`lean4-tactic-hierarchy.md`](./lean4-tactic-hierarchy.md) for tactic
> selection, and with [`mathlib4-conventions.md`](./mathlib4-conventions.md)
> for naming and style.

---

## 1. One Step at a Time

Write one tactic, check diagnostics (use `done` to see unsolved goals), repeat.
Never write multiple tactics before checking.

- `by sorry` is acceptable as a placeholder you are not actively working on.
- `done` is required when you expect further steps in an active proof.

## 2. Error Priority

Fix errors in this strict order — higher-priority errors make lower-priority
ones unreliable:

1. **Syntax errors**
2. **Type errors**
3. **Unsolved goals / tactic failures**
4. **Linter warnings**

"Unsolved goals" errors appear on `by` or `=>` lines, NOT where you add tactics.
If there is an "unsolved goals" on line 59 but a tactic error on line 65 — fix
line 65 **first**.

Stop writing tactics after any error. If you have an "unsolved goals" error,
do not add more tactics until you fix it. Same for type errors and syntax
errors.

## 3. Work on the Hardest Case First

**Across theorems:** Go directly to the target theorem. Do not fill in
`sorry`s in helper lemmas first — Lean treats `sorry` as an axiom, so dependent
theorems still work. If the main theorem fails, effort on helper lemmas is
wasted. If the main theorem succeeds, you can fill in the easier lemmas later.

**Within a proof:** Move `sorry`s earlier in the file by replacing a `sorry`
proof with references to simpler lemmas:

```lean
-- Before:
theorem main_theorem : A = C := by sorry

-- After:
theorem lemma1 : A = B := by sorry
theorem lemma2 : B = C := by sorry
theorem main_theorem : A = C := by rw [lemma1, lemma2]
```

**Within a proof case-split:** `sorry` the easy cases and work on the hardest
one first. If the hard case fails, effort on easy cases is wasted.

## 4. Proof Cleanup

After getting a proof to work, clean it up immediately:

- Combine redundant steps (`rw [a]; rw [b]` → `rw [a, b]`)
- Test if `simp` can handle more (remove earlier steps one by one)
- Find the truly minimal proof
- Replace `aesop?` / `grind?` with the script they suggest
- Replace named hypotheses with `_` if they are unused after cleanup

## 5. Dependent Type Rewriting Issues

When you encounter "motive is not type correct" or similar errors during
rewriting:

**The problem:** Rewriting a term `b` that appears in dependent types (like
`hab : a ≤ b`) fails because the motive cannot abstract over the dependencies.

**The solution — generalize first, instantiate last:**

```lean
suffices ∀ s, statement_about s by
  have h_specific := the_equality_you_have
  convert this ?_ <;> exact h_specific
intro s
-- Now prove the general statement for arbitrary s
```

## 6. Verification

Never declare a proof complete while `sorry` placeholders or error diagnostics
remain. Run `lake build` to confirm zero errors and zero warnings before
considering a module finished.

---

## 7. Common Patterns

### Nat Division and Modular Arithmetic

Scaled `Nat` arithmetic is common in formalization projects (e.g. probabilities
represented as `Nat / 100`). `Nat.div` truncates, so proofs about `(a * b) / c`
often need:

- `Nat.mul_div_cancel` (exact division)
- `Nat.div_le_div_right` (monotonicity)
- Explicit `have : c ∣ (a * b)` for divisibility prerequisites

### Simplex Proofs

Vectors on the simplex (`x + y + z = N`) appear in probability, game theory,
and resource allocation. Common pattern:

```lean
theorem foo (h : x + y + z = N) : ... := by
  have hz : z = N - x - y := by omega
  rw [hz]
  omega  -- or nlinarith for nonlinear goals
```

### Regime / Case Exhaustiveness

Classification proofs often require case splitting on all regimes:

```lean
match regime with
| .stable     => ...
| .transition => ...
| .chaotic    => ...
| .collapse   => ...
```

Use `decide` or `omega` to close each case when thresholds are concrete `Nat`
values.

### Real-Valued Contraction Proofs

For Banach-style contraction (Lyapunov stability, trust convergence), the
standard pattern:

```lean
theorem contraction (hα : 0 ≤ α) (hα1 : α < 1) :
    |f x - target| = α * |x - target| := by
  unfold f
  ring_nf
  rw [abs_mul, abs_of_nonneg hα]
```

Geometric decay follows by induction with `pow_le_pow_of_le_one`.

### Verified Derivatives (Catastrophe / Cusp Calculus)

Use Mathlib's `HasDerivAt` for verified derivatives:

```lean
theorem cusp_deriv (x a : ℝ) :
    HasDerivAt (fun x => x^4/4 + a*x^2/2) (x^3 + a*x) x := by
  have h1 := hasDerivAt_pow 4 x
  have h2 := hasDerivAt_pow 2 x
  ...
  convert ... using 1; ring
```

### Doc Comments with Brackets (CSLib Pitfall)

CSLib extends list literal syntax. Do **NOT** use `[` inside `/-- ... -/` doc
comments on `unsafe def` blocks. Use `--` line comments instead.

---

## 8. When Fixing Build Errors

Follow the error priority strictly: Syntax → Type → Unsolved goals → Linter.

Common fixes:

- `unknown identifier 'X'` — check if the prerequisite module is imported.
- `type mismatch ... expected Nat, got Int` — scaled-Nat projects usually avoid
  `Int` outside signed-arithmetic sections; pick a consistent representation
  and stick to it.
- `omega` fails on multiplication — extract the multiplicative step as a
  `have` proven with `nlinarith`/`linarith`, then use `omega` on the
  remaining linear goal.
- `linarith` fails on `Real` goals — ensure all hypotheses are in scope; try
  `nlinarith` for nonlinear terms; add `sq_nonneg` or `mul_self_nonneg`
  manually.
- Duplicate name — check `grep -n "theorem X" <lean-dir>/*.lean` before
  naming.
- "motive is not type correct" — see §5 (generalize first, instantiate last).
- "instance not found" — check for missing typeclass imports or for an
  instance that lives in a namespace you have not opened. Use
  `set_option trace.Meta.synthInstance true in` to diagnose.

---

## 9. Resource Lookups (When Stuck)

| Resource | URL | Use for |
|---|---|---|
| Loogle | <https://loogle.lean-lang.org/> | Search Mathlib by type signature |
| Mathlib Tactics index | <https://leanprover-community.github.io/mathlib4_docs/tactics.html> | Full tactic list with descriptions |
| Mathlib docs | <https://leanprover-community.github.io/mathlib4_docs/> | API documentation |
| Reservoir | <https://reservoir.lean-lang.org/> | Community packages |
| Lean Reference | <https://lean-lang.org/doc/reference/latest/> | Language reference |
| Zulip `lean4` stream | <https://leanprover.zulipchat.com/> | Live help from the community |

Inside a proof, also try `exact?`, `apply?`, `rw?`, `simp?`, `aesop?`,
`grind?` to discover relevant lemmas.

---

## 10. Workflow Checklist

When adding a new theorem:

1. Identify the source claim (paper, spec, requirement).
2. Add the definition/theorem in the appropriate module following the
   module's section numbering convention.
3. Build incrementally: `lake build <YourModule>`.
4. After the proof compiles, clean it up (see §4).
5. Run full build: `lake build` — must produce 0 errors.
6. Update any external metric documents (theorem counts, appendix tables).

When fixing build errors:

1. Sort error list by file location.
2. Apply the error-priority rule (§2) — never start on a low-priority error
   while a higher-priority one is unresolved.
3. After each fix, rebuild before adding more tactics.
