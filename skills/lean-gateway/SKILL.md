---
name: "lean-gateway"
description: |
  USE FOR: routing the top-level entry-point for a complex Lean 4 task; selecting which downstream skill(s) own each phase.
  DO NOT USE FOR: doing any actual work (always delegate to a domain skill).
  TRIGGERS: gateway, orchestrate, route, dispatch, top-level.
tier: "hot"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets:
  - "skill:lean-proof"
  - "skill:lean-proof-review"
  - "skill:lean-review-council"
  - "skill:lean-zettelkasten"
  - "skill:lean-specification"
  - "skill:lean-setup"
  - "skill:lean-blueprint"
  - "skill:lean-research"
  - "skill:lean-quality-engine"
  - "skill:lean-enforcement"
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
- **USE FOR:** receiving a Lean 4 task at session start, decomposing it into phases, routing each phase to the
  appropriate skill
  in
  [`references/lean-gateway-handbook.md`](../../references/lean-gateway-handbook.md) Part 1's registry;
  deciding fan-in vs fan-out
  vs sequential topology; maintaining the per-task state document; detecting
  context-collapse signals and prescribing a fresh session.
- **DO NOT USE FOR:** writing a proof (delegate to `@lean-proof`); reviewing a proof (delegate to
  `@lean-proof-review`); editing
  docs
  (delegate to
  `@lean-doc-improvement`); running scripts (delegate to `@lean-enforcement`).
## Workflow
1. **Discover** [discover] — receive the task, locate prior tracker for this scope (if any), enumerate the
  candidate skills from
  the
   registry.
2. **Plan** [discover] — partition the task into phases; for each phase, pick the owning skill; choose
  topology (sequential /
  fan-out /
   fan-in / hybrid);
   STOP if confidence < 90 %.
3. **Delegate** [execute] — invoke each phase's owning skill in the chosen order; capture the returned
  artefact reference +
  sign-off state.
4. **Integrate** [validate] — when fanning in, confirm every parallel branch returned a sign-off; halt on any
  unsigned branch.
5. **Health-check** [validate] — sweep for context-collapse signals; recommend a fresh session if ≥ 2 are
  present.
## Recovery & STOP
- No clear owning skill for a phase → STOP, ask which skill to add or extend.
- A downstream skill returns a hard failure → STOP, do NOT silently retry; escalate to that skill's owner.
- Fan-in fails because a parallel branch is unsigned → STOP, complete the missing branch before integrating.
- ≥ 2 context-collapse signals from `AGENTS.md` → STOP, recommend a fresh session.
- Confidence < 90 % on phase decomposition or topology → STOP, ask.
## Handoffs
- **Predecessors / successors:** see FM `handoffs` (grammar from ADR-0080).
- **Dispatch targets:** see FM `dispatch_targets` for the full set of downstream skills the gateway may
  delegate to.
- **Source spec:** `specs/lean/gateway/requirements.md` — every G-rule traces to an AC there.
- **Related ADRs:** ADR-0076, ADR-0080.
- **Reference:** see [`references/lean-gateway-handbook.md`](../../references/lean-gateway-handbook.md) for
  the full skill
  registry, context-collapse signal list, feedback-loop topology, fan-in/fan-out
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-gateway-handbook.md`](../../references/lean-gateway-handbook.md) .
## See also
- [`../../references/lean-gateway-handbook.md`](../../references/lean-gateway-handbook.md) -- Complete
  `lean-gateway` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
