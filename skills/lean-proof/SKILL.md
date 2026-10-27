---
name: "lean-proof"
description: |
  USE FOR: writing Lean 4 proofs one tactic at a time, fixing tactic errors by priority, planning sorry placeholders.
  DO NOT USE FOR: reviewing existing proofs (@lean-proof-review).
  TRIGGERS: prove, tactic, sorry, unsolved goals, motive is not type correct.
tier: "hot"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors:
    - "skill:lean-setup"
    - "skill:lean-specification"
    - "skill:lean-research"
  successors:
    - "skill:lean-proof-review"
    - "skill:lean-mwe"
    - "skill:lean-zettelkasten"
metadata:
  version: "0.2.2"
  source_spec: "specs/lean/proof/requirements.md"
  last_reviewed: "2026-10-20"
r_caveats: [F1, F6]
---

# lean-proof
> ⚠️ **MANDATORY** (hot-tier): the gates in §Behavioural rules and the Persist
## Routing
- **USE FOR:** writing Lean 4 proofs one tactic at a time with `done`-driven diagnostics; resolving errors in
  syntax → type →
  unsolved-goals
  → linter
  order; planning `sorry` placeholders so the hardest case is attacked first; cleaning a working proof into
  its minimal form;
  recovering
from `motive is
  not type correct` via generalise-then-instantiate.
- **DO NOT USE FOR:** reviewing or auditing existing proofs (use `@lean-proof-review`); project-level QA
  orchestration (use
  `@lean-quality-engine`);
## Workflow
1. **Discover** [discover] — read the target theorem, locate its spec via `lean_lookup_symbol` (`{"symbol":
  "..."}`), list open
  `sorry`s and
   existing
   diagnostics via `lean_diagnostics` (`{"filePath": "..."}`, which also runs the Rust/WASM `lean-analyzer`
   static abstract
   interpretation
engine for
   `NatSubTruncation`, `NatDivModByZero`, Zone DBM `decreasing_by` synthesis, Octagon conservation `±x_i ± x_j
   <= c`, Bourdoncle
   WTO loop
widening, and
   trace partitioning certificates). Confirm `lake env lean` resolves (else hand back to `@lean-setup`).
2. **Plan** [discover] — pick the target theorem (not a helper lemma); within it, pick the hardest case. If
  the theorem statement
  is newly
   authored or
## Recovery & STOP
- Same error class fails ×3 attempts → STOP, escalate to human or hand off to `@lean-mwe` to isolate the
  failure.
- Scope drift (edit outside the target theorem, its helper lemmas, or its imports) → immediate STOP, re-anchor
  on the target.
- Confidence < 80 % on tactic strategy → STOP and hand off to `@lean-research`.
- Context degradation signals (≥2 from AGENTS.md — repeated tactic, ignored prior diagnostic, persona drift) →
  recommend a fresh
  session and
  re-anchor the
  theorem.
## Handoffs
- **Predecessors / successors**: see FM `handoffs` (grammar from ADR-0080). Typical inbound: `@lean-setup`
  confirms toolchain;
  `@lean-specification`
  supplies the theorem; `@lean-research` supplies tactic strategy. Typical outbound: `@lean-proof-review`
  audits; `@lean-mwe` if
  stuck;
  `@lean-zettelkasten` records the pattern.
- **Source spec**: `specs/lean/proof/requirements.md` — every G-rule traces to an AC there.
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-proof-handbook.md`](../../references/lean-proof-handbook.md) .
## See also
- [`../../references/lean-proof-handbook.md`](../../references/lean-proof-handbook.md) -- Complete
  `lean-proof` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
