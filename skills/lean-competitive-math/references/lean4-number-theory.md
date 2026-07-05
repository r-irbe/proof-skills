# Lean 4 Number Theory -- Euler / Competition Handbook

> Concise map of the Mathlib facilities most useful for Project-Euler and
> competition-math formalization, plus the Bronze/Silver/Gold tactic ladder and
> the `native_decide` trust note. Project-agnostic. Handbook for the
> `lean-competitive-math` (euler-prover) skill; pair with
> [`../../../references/lean4-tactic-hierarchy.md`](../../../references/lean4-tactic-hierarchy.md)
> and [`../../../references/lean4-proof-strategy.md`](../../../references/lean4-proof-strategy.md).

All Lean identifiers below are written in ASCII function-application form. Where
Mathlib also ships a Unicode notation (big-operator sum, the divides bar, the
`phi` / `sigma` letters, the factorial bang), the notation is named in words and
the ASCII identifier is given so the material stays ASCII-clean. Verify every
symbol exists at your Mathlib pin before relying on it -- names drift between
releases (see `@lean-research`).

---

## 1. Core facilities

| Facility | ASCII form / signature | What it gives you | Key lemmas (spot-check at your pin) |
|---|---|---|---|
| Primality | `Nat.Prime p : Prop` | Decidable primality of a `Nat`. `Nat.decidablePrime` makes `decide`/`native_decide` work; `Nat.minFac` finds the least factor. | `Nat.Prime.two_le`, `Nat.prime_def_lt`, `Nat.Prime.eq_one_or_self_of_dvd`, `Nat.exists_infinite_primes` |
| GCD / LCM | `Nat.gcd a b`, `Nat.lcm a b` | Greatest common divisor / least common multiple (both computable). | `Nat.gcd_dvd_left`, `Nat.gcd_comm`, `Nat.gcd_mul_lcm`, `Nat.Coprime` (defined as `Nat.gcd a b = 1`) |
| Coprimality | `Nat.Coprime a b : Prop` | `gcd a b = 1`; the workhorse for CRT / multiplicative arguments. | `Nat.Coprime.eq_one_of_dvd`, `Nat.Coprime.mul`, `Nat.Coprime.pow` |
| Divisors | `Nat.divisors n : Finset Nat` | The finite set of positive divisors of `n` (empty for `n = 0`). `Nat.properDivisors n` excludes `n`. | `Nat.mem_divisors`, `Nat.sum_divisors_eq_sum_properDivisors_add_self`, `Nat.divisors_prime_pow` |
| Divisor sums | `Nat.ArithmeticFunction.sigma k n` | The divisor-power sum (capital-sigma). `sigma 0 n` = number of divisors; `sigma 1 n` = sum of divisors. Perfect / abundant / deficient tests live here. | `Nat.ArithmeticFunction.sigma_apply`, `Nat.ArithmeticFunction.sigma_one_apply`, `Nat.ArithmeticFunction.isMultiplicative_sigma` |
| Totient | `Nat.totient n` | Euler `phi`: the count of `k < n` coprime to `n`. | `Nat.totient_prime`, `Nat.totient_mul` (coprime args), `Nat.totient_eq_card_coprime`, `Nat.sum_totient` |
| Fibonacci | `Nat.fib n` | The Fibonacci sequence (`fib 0 = 0`, `fib 1 = 1`). | `Nat.fib_add_two`, `Nat.fib_pos`, `Nat.fib_coprime_fib_succ`, `Nat.fib_add_two_strictMono` |
| Factorial | `Nat.factorial n` | `n!` (Unicode bang notation `n !`). | `Nat.factorial_pos`, `Nat.factorial_dvd_factorial`, `Nat.factorial_lt`, `Nat.succ_mul_factorial` |
| Binomials | `Nat.choose n k` (`n.choose k`) | Binomial coefficient. | `Nat.choose_symm`, `Nat.succ_mul_choose_eq`, `Nat.sum_range_choose`, `Nat.choose_mul_factorial_le` |

### Divisibility

Divisibility is `Dvd.dvd a b` (Mathlib infix is the divides bar, `a | b` in
source). It is decidable on `Nat`, so finite divisibility questions fall to
`decide` / `native_decide`. Useful: `Nat.dvd_sub'`, `Nat.dvd_gcd`,
`Nat.Prime.dvd_mul`, `Nat.dvd_factorial`.

---

## 2. Finite enumeration (the Euler bread-and-butter)

Most Euler answers are a sum or a count over a bounded range with a predicate.

| Facility | ASCII form | Notes |
|---|---|---|
| Range | `Finset.range n` | `{0, 1, ..., n-1}` as a `Finset Nat`. |
| Filter | `Finset.filter p s` | Keep elements of `s` satisfying decidable `p`. |
| Sum | `Finset.sum s f` | Big-operator sum notation (capital sigma over `i` in `s`). Function form shown here for ASCII. |
| Product | `Finset.prod s f` | Big-operator product. |
| Card | `Finset.card s` | Count of elements. |
| Interval | `Finset.Icc a b`, `Finset.Ico a b` | Closed / half-open integer intervals (need the `LocallyFiniteOrder` instance). |

Canonical "sum over a filtered range" (ASCII, Mathlib):

```lean
-- Sum of i*i for even i in 0..99 (idiomatic Finset form; needs Mathlib).
def s : Nat := Finset.sum (Finset.filter (fun i => i % 2 == 0) (Finset.range 100))
                          (fun i => i * i)
```

The same thing with a core `List` (no Mathlib -- handy for a self-contained
sanity check or a template that must compile with just `lean`):

```lean
def s : Nat :=
  ((List.range 100).filter (fun i => i % 2 == 0)).foldl (fun acc i => acc + i * i) 0
```

Key rewriting lemmas when you leave enumeration for structure:
`Finset.sum_range_succ`, `Finset.sum_filter`, `Finset.sum_range_id`
(`sum of 0..n-1 = n*(n-1)/2`), `Gauss`-style `Finset.sum_range_id_mul_two`.

---

## 3. The Bronze / Silver / Gold tactic ladder

The defining Euler move is closing `theorem eulerN : answer = <KNOWN>`. There are
three rungs of increasing trust. Climb as far as is feasible (skill rule G-3).

| Rung | Tactic(s) | Trust surface | When it applies |
|---|---|---|---|
| **Bronze** | `native_decide` | Compiler-trusted: adds a `native_decide` axiom (see Section 4). Fast; evaluates the compiled decision procedure. | First green proof; large enumerations where the kernel cannot reduce in time. |
| **Silver** | `decide`, `rfl`, `norm_num` | Kernel-checked: NO extra axioms. `decide` reduces the `Decidable` instance in the kernel; `rfl` uses definitional equality; `norm_num` for closed numeric goals. | Small enumerations, or once you have a cheap closed form. Kernel `decide` blows `maxRecDepth` on large ranges. |
| **Gold** | structural proof of a characterising property or closed form | Kernel-checked and general: the theorem no longer depends on brute evaluation. | The improvement target -- prove `answer = <closed form>` or a `..._spec` property, then discharge the numeral with `decide` / `norm_num`. |

Ladder guidance:

- Start Bronze to get GREEN, then improve. A permanent Bronze proof is only
  acceptable under the L3 carve-out (skill rule G-6): file a structural-proof
  follow-up, else `@lean-proof-review` L3 flags the one-tactic close.
- Silver often fails on raw Euler enumerations: kernel `decide` on a
  1000-element filtered range raises `maximum recursion depth has been reached`.
  Do NOT just crank `maxRecDepth` -- prefer a closed form.
- Gold is the honest endpoint: replace enumeration with a formula
  (inclusion-exclusion, triangular numbers, a multiplicative-function identity),
  prove the equivalence structurally, and the numeral falls to `decide` /
  `norm_num` with an empty axiom set.

See [`../../../references/lean4-tactic-hierarchy.md`](../../../references/lean4-tactic-hierarchy.md)
for the full tactic priority table (`decide` / `native_decide` sit at the
concrete-evaluation tier: "Prefer `decide` over `native_decide` for
kernel-checkability").

---

## 4. Trust note: what `native_decide` costs, and how to audit it

`native_decide` compiles and runs the decision procedure in native code, then
asserts the result as an axiom -- it does NOT re-check the computation in the
trusted kernel. That is why it is fast and why it is a strictly larger trust
surface than `decide`.

- The primitive is `Lean.ofReduceBool : forall (a b : Bool), Lean.reduceBool a = b -> a = b`,
  which itself depends on `[Lean.ofReduceBool, Lean.trustCompiler]`. In older
  Lean, `#print axioms` surfaced `Lean.trustCompiler` directly.
- In current Lean (verified on 4.30.0), `native_decide` instead emits a
  per-theorem generated axiom of the shape
  `<thm>._native.native_decide.ax_1_1 : decide (<prop>) = true`, which
  encapsulates that same compiler trust. (`Lean.reduceBool`, the old in-kernel
  path, is now deprecated with the message "assert native evaluations with
  axioms instead".)

**Always audit.** After the proof closes, run:

```lean
#print axioms eulerN
```

Interpretation:

- Bronze `native_decide` prints a `native_decide` axiom, e.g.
  `'eulerN' depends on axioms: [eulerN._native.native_decide.ax_1_1]`.
  Record this string in the file / review note (skill rule G-4).
- Silver / Gold prints either `does not depend on any axioms` or only the three
  standard axioms `[propext, Classical.choice, Quot.sound]`.
- Any `sorry` shows as `sorryAx` -- an automatic reject (skill rule G-5).

`@lean-enforcement`'s `axiom_audit.py` scans for exactly these markers; the
`@lean-proof-review` REFERENCE flags the compiler-trust axiom as a non-triviality
signal. The `lean-competitive-math` L3 carve-out (G-6) is the one place a
`native_decide` answer-check is allowed to pass review -- and only when a
structural follow-up is on file.

---

## 5. Verified micro-examples (Lean 4.30.0, core-only, ASCII)

Euler 1 -- sum of multiples of 3 or 5 below 1000; known answer `233168`.

```lean
-- Bronze: fast, compiler-trusted.
def answer : Nat :=
  ((List.range 1000).filter (fun n => n % 3 == 0 || n % 5 == 0)).foldl
    (fun acc n => acc + n) 0

#eval answer                                   -- 233168
theorem euler1 : answer = 233168 := by native_decide
#print axioms euler1
-- 'euler1' depends on axioms: [euler1._native.native_decide.ax_1_1]
```

```lean
-- Silver at this scale FAILS: kernel `decide` on 1000 elements ->
--   "maximum recursion depth has been reached".
-- Lesson: do not brute-force large enumerations in the kernel; go Gold.
```

```lean
-- Gold: inclusion-exclusion + triangular numbers T(k) = k*(k+1)/2.
--   multiples of 3 below 1000: 3*T(333); of 5: 5*T(199); of 15: 15*T(66).
def answer' : Nat := 3 * (333 * 334 / 2) + 5 * (199 * 200 / 2) - 15 * (66 * 67 / 2)

#eval answer'                                  -- 233168
theorem euler1_closed : answer' = 233168 := by decide
#print axioms euler1_closed
-- 'euler1_closed' does not depend on any axioms
```

The honest Gold endpoint additionally proves `answer = answer'` structurally
(reasoning about the filtered enumeration), which retires the `native_decide`
axiom from `euler1` entirely. Until that bridge lands, keep the Bronze `euler1`
AND file the follow-up (G-6).

---

## See also

- [`../../../references/lean4-tactic-hierarchy.md`](../../../references/lean4-tactic-hierarchy.md) -- full tactic priority table.
- [`../../../references/lean4-proof-strategy.md`](../../../references/lean4-proof-strategy.md) -- one-step-at-a-time proof strategy.
- [`../SKILL.md`](../SKILL.md) -- the `lean-competitive-math` (euler-prover) contract.
- [`../Template_Euler.md`](../Template_Euler.md) -- per-problem Lean file template.
