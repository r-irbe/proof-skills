---
name: lean-kernel-optimization-handbook
description: Reference handbook for @lean-kernel-optimization.
extracted_from: skills/lean-kernel-optimization/SKILL.md
---

# Lean 4 Kernel WHNF, ZDD, SWAR, and Proof-Carrying Hardware Codegen Handbook (`KERNEL-LAW-01..31`)

> **Scope**: Public reference manual for Lean 4 kernel reduction cost (`type_checker.cpp` WHNF, `m_st->m_whnf` caching, `@Nat.rec` / `@Bool.rec` dispatch, GMP `mpz` big-integer arithmetic, SWAR word packing, ZDD state compression), the `WAVE-13 G1` Abstraction-Concrete Duality Cost Law, `ADR-INV-0025` step-index vs fuel mechanics, and Proof-Carrying Hardware Lowering (`PolyBitOp` MLIR/PTX/AVX2/C++20, exact vs packed arithmetic boundaries, and 128B wait-free SPSC / `.leangrph` `mmap` / `io_uring` substrates).
> **Encoding**: Scoped Unicode policy (`typographic-free` by default) per `INV-001`.

---

## 1. Quick-Lookup Indexing Tables (`mathcomp-skills` Three-Entry-Point Pattern)

### Table 1: Goal-Shape-First (`templates` Entry Point)

| Goal / Term Shape | Primary Kernel Law(s) | Recommended AltProof Route | Canonical Kernel Pattern / Tactic |
| :--- | :--- | :--- | :--- |
| `let x := e` inside hot `@Nat.rec` step body | `KERNEL-LAW-01`, `KERNEL-LAW-01B`, `ADR-INV-0025` | `kernel-friendly-term-design` | Inline single-use `let` bindings (`Expr::Let` + zeta tax); bind `let x := e` only when `>= 2` uses are dynamically evaluated on the active path AND confirmed by `real - twinlit` PMU |
| Sibling calls `(f x, g (f x))` or `Nat.add (f x) (f x)` | `KERNEL-LAW-01C` | `kernel-friendly-term-design` | Lean's WHNF cache is NOT shared across sibling `Expr` nodes; hoist `let fx := f x` once when `f` is non-trivial |
| Closed expression `(1 <<< 64) - 1` or table inside lambda | `KERNEL-LAW-02`, `KERNEL-LAW-11` | `closed-def-whnf-caching` | Hoist to a top-level closed `def` (memoized in `m_st->m_whnf`) or pre-evaluate at elaboration time via `eval_nat%` |
| Deeply curried `fun a b c d => ...` or `k + 1` step increment | `KERNEL-LAW-02B`, `KERNEL-LAW-03`, `KERNEL-LAW-03B` | `kernel-friendly-term-design` | Place invariant binders outermost; prefer `Nat.succ k` on `@Nat.rec` step accumulators and `Nat.add 1 q` (constant on LHS) on non-structural counters (`ADR-INV-0025`) |
| `termination_by` / `brecOn` or `if h : c then ... else ...` | `KERNEL-LAW-06`, `KERNEL-LAW-07`, `KERNEL-LAW-08` | `kernel-friendly-term-design` | Replace `WellFounded.fix`/`brecOn` with direct `@Nat.rec`; replace `ite`/`dite` (`Decidable` synthesis) with `@Bool.rec` or `cond` (`cond` also compiles in LCNF) |
| Nested tuple state `(a, (b, (c, d)))` or wide CPS arity | `KERNEL-LAW-09`, `KERNEL-LAW-10`, `KERNEL-LAW-24` | `kernel-friendly-term-design` | Flatten into unboxed CPS (`<= 6` scalar registers) or SWAR width-2 word pairs (`KERNEL-LAW-24`: width-2 + 1-bit step beats width-1, width-3, and width-4) |
| Signed recurrence `a - b` or modular polynomial GCD | `KERNEL-LAW-12`, `KERNEL-LAW-12B` | `kernel-friendly-term-design` | Avoid `Int`/`Rat`/`ZMod` boxing in hot kernels; use direct `@Nat.rec` sign-magnitude or unnormalized `(pos, neg)` `Nat` pairs |
| `x * x` on multi-limb (`>= 32` limbs) vs single-limb `Nat` | `KERNEL-LAW-13`, `KERNEL-LAW-13B` | `gmp-swar-word-packing` | `mpz_mul(r, a, a)` triggers `mpn_sqr` above `SQR_TOOM2_THRESHOLD` (~30 limbs), saving `-14%..-21%` in own window (`NR-076`); below ~20 limbs `let`-sharing overhead dominates |
| `n / 2^k`, `n % 2^k`, or base-`B` Horner digit packing | `KERNEL-LAW-14`, `KERNEL-LAW-14B`, `KERNEL-LAW-14C` | `gmp-swar-word-packing` | Replace `/ 2^k` and `% 2^k` with `Nat.shiftRight` and `Nat.land`; aggregate Horner digits in balanced binary chunks aligned to 64-bit GMP limbs (`KERNEL-LAW-16B`) |
| Fixed-width array/DP recurrence or bitboard transition | `KERNEL-LAW-15`, `KERNEL-LAW-16`, `KERNEL-LAW-20` | `gmp-swar-word-packing` | Pack `k` lanes into one GMP `Nat` word (Kronecker SWAR); unroll fixed-trip kernels via binary-doubling combinators (`t0..t6`); evaluate cellular/crypto rules in ANF (`^^^`, `&&&`, `|||`) |
| Finite-state graph/polyomino/automaton frontier search | `KERNEL-LAW-17`, `KERNEL-LAW-18`, `KERNEL-LAW-18B` | `algorithm-class-substitution` | Canonicalize states as CBV `Nat` words (never tree-recurse over lists); compress frontiers as ZDD/bitmasks; count/test 1-bit shift overlaps (`overlap := w &&& (w >>> 1)`) without `Nat` underflow |
| Branching search with lookahead constraints & symmetry | `KERNEL-LAW-19`, `KERNEL-LAW-19B`, `KERNEL-LAW-21` | `algorithm-class-substitution` | Fuse lookahead checks into one bitwise mask guard; short-circuit `Nat.beq avail 0` immediately; prove finite symmetry/heuristic reorderings via decoupled `List.Perm` certificates |
| Parametric hot `def step (cfg : Config)` vs concrete loop | `KERNEL-LAW-22..25B`, `WAVE-13 G1`, `KERNEL-LAW-31` | `abstraction-concrete-duality` | Specialize hot `def`s to raw unboxed `Nat` literals (`1,600x..3,345x` penalty for parametric hot steps!); isolate Section 1 (Spec), Section 2 (Impl), Section 3 (Bridge via `rfl`) |
| Hardware codegen from verified Lean bit/word kernel | `PolyBitOp`, Exact-vs-Packed Lowering | `proof-carrying-codegen` | Emit MLIR (`ctpop`/`gpu.shuffle xor`), Ada `sm_89` PTX, AVX2/AVX-512 Rust, or freestanding C++20; enforce `exact` (`GMP`/`rug`) vs `checked-small -> NeedsWide` overflow traps (`N01..N12`) |
| Dense Kronecker packing of wide polynomial/grid states | `KERNEL-LAW-29`, `KERNEL-LAW-29B`, `KERNEL-LAW-30` | `algorithm-class-substitution` | Avoid artificial contest cutoffs (`KERNEL-LAW-29`) and static lookup tables (`KERNEL-LAW-30`); refute multi-hundred-limb Kronecker huge-`Nat` blowup (`polydisc`) with bounded subresultant/modular limb regimes |
| Discovery automation (`grind`/EqSat) targeting strict `no-grind` | `KERNEL-LAW-31` Discovery-vs-Submission Boundary | `constructive-decidable-reduction` | Discover rewrites via `grind`/`egg`/CP-SAT off-path; materialize explicit 3-axiom proofs (`kernel_decide`) with zero `grind` residue on submission paths |

---

### Table 2: Intent-First (`phrasebook` Entry Point)

| User / Engineer Intent | Target Kernel Law(s) | Actionable Transformation Recipe |
| :--- | :--- | :--- |
| "Speed up `rfl` / `decide +kernel` on a recursive function" | `KERNEL-LAW-06`, `KERNEL-LAW-02`, `KERNEL-LAW-23` | Replace `WellFounded.fix` with direct `@Nat.rec`; hoist closed constants outside step lambdas; replace polymorphic `+`/`*` with `Nat.add`/`Nat.mul` |
| "Abstract repeated proof logic without slowing down the kernel" | `WAVE-13 G1`, `KERNEL-LAW-07`, `KERNEL-LAW-22B` | Keep hot `def` specialized to raw unboxed `Nat` + inline `nat_lit`s; state a parametric proof theorem over abstract step parameters and discharge the concrete instance by `rfl` |
| "Choose `Nat.succ k` vs `Nat.add 1 k` in a tight loop" | `ADR-INV-0025`, `KERNEL-LAW-03` | Use `Nat.succ k` when `k` is consumed by a structural `@Nat.rec` eliminator (`Expr::App(Const("Nat.succ"), k)` directly matches the `succ` arm); use `Nat.add 1 q` for arithmetic counters evaluated to `nat_lit` |
| "Eliminate `Classical.choice` and `Lean.ofReduceBool` from a proof" | `KERNEL-LAW-08`, `KERNEL-LAW-22`, `kernel_decide` | Replace `if`/`split` with `@Bool.rec`/`cond`; close concrete goals with 3-rung `kernel_decide` (`first | rfl | decide +kernel | omega`), never `native_decide` or `bv_decide` on strict 3-axiom lanes |
| "Implement branch-free low-bit cut/mask on `Nat` words" | `KERNEL-LAW-14`, Nov 11-12 Cut/Mask Contract | Exploit truncating `Nat.sub`: when `k <= s`, `k - s = 0` yields `1 <<< 0 - 1 = 0` mask automatically; guard multi-limb shifts with `Nat.ble a (1 <<< (k - s) - 1)` skip-to-plain-shift when profitable |
| "Lower a Lean SWAR/BitVec kernel to C++20, Rust SIMD, or CUDA PTX" | `PolyBitOp`, Exact-vs-Packed Lowering | Prove equivalence to spec in Lean (`Template_ProofCarryingCodegen.lean`), lower pure bitwise kernels via `PolyBitOp`, and guard multi-limb arithmetic with `checked-small -> NeedsWide` + operand snapshotting |
| "Stream verified state transitions over zero-copy IPC / NVMe" | `alignas(128)` SPSC, `.leangrph`, `io_uring` | Separate cache lines to `128 B` (Zen 3 L2 streamer prefetch pair), align `.leangrph` CSR headers to `128 B` (`64 B` magic/counts + `64 B` SHA-256), and register `2 MB` `HugeTLB` buffers with `io_uring` |
| "Square a wide `Nat` (>= 30 limbs) vs an unboxed `< 2^63` scalar" | `KERNEL-LAW-13`, `KERNEL-LAW-13B`, `KERNEL-LAW-30` | Above ~30 GMP limbs use `Nat.pow x 2` (`0.58x` cost via `mpz_pow_ui -> mpn_sqr`) or shared `Nat.mul`; for single-limb `< 2^63` scalars use direct `Nat.mul x x`; exploit linear `O(L)` single-limb x multi-limb scaling vs `O(L^2)` multi-limb products |
| "Harden a strict `no-grind` 3-axiom submission after e-graph discovery" | `KERNEL-LAW-29`, `KERNEL-LAW-30`, `KERNEL-LAW-31` | Enforce Section 1/2/3 split (`KERNEL-LAW-31`), purge lookup tables/band cutoffs (`KERNEL-LAW-29`/`30`), and replace discovery `grind`/`eqsat` traces with direct `kernel_decide` / `rw` proofs |

---

### Table 3: Error / Kernel Bottleneck-First (`errors` Entry Point)

| Symptom / Elaborator Error / Bottleneck | Root Cause in `type_checker.cpp` / Lowering | Remediating Kernel Law(s) & Fix |
| :--- | :--- | :--- |
| `(deterministic) timeout at whnf, maximum number of heartbeats` | Unfolding `WellFounded.fix`/`brecOn`, parametric typeclass dictionaries in hot step (`WAVE-13 G1`), or unshared sibling WHNF trees | `KERNEL-LAW-06` (`@Nat.rec`), `KERNEL-LAW-23` (primitive `Nat.*` constants), `WAVE-13 G1` (monomorphize hot `def`) |
| `code generator does not support recursor 'Nat.rec' / 'Bool.rec'` | Raw `@Nat.rec` / `@Bool.rec` is fast in kernel WHNF (`rfl`), but Lean 4's LCNF native compiler requires structural `match` / `cond` | Use `@Nat.rec`/`@Bool.rec` only in kernel-evaluated `rfl` lanes, OR pair with a computable `@[csimp]` twin using `cond` + structural pattern matching (`KERNEL-LAW-07`, `KERNEL-LAW-08`) |
| Microbenchmark win (`-5%`) turns into full-file regression (`+3%`) | `ADR-INV-0025` Single-Consumer Isolation Paradox: microbench evaluated result directly to WHNF without realistic downstream consumer | Always benchmark inside the real consumer pipeline using `real - twinlit` PMU **sum-of-per-slot-medians-of-three** (`instructions:u`) |
| Wrong answer `0` when isolating lowest set bit with `x &&& (0 - x)` | Truncating `Nat` subtraction evaluates `0 - x = 0` for all `x : Nat`! Two's-complement `-x` only holds on `BitVec w` / `UInt64` | Never write `0 - x` on `Nat`! On `BitVec w` use `x &&& (-x)`; on `Nat` clear lowest bit via `x &&& (x - 1)` (for `x > 0`) or compute 1-bit shift overlap `x &&& (x >>> 1)` (`KERNEL-LAW-18B`) |
| `depends on axiom Lean.ofReduceBool` / `Lean.trustCompiler` | Proof invoked `native_decide`, `decide +native`, or `bv_decide` on a strict 3-axiom target | Switch to 3-rung `kernel_decide` (`first | rfl | decide +kernel | omega`) and verify with `#print axioms` |
| Native Rust/C++ port silently overflows or corrupts aliased buffer | Arbitrary-precision Lean `Nat`/`Int` lowered to fixed `u64`/`i64` without width guard, or in-place `out == lhs` clobbered before read | Enforce `checked-small -> NeedsWide` fallback to `GMP`/`rug`, snapshot aliased inputs before mutation, and run `#eval` vs native conformance vectors `N01..N12` |
| Kronecker polynomial packing regresses kernel time (`polydisc`) | Packing degrees into one huge `> 100`-limb `Nat` induces `O(L^2)` GMP multiplication overhead | Apply `KERNEL-LAW-29B` / `KERNEL-LAW-30`: keep coefficients in bounded limb tuples or subresultant PRS rather than monolithic Kronecker `Nat`s |
| Wide squaring misses `0.58x` GMP speedup or scalar `x ^ 2` regresses | Wrong choice between `Nat.pow x 2` and `Nat.mul x x` across limb regimes | Use `Nat.mul x x` on `< 2^63` scalars (`KERNEL-LAW-13B`) and `Nat.pow x 2` (`mpn_sqr`, `0.58x`) on wide `>= 30`-limb `Nat`s (`KERNEL-LAW-13`/`30`) |

---

## 2. AltProof Routes 7..12 (Kernel WHNF, Constructive & Hardware Codegen Routes)

| Route ID | Family | Match Shape | Rewrite / Transformation Strategy | Yield & Cost Profile |
| :--- | :--- | :--- | :--- | :--- |
| **Route 7**: `algorithm-class-substitution` | `algorithm-class-substitution` | Exponential recursion, naive list enumeration, `List.filter Nat.Prime`, or division-heavy Bareiss elimination | Substitute O(N) / O(N log N) DP, single-pass `primeFactorsList`, or division-free subresultant PRS; prove `fastFn n = specFn n` | **15x-30x** reduction in kernel WHNF steps and `rfl` check time |
| **Route 8**: `kernel-friendly-term-design` | `kernel-friendly-term-design` | `WellFounded.fix`/`brecOn`, `ite` dictionary dispatch, nested `Prod.mk`, or polymorphic typeclasses in hot cones | Rewrite with direct `@Nat.rec` / `cond`, CPS or width-2 SWAR state, primitive `Nat.*` ops, and inline `nat_lit`s | **3x-10x** instruction reduction; avoids `1,600x..3,345x` parametric hot-step penalty |
| **Route 9**: `constructive-decidable-reduction` | `kernel-friendly-term-design` | `Classical.choice` or `Lean.ofReduceBool` leakage in decidable `Nat`/`Int`/`Bool` theorems | Replace classical `split`/`by_cases` with `@Bool.rec`, `Bool.and_eq_true`, `decide +kernel`, or `omega` (`kernel_decide`) | Strict `[propext, Classical.choice, Quot.sound]` (or purely constructive `[]`) axiom closure |
| **Route 10**: `closed-def-whnf-caching` | `kernel-friendly-term-design` | Closed masks, basis tables, or shift-add constants recomputed inside recursive step lambdas | Hoist to top-level closed `def` (`m_st->m_whnf` memoization) in hot kernels; keep human-readable `abbrev` formulas in cold spec/proof sections (`KERNEL-LAW-25B`) | Eliminates per-step closed-term re-reduction |
| **Route 11**: `gmp-swar-word-packing` | `algorithm-class-substitution` | Fixed-width integer/boolean lane arrays, cellular automata, or bounded-degree polynomial convolutions | Pack `k` lanes into one `64*m`-aligned GMP `Nat` word (Kronecker SWAR / ANF) and unroll fixed-trip blocks via binary doubling (`t0..t6`) | **15x-70x** kernel instruction speedup on bitboard and convolution workloads |
| **Route 12**: `proof-carrying-codegen` | `abstraction-concrete-duality` | Verified Lean `BitVec`/`Nat` SWAR kernel targeted at native Rust, C++20, MLIR, or CUDA `sm_89` execution | Prove `@[csimp]` / equivalence bridge in Lean; lower bitwise DAGs via `PolyBitOp` and guard multi-limb arithmetic via `exact` vs `checked-small -> NeedsWide` | Zero-UB hardware execution with bit-exact `#eval` conformance (`N01..N12`) |

---

## 3. Complete Catalog of the Kernel Optimization Laws (`KERNEL-LAW-01..31`)

> **Diagnostic Mapping Note**: `KERNEL-LAW-01..25B` (`39` base laws) plus the architectural/static laws `KERNEL-LAW-26..31` (`26`, `27/27A`, `28`, `29`, `29B`, `30`, `31`) align with `KernelLawAuditor` and `lean-analyzer`'s static diagnostic engine (`src/source_diagnostics.rs`). Note that `KERNEL-LAW-26..28` document both the auditor static checks (`26` constant derivation coverage, `27A` stale doc refs, `28` `maxRecStepLamNodes <= 30`) and the associated WHNF structural patterns (recursor shell specialization, tail-accumulator flattening, and macro AST DAG deduplication).

### Layer I: Memory, Reference Counting, and Substitution (`KERNEL-LAW-01` .. `KERNEL-LAW-05`)

1. **`KERNEL-LAW-01` (`KernelLaw01LetZetaTax`) -- Single-Use `let` Zeta-Expansion Tax**
   - **Kernel Mechanism**: In `type_checker.cpp`, every `Expr::Let` inside a step lambda allocates a node and triggers `instantiate_rev` substitution during zeta-reduction. Moreover, in lazy branches (`@Bool.rec`), hoisting a `let` above the branch forces eager binding construction on paths that discard it.
   - **Rule**: Inline every local `let x := e` referenced at most once on any dynamically taken execution path.

2. **`KERNEL-LAW-01B` (`KernelLaw01bDagSharing`) -- Multi-Use `let` DAG Pointer Sharing (PMU-Qualified)**
   - **Kernel Mechanism**: Binding `let x := e` shares the `Expr` pointer across multiple occurrences in `instantiate_rev`, avoiding duplicate WHNF reduction of `e`. However, `Expr::Let` + `instantiate_rev` itself costs instructions on every step.
   - **Rule**: Use `let x := e` only when `e` is a genuinely expensive compound or multi-limb expression dynamically evaluated `>= 2` times on the active branch, and verify net savings via `real - twinlit` PMU (`catalan` `+12.27%` and `partition` `+4.399%` regressed when over-sharing cheap scalar expressions).

3. **`KERNEL-LAW-01C` (`KernelLaw01cSiblingWhnfCse`) -- Sibling WHNF Common Subexpression Elimination**
   - **Kernel Mechanism**: Lean's `m_whnf` cache memoizes closed constants and specific `Expr` pointers, NOT arbitrary open sibling subtrees `g (f x) (h (f x))` constructed separately.
   - **Rule**: Hoist repeated non-trivial open sibling calls `f x` into a shared `let fx := f x` before constructing the outer application.

4. **`KERNEL-LAW-02` (`KernelLaw02ClosedSubtreeHoist`) -- Closed Subtree Hoisting (`m_st->m_whnf` Cache)**
   - **Kernel Mechanism**: Closed `Expr::Const` declarations (zero free variables / loose `bvar`s) have their WHNF result memoized once per kernel invocation in `m_st->m_whnf`. Open expressions inside lambdas re-reduce on every iteration.
   - **Rule**: Hoist closed masks, basis constants, and lookup words out of recursive lambdas into top-level closed `def`s (or inline pre-evaluated raw `nat_lit` numerals; see `KERNEL-LAW-25B`).

5. **`KERNEL-LAW-02B` (`KernelLaw02bInnerBinderOrder`) -- Invariant-Outermost Binder Ordering**
   - **Kernel Mechanism**: Beta-reduction `instantiate_rev` copies the lambda spine underneath the substituted binder; varying outer arguments copies inner invariant lambdas repeatedly.
   - **Rule**: Place loop-invariant parameters outermost (or specialize them directly in hot kernels) and vary only the innermost state/accumulator binders on `@Nat.rec`.

6. **`KERNEL-LAW-03` (`KernelLaw03ConstantLeftOp`) -- `Nat.add` / `Nat.mul` Small-Constant LHS Placement**
   - **Kernel Mechanism**: When one operand is a small constant (`1 + acc` or `Nat.add 1 q`) and the expression may be inspected symbolically or partially reduced before full `nat_lit` folding, placing the small constant on the non-recursive LHS avoids blocked RHS structural unfolding, while for pure `nat_lit` values `Nat.add 1 q` dispatches directly to C++ `nat_lit` addition (`ADR-INV-0025`).
   - **Rule**: Standardize non-structural arithmetic increments on `Nat.add 1 q` (and structural `@Nat.rec` step indices on `Nat.succ k`; see Section 4.1).

7. **`KERNEL-LAW-03B` (`KernelLaw03bConstantLeftPow2Mask`) -- Power-of-Two Bitmask Canonicalization**
   - **Kernel Mechanism**: `Nat.mod n (2^k)` calls general GMP division `mpz_tdiv_r`, whereas `Nat.land n mask` masks the low limb(s) directly.
   - **Rule**: Replace `% (2^k)` with `Nat.land n mask` where `mask = 2^k - 1` is a raw `nat_lit` or hoisted closed `def`.

8. **`KERNEL-LAW-04` (`KernelLaw04PointFreeEtaWrapper`) -- Point-Free Eta Wrapper & Final-Arg Context Contraction**
   - **Kernel Mechanism**: Eta-expanded closures `fun x => f x` allocate an extra lambda frame and require one extra beta-reduction per step (`-354k` instructions saved on `primecount(10000)` by contracting final-argument step wrappers).
   - **Rule**: Eta-reduce `fun x => f x` to `f` in `@Nat.rec` / fold combinators and inline single-forwarding step wrappers.

9. **`KERNEL-LAW-05` (`KernelLaw05SharedAbbrevMotive`) -- Shared `abbrev` Motive Compression**
   - **Kernel Mechanism**: Repeating complex function-type motives across `@Nat.rec` / `@Bool.rec` nodes inflates `Expr` DAG size and type-inference work.
   - **Rule**: Factor multi-arrow recursor motives into a shared `abbrev Motive := ...`.

---

### Layer II: Inductive & Recursor Dispatch (`KERNEL-LAW-06` .. `KERNEL-LAW-12B`)

10. **`KERNEL-LAW-06` (`KernelBrecOnTax`) -- Direct `@Nat.rec` Over Equation-Compiler `brecOn` / `WellFounded.fix`**
    - **Kernel Mechanism**: Functions compiled via `termination_by` or course-of-values `brecOn` allocate `Below` tuples and accessibility proof terms on every step during `whnf`. Even structural equation-compiler wrappers add auxiliary `_unary` / `brecOn` plumbing compared to raw `@Nat.rec`.
    - **Rule**: In kernel-scored `rfl` definitions, write direct `@Nat.rec` eliminators. *(Compiler Dual-Use Caveat)*: Lean 4's native LCNF compiler rejects raw `@Nat.rec` unless marked `noncomputable` or paired with a computable `@[csimp]` twin (`KERNEL-LAW-07`).

11. **`KERNEL-LAW-07` (`KernelLaw07CsimpDualPath`) -- `@[csimp]` Computable Twin & Dual-Path Architecture**
    - **Kernel Mechanism**: Clean inductive specs (`specFn`) make human review and Mathlib proofs easy, whereas monomorphic SWAR/tail-recursive kernels (`fastFn`) maximize runtime and WHNF speed.
    - **Rule**: Pair `specFn` with `fastFn` via `@[csimp] theorem specFn_eq_fastFn : @specFn = @fastFn` for native LCNF execution, and use `rw [specFn_eq_fastFn]; rfl` for fast kernel proof checking.

12. **`KERNEL-LAW-08` (`KernelLaw08BoolRecOverIte`) -- `@Bool.rec` / `cond` Over `ite` (`Decidable` Elimination)**
    - **Kernel Mechanism**: `if p then t else e` (`ite`) synthesizes a `Decidable p` dictionary and reduces its proof payload in WHNF. Note carefully the argument order of `@Bool.rec`: `@Bool.rec motive falseBranch trueBranch condBool` (`false` arm FIRST, `true` arm SECOND!), whereas `cond condBool trueBranch falseBranch` puts `true` first and is natively supported by Lean 4's LCNF code generator.
    - **Rule**: Replace `ite`/`dite` in hot computational defs with `@Bool.rec` (for minimum WHNF overhead in `rfl`-only kernels, taking extreme care with `false`-first argument order) or `cond` (when native LCNF compilation is also required). Never auto-rewrite `ite` without verifying both branch types and argument order.

13. **`KERNEL-LAW-09` (`KernelLaw09UnboxedProductSpine`) -- Unboxed Product Spine (`Prod.mk` Elimination)**
    - **Kernel Mechanism**: Returning `(a, (b, c))` constructs heap `Prod.mk` nodes and forces `Prod.fst`/`Prod.snd` projection reductions every iteration.
    - **Rule**: Eliminate nested `Prod` tuples in hot loops via CPS scalar passing (`KERNEL-LAW-10`) or packed SWAR `Nat` words (`KERNEL-LAW-15`, `KERNEL-LAW-24`).

14. **`KERNEL-LAW-10` (`KernelLaw10CpsPairElim`) -- CPS Continuation Pair Elimination & Danvy Refunctionalized Closed CPS**
    - **Kernel Mechanism**: Passing state registers as curried arguments to a continuation `k a b c` keeps scalars on the WHNF stack without constructor boxing. Danvy-style refunctionalized closed CPS continuations (`-20.72%` instructions on `bell(60)`) further avoid closure allocation when the continuation family is closed.
    - **Rule**: Replace multi-return tuple helpers with CPS `f x (fun a b => ...)` or refunctionalized closed CPS steps.

15. **`KERNEL-LAW-11` (`KernelLaw11InductivePreHoist`) -- Inductive Step Pre-Hoisting**
    - **Kernel Mechanism**: Expressions inside `@Nat.rec` step lambdas `(fun k ih => ...)` that depend on neither `k` nor `ih` are re-substituted and re-evaluated `N` times.
    - **Rule**: Hoist every `k`/`ih`-invariant expression outside `@Nat.rec`.

16. **`KERNEL-LAW-12` (`KernelLaw12DirectNatRecSign`) -- Direct `@Nat.rec` Parity/Sign Tracking Over `Int`**
    - **Kernel Mechanism**: `Int` operations case-split on `Int.ofNat` vs `Int.negSucc` and allocate constructor wrappers on every arithmetic op in the kernel.
    - **Rule**: Represent alternating signs `(-1)^k` or signed accumulators via boolean parity flags or separate `(posSum, negSum : Nat)` registers in `@Nat.rec`, subtracting once at the outer boundary.

17. **`KERNEL-LAW-12B` (`KernelLaw12bUnboxedQuotientSignDiff`) -- Unboxed Quotient / Division-Free Rational Triples**
    - **Kernel Mechanism**: `Rat`, `ZMod`, and Bareiss exact division (`Int.ediv`, `NR-026` `8.4x` regression) invoke GCD or division normalization at every intermediate step.
    - **Rule**: Keep intermediate rational/polynomial states as unnormalized `Nat` tuples `(numPos, numNeg, den)` or division-free subresultant pseudo-remainders, normalizing only at output.

---

### Layer III: Native GMP Big-Nat & SWAR (`KERNEL-LAW-13` .. `KERNEL-LAW-16B`)

18. **`KERNEL-LAW-13` (`KernelLaw13MultiLimbSquare`) -- Multi-Limb GMP Squaring Window (`>= 30` Limbs)**
    - **Kernel Mechanism**: Lean's `nat_lit * nat_lit` calls GMP `mpz_mul(r, a, b)`. When `a` and `b` share the exact same `Expr`/`mpz` pointer (`let y := x; Nat.mul y y`), GMP dispatches to `mpn_sqr`, beating `mpn_mul_n` via Karatsuba/Toom22 squaring **only above GMP's squaring threshold** (`SQR_TOOM2_THRESHOLD` ~ 28-32 limbs, i.e., `>= 1,800..2,048` bits). In its own multi-limb window (e.g., giant modular exponentiation / Catalan / Fibonacci doubling above 32 limbs), pointer-shared squaring saves **`-14% .. -21%`** (`NR-076` own-window qualification).
    - **Rule**: Bind `let y := expr; Nat.mul y y` when `expr` is non-trivial AND operands exceed ~30 GMP limbs (`>= 2,048` bits).

19. **`KERNEL-LAW-13B` (`KernelLaw13bSingleLimbSquare`) -- Small / Single-Limb Squaring (`< 20` Limbs)**
    - **Kernel Mechanism**: Below ~20 limbs (and especially for single-limb `< 2^62` boxed/unboxed scalars), `mpn_sqr_basecase` offers negligible advantage over `mpn_mul_basecase` while allocating an extra `Expr::Let` incurs `KERNEL-LAW-01` zeta overhead. Never write `x ^ 2` (`Nat.pow x 2`), which unfolds recursion steps!
    - **Rule**: For already-bound variables `x`, always write `Nat.mul x x` directly; for small (<20 limb) expressions, avoid introducing single-purpose `let` wrappers unless `expr` itself is expensive to compute.

20. **`KERNEL-LAW-14` (`KernelPowerOfTwoDivMod`) -- Power-of-Two `Nat.shiftRight` and `Nat.land` + Branch-Free Low-Bit Cut**
    - **Kernel Mechanism**: `Nat.shiftRight n k` (`n >>> k`) and `Nat.land n mask` (`n &&& mask`) avoid GMP division `mpz_tdiv_qr`. Furthermore, Lean's truncating `Nat.sub` gives a **branch-free low-bit cut/mask**: when cutting at bit `k` after shifting by `s`, `(1 <<< (Nat.sub k s)) - 1` automatically evaluates to `0` whenever `k <= s` without an `if`/`Bool.rec` branch! Conversely, when `a < 2^(k - s)` frequently holds on multi-limb words, a conditional skip-to-plain-shift avoids constructing large shift masks.
    - **Rule**: Replace `/ 2^k` and `% 2^k` with `Nat.shiftRight` and `Nat.land`, and exploit `Nat.sub k s = 0` for branch-free low-shift masking.

21. **`KERNEL-LAW-14B` (`KernelLaw14bGmpHornerAsymmetry`) -- Balanced Binary-Splitting Over Asymmetric Horner Packing**
    - **Kernel Mechanism**: Packing `N` lanes via sequential Horner `acc * B + d_i` performs `N` multiplications against a linearly growing `O(N)`-limb accumulator (`O(N^2)` limb ops), whereas balanced binary tree merging (`lo ||| (hi <<< halfWidth)`) performs `O(N log N)` limb copies aligned to word boundaries.
    - **Rule**: Pack large output arrays or multi-thousand-digit witnesses via balanced binary tree shifts rather than linear Horner accumulation.

22. **`KERNEL-LAW-14C` (`KernelLaw14cBitwiseSubpipeline`) -- Pure Bitwise Sub-Pipeline Fusion**
    - **Kernel Mechanism**: Interleaving arithmetic `Nat.add`/`Nat.sub` inside bitwise masking chains forces carry/borrow propagation across GMP limbs and prevents constant mask folding.
    - **Rule**: Fuse consecutive shifts and masks (`(x >>> a) >>> b` -> `x >>> (a + b)`, `(x &&& m1) &&& m2` -> `x &&& (m1 &&& m2)`) and isolate carry-producing arithmetic to explicit sync points.

23. **`KERNEL-LAW-15` (`KernelLaw15SwarWordPacking`) -- Kronecker / SWAR Multi-Lane Word Packing**
    - **Kernel Mechanism**: A single GMP `Nat` word `sum_{i=0}^{k-1} a_i * 2^(i*b)` (with `b` chosen strictly above `ceil(log2(max_lane_val + 1))` to prevent inter-lane carry bleed) executes `k`-lane vector addition (`Nat.add`) or `k x k` polynomial convolution (`Nat.mul`, Kronecker substitution) in **one kernel primitive call**.
    - **Rule**: Pack bounded DP rows, histogram counters, and polynomial coefficients into SWAR `Nat` words with proven carry-free lane widths.

24. **`KERNEL-LAW-16` (`KernelLaw16FixedTripUnroll`) -- Binary-Doubling Combinators (`t0..t6`) Over Manual Copy-Paste**
    - **Kernel Mechanism**: Unrolling `2^m` steps via `t0 := step`, `t1 x := t0 (t0 x)`, ..., `t6 x := t5 (t5 x)` (optionally pre-unfolded via elaboration macros `preunfold%` / `unroll_top%`) eliminates `@Nat.rec` step dispatch while keeping term DAGs compact and human-auditable.
    - **Rule**: Express fixed-trip inner unrolling via binary-doubling combinators rather than monolithic copy-pasted blocks.

25. **`KERNEL-LAW-16B` (`KernelLaw16bGmpLimbAlignment`) -- 64-Bit GMP Limb Boundary Alignment**
    - **Kernel Mechanism**: GMP stores big integers in 64-bit `mp_limb_t` arrays. Shifts `<<< (64 * m)` and `>>> (64 * m)` execute pure word-aligned `mpn_copyi` without cross-limb `mpn_lshift`/`mpn_rshift` funnel shifts.
    - **Rule**: Pad SWAR lane widths `b` (or super-lane block widths) to multiples of `64` bits (`64, 128, 192, 256`) whenever limb growth remains sub-quadratic.

---

### Layer IV: Decision Diagrams, Boolean Algebra, and Search (`KERNEL-LAW-17` .. `KERNEL-LAW-20`)

26. **`KERNEL-LAW-17` (`KernelLaw17CbvStateCanonical`) -- Flat CBV Word State Over Tree-Recursive List Enumeration**
    - **Kernel Mechanism**: Tree-recursive backtracking over `List` / `Array` states allocates O(branching^depth) constructor spines and suffers catastrophic WHNF GC/substitution churn. Encoding states as canonical packed `Nat` words enables O(1) equality/order comparison and flat iterative frontier sweeps.
    - **Rule**: Never use tree-recursive list backtracking in hot kernel solvers; canonicalize states into packed CBV `Nat` words and advance layer-by-layer (`ReadClipped` bounded-window reads when scanning fixed-radius neighborhoods).

27. **`KERNEL-LAW-18` (`KernelLaw18FrontierZddMask`) -- Frontier Bitset / ZDD Transfer-Matrix Compression**
    - **Kernel Mechanism**: Grid/graph counting problems (polyominoes, Hamiltonian paths, independent sets, bounded-height transfer matrices such as four-row height `<= 11` certificates) have exponentially many paths but small boundary frontiers representable as packed ZDD / bitset words.
    - **Rule**: Compress DP frontiers into packed bitsets or canonical ZDD node tables updated via word-level transitions.

28. **`KERNEL-LAW-18B` (`KernelLaw18bSingleBitPopcount`) -- `Nat`-Safe Bit Popcount & 1-Bit Shift Overlap (`w &&& (w >>> 1)`)**
    - **Kernel Mechanism**: **CRITICAL SOUNDNESS RULE**: Never write `x &&& (0 - x)` on `Nat`! Because `Nat.sub` truncates at zero, `0 - x = 0` for all `x : Nat`, silently collapsing `x &&& (0 - x)` to `0`! Two's-complement lowest-bit isolation `x &&& (-x)` is valid **only** on fixed-width `BitVec w` / `UInt64`. On `Nat` bitboards:
      * Clear lowest set bit (for `x > 0`): `Nat.land x (Nat.sub x 1)`.
      * Detect/count adjacent horizontal/vertical cell overlaps in 1 instruction: `let overlap := Nat.land w (Nat.shiftRight w stride)` followed by SWAR parallel popcount (or Kernighan loop bounded by popcount).
    - **Rule**: Use `Nat.land x (Nat.sub x 1)` or shift-overlap `Nat.land w (Nat.shiftRight w s)` on `Nat` words; restrict `-x` bit-tricks strictly to `BitVec w`.

29. **`KERNEL-LAW-19` (`KernelLaw19CombinedLookaheadGuard`) -- Combined Bitwise Lookahead Guard**
    - **Kernel Mechanism**: Chaining `k` sequential `@Bool.rec` feasibility tests evaluates `k` branches per candidate; packing all conflict/boundary masks into one word tests `(candMask &&& conflictMask) == 0` in a single `Nat.beq`.
    - **Rule**: Pre-OR all forbidden-cell, border, and occupancy masks into a single `conflictMask` before inner candidate checks.

30. **`KERNEL-LAW-19B` (`KernelLaw19bZeroMaskPrune`) -- Early Zero-Mask Short-Circuit Pruning**
    - **Kernel Mechanism**: Entering a recursive/step body when `availMask == 0` wastes full binder instantiation and mask unpacking for dead states.
    - **Rule**: Gate recursion immediately on `Nat.beq availMask 0` before computing child state transitions.

31. **`KERNEL-LAW-20` (`KernelLaw20AnfZhegalkinRotation`) -- Algebraic Normal Form (ANF / Zhegalkin) Word-Level Boolean Evaluation**
    - **Kernel Mechanism**: Per-bit `match`/`if` transition tables cost `O(W)` branches per word; Algebraic Normal Form over `Nat.xor`, `Nat.land`, `Nat.lor`, and bit shifts updates all `W` cells in parallel (e.g., Rule 110 `(c ||| r) ^^^ (l &&& c &&& r)` -> `36.48x..70x` WHNF speedup).
    - **Rule**: Compile finite boolean truth tables into minimal-gate ANF word polynomials over shifted `Nat`/`BitVec` lanes.

---

### Layer V: Verification, Anti-Gating, Duality & Clean-Code (`KERNEL-LAW-21` .. `KERNEL-LAW-31`)

32. **`KERNEL-LAW-21` (`KernelLaw21HeuristicListPerm`) -- Decoupled `List.Perm` / Certificate Equivalence Over Ordered Search**
    - **Kernel Mechanism**: Reordering search variables (e.g., fail-first / MRV column ordering in exact cover or SAT) dramatically shrinks the runtime search tree, while proving equivalence directly on the heuristic recursion is intricate. Bridging the reordered solver to the canonical solver via a cold `List.Perm` invariance theorem (`fold_perm` over commutative-associative state joins) costs **zero** runtime WHNF instructions.
    - **Rule**: Run fail-first / symmetry-broken orderings in the hot `def` and justify equivalence in the cold proof section via `List.Perm` or witness certificate checking.

33. **`KERNEL-LAW-22` (`KernelLaw22ZeroPropRuntimeCone`) -- Zero `Prop` / `Fin` / `Subtype` in the Hot Computation Cone**
    - **Kernel Mechanism**: Passing `Fin n` (`⟨val, isLt⟩`), `{x : Nat // P x}`, or `h : x < n` through a hot `def` forces `whnf` to construct and substitute proof terms inside computational steps.
    - **Rule**: Keep every type in the transitive dependency cone of `Submission.impl` strictly free of `Prop`, `Fin`, and `Subtype`; state invariants as external theorems over raw `Nat` / `Bool` / `BitVec`.

34. **`KERNEL-LAW-22B` (`KernelLaw22bHotColdSeparation`) -- Strict Hot Computation Section vs Cold Proof Section Separation**
    - **Kernel Mechanism**: Mixing helper lemmas, `abbrev` spec aliases, or Mathlib tactics into hot `def` bodies risks accidental unfolding of heavy terms during `rfl`.
    - **Rule**: Partition modules into: (1) Named Spec Constants (`abbrev`, cold), (2) Hot Computational Kernel (`def`, raw `Nat.*` + inline `nat_lit`s), and (3) Cold Equivalence & Soundness Proofs (`theorem`).

35. **`KERNEL-LAW-22C` (`KernelLaw22cNamedRecursorBinders`) -- Domain-Named Recursor Binders & Explicit Motive Annotations**
    - **Kernel Mechanism**: Anonymous `(fun _ ih => ...)` or single-letter shadowed `@Nat.rec` spines cause off-by-one bugs between remaining fuel `rem` and upward step index `k`, and confuse human/council auditors.
    - **Rule**: Name every `@Nat.rec` binder by its exact role (`fun stepIdx accWord => ...`) and document bit-field invariants at each loop header.

36. **`KERNEL-LAW-23` (`KernelLaw23ZeroTypeclassHotCone`) -- Zero Typeclass Dictionaries in the Hot Cone**
    - **Kernel Mechanism**: Operators `+`, `-`, `*`, `<<<`, `>>>`, `&&&`, `|||`, `^^^`, `==` elaborate to `HAdd.hAdd instHAddNat ...`, requiring dictionary projection unfolding on every step in `whnf`.
    - **Rule**: In hot kernel loops evaluated by `rfl`, invoke primitive kernel constants directly (`Nat.add`, `Nat.sub`, `Nat.mul`, `Nat.shiftLeft`, `Nat.shiftRight`, `Nat.land`, `Nat.lor`, `Nat.xor`, `Nat.beq`, `Nat.ble`).

37. **`KERNEL-LAW-24` (`KernelLaw24OptimalCpsArity`) -- SWAR Width-2 + 1-Bit Step Optimum & Bounded CPS Arity (`<= 6`)**
    - **Kernel Mechanism**: Empirical PMU sweeps across bitboard/convolution kernels show a sharp Pareto sweet spot: **width-2 SWAR register pairs (`loWord`, `hiWord`) with 1-bit elementary shifts** outperform width-1 (excessive loop trips), width-3, and width-4 (register-spill / `instantiate_rev` arity growth + multi-limb mask overhead), while general CPS continuations peak at `2..6` scalar arguments.
    - **Rule**: Prefer width-2 packed register pairs + 1-bit step transitions on bitboard recurrences, and cap general CPS accumulator arity at `<= 6` scalars.

38. **`KERNEL-LAW-25` (`KernelLaw25ModuleHeaderHumanization`) -- Mandatory Four-Section Module Header & Bit-Layout Diagram**
    - **Kernel Mechanism**: Auditable kernel submissions require explicit documentation of: `## 1. Objective`, `## 2. Architecture & Bit Layout`, `## 3. Kernel Cost Analysis`, and `## 4. Verification Contract`.
    - **Rule**: Include the 4-section module header and ASCII bit-lane diagram in every kernel / SWAR module.

39. **`KERNEL-LAW-25B` (`KernelLaw25bAbbrevLiteralExtraction`) -- Raw `nat_lit` in Hot Defs + Section-1 `abbrev` Spec Pins**
    - **Kernel Mechanism**: Referencing a `reducible` `abbrev` formula (like `abbrev mask := (1 <<< 64) - 1`) inside a hot `@Nat.rec` step **re-unfolds the formula on every step**! Conversely, bare magic numbers in specs are unreadable.
    - **Rule**: Define readable `abbrev` formulas in Section 1 (cold spec), place **pre-computed raw `nat_lit` numerals** (or closed `def` constants cached in `m_st->m_whnf`) inside Section 2 hot `def`s, and connect them in Section 3 with a zero-runtime-cost `theorem hotMask_eq_specMask : hotMask = specMask := rfl` pin!

40. **`KERNEL-LAW-26` (`KernelLaw26DerivationCoverage` / `KernelLaw26RecursorShellSpecialization`) -- Constant Derivation Coverage & Recursor Shell Specialization**
    - **Kernel Mechanism**: Literals `>= 2^16` without derivation formulas or `CONSTANTS-GUIDE` anchors undermine auditability; simultaneously, inline branching lambdas (`Bool.rec`, `Int.rec`) inside `@Nat.rec` exceeding 30 AST nodes force repeated substitution per step.
    - **Rule**: Supply mathematical derivation formulas (or a `CONSTANTS-GUIDE` anchor) for every literal `>= 2^16`, factor branching step bodies into first-order helper `def`s, and keep 100% branch-free arithmetic step bodies inline (`m_st->m_whnf`).

41. **`KERNEL-LAW-27` / `KERNEL-LAW-27A` (`KernelLaw27StaleDocRef` / `KernelLaw27ConstantVectorFlattening`) -- Docstring Hygiene & Unboxed Tail Accumulators**
    - **Kernel Mechanism**: Stale backticked identifiers in docstrings/`#verso` notes mislead auditors; structurally, unpacking/repacking `Prod.rec`/`WPair.rec` inside recursor steps and non-constructor `Nat.add 1 k` thunks incur $\Theta(s^2)$ traversal tax.
    - **Rule**: Eliminate stale docstring/`#verso` symbol references (`27A`), keep accumulators eliminated by `@Nat.rec` in `Nat.succ` constructor-normal form, and flatten multi-variable state into unboxed tail arguments.

42. **`KERNEL-LAW-28` (`KernelLaw28RecStepSize` / `KernelLaw28TwinlitMacroDeduplication`) -- `maxRecStepLamNodes <= 30`, Macro Deduplication & `twinlit` Differential**
    - **Kernel Mechanism**: Elaboration-time macro duplication inflates kernel AST size exponentially and breaks DAG sharing; branching recursor step lambdas above 30 AST nodes degrade step substitution.
    - **Rule**: Keep branching recursor step-lambda bodies `<= 30` AST nodes, factor repeated macro subtrees into closed helper `def`s, and measure pure kernel cost via the proof-irrelevant `real - twinlit` differential `(impl n = impl n) /\ (v = v)` (`⟨rfl, rfl⟩`).

43. **`KERNEL-LAW-29` & `KERNEL-LAW-29B` (`KernelLaw29AntiGatingCutoff` / `KernelLaw29bStructuralRegime`) -- Anti-Gating Ban vs Authentic Hardware/Math Regimes & Kronecker Refutation**
    - **Kernel Mechanism**: Artificial contest-band cutoffs (for example branching at `n <= 961` to a slow quadratic fallback) game benchmarks without genuine algorithmic improvement (`KERNEL-LAW-29`). Conversely, authentic Timsort-style transitions dictated by mathematical structure, `lean_box` `< 2^63` scalar vs multi-limb `mpz_t`, or GMP thresholds are valid (`KERNEL-LAW-29B`). Notably, empirical `polydisc` benchmarking refutes naive Kronecker substitution when packing multivariate coefficients into one multi-hundred-limb `Nat` inflates `O(L^2)` GMP multiplication beyond bounded limb arrays or subresultant PRS.
    - **Rule**: Never insert hardcoded contest-band cutoffs with slow fallbacks (`KERNEL-LAW-29`); dispatch cleanly on intrinsic mathematical or word-width regime boundaries (`KERNEL-LAW-29B`) and reject monolithic Kronecker huge-`Nat` packing when multi-limb multiplication cost dominates.

44. **`KERNEL-LAW-30` (`KernelLaw30ZeroLookupTable`) -- Dynamic Evaluation, Zero Lookup Tables, Wide `Nat.pow x 2` (`0.58x`) & Linear `O(L)` Limb Scaling**
    - **Kernel Mechanism**: Precomputed prime/answer tables (`[11, 13, ...]`) and inline constants `> 2^64` in computational cones substitute memory lookup for algorithmic reduction. Separately, GMP exhibits a sharp crossover across operand widths: on `< 2^63` scalars `Nat.mul x x` avoids `pow` overhead, whereas on wide multi-limb `Nat`s (`>= 30` limbs) **`Nat.pow x (nat_lit 2)` dispatches `mpz_pow_ui -> mpn_sqr`, executing in `0.58x` the instructions of `Nat.mul x x`**! Moreover, single-limb (`< 2^64`) x multi-limb products scale linearly **`O(L)`** via `mpn_mul_1`, avoiding `O(L^2)` multi-limb x multi-limb convolution.
    - **Rule**: Eliminate hardcoded lookup tables and unboxed `> 2^64` constants from Section-2 cones (`KERNEL-LAW-30`, using dynamic sieves per `@lean-asymptotic-algorithms`); use `Nat.pow x 2` on wide multi-limb `Nat`s vs `Nat.mul x x` on `< 2^63` scalars, and preserve `O(L)` single-limb multipliers wherever possible.

45. **`KERNEL-LAW-31` (`KernelLaw31Section123Duality`) -- Section 1/2/3 Abstraction-Concrete Duality & Discovery `grind`/EqSat vs `no-grind` Submission Boundary**
    - **Kernel Mechanism**: Conflating abstract specs (`Prop`, typeclasses) with concrete hot `def`s creates `1,600x..3,345x` WHNF slowdown, while leaving discovery automation (`grind`, `egg`, CP-SAT search) on strict submission paths risks `Lean.ofReduceBool`, excess axioms, or elaboration timeouts.
    - **Rule**: Enforce strict Section 1 (`abbrev` cold specs) / Section 2 (monomorphic zero-`Prop` kernel `def`s) / Section 3 (`rfl` / `@[csimp]` proof bridge + `kernel_decide`) separation (`KERNEL-LAW-31`), and run `grind`/e-graph/CP-SAT strictly in offline discovery while materializing clean `no-grind` 3-axiom proofs (`[propext, Classical.choice, Quot.sound]`).

---

## 4. Foundational Kernel Cost Laws (`ADR-INV-0025`, `WAVE-13 G1`, and Official PMU Metric)

### 4.1 `ADR-INV-0025` -- `@Nat.rec` Step Accumulator (`Nat.succ`) vs Arithmetic Fuel (`Nat.add 1`) & Single-Consumer Isolation Paradox
1. **Constructor vs Primitive Dispatch**:
   - When an accumulator `k` is eliminated downstream by `@Nat.rec`, incrementing via **`Nat.succ k`** builds the constructor `Expr::App(Const("Nat.succ"), k)` directly (`0` GMP calls), allowing `@Nat.rec` to peel `succ` in O(1) iota-reduction without converting a `nat_lit` back into `Nat.succ (Nat.sub n 1)`.
   - When a counter `q` is only combined arithmetically or compared as a `nat_lit`, **`Nat.add 1 q`** folds immediately to a single unboxed `nat_lit` in C++ without building an `O(N)` chain of `Nat.succ` constructors!
2. **Single-Consumer Microbenchmark Isolation Paradox**:
   - Measuring an isolated helper `theorem bench : helper n = v := rfl` can report a synthetic `-3% .. -8%` win (e.g., returning an unforced `Nat.succ` spine or CPS closure) that turns into a **net regression** inside the real caller when the consumer forces `nat_lit` normalization or multi-use projections.
   - **Rule**: Never promote a micro-optimization from an isolated helper harness alone; always measure the **full end-to-end submission theorem** against its `twinlit` control.

### 4.2 `WAVE-13 G1` -- The Abstraction-Concrete Duality Cost Law (`1,600x..3,345x` vs `<= 1%`)
- **Measured Penalty on Hot Computation**: Parameterizing a hot kernel step over abstract functions, typeclasses (`[Semiring R]`), or record configurations (`cfg : StepConfig`) inside `@Nat.rec` inflates kernel WHNF instructions by **`1,600x .. 3,345x`** due to per-step dictionary projection, closure allocation, and blocked `nat_lit` folding.
- **Zero-Runtime-Cost Abstract Proofs**: Keeping `fastStep : Nat -> Nat -> Nat` completely monomorphic and concrete (raw `Nat.*` + inline `nat_lit`), while proving reusable mathematical lemmas over a parametric `abstractStep (f : alpha -> alpha)` in the cold proof section and bridging the concrete kernel via `theorem fast_eq_inst : fastStep = abstractStep concreteCfg := rfl`, incurs **`0` runtime WHNF overhead (`<= 1%` total file instructions)** while eliminating duplicated proof scripts!

### 4.3 Contest 3-Axiom Gate & Official Sum-of-Medians-of-Three `twinlit` PMU Protocol
1. **Strict 3-Axiom Gate (`[propext, Classical.choice, Quot.sound]`)**:
   - **Allowed Axiom Ceiling**: Transitively closed axioms for `Submission.impl_correct` must strictly satisfy:
     $$\text{Axioms}(\text{Submission.impl\_correct}) \subseteq \{\text{propext}, \text{Classical.choice}, \text{Quot.sound}\}$$
   - **Fatal Rejection Axioms**: Any presence of `Lean.ofReduceBool` (introduced by `native_decide` or `bv_decide`) or `sorryAx` (introduced by `sorry` or `admit`) causes immediate and fatal disqualification.
   - **Prohibited Tactics & Attributes on Scored/Proof Paths**:
     - `native_decide`, `decide +native`, `bv_decide` (introduce unapproved axiom `Lean.ofReduceBool`).
     - `sorry`, `admit` (introduce unapproved axiom `sorryAx`).
     - `partial`, `unsafe` (violate totality and kernel reducibility).
     - `@[implemented_by]`, `@[extern]` (compiler-trusting bypasses that invalidate kernel evaluation).
   - **Universal Correctness**: Must prove `impl_correct : ∀ n, impl n = spec n` universally; verifying sample inputs only is fatal rejection.
   - **Canonical 3-rung kernel closer**:
     ```lean
     macro "kernel_decide" : tactic =>
       `(tactic| first | rfl | decide +kernel | omega)
     ```
2. **Sum-of-Per-Slot-Medians-of-Three `real - twinlit` Metric**:
   - For each benchmark slot `i in {1..K}`, run **3 interleaved pairs** `(real_i, twinlit_i)` with `perf stat -e instructions:u`:
     ```lean
     theorem twinlit_slot_i : (impl n_i = impl n_i) /\ (ans_i = ans_i) := ⟨rfl, rfl⟩
     ```
   - Compute `delta_i = median_{r in 1..3}(real_{i,r}) - median_{r in 1..3}(twinlit_{i,r})`, and rank candidates by **`S = sum_{i=1}^K delta_i`**. Taking per-slot medians of 3 eliminates OS page-fault outliers while summing across scale slots weights asymptotic scaling faithfully.

---

## 5. Proof-Carrying Hardware Codegen & Systems Substrates

When extracting verified Lean 4 kernels (`BitVec w`, bounded SWAR `Nat`, or discrete state machines) into production systems code (see [`Template_ProofCarryingCodegen.md`](../../templates/core/Template_ProofCarryingCodegen.md) and [`Template_ProofCarryingCodegen.lean`](../../templates/core/examples/Template_ProofCarryingCodegen.lean)):

### 5.1 `PolyBitOp` Multi-Target Hardware Lowering
Restrict inner bit-parallel kernels to the algebraically verified `PolyBitOp` fragment (`xor`, `and`, `or`, `not`, `shl`, `lshr`, `rotl`, `popcnt`, `clz`, `lane_shuffle`) proven equal to the mathematical specification in Lean, then lower 1-to-1 across four hardware targets:
1. **MLIR Dialect Pipeline**: `arith` + `math.ctpop` + `affine.for` / `memref` + `gpu.shuffle xor` for warp reductions.
2. **NVIDIA Ada Lovelace (`sm_89`) CUDA / PTX**: `lop3.b32` (3-input truth-table fusion in 1 cycle for ANF rules!), `popc.b64`, `shfl.sync.bfly.b32` warp butterfly reductions, `cp.async.cg.shared.global` L2-bypassing 16B stages, and `mma.sync.aligned.m16n8k16` Tensor Core bit/int8 contractions.
3. **Rust SIMD (`#[repr(C, align(64))]`)**: Cache-line-aligned lane blocks lowered to `core::arch::x86_64` AVX2 (`_mm256_xor_si256`, `_mm256_shuffle_epi8` nibble popcount) and AVX-512 `VPOPCNTDQ` / `VPTERNLOGD`.
4. **Freestanding C++20 (`-fno-exceptions -fno-rtti`)**: `constexpr` `std::uint64_t` / `std::popcount` / `std::rotl` templates with static layout assertions (`static_assert(sizeof(State) == 64)`).

### 5.2 Exact-vs-Packed Arithmetic Lowering Boundary (`N01..N12` Conformance)
Lean `Nat` and `Int` have **unbounded precision**, whereas hardware `u64`/`i64`/SIMD lanes wrap or UB on overflow! Every extracted arithmetic operator must declare one of three verified lowering contracts:
1. **`exact` (`GMP` / Rust `rug::Integer`)**: Mandatory when intermediate limbs can exceed 64 bits unconditionally.
2. **`checked-small -> NeedsWide`**: Fast-path unboxed `i64`/`u64` (`checked_add`, `checked_mul`, limb-bound guard `x < (1 << 62)`) that returns `Err(NeedsWide)` (or branches to `exact` scratch replay in **`auto`** mode) on boundary overflow -- proven sound in Lean via bounded-width bridge theorems!
3. **Aliasing & Scratch Discipline**:
   - **Operand Snapshotting**: When destination and source buffers may alias (`out_ptr == lhs_ptr`), snapshot scalar/limb inputs before mutating `out` so multi-limb carry loops never clobber live operands.
   - **Scoped Scratch Temporaries**: Pre-allocate thread-local GMP/`rug` scratch pools outside loops rather than heap-allocating per step.
   - **Differential Gate (`N01..N12`)**: Validate native binaries against Lean `#eval` golden vectors across 12 boundary classes (`0`, `1`, `2^63 - 1`, `2^63`, `2^64 - 1`, `2^64`, multi-limb carry chains, negative zero/truncation, aliased in-place buffers, and `NeedsWide` promotion).

### 5.3 Zero-Copy Memory, Cache-Line, and I/O Substrates
1. **128-Byte Cache-Line Isolation (`alignas(128)` / `#[repr(C, align(128))]`)**:
   - On AMD Zen 3/4/5 and modern x86_64, the L2 adjacent-line streamer prefetches **128-byte pairs** (`2 x 64 B`). Separating producer `head` and consumer `tail` indices in wait-free SPSC ring buffers by `128 B` eliminates false-sharing coherence invalidations across CCX/NUMA domains.
2. **128-Byte `.leangrph` CSR `mmap` Header**:
   - Binary proof/state graphs use a fixed `128 B` header (`64 B` magic + schema version + node/edge/offset counts + `64 B` SHA-256 payload digest) followed by `64 B`-aligned Compressed Sparse Row (`row_offsets : u64[]`, `col_indices : u32[]`) arrays mapped zero-copy via `MAP_SHARED | MAP_POPULATE`.
3. **Linux `io_uring` + `2 MB` `HugeTLB` Direct DMA**:
   - Pre-register `O_DIRECT` `2 MB` `MAP_HUGETLB` fixed buffers (`IORING_REGISTER_BUFFERS`) aligned to NVMe 4096B logical sectors to eliminate page-cache copies and TLB shootdowns during high-throughput trace/certificate streaming.
