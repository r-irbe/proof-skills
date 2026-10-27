---
name: "isabelle-isar-adapter"
description: |
  USE FOR: translating Isabelle/HOL and Isar proofs (locales, transfer, HOL-Analysis) into Lean 4.
  DO NOT USE FOR: Rocq ports (@rocq-proof-adapter) or HOL/Metamath (@hol-metamath-adapter).
  TRIGGERS: Isabelle, Isar, locale, lift_definition, transfer, Sledgehammer, Isabelle to Lean.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["skill:lean-gateway", "skill:itp-cross-porting", "skill:lean-specification"]
  successors: ["skill:lean-proof", "skill:lean-proof-review", "skill:lean-axiom-closure"]
metadata:
  version: "0.2.0"
  source_spec: "skills/isabelle-isar-adapter/SKILL.md (this file)"
  last_reviewed: "2026-10-27"
---

# Isabelle/HOL & Isar Structured Proof Adapter (`isabelle_hol` -> `lean4`)
Translate Isabelle/HOL theories (`.thy`) -- including structured Isar blocks (`fix` / `assume` / `obtain` /
`have` / `moreover` /
`ultimately` / `show`), `locale` hierarchies, Krauss `function` packages, Lifting & Transfer, and
`HOL-Analysis` filter/measure
proofs --
into idiomatic Lean 4.
## Routing
- **USE FOR:** porting Isabelle/HOL `.thy` files, Archive of Formal Proofs (AFP) developments, seL4/word
  theories, and
  `HOL-Analysis` /
  `HOL-Probability` proofs into Lean 4 + Mathlib4.
- **DO NOT USE FOR:** Rocq/Coq `.v` ports (delegate to `@rocq-proof-adapter`); HOL Light `.ml` or Metamath
  `.mm` ports (delegate
  to
  `@hol-metamath-adapter`).
- **TRIGGERS:** Isabelle, Isar, `.thy`, `locale`, `interpretation`, `obtain ... where`, `also have`, `finally
  show`,
  `lift_definition`, `by
  transfer`, `sledgehammer`, `meson`.
## Workflow
1. **Load Dialect & Concordance Map**: Read `references/dialects/isabelle.json` and query `lean_search(source:
  "concordance")` for
   `CONC-01..20`.
2. **Translate Locales & Type Definitions (`CONC-04`, `CONC-13`, `CONC-14`)**:
   - Single-carrier `locale` / `class` -> Lean 4 `class` (`[Group G]`).
   - Multi-carrier `locale` -> Lean 4 bundled `structure` or multi-parameter typeclass (`[Module R M]`).
   - `quotient_type` + `lift_definition` + `by transfer` -> `Quotient` + `Quotient.lift` +
  `Quotient.inductionOn`.
3. **Translate Isar Structured Blocks (`CONC-02`, `CONC-06`)**:
   - `fix x assume h: "P x"` -> `intro x h`.
   - `obtain w where hw: "Q w" using h by blast` -> `obtain ⟨w, hw⟩ := h`.
## Recovery & STOP
- **STOP** when porting `(f ⤏ l) (at x within s)`: Isabelle's `at x within s` excludes `x` (`𝓝[s \ {x}] x`),
  whereas Mathlib's
  `𝓝[s] x`
  includes `x`! Verify whether `x ∈ s` matters before choosing `𝓝[≠] x` vs `𝓝 x`.
- **STOP** if an Isabelle type definition relies on non-emptiness (`typedef`) where the Lean `Type*` requires
  an `[Inhabited α]`
  or
  `[Nonempty α]` typeclass hypothesis.
## Handoffs
- **Predecessors:** `skill:lean-gateway`, `skill:itp-cross-porting`, `skill:lean-specification`.
- **Successors:** `skill:lean-proof`, `skill:lean-proof-review`, `skill:lean-axiom-closure`.
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/isabelle-isar-adapter-handbook.md`](../../references/isabelle-isar-adapter-handbook.md) .
## See also
- [`../../references/isabelle-isar-adapter-handbook.md`](../../references/isabelle-isar-adapter-handbook.md)
  -- Complete
  `isabelle-isar-adapter` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
