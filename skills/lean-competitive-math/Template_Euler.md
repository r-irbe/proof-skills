# Template_Euler -- Project-Euler / competition-math Lean file

Per-problem template for the `lean-competitive-math` (euler-prover) skill. Copy it
to `EulerN.lean`, fill the four placeholders, get a GREEN Bronze proof, then climb
the trust ladder. Companion:
[`references/lean4-number-theory.md`](references/lean4-number-theory.md).

Placeholders to fill:

- `<N>`      -- the problem number (e.g. `1`).
- `<KNOWN>`  -- the known numeric answer from the problem source.
- `<ENCODING>` -- the Lean expression computing the answer.
- `<SPEC>`   -- (optional) a characterising property the answer must satisfy.

Anatomy (in order): `def answer` -> `#eval` sanity -> Bronze answer theorem ->
optional `_spec` -> optional closed form `answer'` + equivalence -> `main` ->
`#print axioms` audit.

## Improvement checklist (skill G-rules)

- [ ] `theorem eulerN : answer = <KNOWN>` pins the exact numeral (G-1).
- [ ] `#eval answer` prints `<KNOWN>` AND the theorem closes (G-2).
- [ ] `#print axioms eulerN` run and recorded (G-4).
- [ ] no `sorry` / `admit` anywhere (G-5).
- [ ] climbed Bronze -> Silver -> Gold as far as feasible (G-3).
- [ ] if a `native_decide` answer-check remains, a structural follow-up is filed
      so `@lean-proof-review` L3 passes it under the carve-out (G-6).

## References

* Handbook: [`references/lean4-number-theory.md`](references/lean4-number-theory.md)
* Tactic table: [`../../references/lean4-tactic-hierarchy.md`](../../references/lean4-tactic-hierarchy.md)
* mathlib4 docs: https://leanprover-community.github.io/mathlib4_docs/

## Tags

template, euler, competition-math, native_decide, decide, axioms, closed-form

---

## Generic skeleton

Self-contained (core `List`, no Mathlib) so it compiles with plain `lean`. For the
idiomatic Mathlib `Finset` form of `<ENCODING>` see the handbook Section 2.

```lean
/-
Copyright (c) <YEAR> <Project> Authors. Released under Apache 2.0.
-/

/-!
# EulerN -- <one-line problem statement>

Answer: <KNOWN>. Encoding: <describe the computation>.

## Reference
Project Euler problem <N> (or competition source + year).

## Tags
euler, problem-<N>, number-theory
-/

-- 1. The computed answer.
def answer : Nat := <ENCODING>

-- 2. Sanity: this must print <KNOWN>.
#eval answer

-- 3. Bronze answer-check (first GREEN proof; compiler-trusted).
theorem eulerN : answer = <KNOWN> := by native_decide

-- 4. (Optional) characterising property -- the Silver/Gold target.
--    Prove structurally; do NOT ship with `sorry`.
-- theorem eulerN_spec : <SPEC> := by
--   decide   -- or a structural proof

-- 5. (Optional) closed form + equivalence -- the Gold endpoint.
--    A closed form usually closes with `decide` / `norm_num` (no axioms);
--    the equivalence `answer = answer'` is the structural work that retires
--    the native_decide axiom from `eulerN`.
-- def answer' : Nat := <CLOSED_FORM>
-- theorem eulerN_closed : answer' = <KNOWN> := by decide
-- theorem answer_eq : answer = answer' := by
--   <structural proof>   -- Gold; then `eulerN` can be re-proved via this

-- 6. Runnable entry point.
def main : IO Unit := IO.println (toString answer)

-- 7. Trust audit (record the output in the file / review note, G-4).
#print axioms eulerN
```

---

## Minimal WORKING example -- Euler 1 (verified, Lean 4.30.0, core-only)

Sum of all multiples of 3 or 5 below 1000; known answer `233168`. Every line
below was compiled with `lean` (no Mathlib) and behaves as annotated.

```lean
/-!
# Euler1 -- multiples of 3 or 5 below 1000
Answer: 233168.
-/

-- 1-2. Computed answer + sanity.
def answer : Nat :=
  ((List.range 1000).filter (fun n => n % 3 == 0 || n % 5 == 0)).foldl
    (fun acc n => acc + n) 0

#eval answer   -- 233168

-- 3. Bronze: fast, compiler-trusted.
theorem euler1 : answer = 233168 := by native_decide

-- 5. Gold-style closed form via inclusion-exclusion + triangular numbers
--    T(k) = k*(k+1)/2 : 3*T(333) + 5*T(199) - 15*T(66).
def answer' : Nat := 3 * (333 * 334 / 2) + 5 * (199 * 200 / 2) - 15 * (66 * 67 / 2)

#eval answer'  -- 233168

-- The closed form is kernel-checked (Silver: no axioms).
theorem euler1_closed : answer' = 233168 := by decide

-- 6. Runnable.
def main : IO Unit := IO.println (toString answer)

-- 7. Audit.
#print axioms euler1
-- 'euler1' depends on axioms: [euler1._native.native_decide.ax_1_1]
#print axioms euler1_closed
-- 'euler1_closed' does not depend on any axioms
```

Notes tying back to the ladder (handbook Section 3):

- Bronze `euler1` (`native_decide`) is GREEN and carries the generated
  `native_decide` axiom -- fine as a first proof, but only permanent under the
  L3 carve-out with a follow-up filed (G-6).
- Kernel `decide` on the full 1000-element `answer` is NOT viable here: it raises
  `maximum recursion depth has been reached`. That is why the Gold path uses a
  closed form instead of brute kernel evaluation.
- The honest Gold finish additionally proves `answer = answer'` structurally,
  after which `euler1` can be re-proved with an EMPTY axiom set. Until then, keep
  Bronze `euler1` AND `euler1_closed`, and file the equivalence as the follow-up.
