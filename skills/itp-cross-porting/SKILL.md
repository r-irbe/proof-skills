---
name: "itp-cross-porting"
description: |
  USE FOR: porting proofs across Lean 4, Rocq, Isabelle, HOL Light, Agda, and Metamath (CONC-01..20).
  DO NOT USE FOR: single-prover Lean 4 proving (@lean-proof) or Mathlib PRs (@lean-upstream-porting).
  TRIGGERS: cross-ITP port, translate proof, Agda to Lean, concordance, CONC-01.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["skill:lean-gateway", "skill:lean-research", "skill:lean-specification"]
  successors:
    - "skill:rocq-proof-adapter"
    - "skill:isabelle-isar-adapter"
    - "skill:hol-metamath-adapter"
    - "skill:lean-proof"
    - "skill:lean-proof-review"
metadata:
  version: "0.2.0"
  source_spec: "skills/itp-cross-porting/SKILL.md (this file)"
  last_reviewed: "2026-10-27"
---

# Cross-ITP Proof Porting & Concordance Router (`CONC-01..20`)
Coordinate proof and specification translation across the 6 supported Interactive Theorem Prover (ITP)
families (`lean4`,
`coq_mathcomp`,
`isabelle_hol`, `hol_light`, `agda`, `metamath`) using `vendor/itp-ontology/cross-itp-concordance.v1.json` and
`references/dialects/*.json`.
## Routing
- **USE FOR:** end-to-end cross-prover translation planning, Agda <-> Lean 4 ports, multi-prover concordance
  queries
  (`lean_search(source:
  "concordance")`), and routing dialect-specific translations to `@rocq-proof-adapter`,
  `@isabelle-isar-adapter`, or
  `@hol-metamath-adapter`.
- **DO NOT USE FOR:** standard Lean 4 proof authoring without a foreign source proof (delegate to
  `@lean-proof`); porting existing
  Lean 4
  corpus lemmas into Mathlib4 PRs (delegate to `@lean-upstream-porting`).
- **TRIGGERS:** cross-ITP port, translate proof, Agda to Lean, Coq to Lean, Isabelle to Lean, HOL Light to
  Lean, Metamath to Lean,
  `CONC-01`..`CONC-20`.
## Workflow
1. **Identify Source Prover & Foundation Delta**: Classify the source artifact (`coq_mathcomp`,
  `isabelle_hol`, `hol_light`,
  `agda`,
   `metamath`) and load its dialect table from `references/dialects/<dialect>.json`.
2. **Query Concordance (`lean_search(source: "concordance")`)**: Map each foreign proof mechanism (`CONC-01`
  through `CONC-20`) to
  its
   idiomatic Lean 4 counterpart rather than translating line-by-line tactical plumbing.
3. **Dispatch Dialect Adapter when Specialized**:
   - Rocq / Coq / SSReflect / MathComp -> `@rocq-proof-adapter`
   - Isabelle/HOL / Isar / locales -> `@isabelle-isar-adapter`
   - HOL Light / Metamath (`set.mm`) -> `@hol-metamath-adapter`
## Recovery & STOP
- **STOP** if a foreign proof relies on untyped partiality or set-theoretic junk values that falsify the naïve
  Lean 4 translation;
  add
  explicit domain preconditions via `@lean-specification`.
- **STOP** if porting from Agda/Coq introduces a custom `axiom` in Lean 4; map classical/extensional
  postulates to Lean's standard
  `[propext, Classical.choice, Quot.sound]`.
## Handoffs
- **Predecessors:** `skill:lean-gateway`, `skill:lean-research`, `skill:lean-specification`.
- **Successors:** `skill:rocq-proof-adapter`, `skill:isabelle-isar-adapter`, `skill:hol-metamath-adapter`,
  `skill:lean-proof`,
  `skill:lean-proof-review`.
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/itp-cross-porting-handbook.md`](../../references/itp-cross-porting-handbook.md) .
## See also
- [`../../references/itp-cross-porting-handbook.md`](../../references/itp-cross-porting-handbook.md) --
  Complete
  `itp-cross-porting` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
