---
name: "lean-axiom-closure"
description: |
  USE FOR: enforcing a project-wide axiom lockdown - verifying that EVERY declaration's transitive axiom closure restricts strictly to the standard axioms (propext, Quot.sound, Classical.choice) via a compile-time metaprogram audit; setting up the FinalCheck discipline (a guard_msgs-wrapped audit module that runs inside the project's normal build); detecting sorryAx, Lean.ofReduceBool (native_decide), and custom axiom leakage across the whole environment, not just per-theorem spot checks.
  DO NOT USE FOR: writing or fixing a proof (use @lean-proof); replay/verification-cadence policy (use @lean-replay-verification, which this skill supplies R2's executor for); finding tautological statements (use @lean-tautology-triage); running the build itself (use @lean-build).
  TRIGGERS: axiom closure, axiom lockdown, FinalCheck, print axioms, trust base, sorryAx leak, native_decide ban, implemented_by, extern, whole-corpus axiom audit, "which theorems use which axioms", allowlist.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ["skill:lean-replay-verification", "skill:lean-deep-audit"]
  successors: ["skill:lean-proof-review", "skill:lean-enforcement"]
---

# Axiom-Closure Audit (the FinalCheck discipline)

## Why

`#print axioms foo` checks ONE declaration. A project that claims
"only the standard axioms" needs the claim over EVERY declaration,
re-checked automatically on every build, with a failure that blocks
the build. Spot checks rot; a compile-time lockdown does not.

## The instrument

`AxiomClosure.lean.tmpl` (this directory) is a small, dependency-free
Lean module defining `Audit.axiomClosureAudit (root : Name)
(allow : Array Name) : CommandElabM Unit`: it walks every constant in
the environment whose root namespace is `root`, computes each
declaration's transitive axiom closure (`Lean.collectAxioms`, the same
machinery as `#print axioms`), and throws an error naming the
declaration for every axiom outside `allow`. Internal
implementation-detail names are excluded. Full-corpus cost measured on
a Mathlib-dependent corpus of ~9k named declarations: **seconds**.

## Workflow (the FinalCheck setup discipline)

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
   have a recorded reason.

## What violations mean

- `sorryAx` - a `sorry` (or `admit`) in the closure: the proof is not
  complete. This is how incomplete proofs hide behind wrappers,
  aliases, and re-exports that per-theorem checks miss.
- `Lean.ofReduceBool` - a `native_decide` somewhere in the closure:
  compiled evaluation is trusted, not kernel-checked. Replace with
  `decide`/`native_decide`-free proofs or record an explicit,
  reviewed exception (a widened allowlist entry with a reason).
- A custom axiom name - an `axiom` declaration is in the closure:
  either remove it and prove the statement, or document it in the
  allowlist with justification.

## Behavioural rules (G-*)

- **G-1** (MUST): the audit module runs inside the project's normal
  build (source globs), not as an optional side script.
- **G-2** (MUST): the allowlist is explicit and versioned; an empty or
  implicit allowlist makes the audit meaningless.
- **G-3** (MUST): a new allowlist entry requires a recorded reason and
  a named owner decision - tightening is free, widening is a decision.
- **G-4** (SHOULD): pair with `@lean-replay-verification` R2: the
  closure audit is the per-build instrument; the replay ladder is the
  cadence.

## Pitfalls

- The audit checks declarations under ONE root namespace; imported
  dependencies (Mathlib, core) are trusted at their own guarantee.
  State the boundary.
- `#eval` runs at elaboration: the consumer file re-runs the audit on
  every rebuild of itself - that is the point, but keep the consumer
  small so rebuilds stay fast (the audit itself is seconds).
- Compile-time `decide`-heavy environments may see slower elaboration
  of the consumer file; that cost is the audit running.
- Name-literal allowlist entries (`propext`, not "propext" strings):
  the parameter is `Array Name`.

## Verification

- The consumer file builds as part of `lake build` and is silent.
- Deliberately introducing a `sorry` makes the build FAIL with
  `<name> : axiom closure contains sorryAx` - verify the failure path
  once during setup.
- The summary line (dropped by the guard in CI) is printable by
  running the same `#eval` without the guard; quote checked/violation
  counts as the audit evidence.

## Recovery

- If `Audit.axiomClosureAudit` reports `sorryAx`, trace the offending declaration via `#print axioms` and hand off to `@lean-proof` to close the open subgoal.
- If `Lean.ofReduceBool` appears, replace `native_decide` with kernel-checked `decide` / `omega` or obtain explicit owner sign-off before widening the allowlist.

## Handoffs

- **Predecessors:** `@lean-replay-verification` (R2 cadence), `@lean-deep-audit` (P1 trust-base lockdown).
- **Successors:** `@lean-proof-review` (single-module audit), `@lean-enforcement` (CI gate execution).
