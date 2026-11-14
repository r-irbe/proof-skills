---
name: "lean-sair-kernel-optimization-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-sair-kernel-optimization-handbook.md."
generated_from: "references/handbooks/lean-sair-kernel-optimization-handbook.md"
skill_ref: "skills/lean-sair-kernel-optimization/SKILL.md"
---

# `lean-sair-kernel-optimization` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-sair-kernel-optimization-handbook.md`](../handbooks/lean-sair-kernel-optimization-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| `let x := e; ... x ... x ...` inside recursive step | `SAIR-LAW-01`, `SAIR-LAW-01B` | `kernel-friendly-term-design` |
| Sibling calls `g (f x)` and `h (f x)` in same branch | `SAIR-LAW-01C` | `kernel-friendly-term-design` |
| Closed expression `2^64 - 1` or `List.range 64` inside loop | `SAIR-LAW-02`, `SAIR-LAW-11` | `closed-def-whnf-caching` |
| Deeply curried `fun a b c d => ...` where `a, b, c` are invariant | `SAIR-LAW-02B`, `SAIR-LAW-04` | `kernel-friendly-term-design` |
| Commutative Nat op `acc + 1` or `n &&& (2^k - 1)` | `SAIR-LAW-03`, `SAIR-LAW-03B` | `kernel-friendly-term-design` |
| Well-founded recursion `termination_by` / `brecOn` | `SAIR-LAW-06`, `SAIR-LAW-07` | `kernel-friendly-term-design` |
| `if c then a else b` on `Bool` inside hot kernel loop | `SAIR-LAW-08` | `constructive-decidable-reduction` |
| Nested tuple state `(a, (b, (c, d)))` in `Nat.rec` | `SAIR-LAW-09`, `SAIR-LAW-10`, `SAIR-LAW-24` | `kernel-friendly-term-design` |
| Signed integer difference `(a : Int) - (b : Int)` in kernel | `SAIR-LAW-12`, `SAIR-LAW-12B` | `kernel-friendly-term-design` |
| `x * x` on multi-limb vs single-limb `Nat` | `SAIR-LAW-13`, `SAIR-LAW-13B` | `gmp-swar-word-packing` |
| `n / 2^k` and `n % 2^k` on large `Nat` | `SAIR-LAW-14`, `SAIR-LAW-14B`, `SAIR-LAW-14C` | `gmp-swar-word-packing` |
| Fixed-width array/vector recurrence `dp[i] = dp[i-1] + dp[i-k]` | `SAIR-LAW-15`, `SAIR-LAW-16`, `SAIR-LAW-16B` | `gmp-swar-word-packing` |
| Graph/automaton state space exploration in `decide` | `SAIR-LAW-17`, `SAIR-LAW-18`, `SAIR-LAW-18B` | `algorithm-class-substitution` |
| Branching search with multiple pruning guards | `SAIR-LAW-19`, `SAIR-LAW-19B`, `SAIR-LAW-20` | `algorithm-class-substitution` |
| Proof of `List.Perm` or finite invariant inside `rfl` | `SAIR-LAW-21`, `SAIR-LAW-22`, `SAIR-LAW-23` | `constructive-decidable-reduction` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| "Speed up `rfl` / `decide` on a recursive function" | `SAIR-LAW-06`, `SAIR-LAW-07`, `SAIR-LAW-02` | Replace `WellFounded.fix` with structural `Nat.rec`; hoist closed constants outside `Nat.rec` step lambdas |
| "Eliminate `Classical.choice` from a `Nat`/`Bool`/`BitVec` theorem" | `SAIR-LAW-08`, `SAIR-LAW-22`, `SAIR-LAW-23` | Use AltProof Route 9 (`constructive-decidable-reduction`): replace `split`/`by_cases` with `Bool.and_eq_true`, `decide_eq_true_eq`, `omega`, or `bv_decide` |
| "Avoid recomputing a huge constant inside every recursion step" | `SAIR-LAW-02`, `SAIR-LAW-11`, `SAIR-LAW-25B` | Use AltProof Route 10 (`closed-def-whnf-caching`): define a closed top-level `def C : Nat := ...` (cached in `m_st->m_whnf`) or compute via `eval_nat%` |
| "Vectorize a DP table or cellular automaton inside Lean's kernel" | `SAIR-LAW-15`, `SAIR-LAW-16B`, `SAIR-LAW-20` | Use AltProof Route 11 (`gmp-swar-word-packing`): pack `k` lanes into a `b`-bit `Nat` word (aligning `b` to multiples of 64 bits where possible) |
| "Reduce memory allocation and `Prod.mk` boxing in state loops" | `SAIR-LAW-09`, `SAIR-LAW-10`, `SAIR-LAW-24` | Convert tuple returns `(a, b, c)` into CPS (`fun k => k a b c`) or a flat `structure` with unboxed scalar fields |
| "Prune dead search branches in a kernel-checked solver" | `SAIR-LAW-18`, `SAIR-LAW-19`, `SAIR-LAW-19B` | Represent frontiers as `Nat` bitmasks; test `(frontier &&& validMask) == 0` before spawning recursive calls |
| "Clean up unreadably large unrolled definitions without losing speed" | `SAIR-LAW-16`, `SAIR-LAW-25`, `SAIR-LAW-25B` | Use binary-doubling combinators (`t0..t6`) with elaboration-time pre-unfolding (`preunfold%` / `unroll_top%`) and named `abbrev` constants |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| `(deterministic) timeout at whnf, maximum number of heartbeats (200000) has been reached` | Deep unfolding of `WellFounded.fix` / `brecOn` or unshared subtrees in `is_def_eq` | `SAIR-LAW-06` (switch to structural `Nat.rec`), `SAIR-LAW-01B` (share repeated subexpressions via `let`), `SAIR-LAW-02` (hoist closed subtrees) |
| `theorem depends on axiom Classical.choice` on decidable arithmetic | `if ... then ... else ...` or `split` used `Classical.propDecidable` instead of `Bool` / `Decidable` instance | `SAIR-LAW-08`, `SAIR-LAW-23`, Route 9 (`constructive-decidable-reduction`): switch to `cond`, `Bool.rec`, `omega`, or `bv_decide` |
| `maximum recursion depth has been reached` during `rfl` / `decide` | Non-tail-recursive list pipeline or deep left-associated expression tree | `SAIR-LAW-10` (CPS / tail accumulator), `SAIR-LAW-16` (binary-doubling tree instead of linear chain) |
| `Nat.div` / `Nat.mod` dominates kernel profile (`>40%` instructions) | Repeated division/modulo by powers of 2 or fixed bases in inner loop | `SAIR-LAW-14` (`>>>` and `&&&`), `SAIR-LAW-14B` (chunked Horner radix), `SAIR-LAW-14C` (bitwise subpipeline) |
| Slow `is_def_eq` on functions carrying proof witnesses `{x : Nat // P x}` | Kernel reduces proof terms inside `Subtype` projections during WHNF | `SAIR-LAW-22` (`ZeroPropRuntimeCone`), `SAIR-LAW-22B` (`HotColdSeparation`): compute on raw `Nat`, prove `P` externally |
| High heartbeat count on `Prod.fst` / `Prod.snd` chains | Repeated projection reduction `proj(0, mk(a, b))` across recursion steps | `SAIR-LAW-09` (`UnboxedProductSpine`), `SAIR-LAW-10` (`CpsPairElim`) |
| `bv_decide` fails to apply because goal uses unbounded `Nat` bitwise ops | Goal is stated over `Nat.land`/`Nat.lor` rather than fixed-width `BitVec w` | Bridge bounded `Nat` `< 2^w` to `BitVec w` via `BitVec.ofNat`, close with `bv_decide` (`SAIR-LAW-15`, `SAIR-LAW-20`) |
