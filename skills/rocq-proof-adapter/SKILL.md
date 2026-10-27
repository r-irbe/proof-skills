---
name: "rocq-proof-adapter"
description: |
  USE FOR: translating Rocq / Coq proofs (SSReflect, MathComp, Ltac2, lia/lra) into Lean 4.
  DO NOT USE FOR: Isabelle ports (@isabelle-isar-adapter) or HOL/Metamath (@hol-metamath-adapter).
  TRIGGERS: Rocq, Coq, SSReflect, MathComp, move:, elim:, bigop, Coq to Lean.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["skill:lean-gateway", "skill:itp-cross-porting", "skill:lean-specification"]
  successors: ["skill:lean-proof", "skill:lean-proof-review", "skill:lean-axiom-closure"]
metadata:
  version: "0.2.0"
  source_spec: "skills/rocq-proof-adapter/SKILL.md (this file)"
  last_reviewed: "2026-10-27"
---

# Rocq / Coq & MathComp Proof Adapter (`coq_mathcomp` -> `lean4`)
Translate Rocq/Coq formalizations -- including SSReflect intro/discharge pipelines (`move:`, `elim:`, `case:`,
`rewrite //=`),
Mathematical
Components (`finType`, `bigop`, `matrix`), Hierarchy Builder (`HB.instance`), and `Equations` -- into
idiomatic Lean 4.
## Routing
- **USE FOR:** porting Coq/Rocq `.v` theories, SSReflect proof scripts, MathComp algebraic/combinatorial
  developments, and
  MathComp-Analysis
  filter/measure proofs into Lean 4.
- **DO NOT USE FOR:** Isabelle `.thy` theories (delegate to `@isabelle-isar-adapter`); HOL Light `.ml` or
  Metamath `.mm` files
  (delegate to
  `@hol-metamath-adapter`).
- **TRIGGERS:** Rocq, Coq, SSReflect, MathComp, `move:`, `elim:`, `case:`, `apply/`, `\big[`, `finType`,
  `zmodType`,
  `HB.instance`, `lia`,
  `lra`.
## Workflow
1. **Load Dialect & Concordance Map**: Read `references/dialects/rocq.json` and query `lean_search(source:
  "concordance")` for the
  relevant
   `CONC-01..20` mechanisms.
2. **Translate Signatures & Canonical Structures (`CONC-04`, `CONC-13`, `CONC-17`)**:
   - Map `(T : finType)` -> `{T : Type*} [Fintype T] [DecidableEq T]`.
   - Map `(R : ringType)` / `(R : comRingType)` -> `{R : Type*} [Ring R]` / `[CommRing R]`.
   - Map `\sum_(i < n | P i) F i` -> `∑ i ∈ Finset.univ.filter P, F i` (over `Fin n`).
3. **Translate SSReflect Bookkeeping to Structured Lean 4**:
   - `move=> x /andP [h1 h2]` -> `rintro x ⟨h1, h2⟩` (since Lean `And` needs no boolean view `/andP`).
   - `elim: n => [| n ih] //=` -> `induction n with | zero => simp | succ n ih => ...`.
## Recovery & STOP
- **STOP** if an SSReflect `rewrite` relies on keyed canonical-structure projection unification that fails in
  Lean's type-directed
  `rw`;
  state the intermediate step explicitly with `have` or `calc`.
- **STOP** if `ssrnat` truncated subtraction `m - n` is used as a boolean predicate `m - n == 0` for `m <= n`;
  translate `m <= n`
  directly
  to `Nat.le` (`m <= n`) and solve with `omega`.
## Handoffs
- **Predecessors:** `skill:lean-gateway`, `skill:itp-cross-porting`, `skill:lean-specification`.
- **Successors:** `skill:lean-proof`, `skill:lean-proof-review`, `skill:lean-axiom-closure`.
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/rocq-proof-adapter-handbook.md`](../../references/rocq-proof-adapter-handbook.md) .
## See also
- [`../../references/rocq-proof-adapter-handbook.md`](../../references/rocq-proof-adapter-handbook.md) --
  Complete
  `rocq-proof-adapter` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
