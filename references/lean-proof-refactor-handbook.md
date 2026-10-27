---
name: "lean-proof-refactor-handbook"
description: "Reference handbook for @lean-proof-refactor."
extracted_from: "skills/lean-proof-refactor/SKILL.md"
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

## AltProof 3-Tier Tactic Slimming & Advisor

When refactoring verbose algebraic, big-operator (`Finset.sum`), or finite-simplex proofs, combine helper-lemma extraction with the 3-tier AltProof
pipeline (template: [Template_AltProofTactics.md](../../templates/Template_AltProofTactics.md)):

1. **Tier 1 (Live Lean 4 Meta-Tactics)**:
   - `sum_congr_ring`: normalizes `Finset.sum` linearity (`sum_add_distrib`, `sum_sub_distrib`, `mul_sum`, `sum_mul`, `sum_neg_distrib`) and closes
     equalities of sums by pointwise `ring` inside `Finset.sum_congr rfl`.
   - `finset_mono`: discharges `Finset.sum s f <= Finset.sum s g` (including nested double sums) via `Finset.sum_le_sum`, automatic specialization of
     universally quantified context hypotheses (`h : forall i, ...`), and ordered-ring monotonicity closers (`gcongr`, `linarith`, `nlinarith`,
     `positivity`, `omega`).
   - `finset_nonneg`: discharges `0 <= Finset.sum s f` (single or nested sums) via `Finset.sum_nonneg` + `positivity` / `linarith` / `nlinarith` / `omega`.
   - `wellformed_tac` & `channel_fields`: shape-driven structural closers for finite-simplex and Markov-channel obligations over `Fin 1..8`.
   - `elegance?` / `alt_proof`: speculative search (`withoutModifyingState`) across 13 ranked closers, reporting the highest-ranked closer via `Try this:
     <tactic>`.
2. **Tier 2 (MCP Goal Advisor & Two-Axis Scorer)**:
   - Query `lean_goal(file, line, target="altproof")` or `lean_metrics(file, action="altproof", goal=..., proof=...)` to obtain ranked tactic
     recommendations, verbose-lean4 legibility scores (`verbose_score`), and two-axis elegance/kernel-cost dominance verdicts.
   - Offline CLI fallback: `python3 scripts/lean/altproof_tactic_advisor.py --goal "<goal>" --proof "<block>"`.

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

## Recovery

- If a candidate helper extraction fails to compile or increases total proof complexity without reuse, revert the cut and record a `CONSIDERED-NEGATIVE`
  entry in the batch ledger.
- On transient stale-`.olean` errors in shared build directories, retry the targeted build once before diagnosing a proof regression.

## Handoffs

- **Predecessors:** `lean-proof` (the proof exists), `lean-quality-engine` (findings).
- **Successors:** `lean-proof-review` (audit the extraction), `lean-proof` (fix the caller).
