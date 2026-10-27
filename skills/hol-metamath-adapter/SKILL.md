---
name: "hol-metamath-adapter"
description: |
  USE FOR: translating HOL Light (.ml tactical scripts) and Metamath (set.mm ZFC proofs) into Lean 4.
  DO NOT USE FOR: Rocq ports (@rocq-proof-adapter) or Isabelle ports (@isabelle-isar-adapter).
  TRIGGERS: HOL Light, Metamath, set.mm, MESON_TAC, REAL_ARITH_TAC, WORD_BLAST, uzind, 3eqtri.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["skill:lean-gateway", "skill:itp-cross-porting", "skill:lean-specification"]
  successors: ["skill:lean-proof", "skill:lean-proof-review", "skill:lean-axiom-closure"]
metadata:
  version: "0.2.0"
  source_spec: "skills/hol-metamath-adapter/SKILL.md (this file)"
  last_reviewed: "2026-10-27"
---

# HOL Light & Metamath (`set.mm`) Proof Adapter (`hol_light` / `metamath` -> `lean4`)
Translate HOL Light OCaml tactical scripts (`THEN`, `THENL`, `MESON_TAC`, `REAL_ARITH_TAC`, `REAL_RING`,
`WORD_BLAST`, `real^N`
analysis)
and Metamath `set.mm` ZFC deduction trees (`syl`, `mpd`, `3eqtri`, `uzind`, `fsum`, extensible slot
structures) into structured
Lean 4 +
Mathlib4.
## Routing
- **USE FOR:** porting HOL Light `.ml` theorems (multivariate analysis, Flyspeck, `s2n-bignum` word proofs)
  and Metamath `set.mm`
  /
  `iset.mm` theorems into Lean 4.
- **DO NOT USE FOR:** Rocq/MathComp `.v` ports (delegate to `@rocq-proof-adapter`); Isabelle/Isar `.thy` ports
  (delegate to
  `@isabelle-isar-adapter`).
- **TRIGGERS:** HOL Light, Metamath, `set.mm`, `MESON_TAC`, `REAL_ARITH_TAC`, `REAL_RING`, `WORD_BLAST`,
  `SUBGOAL_THEN`, `3eqtri`,
  `uzind`,
  `fsum`.
## Workflow
1. **Load Dialect & Concordance Map**: Read `references/dialects/hol_light.json` or
  `references/dialects/metamath.json` and query
   `lean_search(source: "concordance")` for `CONC-01..20`.
2. **Lift Untyped / Predicate Domains to Lean Types (`CONC-04`, `CONC-14`)**:
   - Metamath `x e. N`, `y e. R`, `G e. Grp` -> typed binders `(x : Nat)`, `(y : Real)`, `{G : Type*} [Group
  G]`.
   - HOL Light `s : A -> bool` finite sums `nsum (m..n) f` -> `∑ i ∈ Finset.Icc m n, f i`.
3. **Collapse Low-Level Plumbing Chains into High-Level Tactics (`CONC-05`, `CONC-13`, `CONC-18`)**:
   - Collapse 20-100 step Metamath `syl`/`mpd`/`addass`/`leadd1i` chains into `tauto`, `ring`, `linarith`,
  `omega`, or
  `positivity`.
## Recovery & STOP
- **STOP** when porting Metamath `m - n` where `m, n e. N`: in `set.mm`, `N c_ Z c_ C` so `2 - 5 = -3`,
  whereas in Lean `(2 - 5 :
  Nat) = 0`!
  Either cast to `Int` via `zify` or prove `n <= m` before using `Nat.sub`.
- **STOP** when porting HOL Light `has_integral` on improper oscillating functions; verify `IntegrableOn f s
  volume` for Mathlib
  Bochner
  integration.
## Handoffs
- **Predecessors:** `skill:lean-gateway`, `skill:itp-cross-porting`, `skill:lean-specification`.
- **Successors:** `skill:lean-proof`, `skill:lean-proof-review`, `skill:lean-axiom-closure`.
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/hol-metamath-adapter-handbook.md`](../../references/hol-metamath-adapter-handbook.md) .
## See also
- [`../../references/hol-metamath-adapter-handbook.md`](../../references/hol-metamath-adapter-handbook.md) --
  Complete
  `hol-metamath-adapter` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
