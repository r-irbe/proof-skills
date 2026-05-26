---
name: "lean-proof-review"
description: |
  USE FOR: reviewing one Lean 4 proof / file for correctness, soundness, statement faithfulness, non-triviality, and proof quality; running the 4-layer verification checklist (formal soundness → statement → non-triviality → quality); flagging common Lean pitfalls; recommending tactic alternatives from the Mathlib + Aesop + Duper + Canonical stack.
  DO NOT USE FOR: writing a new proof (use @lean-proof); multi-agent council deliberation (use @lean-review-council); running CI scripts (use @lean-enforcement); scoring the whole project (use @lean-quality-engine).
  TRIGGERS: proof review, audit proof, verify Lean, 4-layer checklist, lean-pitfalls, proof quality.
tier: "hot"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-proof"]
  successors: ["skill:lean-review-council", "skill:lean-enforcement", "skill:lean-doc-feedback"]
metadata:
  version: "0.2.0"
  source_spec: "specs/lean/proof-review/requirements.md"
  last_reviewed: "2026-05-27"
---

# lean-proof-review

> ⚠️ **MANDATORY** (hot-tier): layers L1 (soundness) and L2 (statement) are
> hard gates — a failure at either MUST block sign-off, regardless of L3/L4.
> Skipping Persist = incomplete.

## Routing

- **USE FOR:** auditing a single Lean 4 proof or file across the 4-layer checklist (L1 soundness, L2 statement, L3 non-triviality, L4 quality); cross-checking that imported tactics from the project automation stack are used correctly; spotting common pitfalls (vacuous truth, unused hypothesis, broken simp set, scope drift).
- **DO NOT USE FOR:** authoring the proof (delegate to `@lean-proof`); convening a multi-agent review (delegate to `@lean-review-council`); running the CI scripts (delegate to `@lean-enforcement`).
- **TRIGGERS:** proof review, audit proof, verify Lean, 4-layer checklist, lean-pitfalls, proof quality.

## Behavioural rules (G-*)

- **G-1** (MUST): The reviewer MUST run the four layers in order (L1 → L2 → L3 → L4); a failure at L1 or L2 MUST halt the review. [Trace: AC-01]
- **G-2** (MUST): The reviewer MUST verify the theorem statement matches the source spec / paper / requirement before judging the proof. [Trace: AC-02]
- **G-3** (MUST NOT): The reviewer MUST NOT silently rewrite the proof; suggested rewrites MUST be flagged as suggestions for the author. [Trace: AC-03]
- **G-4** (SHOULD): The reviewer SHOULD recommend the higher-quality tactic when a lower-priority one was used unnecessarily (see [`REFERENCE.md`](./REFERENCE.md) "Proof Search Priority"). [Trace: AC-04]
- **G-5** (MUST): A non-trivial theorem with a one-tactic `decide` / `aesop` / `grind` close MUST be flagged for L3 (non-triviality) review. [Trace: AC-05]
- **G-6** (SHOULD NOT): The reviewer SHOULD NOT mark a proof "approved" without confirming `lake build` is green on the containing file. [Trace: AC-06]
- **G-7** (MUST): Every flagged finding MUST cite the layer, the line(s), and the rule from `REFERENCE.md` or `GUARDRAILS.md`. [Trace: AC-07]
- **G-8** (MUST): On any guard failure the skill MUST escalate per §Recovery & STOP. [Trace: AC-08]

## Workflow

1. **Discover** [discover] — read the target file, locate the theorem(s), find the source spec and any prior review record.
2. **L1 soundness** [validate] — confirm no `sorry`, no `admit`, no `sorryAx`; defer to `@lean-enforcement` for axiom audit if needed.
3. **L2 statement** [validate] — diff the theorem statement against the spec / paper; halt if it has drifted.
4. **L3 non-triviality** [validate] — confirm the hypothesis is non-vacuous; spot pattern-match for hidden trivialities.
5. **L4 quality** [validate] — apply the proof-search priority table; flag tactic mis-selection, unused hypothesis, fragile rewrite chains; suggest improvements but do NOT apply them.
6. **Persist** [persist] *(MANDATORY)* — write the review record (per-layer status, findings, suggestions) to the project's review log, link it from the theorem, update sign-off state. Skipping Persist = incomplete.

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
- **Reference:** see [`REFERENCE.md`](./REFERENCE.md) for the full project automation stack, proof-search priority table, reusable `Tactics` lemma library, common Lean pitfalls, and the 4-layer verification checklist (original v1 content, preserved verbatim).

## Common failure modes

> AI agents commonly: rewrite the proof inline instead of suggesting changes;
> approve at L4 without confirming L1/L2 passed; miss vacuous-truth L3
> failures behind a clean `aesop` close; cite a pitfall without quoting line
> numbers or the source rule. Full registry: GUARDRAILS.md §Agent failure
> taxonomy.
