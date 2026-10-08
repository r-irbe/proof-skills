---
name: "lean-proof-refactor"
description: |
  USE FOR: slimming long proofs after they are proven (decomposition into reusable lemmas), adjudicating long-proof findings (cut vs considered-negative), extracting shared helper lemmas without regressions, running a proof-refactor campaign with quality gates.
  DO NOT USE FOR: reviewing proofs for correctness (use @lean-proof-review); writing a first proof (use @lean-proof); finding tautology/vacuity candidates (use @lean-tautology-triage); project-wide QA orchestration (use @lean-quality-engine).
  TRIGGERS: long-proof, decompose proof, slim proof, helper-lemma extraction, proof is too long, proof_quality, refactor campaign.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ["skill:lean-proof", "skill:lean-quality-engine"]
  successors: ["skill:lean-proof-review", "skill:lean-proof"]
metadata:
  version: "0.1.0"
  source_spec: "campaign methodology distilled from a 13-decomposition series (2026-09/10)"
  last_reviewed: "2026-10"
---

# Lean Proof Refactoring (post-hoc proof slimming)

A proven proof that is long is a maintenance liability and a reuse
opportunity. This skill runs the campaign loop that turns long proofs
into short callers plus named, reusable lemmas - without regressions.

## Routing

- **USE FOR:** finding and adjudicating long-proof findings; extracting
  shared lemmas; running multi-batch refactor campaigns.
- **DO NOT USE FOR:** first-time proving, correctness review, tautology triage.

## Workflow

1. **Find** - scan the corpus for long proofs. A generic scanner exists:
   `scripts/lean/proof_quality.py --lean-dir <dir> --output <report.md>`
   (line count + branch points + style classes). Repos wrap it with
   their own config defaults; never edit the scanner per-repo.
2. **Adjudicate each finding** against one test: *can a generic block be
   named once and called elsewhere?* Three verdicts:
   - **CUT** - extract the shared lemma (see 3).
   - **CONSIDERED-NEGATIVE** - the proof is single-use glue; record the
     reason in the tracking doc. Forcing a cut creates single-use
     lemmas (the bundle effect: extraction that only relocates length).
   - **DEFER** - branchy or threshold-sitting proofs wait for a calmer
     window (2 branch points +  50 lines is the sweet spot).
3. **Extract** - the lemma statement must be *more general* than the
   caller's need (finite type, arbitrary functions), placed where
   callers of its shape live, and proved independently. The caller
   keeps a one-line bridge. If the extracted lemma is itself long
   (~36+ lines) but *reusable and library-worthy*, that is the good
   bundle effect - record it as such.
4. **Gate** - full corpus build (0 errors, 0 warnings), test suite,
   and the scanner re-run. The metric line: `60 -> 52` per target.
   One regression anywhere stops the batch.
5. **Record** - per-batch ledger entry: target, extraction, measured
   before/after, verdicts for the non-cuts. A considered-negative with
   no recorded reason will be rediscovered and re-litigated.

## Pitfalls

- Folding a `rw` and a `simp only` into one call: `rw` cannot unfold
  definitions by name; `simp only` can. The two-step form is often
  load-bearing (the folded term must match the callee's unfolded
  conclusion for `nlinarith` atom-matching).
- Linter-suggested renames are not always drop-in: a "use `_name`"
  advice breaks declarations that reference the binder in their TYPE;
  a deprecation rename may swap argument order. Build after every
  rename class; revert on first error and record why.
- In shared build directories, stale-olean errors are transient -
  retry once before diagnosing.

## Handoffs

- **Predecessors:** `lean-proof` (the proof exists), `lean-quality-engine` (findings).
- **Successors:** `lean-proof-review` (audit the extraction), `lean-proof` (fix the caller).
