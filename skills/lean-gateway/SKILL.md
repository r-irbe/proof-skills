---
name: "lean-gateway"
description: |
  USE FOR: routing the top-level entry-point for a complex Lean 4 task; selecting which downstream skill(s) own each phase.
  DO NOT USE FOR: doing any actual work (always delegate to a domain skill).
  TRIGGERS: gateway, orchestrate, route, dispatch, top-level.
tier: hot
runtime_targets:
- copilot-cli
- claude-code
- antigravity
- pi
- cursor
- gemini-cli
dispatch_targets:
- skill:lean-proof
- skill:lean-proof-review
- skill:lean-review-council
- skill:lean-retro-methodology
- skill:lean-specification
- skill:lean-setup
- skill:lean-blueprint
- skill:lean-research
- skill:lean-corpus-audit
- skill:lean-verification-gate
- skill:lean-kernel-optimization
- skill:lean-asymptotic-algorithms
- skill:lean-computational-reflection
- skill:lean-egraph-cpsat-superopt
- skill:lean-unboxed-limbs-swar
- skill:lean-worker-wrapper-cps
handoffs:
  predecessors:
  - agent:user
  - agent:gateway
  successors:
  - skill:lean-proof
  - skill:lean-corpus-audit
  - skill:lean-verification-gate
  - skill:lean-review-council
metadata:
  version: 0.5.0
  source_spec: specs/lean/gateway/requirements.md
  last_reviewed: '2026-11-15'
---

# lean-gateway
> **MANDATORY** (hot-tier): the gateway NEVER authors substantive proofs or prose -- every operation is a delegation.
> Skipping Persist (the task tracker) = incomplete (GT-01, GT-05).

## Routing
- **USE FOR:** receiving a multi-step Lean 4 task, decomposing it into phases, selecting the owning skill from
  [`references/handbooks/lean-gateway-handbook.md`](../../references/handbooks/lean-gateway-handbook.md), choosing topology (sequential / fan-out / fan-in),
  maintaining the task state tracker, and detecting context-collapse signals.
- **DO NOT USE FOR:** writing proofs (`@lean-proof`), reviewing proofs (`@lean-proof-review`), syncing docs (`@lean-doc-sync`), or running gates
  (`@lean-verification-gate`).

## Workflow
1. **Discover** [discover] -- read the request, locate any prior tracker for the scope, and enumerate candidate skills from the registry.
2. **Plan** [discover] -- partition into phases, assign one owning skill per phase, and pick topology (sequential / fan-out / fan-in); STOP if
   confidence < 90 %.
3. **Delegate** [execute] -- dispatch each phase to its owning skill (`lean_skill_dispatch`) and record returned artifacts + sign-offs.
4. **Integrate** [validate] -- on fan-in, verify every parallel branch returned a clean sign-off before proceeding.
5. **Persist & Health-check** [persist] -- update the tracker and check for context-collapse signals (recommend fresh session if >= 2).

## Recovery & STOP
- No clear owning skill for a phase -> STOP, ask which skill to invoke or extend.
- Downstream skill returns a hard gate failure -> STOP, do NOT silently retry; escalate.
- Unsigned parallel branch at fan-in -> STOP until resolved.
- >= 2 context-collapse signals -> STOP, recommend a fresh session.

## Handoffs
- **Predecessors / successors:** see FM `handoffs` and `dispatch_targets`.
- **Source spec:** `specs/lean/gateway/requirements.md`.

## Detailed reference
- **Layer-1 Fast Lookup Card (read first)**: [`references/cards/lean-gateway-tables.md`](../../references/cards/lean-gateway-tables.md)
- **Layer-2 Handbook**: [`references/handbooks/lean-gateway-handbook.md`](../../references/handbooks/lean-gateway-handbook.md)

## See also
- [`../../references/handbooks/lean-gateway-handbook.md`](../../references/handbooks/lean-gateway-handbook.md) -- Complete `lean-gateway` Handbook
- [`../../ROLES.md`](../../ROLES.md) -- 5-Role Actor Container & 21-MCP-Tool Architecture
