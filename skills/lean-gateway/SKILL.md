---
name: "lean-gateway"
description: |
  USE FOR: routing the top-level entry-point for a complex Lean 4 task; selecting which downstream skill(s) own each phase; preventing context collapse across long sessions; maintaining feedback / feedforward loops; fan-in / fan-out coordination; system-wide health monitoring.
  DO NOT USE FOR: doing any actual work (always delegate to a domain skill); single-file editing (use @lean-proof or @lean-doc-improvement); script-level enforcement (use @lean-enforcement).
  TRIGGERS: gateway, orchestrate, route, dispatch, top-level, context collapse, fan-out, fan-in, ecosystem health.
tier: "hot"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: ["skill:lean-proof", "skill:lean-proof-review", "skill:lean-review-council", "skill:lean-zettelkasten", "skill:lean-specification", "skill:lean-setup", "skill:lean-blueprint", "skill:lean-research", "skill:lean-quality-engine", "skill:lean-enforcement"]
handoffs:
  predecessors: ["agent:user", "agent:gateway"]
  successors: ["skill:lean-proof", "skill:lean-quality-engine", "skill:lean-enforcement", "skill:lean-review-council"]
metadata:
  version: "0.2.0"
  source_spec: "specs/lean/gateway/requirements.md"
  last_reviewed: "2026-05-27"
---

# lean-gateway

> ⚠️ **MANDATORY** (hot-tier): the gateway NEVER does substantive proof or
> documentation work — every operation is a delegation. Skipping Persist
> (the global task tracker) = incomplete.

## Routing

- **USE FOR:** receiving a Lean 4 task at session start, decomposing it into phases, routing each phase to the appropriate skill in [`REFERENCE.md`](./REFERENCE.md) Part 1's registry; deciding fan-in vs fan-out vs sequential topology; maintaining the per-task state document; detecting context-collapse signals and prescribing a fresh session.
- **DO NOT USE FOR:** writing a proof (delegate to `@lean-proof`); reviewing a proof (delegate to `@lean-proof-review`); editing docs (delegate to `@lean-doc-improvement`); running scripts (delegate to `@lean-enforcement`).
- **TRIGGERS:** gateway, orchestrate, route, dispatch, top-level, context collapse, fan-out, fan-in, ecosystem health.

## Behavioural rules (G-*)

- **G-1** (MUST NOT): The gateway MUST NOT execute substantive proof, doc, or research work itself; every such operation MUST be a delegation. [Trace: AC-01]
- **G-2** (MUST): Each phase MUST be routed to exactly one owning skill from the registry; if no clear owner exists, the gateway MUST escalate per §Recovery & STOP. [Trace: AC-02]
- **G-3** (MUST): Fan-out topology (parallel skills) MUST converge through a documented fan-in (a single skill that integrates the results). [Trace: AC-03]
- **G-4** (SHOULD): The gateway SHOULD prefer the most specific skill in the registry over a broader one (e.g. `@lean-blueprint` over `@lean-doc-improvement` for blueprint work). [Trace: AC-04]
- **G-5** (MUST): On any of the documented context-collapse signals (≥ 2 from `AGENT.md`), the gateway MUST recommend a fresh session before continuing. [Trace: AC-05]
- **G-6** (MUST): The gateway MUST maintain the per-task tracker (phase status, owner, predecessors, successors, sign-offs); a missing tracker entry = a missing delegation. [Trace: AC-06]
- **G-7** (SHOULD NOT): The gateway SHOULD NOT silently retry a failed downstream delegation; it MUST escalate per §Recovery & STOP. [Trace: AC-07]
- **G-8** (MUST): On any guard failure the skill MUST escalate per §Recovery & STOP. [Trace: AC-08]

## Workflow

1. **Discover** [discover] — receive the task, locate prior tracker for this scope (if any), enumerate the candidate skills from the registry.
2. **Plan** [discover] — partition the task into phases; for each phase, pick the owning skill; choose topology (sequential / fan-out / fan-in / hybrid); STOP if confidence < 90 %.
3. **Delegate** [execute] — invoke each phase's owning skill in the chosen order; capture the returned artefact reference + sign-off state.
4. **Integrate** [validate] — when fanning in, confirm every parallel branch returned a sign-off; halt on any unsigned branch.
5. **Health-check** [validate] — sweep for context-collapse signals; recommend a fresh session if ≥ 2 are present.
6. **Persist** [persist] *(MANDATORY)* — update the per-task tracker (phase status, owner, artefact links, sign-offs); update the ecosystem-health dashboard; tick the global tasks list. Skipping Persist = incomplete.

## Recovery & STOP

- No clear owning skill for a phase → STOP, ask which skill to add or extend.
- A downstream skill returns a hard failure → STOP, do NOT silently retry; escalate to that skill's owner.
- Fan-in fails because a parallel branch is unsigned → STOP, complete the missing branch before integrating.
- ≥ 2 context-collapse signals from `AGENT.md` → STOP, recommend a fresh session.
- Confidence < 90 % on phase decomposition or topology → STOP, ask.

## Handoffs

- **Predecessors / successors:** see FM `handoffs` (grammar from ADR-0080).
- **Dispatch targets:** see FM `dispatch_targets` for the full set of downstream skills the gateway may delegate to.
- **Source spec:** `specs/lean/gateway/requirements.md` — every G-rule traces to an AC there.
- **Related ADRs:** ADR-0076, ADR-0080.
- **Reference:** see [`REFERENCE.md`](./REFERENCE.md) for the full skill registry, context-collapse signal list, feedback-loop topology, fan-in/fan-out patterns, health dashboard schema, hierarchy management, enforcement-script orchestration, and ecosystem topology diagram (original v1 content, preserved verbatim).

## Common failure modes

> AI agents commonly: do the work themselves "to save a delegation"; pick a
> broad skill when a specific one exists; retry a failed delegation instead of
> escalating; ignore context-collapse signals; skip the per-task tracker update.
> Full registry: GUARDRAILS.md §Agent failure taxonomy.
