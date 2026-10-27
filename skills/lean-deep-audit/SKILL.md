---
name: "lean-deep-audit"
description: |
  USE FOR: running a systematic whole-corpus quality audit over a large Lean formalization project: trust-base lockdown.
  DO NOT USE FOR: reviewing a single theorem's proof (@lean-proof-review).
  TRIGGERS: deep audit, corpus audit, whole-corpus review.
tier: "cold"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["skill:lean-gateway", "skill:lean-quality-engine"]
  successors: ["skill:lean-axiom-closure", "skill:lean-tautology-triage", "skill:lean-proof-review"]
---

# The Deep-Audit Program (whole-corpus, seven lenses)
Operational dispatch contract for `@lean-deep-audit`.
## Routing
- **USE FOR:** tasks routed to `@lean-deep-audit`.
- **DO NOT USE FOR:** out-of-scope tasks (delegate via `@lean-gateway`).
## Workflow
1. **P1 - Trust-base lockdown.** Every declaration's transitive axiom
   closure restricted to the declared allowlist, enforced in the normal
   build. EXECUTOR: the `lean-axiom-closure` skill (vendored metaprogram
   + FinalCheck consumer). Expected first catches: `sorryAx` behind
   wrappers/aliases, `native_decide` (`Lean.ofReduceBool`), custom
   axioms.
2. **P2 - Literature faithfulness, tower by tower.** For each
   foundational module: read every core definition; compare with the
   cited formula; classify faithful-formula / scoped-specialization /
   free-record-proxy. The proxy signature: a structure with free
   fields + arithmetic defs over those fields + projection-style
   theorems, while the module prose narrates mathematics the code
## Recovery & STOP
- If a census script times out or drifts after upstream edits, re-run the precompiled two-pass scanner on a
  clean tree before
  quoting line
  numbers or counts.
- If a module family is guest or template material, register the finding in the remediation queue and escalate
  disposition to the
  owning
  lane rather than
  deleting modules unilaterally.
## Handoffs
- **Predecessors:** `@lean-gateway` (top-level routing), `@lean-quality-engine` (project QA orchestration).
- **Successors:** `@lean-axiom-closure` (P1 executor), `@lean-tautology-triage` (P3 candidate triage),
  `@lean-proof-review`
  (per-module
  review).
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-deep-audit-handbook.md`](../../references/lean-deep-audit-handbook.md) .
## See also
- [`../../references/lean-deep-audit-handbook.md`](../../references/lean-deep-audit-handbook.md) -- Complete
  `lean-deep-audit`
  Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
