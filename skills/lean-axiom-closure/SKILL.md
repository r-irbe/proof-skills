---
name: "lean-axiom-closure"
description: |
  USE FOR: enforcing a project-wide axiom lockdown: verifying that EVERY declaration's transitive axiom closure restricts.
  DO NOT USE FOR: writing or fixing a proof (@lean-proof).
  TRIGGERS: axiom closure, axiom lockdown, FinalCheck, print axioms.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["skill:lean-replay-verification", "skill:lean-deep-audit"]
  successors: ["skill:lean-proof-review", "skill:lean-enforcement"]
---

# Axiom-Closure Audit (the FinalCheck discipline)
Operational dispatch contract for `@lean-axiom-closure`.
## Routing
- **USE FOR:** tasks routed to `@lean-axiom-closure`.
- **DO NOT USE FOR:** out-of-scope tasks (delegate via `@lean-gateway`).
## Workflow
1. Vendor `AxiomClosure.lean.tmpl` into the project (e.g. `<root>/Audit/AxiomClosure.lean`),
   adjusting only the module path of the example.
2. Create the consumer file (`FinalCheckAll.lean.tmpl`): import the
   audit module + the project root, then
   `#guard_msgs (drop info) in #eval Audit.axiomClosureAudit <root> #[...allowlist]`.
3. Keep the consumer file INSIDE the library's source globs so the
   project's normal build runs it. `#guard_msgs (drop info)` drops the
   summary info line; any violation error - and only a violation
   error - fails the build.
4. The allowlist is the project's DECLARED trust base. Default:
   `#[`propext, `Quot.sound, `Classical.choice]`. Tighten it to exactly
   the axioms the project is willing to assume; every extra entry must
## Recovery & STOP
- If `Audit.axiomClosureAudit` reports `sorryAx`, trace the offending declaration via `#print axioms` and hand
  off to
  `@lean-proof` to close
  the open subgoal.
- If `Lean.ofReduceBool` appears, replace `native_decide` with kernel-checked `decide` / `omega` or obtain
  explicit owner sign-off
  before
  widening the
  allowlist.
## Handoffs
- **Predecessors:** `@lean-replay-verification` (R2 cadence), `@lean-deep-audit` (P1 trust-base lockdown).
- **Successors:** `@lean-proof-review` (single-module audit), `@lean-enforcement` (CI gate execution).
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-axiom-closure-handbook.md`](../../references/lean-axiom-closure-handbook.md) .
## See also
- [`../../references/lean-axiom-closure-handbook.md`](../../references/lean-axiom-closure-handbook.md) --
  Complete
  `lean-axiom-closure` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
