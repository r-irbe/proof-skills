---
name: "lean-replay-verification"
description: |
  USE FOR: verifying that completed proofs are genuinely kernel-checked after `sorry` removal; running the replay ladder (fresh rebuild, axiom-closure audit, cross-version replay, independent-kernel recheck) so an acceptance is not an artifact of stale build state, a hidden axiom, or a single kernel's bug; recording replay evidence for review.
  DO NOT USE FOR: writing or fixing the proof itself (use @lean-proof); reviewing statement faithfulness (use @lean-proof-review); routine incremental builds during development (use @lean-build); project QA scoring (use @lean-quality-engine).
  TRIGGERS: sorry removed, proof completed, replay, fresh rebuild, kernel replay, independent verification, cross-version check, axiom audit, "is the proof really correct", load-bearing result, pre-merge proof gate.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
---

# Replay Verification After Sorry Removal

## Why

An incremental `lake build` re-elaborates only changed modules. That is
enough to kernel-check the edited proof, but it is NOT evidence that the
tree's acceptance is real: stale `.olean` artifacts, a partially applied
edit, or a single kernel release's bug can all make a tree "finish
successfully" without the completed proof being re-checked from a cold
state. Trust in a finished proof should rest on a replay ladder, not on
one incremental green build.

## The replay ladder (R1 -> R4, increasing independence)

- **R1 - fresh kernel replay (same kernel, cold state).** A full build
  from a clean build directory (`lake clean` + `lake build`, or a fresh
  worktree's first build). Kills every stale-artifact and partial-state
  false-accept class. REQUIRED on the commit that removes a `sorry`.
- **R2 - axiom-closure audit.** `#print axioms` over the touched
  declarations (or a project-wide axiom audit against an explicit
  expected-axioms allowlist). `sorryAx` and any non-standard axiom in
  the closure = FAIL. This bounds the trust base to the named axioms
  and catches sorries hiding behind wrappers or aliases.
- **R3 - cross-version replay.** Rebuild the same proofs at the next
  toolchain pin when one is available. A different kernel RELEASE is
  the practical second opinion; institutionalize via the project's
  upgrade/migration campaign rather than ad-hoc. A deferral (no newer
  pin yet) MUST be recorded, not skipped silently.
- **R4 - independent-kernel recheck (load-bearing results).** Export
  the proofs and check them with an independent implementation.
  Known checkers: trepplein (Scala; genuinely independent lineage;
  checks Lean's exported proof terms) and lean4lean (complete Lean 4
  typechecker written in Lean; fast enough for Mathlib-scale corpora,
  but derived from the C++ kernel, so it shares some implementation
  bug classes - weaker independence, still useful). Record WHICH
  checker and version, and the caveat.

## Behavioural rules (G-*)

- **G-1** (MUST): the commit that removes a `sorry` MUST record R1
  replay evidence: toolchain (exact pin/SHA), job/module count,
  exit status. "It builds" from an incremental build is not replay
  evidence. [R1]
- **G-2** (MUST): the R2 axiom-closure audit MUST pass against an
  explicit allowlist of expected axioms; empty or missing allowlist
  makes the audit meaningless. [R2]
- **G-3** (MUST NOT): an incremental build MUST NOT be presented as
  replay evidence in a review, ledger, or commit message. [R1]
- **G-4** (MUST): when a newer toolchain pin exists, R3 MUST either
  run or carry a recorded deferral with the reason. [R3]
- **G-5** (SHOULD): load-bearing result batches SHOULD get R4 with a
  named independent checker; record checker name, version, and the
  lineage caveat when the checker shares kernel lineage. [R4]
- **G-6** (MUST NOT): a cold replay MUST NOT destroy shared in-flight
  state on a multi-writer tree without coordination - clean in an
  agreed window or an isolated worktree, never under active lanes.

## Workflow

1. Identify the proof-completion event (sorry removed / new theorem
   accepted as load-bearing).
2. Run R1 (cold full build); capture pin, job count, rc into the
   commit message or ledger.
3. Run R2 against the expected-axioms allowlist; quote the verdict.
4. Check R3 status: is a newer pin available? Run it via the
   project's migration flow or record the deferral.
5. For load-bearing batches, run R4 with trepplein or lean4lean and
   record checker + version + lineage caveat.
6. Link the replay evidence from the review record (commit, ledger,
   or review file) so a later reader can re-derive it.

## Pitfalls

- Incremental green build presented as replay (G-3) - the most common
  laundering of weak evidence.
- After `lake clean`, dependency caches (e.g. Mathlib's) must be
  re-fetched; budget for it, do not silently skip it.
- `#print axioms` on a wrapper can look clean while the INNER lemma
  is sorry-ed - audit the full closure, not one name.
- lean4lean shares code lineage with the C++ kernel; trepplein covers
  exported proof terms but check its format-version coverage against
  the toolchain's export format.
- A replay re-runs everything: on multi-writer trees coordinate the
  clean (G-6) or other lanes' tooling will fight the missing artifacts.

## Verification

- R1 evidence present (pin, job count, rc) for the sorry-removal commit.
- R2 verdict quoted against the named allowlist: no `sorryAx`, no
  non-standard axioms.
- R3 run or deferred-with-reason, recorded.
- R4 (when applicable): checker name + version + caveat recorded.
