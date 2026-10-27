---
name: "applied-engineering-disciplines"
description: |
  USE FOR: Engineering disciplines relevant to formal mathematical systems: control theory, systems engineering.
  DO NOT USE FOR: formal verification in Lean (@lean-ai-formalization).
  TRIGGERS: control theory, systems engineering, reliability engineering.
tier: "warm"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-research"]
  successors: ["skill:lean-ai-formalization", "skill:lean-security-formalization", "skill:lean-math-dynamical"]
metadata:
  version: "0.2.0"
  source_spec: "skills/applied-engineering-disciplines/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Engineering Disciplines for Formal Mathematical Systems
Engineering methods and frameworks that connect formal mathematics to practical system design, verification,
testing, and
deployment.
---
## Routing
- **USE FOR:** Engineering disciplines relevant to formal mathematical systems — control theory, systems
  engineering, reliability
  engineering, software
  verification, signal processing, and testing methodology. Use for bridging mathematical foundations to
  engineering practice, and
  for
formalizing
  engineering requirements in Lean 4.
- **DO NOT USE FOR:** formal verification in Lean (use @lean-ai-formalization); security-specific engineering
  (use
  @applied-data-information-security);
  strategy analysis (use @lean-applied-reasoning).
- **TRIGGERS:** control theory, systems engineering, reliability engineering, software verification,
  engineering discipline.
## Workflow
1. Identify the discipline match: control theory, systems engineering, reliability engineering, or software
  verification.
2. Pick the relevant section of the body; trace the chosen methodology end-to-end.
3. Produce the engineering artifact (control law, FMEA, reliability budget) in the form the caller needs.
4. Hand off: to `@lean-ai-formalization` for formal proofs of correctness, to `@lean-math-dynamical` if
  control-theoretic dynamics
  dominate,
   to
   `@lean-zettelkasten`.
## Recovery & STOP
- STOP if the question is about the formal-verification proof itself — delegate to `@lean-ai-formalization`.
- STOP if the discipline match is unclear — surface a clarifying question rather than guessing.
- STOP if the answer needs domain-specific data not in the body — escalate to `@research-council`.
## Handoffs
- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-ai-formalization`, `skill:lean-security-formalization`,
  `skill:lean-math-dynamical`.
---
## Detailed reference
Full content for `applied-engineering-disciplines` lives in
[`references/applied-engineering-disciplines-handbook.md`](../../references/applied-engineering-disciplines-handbook.md)
.
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.
| Section | Topic |
|---|---|
| Part 1 | Control Theory |
| Part 2 | Systems Engineering |
| Part 3 | Reliability Engineering |
| Part 4 | Software Verification & Testing |
| Part 5 | Signal Processing & Estimation |
| Part 6 | Engineering Process for Lean Projects |
| Part 7 | Configuration Management |
| Part 8 | Cross-References |
---
## See also
- [`../../references/applied-engineering-disciplines-handbook.md`](../../references/applied-engineering-disciplines-handbook.md)
  —
  Full handbook (extracted
  from this skill)
- [`../lean-ai-formalization/SKILL.md`](../lean-ai-formalization/SKILL.md) — Successor
- [`../lean-security-formalization/SKILL.md`](../lean-security-formalization/SKILL.md) — Successor
- [`../lean-math-dynamical/SKILL.md`](../lean-math-dynamical/SKILL.md) — Successor
