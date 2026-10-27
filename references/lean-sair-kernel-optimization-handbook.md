---
name: "lean-sair-kernel-optimization-handbook"
description: "Reference handbook for @lean-sair-kernel-optimization."
extracted_from: "skills/lean-sair-kernel-optimization/SKILL.md"
---

# Lean 4 Kernel WHNF, ZDD, and SWAR Optimization Handbook (SAIR-LAW-01..25B)

> **Scope**: Public reference manual for Lean 4 kernel reduction cost (`type_checker.cpp` WHNF, `m_st->m_whnf` caching, GMP `mpz` big-integer arithmetic, SWAR word packing, and decision-diagram state compression) and AltProof Routes 7..11.
> **Encoding**: 7-bit ASCII / typographic-free per `INV-001`.

---

## 1. Quick-Lookup Indexing Tables (`mathcomp-skills` Three-Entry-Point Pattern)

### Table 1: Goal-Shape-First (`templates` Entry Point)

| Goal / Term Shape | Primary SAIR Law(s) | Recommended AltProof Route | Canonical Kernel Pattern / Tactic |
| :--- | :--- | :--- | :--- |
| `let x := e; ... x ... x ...` inside recursive step | `SAIR-LAW-01`, `SAIR-LAW-01B` | `kernel-friendly-term-design` | Bind once via `let x := e` when referenced >=2 times (DAG sharing); inline when referenced once (avoid `Let` + zeta tax) |
| Sibling calls `g (f x)` and `h (f x)` in same branch | `SAIR-LAW-01C` | `kernel-friendly-term-design` | Hoist `let fx := f x` before the branch or tuple application |
| Closed expression `2^64 - 1` or `List.range 64` inside loop | `SAIR-LAW-02`, `SAIR-LAW-11` | `closed-def-whnf-caching` | Hoist to top-level `def C : Nat := ...` or evaluate at elaboration time via `eval_nat%` |
| Deeply curried `fun a b c d => ...` where `a, b, c` are invariant | `SAIR-LAW-02B`, `SAIR-LAW-04` | `kernel-friendly-term-design` | Place invariant binders outermost and vary only the innermost accumulator; eta-reduce point-free wrappers |
| Commutative Nat op `acc + 1` or `n &&& (2^k - 1)` | `SAIR-LAW-03`, `SAIR-LAW-03B` | `kernel-friendly-term-design` | Put small constant on LHS (`1 + acc`) when helpful for structural reduction, or replace `n % 2^k` with `n &&& mask` |
| Well-founded recursion `termination_by` / `brecOn` | `SAIR-LAW-06`, `SAIR-LAW-07` | `kernel-friendly-term-design` | Refactor to structural `Nat.rec` / fuel recursion or attach `@[csimp]` dual-path theorem for compiled execution |
| `if c then a else b` on `Bool` inside hot kernel loop | `SAIR-LAW-08` | `constructive-decidable-reduction` | Replace `ite` (which synthesizes `Decidable` dictionary) with `Bool.rec b a c` or `cond c a b` |
| Nested tuple state `(a, (b, (c, d)))` in `Nat.rec` | `SAIR-LAW-09`, `SAIR-LAW-10`, `SAIR-LAW-24` | `kernel-friendly-term-design` | Flatten into a dedicated `structure State` or CPS continuation `k a b c d` (optimal arity <= 6) |
| Signed integer difference `(a : Int) - (b : Int)` in kernel | `SAIR-LAW-12`, `SAIR-LAW-12B` | `kernel-friendly-term-design` | Represent as unboxed `Nat` pair `(pos, neg)` or direct `Nat.rec` sign-magnitude without `Quot.mk` overhead |
| `x * x` on multi-limb vs single-limb `Nat` | `SAIR-LAW-13`, `SAIR-LAW-13B` | `gmp-swar-word-packing` | Share `let y := x; y * y` so GMP `mpz_mul(r, a, a)` dispatches to Karatsuba/squaring fast path |
| `n / 2^k` and `n % 2^k` on large `Nat` | `SAIR-LAW-14`, `SAIR-LAW-14B`, `SAIR-LAW-14C` | `gmp-swar-word-packing` | Replace with `Nat.shiftRight n k` and `Nat.land n ((1 <<< k) - 1)`; align Horner chunks to 64-bit limb multiples |
| Fixed-width array/vector recurrence `dp[i] = dp[i-1] + dp[i-k]` | `SAIR-LAW-15`, `SAIR-LAW-16`, `SAIR-LAW-16B` | `gmp-swar-word-packing` | Pack `k` lanes of `b` bits into a single GMP `Nat` word (Kronecker SWAR); unroll fixed-trip inner loops via binary doubling |
| Graph/automaton state space exploration in `decide` | `SAIR-LAW-17`, `SAIR-LAW-18`, `SAIR-LAW-18B` | `algorithm-class-substitution` | Canonicalize state words in CBV order; represent frontier sets as bitset/ZDD masks; isolate lowest set bit via `x &&& (0 - x)` |
| Branching search with multiple pruning guards | `SAIR-LAW-19`, `SAIR-LAW-19B`, `SAIR-LAW-20` | `algorithm-class-substitution` | Combine lookahead masks into a single bitwise `!= 0` check; short-circuit `mask == 0` before recursion; use ANF/Zhegalkin word ops |
| Proof of `List.Perm` or finite invariant inside `rfl` | `SAIR-LAW-21`, `SAIR-LAW-22`, `SAIR-LAW-23` | `constructive-decidable-reduction` | Keep `Prop` proofs and typeclass dictionaries completely out of the runtime computation cone; bridge via a separate soundness theorem |

---

### Table 2: Intent-First (`phrasebook` Entry Point)

| User / Engineer Intent | Target SAIR Law(s) | Actionable Transformation Recipe |
| :--- | :--- | :--- |
| "Speed up `rfl` / `decide` on a recursive function" | `SAIR-LAW-06`, `SAIR-LAW-07`, `SAIR-LAW-02` | Replace `WellFounded.fix` with structural `Nat.rec`; hoist closed constants outside `Nat.rec` step lambdas |
| "Eliminate `Classical.choice` from a `Nat`/`Bool`/`BitVec` theorem" | `SAIR-LAW-08`, `SAIR-LAW-22`, `SAIR-LAW-23` | Use AltProof Route 9 (`constructive-decidable-reduction`): replace `split`/`by_cases` with `Bool.and_eq_true`, `decide_eq_true_eq`, `omega`, or `bv_decide` |
| "Avoid recomputing a huge constant inside every recursion step" | `SAIR-LAW-02`, `SAIR-LAW-11`, `SAIR-LAW-25B` | Use AltProof Route 10 (`closed-def-whnf-caching`): define a closed top-level `def C : Nat := ...` (cached in `m_st->m_whnf`) or compute via `eval_nat%` |
| "Vectorize a DP table or cellular automaton inside Lean's kernel" | `SAIR-LAW-15`, `SAIR-LAW-16B`, `SAIR-LAW-20` | Use AltProof Route 11 (`gmp-swar-word-packing`): pack `k` lanes into a `b`-bit `Nat` word (aligning `b` to multiples of 64 bits where possible) |
| "Reduce memory allocation and `Prod.mk` boxing in state loops" | `SAIR-LAW-09`, `SAIR-LAW-10`, `SAIR-LAW-24` | Convert tuple returns `(a, b, c)` into CPS (`fun k => k a b c`) or a flat `structure` with unboxed scalar fields |
| "Prune dead search branches in a kernel-checked solver" | `SAIR-LAW-18`, `SAIR-LAW-19`, `SAIR-LAW-19B` | Represent frontiers as `Nat` bitmasks; test `(frontier &&& validMask) == 0` before spawning recursive calls |
| "Clean up unreadably large unrolled definitions without losing speed" | `SAIR-LAW-16`, `SAIR-LAW-25`, `SAIR-LAW-25B` | Use binary-doubling combinators (`t0..t6`) with elaboration-time pre-unfolding (`preunfold%` / `unroll_top%`) and named `abbrev` constants |

---

### Table 3: Error / Kernel Bottleneck-First (`errors` Entry Point)

| Symptom / Elaborator Error / Bottleneck | Root Cause in `type_checker.cpp` | Remediating SAIR Law(s) & Fix |
| :--- | :--- | :--- |
| `(deterministic) timeout at whnf, maximum number of heartbeats (200000) has been reached` | Deep unfolding of `WellFounded.fix` / `brecOn` or unshared subtrees in `is_def_eq` | `SAIR-LAW-06` (switch to structural `Nat.rec`), `SAIR-LAW-01B` (share repeated subexpressions via `let`), `SAIR-LAW-02` (hoist closed subtrees) |
| `theorem depends on axiom Classical.choice` on decidable arithmetic | `if ... then ... else ...` or `split` used `Classical.propDecidable` instead of `Bool` / `Decidable` instance | `SAIR-LAW-08`, `SAIR-LAW-23`, Route 9 (`constructive-decidable-reduction`): switch to `cond`, `Bool.rec`, `omega`, or `bv_decide` |
| `maximum recursion depth has been reached` during `rfl` / `decide` | Non-tail-recursive list pipeline or deep left-associated expression tree | `SAIR-LAW-10` (CPS / tail accumulator), `SAIR-LAW-16` (binary-doubling tree instead of linear chain) |
| `Nat.div` / `Nat.mod` dominates kernel profile (`>40%` instructions) | Repeated division/modulo by powers of 2 or fixed bases in inner loop | `SAIR-LAW-14` (`>>>` and `&&&`), `SAIR-LAW-14B` (chunked Horner radix), `SAIR-LAW-14C` (bitwise subpipeline) |
| Slow `is_def_eq` on functions carrying proof witnesses `{x : Nat // P x}` | Kernel reduces proof terms inside `Subtype` projections during WHNF | `SAIR-LAW-22` (`ZeroPropRuntimeCone`), `SAIR-LAW-22B` (`HotColdSeparation`): compute on raw `Nat`, prove `P` externally |
| High heartbeat count on `Prod.fst` / `Prod.snd` chains | Repeated projection reduction `proj(0, mk(a, b))` across recursion steps | `SAIR-LAW-09` (`UnboxedProductSpine`), `SAIR-LAW-10` (`CpsPairElim`) |
| `bv_decide` fails to apply because goal uses unbounded `Nat` bitwise ops | Goal is stated over `Nat.land`/`Nat.lor` rather than fixed-width `BitVec w` | Bridge bounded `Nat` `< 2^w` to `BitVec w` via `BitVec.ofNat`, close with `bv_decide` (`SAIR-LAW-15`, `SAIR-LAW-20`) |

---

## 2. AltProof Routes 7..11 (Machine Kernel & Constructive Bridge Routes)

| Route ID | Family | Match Shape | Rewrite / Transformation Strategy | Yield & Cost Profile |
| :--- | :--- | :--- | :--- | :--- |
| **Route 7**: `algorithm-class-substitution` | `algorithm-class-substitution` | Exponential recursion, naive enumeration, or multi-pass list pipelines with an equivalent DP or sieve formulation | Replace the computation definition with an O(N) / O(N log N) DP or bitwise sieve and prove a bridge lemma `fast_fn n = spec_fn n` | **20x-30x** reduction in kernel WHNF steps and `rfl` check time |
| **Route 8**: `kernel-friendly-term-design` | `kernel-friendly-term-design` | `WellFounded.fix`, `brecOn`, boxed tuple accumulators, or unhoisted closed subtrees inside recursion | Rewrite using direct `Nat.rec`, CPS accumulators, hoisted closed definitions, and typeclass-free hot cones | **3x-10x** heartbeat reduction; eliminates `WellFounded.fix` unfolding traps |
| **Route 9**: `constructive-decidable-reduction` | `kernel-friendly-term-design` | `Classical.choice` leakage in first-order `Nat`/`Int`/`Bool`/`BitVec` proofs caused by `split` or classical `by_cases` | Replace classical splits with `Bool.and_eq_true`, `decide_eq_true_eq`, `omega`, or `bv_decide` | Eliminates `Classical.choice` from transitive axiom closure |
| **Route 10**: `closed-def-whnf-caching` | `kernel-friendly-term-design` | Giant decimal `nat_lit` constants (`>64` bits) or closed shift-add formulas recomputed inside `Nat.rec` steps | Evaluate closed constants at elaboration time via `eval_nat%` (0 runtime overhead) or hoist to a closed top-level `def C : Nat` cached in `m_st->m_whnf` | Eliminates repeated constant evaluation across recursion steps |
| **Route 11**: `gmp-swar-word-packing` | `algorithm-class-substitution` | Inner loops over fixed-width integer/boolean arrays, bounded-slot recurrences, or manually unrolled block trees | Pack `k` lanes into a single `b`-bit GMP `Nat` word (Kronecker SWAR / bitboard ANF) and use `preunfold%` / `unroll_top%` over binary-doubling combinators (`t0..t6`) | **15x-30x** kernel instruction reduction on convolution and bitboard workloads |

---

## 3. Complete Catalog of the 37 SAIR Kernel Optimization Laws (`SAIR-LAW-01..25B`)

### Layer I: Memory, Reference Counting, and Substitution (`SAIR-LAW-01` .. `SAIR-LAW-05`)

1. **`SAIR-LAW-01` (`SairLaw01LetZetaTax`) -- Single-Use `let` Zeta-Expansion Tax**
   - **Kernel Mechanism**: Every `Expr::Let` node allocated in a lambda body incurs allocation + `instantiate_rev` substitution overhead when zeta-reduced during WHNF.
   - **Rule**: If a local `let x := e` is referenced **at most once** in the body, inline `e` directly instead of allocating a `let` binding.

2. **`SAIR-LAW-01B` (`SairLaw01bDagSharing`) -- Multi-Use `let` DAG Pointer Sharing**
   - **Kernel Mechanism**: Lean 4 `Expr` nodes are hash-consed / DAG-shared in memory when bound via `let x := e` and passed into `instantiate_rev`.
   - **Rule**: Whenever a non-trivial subexpression `e` is used **>= 2 times** along an execution path, bind `let x := e` so WHNF evaluates or substitutes the pointer once.

3. **`SAIR-LAW-01C` (`SairLaw01cSiblingWhnfCse`) -- Sibling WHNF Common Subexpression Elimination**
   - **Kernel Mechanism**: Sibling arguments `g (f x) (h (f x))` do not share WHNF reduction caches unless `f x` is syntactically the same shared subterm or `let`-bound.
   - **Rule**: Hoist repeated sibling calls `f x` into a shared `let fx := f x` prior to constructing the outer application.

4. **`SAIR-LAW-02` (`SairLaw02ClosedSubtreeHoist`) -- Closed Subtree Hoisting (`m_st->m_whnf` Cache)**
   - **Kernel Mechanism**: Lean's C++ kernel caches WHNF results of **closed** constants (`Expr::Const` with no free variables) in `m_st->m_whnf`. Open subexpressions inside a lambda are re-reduced on every step.
   - **Rule**: Hoist every closed subexpression (`(1 <<< 64) - 1`, fixed lookup tables, basis vectors) out of `fun` / `Nat.rec` step lambdas into a top-level closed `def` or `eval_nat%` literal.

5. **`SAIR-LAW-02B` (`SairLaw02bInnerBinderOrder`) -- Invariant-Outermost Binder Ordering**
   - **Kernel Mechanism**: Each beta-reduction `instantiate_rev` copies the spine of nested lambdas below the substituted binder.
   - **Rule**: Order function parameters so loop-invariant parameters sit outermost and only the changing state/accumulator binders sit innermost on the `Nat.rec` motive.

6. **`SAIR-LAW-03` (`SairLaw03ConstantLeftOp`) -- Constant-Left Structural Argument Placement**
   - **Kernel Mechanism**: Operations whose definition is structural on a specific argument reduce in fewer WHNF steps when the small concrete numeral is placed on the structurally recursive side.
   - **Rule**: Align small constant operands with the structural recursion argument of helper primitives where applicable.

7. **`SAIR-LAW-03B` (`SairLaw03bConstantLeftPow2Mask`) -- Power-of-Two Bitmask Canonicalization**
   - **Kernel Mechanism**: Modulo by `2^k` (`n % 2^k`) invokes general GMP division unless rewritten to bitwise AND (`Nat.land n ((1 <<< k) - 1)`).
   - **Rule**: Replace `% (2^k)` with `&&& mask` where `mask` is a pre-hoisted closed `nat_lit`.

8. **`SAIR-LAW-04` (`SairLaw04PointFreeEtaWrapper`) -- Point-Free Eta Wrapper Elimination**
   - **Kernel Mechanism**: Eta-expanded wrappers `fun x => f x` allocate an extra lambda frame and require an extra beta-reduction on every step.
   - **Rule**: Eta-reduce `fun x => f x` to `f` in higher-order combinators (`Nat.rec`, `List.foldl`).

9. **`SAIR-LAW-05` (`SairLaw05SharedAbbrevMotive`) -- Shared `abbrev` Motive Compression**
   - **Kernel Mechanism**: Large repeated motive types in `Nat.rec` / `List.rec` bloat term size and type-checking time at every recursor node.
   - **Rule**: Factor complex recursor motive types into a transparent `abbrev Motive := ...`.

---

### Layer II: Inductive & Recursor Dispatch (`SAIR-LAW-06` .. `SAIR-LAW-12B`)

10. **`SAIR-LAW-06` (`KernelBrecOnTax`) -- `WellFounded.fix` / `brecOn` Unfolding Tax**
    - **Kernel Mechanism**: Equations compiled via `termination_by` or course-of-values `brecOn` wrap every recursive step in `Below` dictionary tuples and proof witnesses that the kernel must unfold during `rfl`.
    - **Rule**: Replace `WellFounded.fix` / `brecOn` with direct structural `Nat.rec` or explicit fuel `Nat.repeat` in kernel-intensive definitions.

11. **`SAIR-LAW-07` (`SairLaw07CsimpDualPath`) -- `@[csimp]` Dual-Path Specification Pattern**
    - **Kernel Mechanism**: A simple structural definition is ideal for proving theorems, while a tail-recursive/SWAR definition is fast for execution and `rfl`.
    - **Rule**: Pair a clean specification `def spec` with a fast implementation `def fast` and prove `@[csimp] theorem spec_eq_fast : @spec = @fast`.

12. **`SAIR-LAW-08` (`SairLaw08BoolRecOverIte`) -- `Bool.rec` / `cond` Over `ite`**
    - **Kernel Mechanism**: `if p then a else b` (`ite`) takes a `Decidable p` typeclass instance and reduces the decision proof term in WHNF; `cond b x y` / `Bool.rec y x b` branches directly on a `Bool` constructor.
    - **Rule**: Use `cond` or `Bool.rec` instead of `if ... then ... else ...` inside hot computational loops.

13. **`SAIR-LAW-09` (`SairLaw09UnboxedProductSpine`) -- Unboxed Product Spine (`Prod.mk` Elimination)**
    - **Kernel Mechanism**: Returning nested pairs `(a, (b, c))` allocates `Prod.mk` constructor nodes on every step and forces `Prod.fst` / `Prod.snd` projection reductions.
    - **Rule**: Replace nested `Prod` spines with a single flat `structure` or CPS state passing.

14. **`SAIR-LAW-10` (`SairLaw10CpsPairElim`) -- CPS Continuation Pair Elimination**
    - **Kernel Mechanism**: Continuation-Passing Style (`fun a b c => ...`) keeps state registers in lambda binders, avoiding constructor allocation and projection WHNF altogether.
    - **Rule**: Transform multi-output inner helpers from `f x : Nat x Nat` to `f x (k : Nat -> Nat -> alpha) : alpha`.

15. **`SAIR-LAW-11` (`SairLaw11InductivePreHoist`) -- Inductive Step Pre-Hoisting**
    - **Kernel Mechanism**: Subterms inside a `Nat.rec` step function that do not depend on the induction index `i` or accumulator `acc` are re-instantiated at every step `0..N-1`.
    - **Rule**: Hoist loop-invariant step subterms outside `Nat.rec`.

16. **`SAIR-LAW-12` (`SairLaw12DirectNatRecSign`) -- Direct `Nat.rec` Over `Int` Quotient Representation**
    - **Kernel Mechanism**: `Int` arithmetic in the kernel checks `Int.ofNat` vs `Int.negSucc` cases on every operation.
    - **Rule**: Keep unsigned loops in `Nat`; when signed values are needed, track sign bit separately or use offset/biased `Nat` arithmetic.

17. **`SAIR-LAW-12B` (`SairLaw12bUnboxedQuotientSignDiff`) -- Unboxed Quotient / Sign-Difference Representation**
    - **Kernel Mechanism**: `Rat` and `ZMod` quotients carry GCD normalization or modular reduction on every intermediate step.
    - **Rule**: Represent intermediate signed/rational accumulators as unnormalized `(numPos, numNeg, den)` `Nat` triples and normalize once at the boundary.

---

### Layer III: Native GMP Big-Nat & SWAR (`SAIR-LAW-13` .. `SAIR-LAW-16B`)

18. **`SAIR-LAW-13` (`SairLaw13MultiLimbSquare`) -- Multi-Limb GMP Squaring Fast Path**
    - **Kernel Mechanism**: Lean's `nat_lit` multiplication calls GMP `mpz_mul(res, a, b)`. When `a` and `b` are pointer-identical (`let x := ...; x * x`), GMP dispatches to `mpn_sqr` (Karatsuba/Toom squaring, ~1.5x faster than general multiplication).
    - **Rule**: Bind multi-limb operands via `let x := expr; x * x` rather than duplicating `expr * expr`.

19. **`SAIR-LAW-13B` (`SairLaw13bSingleLimbSquare`) -- Single-Limb Scalar Squaring**
    - **Kernel Mechanism**: For single-limb (`< 2^63`) scalars where `x` is already a bound variable, `x * x` hits the immediate scalar fast path without an extra `let`.
    - **Rule**: Use `x * x` directly on already-bound scalar variables; avoid `x ^ 2` inside tight kernel loops (which unfolds `HPow.hPow` -> `Nat.pow` recursion).

20. **`SAIR-LAW-14` (`KernelPowerOfTwoDivMod`) -- Power-of-Two `>>>` and `&&&` Over `/` and `%`**
    - **Kernel Mechanism**: `Nat.shiftRight` (`>>>`) and `Nat.land` (`&&&`) map to native bit shifts/masks on `nat_lit`, whereas `/` and `%` invoke division routines.
    - **Rule**: Always replace `n / 2^k` with `n >>> k` and `n % 2^k` with `n &&& ((1 <<< k) - 1)`.

21. **`SAIR-LAW-14B` (`SairLaw14bGmpHornerAsymmetry`) -- GMP Horner Chunk Asymmetry**
    - **Kernel Mechanism**: Packing digits into a huge `Nat` via step-by-step `acc * B + d` performs O(N) big-by-small multiplications of growing limb size.
    - **Rule**: Aggregate small limbs into 64-bit or balanced binary-tree chunks before combining multi-limb `Nat` words.

22. **`SAIR-LAW-14C` (`SairLaw14cBitwiseSubpipeline`) -- Pure Bitwise Sub-Pipeline Fusion**
    - **Kernel Mechanism**: Mixing arithmetic `+` with bitwise `^^^` / `&&&` forces carry propagation across limbs.
    - **Rule**: Fuse adjacent bitwise masks/shifts (`(x >>> a) >>> b` -> `x >>> (a + b)`, `(x &&& m1) &&& m2` -> `x &&& (m1 &&& m2)`) into a single bitwise pipeline.

23. **`SAIR-LAW-15` (`SairLaw15SwarWordPacking`) -- Kronecker / SWAR Multi-Lane Word Packing**
    - **Kernel Mechanism**: Lean's kernel executes `Nat.add`, `Nat.mul`, `Nat.land`, `Nat.lor`, `Nat.xor`, and `Nat.shiftLeft` as single C++/GMP instructions on arbitrary-precision `nat_lit` values.
    - **Rule**: Pack an array of `k` counters/lanes of `b`-bit width into a single `k * b`-bit `Nat` word `sum_{i=0}^{k-1} a_i * 2^(i*b)` so vector addition, shifting, and polynomial convolution run in **1 kernel instruction per step**.

24. **`SAIR-LAW-16` (`SairLaw16FixedTripUnroll`) -- Binary-Doubling Fixed-Trip Loop Unrolling (`t0..t6`)**
    - **Kernel Mechanism**: A `Nat.rec` loop of `2^m` steps incurs `2^m` recursor dispatch frames. Binary-doubling combinators `t_{k+1} f x = t_k f (t_k f x)` with elaboration-time pre-unfolding (`preunfold%` / `unroll_top%`) eliminate recursor dispatch overhead while keeping source compact.
    - **Rule**: Unroll fixed-trip inner kernels via binary-doubling combinators (`t0..t6`) rather than thousand-line manual copy-paste.

25. **`SAIR-LAW-16B` (`SairLaw16bGmpLimbAlignment`) -- 64-Bit GMP Limb Boundary Alignment**
    - **Kernel Mechanism**: GMP stores `mpz_t` in 64-bit `mp_limb_t` words. Bit shifts `<<< b` and `>>> b` where `b` is a multiple of 64 copy whole limbs (`mpn_copyi`) with zero cross-limb bit-shifting overhead.
    - **Rule**: Choose SWAR lane width `b in {64, 128, 192, 256}` (or pack sub-lanes so inter-block shifts are multiples of 64) whenever lane bounds permit.

---

### Layer IV: Decision Diagrams, Boolean Algebra, and Search (`SAIR-LAW-17` .. `SAIR-LAW-20`)

26. **`SAIR-LAW-17` (`SairLaw17CbvStateCanonical`) -- CBV State Word Canonicalization**
    - **Kernel Mechanism**: Equality checks on canonical `nat_lit` state words take O(1) pointer/limb comparison in WHNF, whereas structural equality on `List` or `Finset` takes O(N) constructor reductions.
    - **Rule**: Encode finite search states (permutations, partitions, board configurations) as canonical packed `Nat` words.

27. **`SAIR-LAW-18` (`SairLaw18FrontierZddMask`) -- Frontier Bitset / ZDD Mask Compression**
    - **Kernel Mechanism**: Maintaining a BFS/DFS frontier as `List State` allocates cons cells on every transition; a packed `Nat` bitset or Zero-suppressed Decision Diagram (ZDD) mask updates all frontier states in parallel via bitwise operations.
    - **Rule**: Represent finite-state frontiers as packed `Nat` bitmasks when state indices fit in a bounded universe.

28. **`SAIR-LAW-18B` (`SairLaw18bSingleBitPopcount`) -- Lowest-Set-Bit Isolation (`x &&& (0 - x)` / Clear-Lowest-Bit)**
    - **Kernel Mechanism**: Iterating over all candidate indices `0..W-1` wastes `W` branches when only `k << W` bits are set in `mask`.
    - **Rule**: Clear the lowest set bit via `mask &&& (mask - 1)` so branch iteration runs in `O(popcount(mask))` steps.

29. **`SAIR-LAW-19` (`SairLaw19CombinedLookaheadGuard`) -- Combined Bitwise Lookahead Guard**
    - **Kernel Mechanism**: Evaluating `m` separate boolean guards `g1 && g2 && ... && gm` reduces `m` sequential `Bool.rec` branches.
    - **Rule**: Combine feasibility/constraint masks into a single bitwise word check `(stateMask &&& forbiddenMask) == 0`.

30. **`SAIR-LAW-19B` (`SairLaw19bZeroMaskPrune`) -- Early Zero-Mask Short-Circuit Pruning**
    - **Kernel Mechanism**: Continuing recursion when an available-moves bitmask `avail == 0` wastes an entire call frame and WHNF unfolding layer.
    - **Rule**: Test `Nat.beq avail 0` immediately after mask intersection and return `0` / `false` before any further state unpacking.

31. **`SAIR-LAW-20` (`SairLaw20AnfZhegalkinRotation`) -- Algebraic Normal Form (ANF / Zhegalkin) Word-Level Boolean Evaluation**
    - **Kernel Mechanism**: Cellular automata (e.g., Rule 110) and cryptographic round functions (SHA-256 `Ch`, `Maj`, `Sigma_0`, `Sigma_1`) expressed as per-cell `if/match` trees require O(W) branches per step.
    - **Rule**: Express local boolean transition rules in Algebraic Normal Form (XOR `^^^`, AND `&&&`, OR `|||`) over shifted `Nat` words (`left := w <<< 1`, `right := w >>> 1`) to update all `W` cells simultaneously in 4-6 kernel bitwise ops.

---

### Layer V: Verification, Type Architecture, and Clean-Code (`SAIR-LAW-21` .. `SAIR-LAW-25B`)

32. **`SAIR-LAW-21` (`SairLaw21HeuristicListPerm`) -- Decoupled Certificate Verification Over Constructive Search**
    - **Kernel Mechanism**: Running a complex search algorithm inside the kernel costs O(search space); checking an emitted witness certificate (e.g., permutation sorting network, Pratt prime certificate, LRAT proof) costs O(certificate size).
    - **Rule**: Compute witnesses outside or at elaboration time and verify them in the kernel with a minimal certificate checker.

33. **`SAIR-LAW-22` (`SairLaw22ZeroPropRuntimeCone`) -- Zero `Prop` Terms in the Runtime Computation Cone**
    - **Kernel Mechanism**: Any `Subtype` (`{x : alpha // P x}`), `Fin n` (which carries `isLt : val < n`), or proof argument passed into a computational function forces the kernel to carry and substitute proof terms during WHNF.
    - **Rule**: Keep the entire computational call graph (`def` cone evaluated by `rfl`/`decide`) strictly in `Nat` / `Bool` / `UInt64` with **zero `Prop` or `Fin` fields**; prove bounds in separate `theorem` declarations.

34. **`SAIR-LAW-22B` (`SairLaw22bHotColdSeparation`) -- Hot Computation Cone vs Cold Proof Cone Separation**
    - **Kernel Mechanism**: Mixing helper lemmas and heavy Mathlib imports into the file that defines a hot computational kernel bloats `.olean` load time and risks pulling typeclass instances into `def` bodies.
    - **Rule**: Isolate hot computational `def`s in a minimal-import module (or top section) and place equivalence/correctness proofs in a downstream section or module.

35. **`SAIR-LAW-22C` (`SairLaw22cNamedRecursorBinders`) -- Explicit Named Recursor Binders**
    - **Kernel Mechanism**: Anonymous nested `Nat.rec` lambdas (`fun _ ih => ...`) obscure which variable is the step index vs accumulator and invite off-by-one defects during equivalence proofs.
    - **Rule**: Always name `Nat.rec` step binders explicitly (`fun stepIdx acc => ...`) and document the loop invariant.

36. **`SAIR-LAW-23` (`SairLaw23ZeroTypeclassHotCone`) -- Zero Typeclass Dictionaries in the Hot Cone**
    - **Kernel Mechanism**: Polymorphic operations (`+`, `*`, `<<<`, `&&&` via `HAdd.hAdd`, `HMul.hMul`, `HShiftLeft.hShiftLeft`) wrap every operation in typeclass instance projections (`instHAddNat`, etc.) that must be unfolded during WHNF.
    - **Rule**: Inside ultra-hot kernel loops, call direct primitive constants (`Nat.add`, `Nat.mul`, `Nat.sub`, `Nat.land`, `Nat.lor`, `Nat.xor`, `Nat.shiftLeft`, `Nat.shiftRight`, `Nat.beq`, `Nat.ble`) to bypass typeclass projection unfolding.

37. **`SAIR-LAW-24` (`SairLaw24OptimalCpsArity`) -- Optimal CPS Accumulator Arity (`<= 6` Scalars)**
    - **Kernel Mechanism**: CPS eliminates tuple boxing (`SAIR-LAW-10`), but passing `> 6` scalar arguments increases `instantiate_rev` array size on every step.
    - **Rule**: Keep CPS continuation arity between 2 and 6 scalar `Nat` arguments; if state requires more than 6 scalars, pack related bounded fields into a single SWAR `Nat` word (`SAIR-LAW-15`).

38. **`SAIR-LAW-25` (`SairLaw25ModuleHeaderHumanization`) -- Module Header & Bit-Layout Documentation**
    - **Kernel Mechanism**: SWAR bit-packed kernels and CPS loops are opaque to human reviewers and proof-repair agents without an explicit bit-layout diagram.
    - **Rule**: Document every SWAR word layout (`[bits 0..b-1: lane 0 | bits b..2b-1: lane 1 | ...]`) and recursion invariant in the module header docstring.

39. **`SAIR-LAW-25B` (`SairLaw25bAbbrevLiteralExtraction`) -- Named `abbrev` / `eval_nat%` Extraction Over Magic Literals**
    - **Kernel Mechanism**: Raw multi-limb hexadecimal or decimal literals embedded inline in bitwise expressions are unreadable and error-prone.
    - **Rule**: Extract every non-trivial bitmask, modulus, or lookup constant into a named `abbrev` or `def` generated by an explicit formula (`eval_nat% ((1 <<< 64) - 1)`), paired with a `theorem ... := rfl` sanity pin.

*(Note: Laws `01..25B` comprise 37 distinct diagnostic codes in `lean-analyzer` across Layers I-V: 9 in Layer I, 8 in Layer II, 8 in Layer III, 6 in Layer IV, and 6 in Layer V.)*
