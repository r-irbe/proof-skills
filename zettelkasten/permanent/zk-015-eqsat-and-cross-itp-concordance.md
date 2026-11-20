---
id: zk-015
title: Pure-Lean equality saturation and cross-ITP concordance
created: 2026-11-15
updated: 2026-11-15
type: permanent
tags: [eqsat, egg, cross-itp, tactics, concordance]
refs:
  - zk-001
  - zk-008
  - zk-014
status: validated
confidence: high
---

# Pure-Lean equality saturation and cross-ITP concordance

**Claim.** Commutative and associative-congruence rewrite loops where directional `simp` diverges are cleanly discharged in pure Lean 4 (`import Lean` only, zero external Rust FFI binaries) via bounded meet-in-the-middle equality saturation (`eqsat_rw` / `egg_rw`) paired with core `grind_close` and `backchain` (`SolveByElim`), while cross-prover ports from Rocq, Isabelle/Isar, HOL Light, Agda, and Metamath map deterministically through mechanisms `CONC-01..CONC-20`.

**Evidence.** Verified in `packages/altproof/AltProof/Core.lean` (`saturateEquality` reconstructs 3-axiom clean `Eq.trans` / `Eq.symm` / `congrArg` / `congrFun` kernel terms) and `vendor/itp-ontology/cross-itp-concordance.v1.json` (served offline by `lean_cross_itp_concordance` in [[zk-014]]).

**Implication.** Eliminating out-of-process C/Rust dynamic-library FFI keeps `AltProof.Core` 100% portable across air-gapped sandboxes and strict 3-axiom kernel lanes while adhering to the tactic priority hierarchy in [[zk-008]] and the project-agnostic override design in [[zk-001]].

See also: [[zk-001]], [[zk-008]], [[zk-014]].
