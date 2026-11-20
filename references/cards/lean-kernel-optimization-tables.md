---
name: "lean-kernel-optimization-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-kernel-optimization-handbook.md."
generated_from: "references/handbooks/lean-kernel-optimization-handbook.md"
skill_ref: "skills/lean-kernel-optimization/SKILL.md"
---

# `lean-kernel-optimization` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-kernel-optimization-handbook.md`](../handbooks/lean-kernel-optimization-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| `let x := e` inside hot `@Nat.rec` step body | `KERNEL-LAW-01`, `KERNEL-LAW-01B`, `ADR-INV-0025` | `kernel-friendly-term-design` |
| Sibling calls `(f x, g (f x))` or `Nat.add (f x) (f x)` | `KERNEL-LAW-01C` | `kernel-friendly-term-design` |
| Closed expression `(1 <<< 64) - 1` or table inside lambda | `KERNEL-LAW-02`, `KERNEL-LAW-11` | `closed-def-whnf-caching` |
| Deeply curried `fun a b c d => ...` or `k + 1` step increment | `KERNEL-LAW-02B`, `KERNEL-LAW-03`, `KERNEL-LAW-03B` | `kernel-friendly-term-design` |
| `termination_by` / `brecOn` or `if h : c then ... else ...` | `KERNEL-LAW-06`, `KERNEL-LAW-07`, `KERNEL-LAW-08` | `kernel-friendly-term-design` |
| Nested tuple state `(a, (b, (c, d)))` or wide CPS arity | `KERNEL-LAW-09`, `KERNEL-LAW-10`, `KERNEL-LAW-24` | `kernel-friendly-term-design` |
| Signed recurrence `a - b` or modular polynomial GCD | `KERNEL-LAW-12`, `KERNEL-LAW-12B` | `kernel-friendly-term-design` |
| `x * x` on multi-limb (`>= 32` limbs) vs single-limb `Nat` | `KERNEL-LAW-13`, `KERNEL-LAW-13B` | `gmp-swar-word-packing` |
| `n / 2^k`, `n % 2^k`, or base-`B` Horner digit packing | `KERNEL-LAW-14`, `KERNEL-LAW-14B`, `KERNEL-LAW-14C` | `gmp-swar-word-packing` |
| Fixed-width array/DP recurrence or bitboard transition | `KERNEL-LAW-15`, `KERNEL-LAW-16`, `KERNEL-LAW-20` | `gmp-swar-word-packing` |
| Finite-state graph/polyomino/automaton frontier search | `KERNEL-LAW-17`, `KERNEL-LAW-18`, `KERNEL-LAW-18B` | `algorithm-class-substitution` |
| Branching search with lookahead constraints & symmetry | `KERNEL-LAW-19`, `KERNEL-LAW-19B`, `KERNEL-LAW-21` | `algorithm-class-substitution` |
| Parametric hot `def step (cfg : Config)` vs concrete loop | `KERNEL-LAW-22..25B`, `WAVE-13 G1` | `abstraction-concrete-duality` |
| Hardware codegen from verified Lean bit/word kernel | `PolyBitOp`, Exact-vs-Packed Lowering | `proof-carrying-codegen` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| "Speed up `rfl` / `decide +kernel` on a recursive function" | `KERNEL-LAW-06`, `KERNEL-LAW-02`, `KERNEL-LAW-23` | Replace `WellFounded.fix` with direct `@Nat.rec`; hoist closed constants outside step lambdas; replace polymorphic `+`/`*` with `Nat.add`/`Nat.mul` |
| "Abstract repeated proof logic without slowing down the kernel" | `WAVE-13 G1`, `KERNEL-LAW-07`, `KERNEL-LAW-22B` | Keep hot `def` specialized to raw unboxed `Nat` + inline `nat_lit`s; state a parametric proof theorem over abstract step parameters and discharge the concrete instance by `rfl` |
| "Choose `Nat.succ k` vs `Nat.add 1 k` in a tight loop" | `ADR-INV-0025`, `KERNEL-LAW-03` | Use `Nat.succ k` when `k` is consumed by a structural `@Nat.rec` eliminator (`Expr::App(Const("Nat.succ"), k)` directly matches the `succ` arm); use `Nat.add 1 q` for arithmetic counters evaluated to `nat_lit` |
| "Eliminate `Classical.choice` and `Lean.ofReduceBool` from a proof" | `KERNEL-LAW-08`, `KERNEL-LAW-22`, `kernel_decide` | Replace `if`/`split` with `@Bool.rec`/`cond`; close concrete goals with 3-rung `kernel_decide` (`first |
| "Implement branch-free low-bit cut/mask on `Nat` words" | `KERNEL-LAW-14`, Nov 11-12 Cut/Mask Contract | Exploit truncating `Nat.sub`: when `k <= s`, `k - s = 0` yields `1 <<< 0 - 1 = 0` mask automatically; guard multi-limb shifts with `Nat.ble a (1 <<< (k - s) - 1)` skip-to-plain-shift when profitable |
| "Lower a Lean SWAR/BitVec kernel to C++20, Rust SIMD, or CUDA PTX" | `PolyBitOp`, Exact-vs-Packed Lowering | Prove equivalence to spec in Lean (`Template_ProofCarryingCodegen.lean`), lower pure bitwise kernels via `PolyBitOp`, and guard multi-limb arithmetic with `checked-small -> NeedsWide` + operand snapshotting |
| "Stream verified state transitions over zero-copy IPC / NVMe" | `alignas(128)` SPSC, `.leangrph`, `io_uring` | Separate cache lines to `128 B` (Zen 3 L2 streamer prefetch pair), align `.leangrph` CSR headers to `128 B` (`64 B` magic/counts + `64 B` SHA-256), and register `2 MB` `HugeTLB` buffers with `io_uring` |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| `(deterministic) timeout at whnf, maximum number of heartbeats` | Unfolding `WellFounded.fix`/`brecOn`, parametric typeclass dictionaries in hot step (`WAVE-13 G1`), or unshared sibling WHNF trees | `KERNEL-LAW-06` (`@Nat.rec`), `KERNEL-LAW-23` (primitive `Nat.*` constants), `WAVE-13 G1` (monomorphize hot `def`) |
| `code generator does not support recursor 'Nat.rec' / 'Bool.rec'` | Raw `@Nat.rec` / `@Bool.rec` is fast in kernel WHNF (`rfl`), but Lean 4's LCNF native compiler requires structural `match` / `cond` | Use `@Nat.rec`/`@Bool.rec` only in kernel-evaluated `rfl` lanes, OR pair with a computable `@[csimp]` twin using `cond` + structural pattern matching (`KERNEL-LAW-07`, `KERNEL-LAW-08`) |
| Microbenchmark win (`-5%`) turns into full-file regression (`+3%`) | `ADR-INV-0025` Single-Consumer Isolation Paradox: microbench evaluated result directly to WHNF without realistic downstream consumer | Always benchmark inside the real consumer pipeline using `real - twinlit` PMU **sum-of-per-slot-medians-of-three** (`instructions:u`) |
| Wrong answer `0` when isolating lowest set bit with `x &&& (0 - x)` | Truncating `Nat` subtraction evaluates `0 - x = 0` for all `x : Nat`! Two's-complement `-x` only holds on `BitVec w` / `UInt64` | Never write `0 - x` on `Nat`! On `BitVec w` use `x &&& (-x)`; on `Nat` clear lowest bit via `x &&& (x - 1)` (for `x > 0`) or compute 1-bit shift overlap `x &&& (x >>> 1)` (`KERNEL-LAW-18B`) |
| `depends on axiom Lean.ofReduceBool` / `Lean.trustCompiler` | Proof invoked `native_decide`, `decide +native`, or `bv_decide` on a strict 3-axiom target | Switch to 3-rung `kernel_decide` (`first |
| Native Rust/C++ port silently overflows or corrupts aliased buffer | Arbitrary-precision Lean `Nat`/`Int` lowered to fixed `u64`/`i64` without width guard, or in-place `out == lhs` clobbered before read | Enforce `checked-small -> NeedsWide` fallback to `GMP`/`rug`, snapshot aliased inputs before mutation, and run `#eval` vs native conformance vectors `N01..N12` |
