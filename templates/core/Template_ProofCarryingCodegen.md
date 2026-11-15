# `Template_ProofCarryingCodegen.md` -- Proof-Carrying SWAR/SIMD/SIMT Hardware Lowering & Substrates (v3.1)

> **Status**: v3.1 canonical template (`@lean-sair-kernel-optimization` + `@lean-proof-refactor`).
> **Compile-tested exemplar**: [`examples/Template_ProofCarryingCodegen.lean`](examples/Template_ProofCarryingCodegen.lean).
> **Handbook**: [`../../references/handbooks/lean-sair-kernel-optimization-handbook.md`](../../references/handbooks/lean-sair-kernel-optimization-handbook.md) (§5).

---

## 1. Architecture: Spec -> Verified `PolyBitOp` / `CheckedWord` -> Multi-Target Native Code

Never hand-port unverified bit-tricks or map unbounded Lean `Nat`/`Int` directly to wrapping `u64`/`i64` registers. Every extracted high-performance kernel follows a 3-layer proof-carrying contract:

1. **Layer A -- Clean Mathematical Spec (`Prop` / `Bool` / unbounded `Nat`/`Int`)**: Human-auditable specification free of word-size or SIMD lane assumptions.
2. **Layer B -- Verified Lowering IR in Lean 4**:
   - **`PolyBitOp` Gate DAG**: Pure bitwise/shift/popcount operations (`^^^`, `&&&`, `|||`, `<<<`, `>>>`, ANF polynomials) proven equal to Layer A via exhaustive `cases` or structural induction.
   - **Exact-vs-Packed Arithmetic Boundary (`exact` vs `checked-small -> NeedsWide`)**: Explicit width-guarded fast path (`w <= 2^62 - 1`) with proven equivalence to unbounded `Nat`/`Int` and deterministic promotion to multi-limb `GMP`/`rug` scratch pools on `NeedsWide`.
3. **Layer C -- Target-Specific Hardware Emission + Differential `N01..N12` Gate**:
   - Lower 1-to-1 to **MLIR**, **CUDA `sm_89` PTX**, **Rust AVX2/AVX-512**, or **Freestanding C++20**, and verify bit-exact agreement against `#eval` across boundary vectors `N01..N12`.

---

## 2. `PolyBitOp` 4-Target Lowering Matrix

| Verified Lean `PolyBitOp` | MLIR Dialect Op | CUDA Ada `sm_89` PTX | Rust (`#[repr(C, align(64))]`) | Freestanding C++20 (`-fno-exceptions -fno-rtti`) |
| :--- | :--- | :--- | :--- | :--- |
| 3-input ANF `(c \|\|\| r) ^^^ (l &&& c &&& r)` | `arith.ori` + `arith.andi` + `arith.xori` | `lop3.b32 d, l, c, r, 0x6e;` (1 cycle) | `_mm256_xor_si256` / `_mm512_ternarylogic_epi64` | `constexpr uint64_t` bitwise inline |
| Word popcount | `math.ctpop %w : i64` | `popc.b64 %d, %w;` | `w.count_ones()` / `VPOPCNTDQ` | `std::popcount(w)` |
| Power-of-two slot `idx &&& (2^k - 1)` | `arith.andi %idx, %mask` | `and.b64 %slot, %idx, %mask;` | `idx & ((1usize << k) - 1)` | `idx & ((1ULL << k) - 1ULL)` |
| Warp / lane butterfly reduction | `gpu.shuffle xor %v, %off, %w` | `shfl.sync.bfly.b32 %d, %v, %off, 0x1f, 0xffffffff;` | `_mm256_permute4x64_epi64` + horizontal add | `std::rotl` / SIMD intrinsics |

---

## 3. Exact-vs-Packed Arithmetic & Aliasing Contract (`N01..N12`)

When lowering Lean `Nat`/`Int` recurrences to native Rust or C++20:

1. **Three Lowering Modes**:
   - `exact`: Unconditional arbitrary-precision (`rug::Integer` / `mpz_t`) with pre-allocated thread-local scratch temporaries (zero heap allocations inside hot loops).
   - `checked-small`: Unboxed 62/63-bit integer fast path returning `Result<i64, NeedsWide>` (`CheckedWord.small` vs `CheckedWord.needsWide` in [`examples/Template_ProofCarryingCodegen.lean`](examples/Template_ProofCarryingCodegen.lean)).
   - `auto`: Runs `checked-small` first and transparently replays from step boundary in pre-allocated `exact` scratch registers upon `NeedsWide`.
2. **Operand Snapshotting (Aliasing Safety)**:
   - In destination-passing C++/Rust kernels `fn op(out: &mut LimbBuf, lhs: &LimbBuf, rhs: &LimbBuf)` where `out` may alias `lhs` or `rhs`, **snapshot scalar/limb inputs before mutating `out`** so carry propagation never reads overwritten limbs.
3. **Mandatory Differential Conformance Suite (`N01..N12`)**:
   - Compare `#eval` output in Lean against compiled Rust/C++/CUDA output on: `N01` (`0`), `N02` (`1`), `N03` (`2^62 - 1` max small), `N04` (`2^62` `NeedsWide` trigger), `N05` (`2^63 - 1`), `N06` (`2^63`), `N07` (`2^64 - 1`), `N08` (`2^64` 2-limb carry), `N09` (`2^256 - 1` 4-limb), `N10` (truncating `Nat.sub` at `a < b`), `N11` (aliased `out == lhs`), and `N12` (10,000-step stateful recurrence).

---

## 4. Zero-Copy Memory, Cache-Line & Direct-I/O Substrates

Pair verified transition kernels with mechanical-sympathy systems layouts:

```cpp
// Freestanding C++20 128-Byte Zen 3/4/5 SPSC Ring Header (prevents L2 streamer false sharing)
#include <atomic>
#include <cstdint>

struct alignas(128) SpscRingHeader {
    alignas(128) std::atomic<std::uint64_t> head{0}; // Producer-owned 128B line pair
    alignas(128) std::atomic<std::uint64_t> tail{0}; // Consumer-owned 128B line pair
    std::uint64_t capacity_mask;                     // (1ULL << k) - 1ULL (proven == % 2^k)
};
static_assert(sizeof(SpscRingHeader) == 384);
```

- **`.leangrph` Zero-Copy CSR `mmap` Format**: `128 B` header (`64 B` magic `"LEANGRPH"` + version + `num_nodes` + `num_edges` + `64 B` SHA-256) + `64 B`-aligned `row_offsets` (`u64`) and `col_indices` (`u32`).
- **`io_uring` Direct DMA**: Register `2 MB` `MAP_HUGETLB` buffers via `IORING_REGISTER_BUFFERS` with `O_DIRECT` 4096B sector alignment for zero-copy certificate/trace ingestion.
