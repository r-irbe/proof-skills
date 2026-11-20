---
id: zk-013
title: Proof-carrying hardware codegen -- PolyBitOp, CheckedWord, and N01..N12
created: 2026-11-15
updated: 2026-11-15
type: permanent
tags: [codegen, swar, simd, simt, bitvec]
refs:
  - zk-011
  - zk-012
  - zk-014
status: validated
confidence: high
---

# Proof-carrying hardware codegen -- PolyBitOp, CheckedWord, and N01..N12

**Claim.** Verified systems kernels (SWAR, AVX2/AVX-512 SIMD, CUDA `sm_89` PTX `lop3.b32`/`cp.async`, lock-free 128-byte SPSC rings, and `io_uring` alignment gates) should be specified as width-polymorphic Lean 4 `BitVec w` / `PolyBitOp` circuits and `CheckedWord` overflow guards (`needsWide`), proved equivalent to mathematical specs via `bv_decide` / `omega`, and checked bit-exactly against `#eval` test vectors under gates `N01..N12`.

**Evidence.** Implemented and kernel-verified in `templates/core/Template_ProofCarryingCodegen.md` and `templates/core/examples/Template_ProofCarryingCodegen.lean`. `PolyBitOp.eval_xor_self` proves polymorphic width-invariant algebraic identities once for all `w`, while `CheckedWord.widen_exact` certifies zero unsigned truncation whenever `needsWide = false`.

**Implication.** Hardware optimization no longer relies on unverified C++/CUDA intrinsics. Combine the kernel WHNF laws in [[zk-011]] with the spec-compute duality in [[zk-012]] to synthesize zero-UB native code, and enforce static soundness invariants continuously via the two-tier WASM analyzer in [[zk-014]].

See also: [[zk-011]], [[zk-012]], [[zk-014]].
