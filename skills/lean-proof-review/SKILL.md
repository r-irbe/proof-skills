---
name: "lean-proof-review"
description: |
  USE FOR: reviewing one Lean 4 proof / file for correctness, soundness, statement faithfulness, non-triviality.
  DO NOT USE FOR: writing a new proof (@lean-proof).
  TRIGGERS: proof review, audit proof, verify Lean, 4-layer checklist.
tier: "hot"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-proof"]
  successors: ["skill:lean-review-council", "skill:lean-enforcement", "skill:lean-doc-feedback"]
metadata:
  version: "0.2.2"
  source_spec: "specs/lean/proof-review/requirements.md"
  last_reviewed: "2026-10-20"
---

# lean-proof-review

> ⚠️ **MANDATORY** (hot-tier): layers L1 (soundness) and L2 (statement) are
> hard gates — a failure at either MUST block sign-off, regardless of L3/L4.
> Skipping Persist = incomplete.

## Routing

- **USE FOR:** auditing a single Lean 4 proof or file across the 4-layer checklist (L1 soundness, L2 statement, L3 non-triviality, L4 quality);
  cross-checking that imported tactics from the project automation stack are used correctly; spotting common pitfalls (vacuous truth, unused hypothesis,
  broken simp set, scope drift).
- **DO NOT USE FOR:** authoring the proof (delegate to `@lean-proof`); convening a multi-agent review (delegate to `@lean-review-council`); running the CI
  scripts (delegate to `@lean-enforcement`).
- **TRIGGERS:** proof review, audit proof, verify Lean, 4-layer checklist, lean-pitfalls, proof quality.

## Behavioural rules (G-*)

- **G-1** (MUST): The reviewer MUST run the four layers in order (L1 → L2 → L3 → L4); a failure at L1 or L2 MUST halt the review. [Trace: AC-01]
- **G-2** (MUST): The reviewer MUST verify the theorem statement matches the source spec / paper / requirement before judging the proof. [Trace: AC-02]
- **G-3** (MUST NOT): The reviewer MUST NOT silently rewrite the proof; suggested rewrites MUST be flagged as suggestions for the author. [Trace: AC-03]
- **G-4** (SHOULD): The reviewer SHOULD recommend the higher-quality tactic when a lower-priority one was used unnecessarily (see
  [`REFERENCE.md`](./REFERENCE.md) "Proof Search Priority"). [Trace: AC-04]
- **G-5** (MUST): A non-trivial theorem with a one-tactic `decide` / `aesop` / `grind` close MUST be flagged for L3 (non-triviality) review. [Trace: AC-05]
- **G-6** (SHOULD NOT): The reviewer SHOULD NOT mark a proof "approved" without confirming `lake build` is green on the containing file. [Trace: AC-06]
- **G-7** (MUST): Every flagged finding MUST cite the layer, the line(s), and the rule from `REFERENCE.md` or `GUARDRAILS.md`. [Trace: AC-07]
- **G-8** (MUST): On any guard failure the skill MUST escalate per §Recovery & STOP. [Trace: AC-08]

## Workflow

1. **Discover** [discover] — read the target file, locate the theorem(s), find the source spec and any prior review record.
2. **L1 soundness** [validate] — confirm no `sorry`, no `admit`, no `sorryAx`, and no unauthorized `Lean.ofReduceBool` via `lean_axiom_closure`
   (`{"symbol": "...", "module": "..."}`) and `lean_diagnostics` (`{"filePath": "..."}`); defer to `@lean-enforcement` for full-module axiom audit if
   needed.
3. **L2 statement** [validate] — diff the theorem statement against the spec / paper; enforce **Check 5** (Necessity & Sufficiency `↔` Pairing for executable `Bool` checkers — no `ONE_WAY_BOOL_CHECKER`), **Check 6** (Precondition Tightness & Boundary Counterexample Witness — no `NAT_SUB_UNGUARDED` or `MISALIGNED_DOCSTRING`), and **Check 7** (100% Barrel Completeness & `Classical.choice`-Free Constructive Gate); check `lean-analyzer` static diagnostics (`NatSubTruncation`, `NatDivModByZero`, `HypothesisEcho`, `ReflexiveTautology`, `NatNonnegTriviality`, `UnusedUnderscoreBinder`, `OneWayBoolChecker`, Zone DBM `decreasing_by` synthesis, Octagon conservation `±x_i ± x_j <= c`, Bourdoncle WTO loop widening, trace partitioning) for silent statement distortions; halt if it has drifted.
4. **L3 non-triviality** [validate] — confirm the hypothesis is non-vacuous; run automated vacuity and specification-fidelity detectors (`python3 scripts/lean/proof_quality.py`, `python3 scripts/lean/tautology_scan.py`, and `lean_metrics` with `action: "proof_fidelity"` in `lean-lsp-mcp`) to catch `HYPOTHESIS_ECHO`, `REFLEXIVE_TAUTOLOGY`, `NAT_NONNEG_TRIVIALITY`, `NAT_SUB_UNGUARDED`, `MISALIGNED_DOCSTRING`, `UNUSED_VALUE_OR_UNDERSCORE_BINDER`, and `ONE_WAY_BOOL_CHECKER`; use `lean_counterexample_search` (`{"filePath": "...", "theoremName": "...", "strategy": "dense"}`, backed by Galois-guided hypothesis domain pruning via `analyzeHeaderHypothesisDomains` / `pruneHeaderNatDomain`) when a statement or helper lemma looks suspect, and hand off to `@lean-tautology-triage` on P1/P2 flags.
5. **L4 quality** [validate] — run `lean-rules` (`node tools/lean-lsp-mcp/bin/lean-rules.js`) and `pi-lens` (`pilens_ast_grep_search`, `pilens_diagnostics`) as sub-second structural pre-checks before `lake build`, plus `lean_goal` (`target: "altproof"`) to evaluate proof-search priority (`bv_decide` for `BitVec`/SWAR goals, `constructive-decidable-reduction` to eliminate `Classical.choice` leakage, `SWAR_BIT_PACKING_SUBSTITUTION`) and two-axis elegance/heartbeat cost; flag tactic mis-selection, bare `simp`, dagger-variable references, unused hypothesis, and fragile rewrite chains; suggest improvements but do NOT apply them.
6. **Persist** [persist] *(MANDATORY)* — write the review record (per-layer status, findings, suggestions) to the repository's review log, link it from the
   theorem, update sign-off state. Skipping Persist = incomplete.

## Recovery & STOP

- L1 fails (`sorry` / `admit` / `sorryAx`) → STOP, do NOT proceed to L2-L4; escalate to author.
- L2 fails (statement drift) → STOP, escalate to spec owner before any proof judgement.
- `lake build` red on containing file → STOP, ask author to fix build first.
- Confidence < 90 % on a tactic suggestion → mark as advisory, do NOT block.
- Scope drift (edits to non-proof files) → immediate STOP, re-anchor.

## Handoffs

- **Predecessors / successors:** see FM `handoffs` (grammar from ADR-0080).
- **Source spec:** `specs/lean/proof-review/requirements.md` — every G-rule traces to an AC there.
- **Related ADRs:** ADR-0076, ADR-0080.
- **Reference:** see [`REFERENCE.md`](./REFERENCE.md) for the full project automation stack, proof-search priority table, reusable `Tactics` lemma library,
  common Lean pitfalls, and the 4-layer verification checklist (original v1 content, preserved verbatim).
- **Mathlib-specific review:** see [`../../references/upstream/mathlib4-review.md`](../../references/upstream/mathlib4-review.md) for the Mathlib PR review
  delta (attributes/API, simp squeezing, normal forms, transparency, file size, canonical naming/style URLs). The former `mathlib-review` SKILL has been
  demoted to a REDIRECT stub pointing at this reference (W4 Wave 1 / move A2).

## Common failure modes

> AI agents commonly: rewrite the proof inline instead of suggesting changes;
> approve at L4 without confirming L1/L2 passed; miss vacuous-truth L3
> failures behind a clean `aesop` close; cite a pitfall without quoting line
> numbers or the source rule; accept an "independent routes" claim without
> checking it — when a project claims two or more independent proofs of one
> theorem, verify the routes actually share no machinery (imports, helper
> lemmas, substrate definitions) before repeating the independence claim in
> a review verdict. Full registry: GUARDRAILS.md §Agent failure taxonomy.
