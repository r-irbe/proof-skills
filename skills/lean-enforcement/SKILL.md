---
name: "lean-enforcement"
description: |
  USE FOR: running programmatic CI / pre-review / post-review gates for a Lean 4 project — axiom audit, council precheck, review coverage, metric sync, zettelkasten lint, bridge validation, proof quality, ecosystem health, workflow gate enforcement.
  DO NOT USE FOR: semantic / judgement review (use @lean-proof-review or @lean-review-council); orchestrating the broader QA lifecycle (use @lean-quality-engine); routing tasks across skills (use @lean-gateway).
  TRIGGERS: enforcement, CI gate, axiom audit, council_precheck, workflow_gate, ecosystem_health, sorry check.
tier: "hot"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-quality-engine"]
  successors: ["skill:lean-review-council", "skill:lean-proof-review", "skill:lean-retro-methodology"]
metadata:
  version: "0.2.0"
  source_spec: "specs/lean/enforcement/requirements.md"
  last_reviewed: "2026-05-27"
---

# lean-enforcement

> ⚠️ **MANDATORY** (hot-tier): blocking scripts (`council_precheck.sh`,
> `axiom_audit.py` on `sorryAx`, `workflow_gate.py` on mandatory gates) are
> hard gates — a failure HALTS the calling workflow. Skipping Persist =
> incomplete.

## Routing

- **USE FOR:** running an individual enforcement script or the full `enforce_all.sh` pipeline; checking a build is clean before review; auditing axioms after a refactor; validating cross-module bridges; gating a workflow step.
- **DO NOT USE FOR:** deciding whether a proof is *correct* (delegate to `@lean-proof-review`); scoring repository quality (delegate to `@lean-quality-engine`); routing across skills (delegate to `@lean-gateway`).
- **TRIGGERS:** enforcement, CI gate, axiom audit, council_precheck, workflow_gate, ecosystem_health, sorry check.

## Behavioural rules (G-*)

- **G-1** (MUST): Every check that CAN be automated MUST be automated — human review time is for judgement, not mechanics. [Trace: AC-01]
- **G-2** (MUST): `axiom_audit.py` detecting `sorryAx` MUST block the calling workflow with exit code ≠ 0. [Trace: AC-02]
- **G-3** (MUST): `council_precheck.sh` failure MUST block council convening; the workflow MUST NOT proceed to review. [Trace: AC-03]
- **G-4** (MUST): `workflow_gate.py` MUST verify all mandatory gates for a given step before that step starts. [Trace: AC-04]
- **G-5** (SHOULD NOT): The skill SHOULD NOT silently retry a failed blocking script; escalate per §Recovery & STOP instead. [Trace: AC-05]
- **G-6** (MUST): Every script invocation MUST emit a structured result (exit code, summary, artefact path) to the repository's enforcement log. [Trace: AC-06]
- **G-7** (SHOULD): When multiple scripts can answer the same question, the skill SHOULD prefer the most specific (e.g. `axiom_audit.py` over `enforce_all.sh` for an axiom-only question). [Trace: AC-07]
- **G-8** (MUST): On any guard failure the skill MUST escalate per §Recovery & STOP. [Trace: AC-08]

## Workflow

1. **Discover** [discover] — identify the target gate (single script, group, or `enforce_all.sh`); read the repository's `lakefile.lean` + recent commit log.
2. **Run** [execute] — execute the script(s) in the order documented in [`REFERENCE.md`](./REFERENCE.md) Part 2; capture stdout, stderr, exit code, artefact paths.
3. **Validate** [validate] — interpret exit codes against the blocking-vs-advisory table; for blocking failures, HALT and route to recovery.
4. **Aggregate** [validate] — compose a per-script status line + overall pass/fail; surface advisories without blocking.
5. **Persist** [persist] *(MANDATORY)* — append the structured result to the enforcement log, update the CI annotation, tick the relevant gate. Skipping Persist = incomplete.

## Recovery & STOP

- `axiom_audit.py` finds `sorryAx` → immediate STOP; escalate to proof author; do NOT mark the workflow green.
- `council_precheck.sh` fails → STOP; fix build / sorry / convention / git state before retrying.
- `workflow_gate.py` blocks a mandatory gate → STOP; complete the prerequisite gate, then retry.
- Any blocking script crashes ×3 → STOP; file a bug against this skill.
- Confidence < 90 % about which script to invoke → STOP, ask.

## Handoffs

- **Predecessors / successors:** see FM `handoffs` (grammar from ADR-0080).
- **Source spec:** `specs/lean/enforcement/requirements.md` — every G-rule traces to an AC there.
- **Related ADRs:** ADR-0076, ADR-0080.
- **Reference:** see [`REFERENCE.md`](./REFERENCE.md) for the full script inventory, integration matrix, anti-patterns, and the workflow-gate enforcement model (original v1 content, preserved verbatim).

## Common failure modes

> AI agents commonly: silently retry a blocking failure; downgrade a hard gate
> to a soft one to "unblock progress"; run `enforce_all.sh` when a single
> script would have answered the question; skip the structured-result emit step.
> Full registry: GUARDRAILS.md §Agent failure taxonomy.
