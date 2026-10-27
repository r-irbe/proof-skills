---
name: "lean-competitive-math-handbook"
description: "Reference handbook for @lean-competitive-math (Project Euler & Competition Math in Lean 4)."
extracted_from: "skills/lean-competitive-math/SKILL.md"
---

# lean-competitive-math (euler-prover)

> **MANDATORY** (hot-tier): the answer-check gate (G-2), the axiom audit (G-4),
> and the no-sorry gate (G-5) are hard gates. A `native_decide` answer-check is
> allowed ONLY as a Bronze rung that ships WITH a structural-proof follow-up
> filed (G-6) -- otherwise it is an ordinary one-tactic `decide` and
> `@lean-proof-review` L3 flags it. Skipping Persist = incomplete.

Formalize a Project-Euler / competition-math problem as a Lean 4 theorem that
pins the concrete numeric answer, prove it, VERIFY the answer computes, then
IMPROVE the proof up the trust ladder. This skill owns the move that trips the
generic review gate -- closing `theorem eulerN : answer = <KNOWN> := by
native_decide` -- and gives it a governed home with an explicit carve-out.

---

## Routing

- **USE FOR:** formalizing a Project-Euler / competition-math problem as a Lean 4
  theorem asserting a concrete numeric answer; getting a first green proof
  (typically Bronze `native_decide`); verifying the answer computes (`#eval` +
  the theorem closes); auditing the compiler-trust axiom via `#print axioms`;
  and driving the improvement pass up the ladder Bronze (`native_decide`) ->
  Silver (`decide` / `norm_num`) -> Gold (characterising property / closed form).
- **DO NOT USE FOR:** authoring the theorem statement alone (use `@lean-specification`);
  writing tactics one step at a time or triaging tactic errors (use `@lean-proof`);
  generic single-proof audit outside the carve-out (use `@lean-proof-review`);
  Mathlib API / lemma discovery (use `@lean-research`); project-wide quality
  scoring (use `@lean-quality-engine`); open problems with no known numeric
  answer (this skill requires a known target).
- **TRIGGERS:** Project Euler, competition math, euler-prover, numeric answer
  theorem, answer = N, native_decide answer-check, computed constant, closed-form
  proof.

## Behavioural rules (G-*)

- **G-1** (MUST): The theorem MUST pin the expected numeric answer as the
  right-hand side (`theorem eulerN : answer = <KNOWN>`), never an existential,
  an opaque bound, or a `True`-shaped restatement. [Trace: AC-EM-01]
- **G-2** (MUST): Before claiming done, the skill MUST verify the answer computes
  -- `#eval answer` MUST print `<KNOWN>` AND the theorem MUST close (via
  `native_decide` or `decide`). A statement that type-checks but does not
  evaluate to the target is NOT done. [Trace: AC-EM-02]
- **G-3** (SHOULD): The skill SHOULD run the improvement pass -- replace
  `native_decide` with a kernel-checked or structural proof along the ladder
  Bronze (`native_decide`) -> Silver (`decide` / `norm_num`) -> Gold
  (characterising property / closed form). In `@lean-core-only` packages
  (no Mathlib; see [`../../references/lean4-core-only-profile.md`](../../references/lean4-core-only-profile.md)),
  `norm_num` is unavailable and `native_decide` introduces `Lean.ofReduceBool`
  (`Lean.trustCompiler`), so Silver MUST use kernel-checked `decide`, `omega`,
  or `rfl`. [Trace: AC-EM-03]
- **G-4** (MUST): When a `native_decide` answer-check ships, the skill MUST record
  its justification -- the compiler-trust axiom (in current Lean a generated
  `<thm>._native.native_decide.ax_*`, underpinned by `Lean.ofReduceBool` /
  `Lean.trustCompiler`) -- and MUST audit it with `#print axioms eulerN`.
  [Trace: AC-EM-04]
- **G-5** (MUST NOT): The skill MUST NOT close with `sorry` or `admit`; a
  placeholder answer-check is not a proof and MUST NOT be persisted as one.
  [Trace: AC-EM-05]
- **G-6** (MUST): L3 carve-out -- a one-tactic `native_decide` (or `decide`)
  close on the answer theorem is legitimate at `@lean-proof-review` L3
  (non-triviality) IFF a structural-proof follow-up task is filed. Absent that
  follow-up it MUST be flagged exactly like any other one-tactic `decide`
  (mirrors `@lean-proof-review` G-5). [Trace: AC-EM-06]
- **G-7** (MUST): On any guard failure the skill MUST escalate per Recovery &
  STOP; it MUST NOT silently downgrade a gate or ship a Bronze proof past a
  fired trigger. [Trace: AC-EM-07]

## Workflow

Discover -> Plan -> Execute -> Validate -> Persist.

1. **Discover** [discover] -- read the problem; extract the KNOWN numeric answer
   from its source; locate or request the Lean/Mathlib encoding of `answer`;
   confirm `lake env lean` (or `lean`) resolves. If the theorem statement is not
   yet written, pull it from `@lean-specification`.
2. **Plan** [discover] -- choose the encoding of `answer` (Finset / List
   enumeration vs closed form) and the ladder rung to aim for. If the encoding
   or a needed Mathlib primitive is uncertain, hand to `@lean-research`. STOP if
   the answer is unknown / the problem is open (this skill needs a known target).
3. **Execute** [execute] -- state `theorem eulerN : answer = <KNOWN>` (G-1);
   get a first GREEN proof, typically Bronze `native_decide`; delegate
   tactic-level work and error triage to `@lean-proof`. Keep `#eval answer` as a
   live sanity check next to the theorem.
4. **Validate** [validate] -- confirm `#eval answer` prints `<KNOWN>` and the
   theorem closes (G-2); run `#print axioms eulerN` and record the compiler-trust
   axiom whenever `native_decide` shipped (G-4); confirm no `sorry` / `admit`
   (G-5); run the improvement pass as far up the ladder as feasible (G-3); route
   the file to `@lean-proof-review` under the L3 carve-out (G-6).
5. **Persist** [persist] *(MANDATORY)* -- commit the Lean file plus the
   `#print axioms` result; whenever a `native_decide` answer-check remains, FILE
   the structural-proof follow-up task the carve-out requires (G-6); update the
   state tracker / tick `tasks.md`; emit a fleeting note via `@lean-zettelkasten`
   if a reusable Euler pattern surfaced. **Skipping Persist = incomplete.**

## Recovery & STOP

- **Novelty** -- answer unknown or the problem is open: STOP. This skill requires
  a known numeric target; ask for the target or decline.
- **Confidence** -- `native_decide` is the only feasible close and no
  structural follow-up can be scoped: STOP at belief < 0.90 and ask before
  shipping a permanent Bronze proof.
- Both `decide` and `native_decide` fail (recursion depth, timeout): STOP; hand
  the encoding to `@lean-research` for a closed-form / structural reduction
  before retrying (kernel `decide` blows `maxRecDepth` on large enumerations).
- **Conflict** -- the encoded `answer` does not match the problem's intended
  quantity: STOP; re-anchor the statement via `@lean-specification` before
  proving.
- **Governance / Irreversible** -- removing `native_decide` would change the
  theorem's trust surface in a way the owner has not accepted: STOP; do NOT
  silently swap axioms; ask.
- Same proof strategy fails 3 times: STOP; escalate to a human or hand to
  `@lean-proof` to isolate the failure.

## Handoffs

- **Predecessors:** `@lean-gateway` routes the task; `@lean-specification`
  supplies the theorem statement; `@lean-research` supplies the encoding and the
  Mathlib primitives.
- **Successors:** `@lean-proof` (tactic-level proving), `@lean-proof-review`
  (audits under the L3 carve-out), `@lean-quality-engine` (project QA).
- **Source spec:** this file (self-specified); every G-rule's `AC-EM-NN` is the
  correspondingly-numbered guarantee in this card.
- **Related ADRs:** ADR-0076 (skill-as-contract), ADR-0080 (handoff DAG).
- **Reference:** [`references/lean4-number-theory.md`](references/lean4-number-theory.md)
  -- Mathlib number-theory facilities, the Bronze/Silver/Gold tactic ladder, and
  the `native_decide` trust note. Template:
  [`Template_Euler.md`](../skills/lean-competitive-math/Template_Euler.md) -- per-problem Lean file template with
  a verified Euler-1 example.

## Common failure modes

> AI agents commonly: state an existential or a bound instead of the exact
> numeric answer; declare done on a green `native_decide` without ever running
> `#print axioms`; leave a Bronze `native_decide` answer-check permanent with no
> structural follow-up filed (defeating the L3 carve-out); reach for kernel
> `decide` at a scale that blows `maxRecDepth` and then give up; paper a gap with
> `sorry`. Full registry: `GUARDRAILS.md` (Agent failure taxonomy).

## See also

- [`references/lean4-number-theory.md`](references/lean4-number-theory.md) -- Mathlib number-theory facilities + Bronze/Silver/Gold ladder + axiom-audit
  trust note (this skill's handbook).
- [`Template_Euler.md`](../skills/lean-competitive-math/Template_Euler.md) -- per-problem Lean file template with a verified Euler-1 example.
- [`../lean-specification/SKILL.md`](../lean-specification/SKILL.md) -- Predecessor (theorem statement).
- [`../lean-research/SKILL.md`](../lean-research/SKILL.md) -- Predecessor (Mathlib encoding).
- [`../lean-proof/SKILL.md`](../lean-proof/SKILL.md) -- Successor (tactic-level proving).
- [`../lean-proof-review/SKILL.md`](../lean-proof-review/SKILL.md) -- Successor (audit under the L3 carve-out).
- [`../lean-quality-engine/SKILL.md`](../lean-quality-engine/SKILL.md) -- Successor (project QA).
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Predecessor / router.
- [`../../references/lean4-tactic-hierarchy.md`](../../references/lean4-tactic-hierarchy.md) -- tactic priority table (`decide` vs `native_decide`).
- [`../../references/lean4-proof-strategy.md`](../../references/lean4-proof-strategy.md) -- one-step-at-a-time proof strategy.

---

## Number Theory & Decidable Computation Reference

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
- [`../Template_Euler.md`](../skills/lean-competitive-math/Template_Euler.md) -- per-problem Lean file template.
