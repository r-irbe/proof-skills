/-
metric_sync: theorem count paper/description sync

Goals:
- Recompute the codebase theorem count from source.
- Update the paper appendix/description so the claimed theorem count matches code.

Non-goals:
- Do not change theorem statements or proofs.
- Do not revise unrelated paper prose.

Invariants:
- The paper appendix theorem count must equal the code-derived count.
- The counting rule must be documented and reproducible.
- Generated/build artifacts must not be counted.

Procedure:
1. Run `python3 scripts/metric_sync.py` to count `^theorem|^lemma`
   declarations per module.
2. Record the exact theorem count, counting rule, and command output.
3. Update the paper's `\description` list and contribution-inventory
   totals with the same count.
4. Re-run the count and documentation checks.

Minimal example:
- If `scripts/metric_sync.py` reports 120 theorem/lemma declarations,
  the paper appendix and contribution-inventory total must both say 120.

Pathological example:
- The appendix says 120, the contribution inventory says 118, and the
  code count says 121; do not average these counts. Stop and reconcile.

Acceptance criteria:
- The appendix and codebase report the same theorem count.
- The change mentions metric_sync or theorem count.
- Reviewers can reproduce the count from documented commands.

Tests:
- Execute theorem-count script successfully.
- Run documentation/link checks if present.
- Run Lean build or smoke test if required by the repo.

STOP/handoff conditions:
- Stop if the count command is missing or ambiguous.
- Stop if multiple paper/description locations disagree.
- Hand off with command output, files inspected, and unresolved discrepancy.
-/
