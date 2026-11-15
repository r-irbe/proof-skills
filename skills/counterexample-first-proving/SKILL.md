---
name: "counterexample-first-proving"
description: |
  USE FOR: falsifying Lean 4 conjectures via Plausible testing, boundary witnesses, and Nat truncation checks.
  DO NOT USE FOR: proving verified claims (@lean-proof) or post-proof triage (@lean-tautology-triage).
  TRIGGERS: counterexample, plausible, falsify, boundary witness, test conjecture, Nat truncation.
tier: hot
runtime_targets:
- copilot-cli
- claude-code
- antigravity
- pi
- cursor
- gemini-cli
dispatch_targets: []
handoffs:
  predecessors:
  - skill:lean-specification
  - skill:lean-gateway
  successors:
  - skill:lean-proof
  - skill:lean-specification
metadata:
  version: 0.5.0
  source_spec: Galois-pruned Plausible falsification & boundary-witness protocol
  last_reviewed: 2026-11
---

# Counterexample-First Proving (Pre-Proof Conjecture Screening)

Screen every non-trivial conjecture or stuck subgoal for small counterexamples before spending tactic budget on a false or under-guarded statement.

## Routing
- **USE FOR:** pre-proof falsification of newly specified theorems, stuck induction hypotheses (>15 tactic steps),
  and suspected `Nat` subtraction / division-by-zero edge cases.
- **DO NOT USE FOR:** closing valid tactic goals (`@lean-proof`) or post-proof vacuity triage (`@lean-tautology-triage`).

## Workflow
1. **Static Truncation Check** -- Run `lean_diagnostics` to inspect `NatSubTruncation` (`a - b` where `a < b`) and
  `NatDivModByZero` certificates before sampling.
2. **Boundary Sweep** -- Probe degenerate witnesses (`0`, `1`, `a = 0 and b = 1`, empty `List`/`Finset`,
  disconnected `Fin 3` graphs) in an isolated scratch context.
3. **Plausible Search** -- Invoke `lean_counterexample_search(filePath, theoremName, strategy: "dense")` to run
  Galois-pruned property-based shrinking without polluting source files.
4. **Route Verdict** -- If 0 counterexamples are found, hand off to `@lean-proof`; if a counterexample witness `w`
  is confirmed, record `w` and escalate to `@lean-specification`.

## Recovery & STOP
- When `SampleableExt` is unavailable for an abstract type `α`, specialize `α := Fin 3` or `Int` in scratch rather than skipping falsification.
- Never silently weaken a public theorem statement inside a Prover session; escalate the minimal counterexample back to `specifier`.

## Handoffs
- **Predecessors:** `lean-specification`, `lean-gateway`.
- **Successors:** `lean-proof`, `lean-specification`.

## Detailed reference
- Fast 3-table lookup card: [`../../references/cards/counterexample-first-proving-tables.md`](../../references/cards/counterexample-first-proving-tables.md)
- Full handbook: [`../../references/handbooks/counterexample-first-proving-handbook.md`](../../references/handbooks/counterexample-first-proving-handbook.md)

## See also
- [`../lean-specification/SKILL.md`](../lean-specification/SKILL.md) -- Three-part theorem specification
- [`../lean-tautology-triage/SKILL.md`](../lean-tautology-triage/SKILL.md) -- Post-proof vacuity & tautology triage
