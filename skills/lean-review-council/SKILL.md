---
name: "lean-review-council"
description: |
  USE FOR: orchestrating a 5-member Lean 4 proof review council (Σ Kernel Guardian, Φ Statement Oracle, Ν Novelty Scout, Λ Quality Architect, Ω Integration Sentinel); running RALPH (Review-Analyze-Learn-Plan-Handle) loops at member / council / project / meta scales; structured voting with structured-disagreement-resolution (SDR); council topology selection (Star / Pipeline / Mesh / Hierarchical / Swarm / Ring / Hub-Spoke); maximum-parallel agent dispatch with cascading completion handlers; specification lifecycle (requirements → design → docs); inter-council collaboration; Zettelkasten knowledge synthesis; calibration scoring; enforcement tactics.
  DO NOT USE FOR: reviewing one Lean proof in isolation (use @lean-proof-review); writing a proof (use @lean-proof); running CI scripts (use @lean-enforcement); single-skill council convocation when no multi-layer review is needed (use the relevant skill directly).
  TRIGGERS: review council, RALPH loop, council vote, SDR, council topology, kernel guardian, statement oracle, novelty scout, quality architect, integration sentinel, meta-council, council session.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-proof-review", "skill:lean-specification", "skill:lean-research"]
  successors: ["skill:lean-proof-review", "skill:lean-enforcement", "skill:lean-doc-feedback", "skill:lean-zettelkasten", "skill:research-council"]
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-review-council/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# Lean 4 Review Council

A formal review council of five voting AI agents that collectively execute the `lean-proof-review` skill with 99.99% reliability and resilience. Each member specializes in one verification layer. The council process prevents agent collapse, maximizes parallel work, enforces correctness through programmatic tactics, and continuously improves its own methodology.

```
┌──────────────────────────────────────────────────────────────────┐
│                     REVIEW COUNCIL ARCHITECTURE                  │
│                                                                  │
│  5 Members × RALPH loops × 7 Topologies × Cascading Dispatch    │
│                                                                  │
│  Σ Kernel Guardian ── formal soundness (Layer 1)                 │
│  Φ Statement Oracle ── statement correctness (Layer 2)           │
│  Ν Novelty Scout ── non-triviality & novelty (Layer 3)          │
│  Λ Quality Architect ── proof quality & readability (Layer 4)    │
│  Ω Integration Sentinel ── cross-cutting coherence (Layer 5)     │
│                                                                  │
│  + Specifier, Designer, Implementer, Documenter, Synthesizer,    │
│    Planner, Enforcer — cascading parallel dispatch               │
└──────────────────────────────────────────────────────────────────┘
```


---

## Routing

- **USE FOR:** orchestrating a 5-member Lean 4 proof review council with RALPH loops at member / council / project / meta scales; structured voting with SDR; council topology selection; maximum-parallel agent dispatch with cascading completion handlers; specification lifecycle, inter-council collaboration, Zettelkasten synthesis, calibration scoring, enforcement tactics.
- **DO NOT USE FOR:** reviewing one Lean proof in isolation (delegate to `@lean-proof-review`); writing a proof (delegate to `@lean-proof`); running CI scripts (delegate to `@lean-enforcement`); single-skill council convocation when no multi-layer review is needed (use the relevant skill directly).
- **TRIGGERS:** review council, RALPH loop, council vote, SDR, council topology, kernel guardian, statement oracle, novelty scout, quality architect, integration sentinel, meta-council, council session.

## Workflow

1. Identify the scope (theorem / file / module / project / meta-council cross-module).
2. Pick a topology (Part 4 of the handbook — Star for first pass, Pipeline for sequential dependencies, Hierarchical for project scale, Hub-Spoke for inter-council).
3. Run Part 12 — Execution Protocol (kept inline below) end-to-end.
4. On a blocking finding, enter SDR (handbook Part 3); on approval, dispatch Documenter + Synthesizer for the session report and Zettelkasten update.
5. Aggregate session reports at the module / project level; convene the Meta-Council for cross-module coherence when needed.

## Recovery & STOP

- STOP if more than two members report 🔴 votes on a single artifact — enter SDR (handbook Part 3) before any further dispatch.
- STOP if RALPH loop iteration count exceeds 3 without convergence — escalate to the Meta-Council (handbook Part 10) or handoff to `@lean-research` to widen evidence.
- STOP if the Documenter or Synthesizer fails to produce a session report — the council session is incomplete; do not advance to module-level aggregation.

## Handoffs

- **Predecessors:** `agent:gateway` (top-level invocation), `skill:lean-proof-review` (when a layer needs council-scale escalation), `skill:lean-specification` (specification lifecycle entry), `skill:lean-research` (when evidence widening is required mid-session).
- **Successors:** `skill:lean-proof-review` (layered re-review on a fix), `skill:lean-enforcement` (CI gates triggered by the council vote), `skill:lean-doc-feedback` (doc sync once review approved), `skill:lean-zettelkasten` (knowledge synthesis), `skill:research-council` (inter-council collaboration via Hub-Spoke).

---

## Detailed reference

Full council methodology (Parts 1–11, 13–15, Appendices A/B/C) lives in
[`references/lean-review-council-handbook.md`](../../references/lean-review-council-handbook.md).
Load that file when convening a council session; the SKILL.md only carries
the dispatch contract and the quick-start Execution Protocol (Part 12) kept
inline below.

| Section | Topic | Covers |
|---|---|---|
| Part 1 | The Five Council Members | Σ / Φ / Ν / Λ / Ω personas, skills, mandates |
| Part 2 | The RALPH Loop | Review-Analyze-Learn-Plan-Handle at all 4 scales |
| Part 3 | Voting and Disagreement Resolution | Vote schema, SDR protocol |
| Part 4 | Council Topologies | Star / Pipeline / Mesh / Hierarchical / Swarm / Ring / Hub-Spoke |
| Part 5 | Parallel Agent Architecture | Maximum-parallel dispatch + cascading completion |
| Part 6 | Specification-Review-Fix Cycle | Requirements + Design + Docs lifecycle |
| Part 7 | Document Templates | Session report, Zettel, ADR, retro templates |
| Part 8 | Zettelkasten Knowledge Management | Synthesis protocol |
| Part 9 | Continuous Self-Improvement | Meta-loop |
| Part 10 | Inter-Council Collaboration | Hub-Spoke between review + research councils |
| Part 11 | Todo List Management | Pre / during / post session |
| Part 13 | Pairwise Collaboration Mechanics | Member-pair protocols |
| Part 14 | Calibration Scoring & Reliability | 99.99% target methodology |
| Part 15 | Enforcement Tactics & Linters | Programmatic gates |
| Appendix A | Reliability and Resilience Mechanisms | Anti-collapse safeguards |
| Appendix B | Skills Required | Cross-skill dispatch matrix |
| Appendix C | Complete Agent Dispatch Reference | Full agent-launch incantations |

## Part 12 — Execution Protocol

### Starting a Council Review Session

```
1. Planner decomposes scope into reviewable units
2. FOR EACH unit:
   a. Launch 5 member agents in parallel (Star topology)
   b. Each member executes RALPH Review + Analyze
   c. Synchronize: collect all findings
   d. Vote
   e. IF blocked: enter SDR
   f. IF approved: proceed
   g. Launch Documenter to record session report
   h. Launch Synthesizer to update Zettelkasten
3. Planner collects all session reports
4. Launch Documenter to produce module-level report
5. IF project-level: Meta-council reviews cross-module coherence
```

### Agent Launch Commands

For the orchestrating agent to dispatch council members:

```
Dispatch Σ: "You are Sigma, the Kernel Guardian. Execute Layer 1 (Formal 
Soundness) review of [artifact]. Run #print axioms on all theorems. Check 
for sorry, admit, native_decide. Verify lake build passes. Report findings 
using the Council Session Report template. Vote ✅/🟡/🟠/🔴."

Dispatch Φ: "You are Phi, the Statement Oracle. Execute Layer 2 (Statement 
Correctness) review of [artifact]. Translate every theorem to English. Run 
the missing-hypothesis checklist. Check for vacuous truth. Cross-reference 
with project-tufte.tex. Report findings using the Council Session Report 
template. Vote ✅/🟡/🟠/🔴."

Dispatch Ν: "You are Nu, the Novelty Scout. Execute Layer 3 (Non-Triviality) 
review of [artifact]. Run exact? on all goals. Check Tactics.lean for 
duplicates. Classify novelty. Report findings using the Council Session 
Report template. Vote ✅/🟡/🟠/🔴."

Dispatch Λ: "You are Lambda, the Quality Architect. Execute Layer 4 (Proof 
Quality) review of [artifact]. Count tactic steps. Flag anti-patterns. 
Check tactic priority compliance. Verify docstrings. Report findings using 
the Council Session Report template. Vote ✅/🟡/🟠/🔴."

Dispatch Ω: "You are Omega, the Integration Sentinel. Execute cross-cutting 
review of [artifact]. Check autoImplicit, naming conventions, section 
organization, module imports, paper cross-references, simplex constraints. 
Report findings using the Council Session Report template. Vote ✅/🟡/🟠/🔴. 
As council chair, collect all votes and produce the final decision."
```

---

## See also

- [`../../references/lean-review-council-handbook.md`](../../references/lean-review-council-handbook.md) — Full council methodology (extracted from this skill)
- [`research-council`](../research-council/SKILL.md) — Sister council for research methodology (Hub-Spoke partner)
- [`lean-proof-review`](../lean-proof-review/SKILL.md) — Single-proof 4-layer review (delegated by Σ Kernel Guardian + Φ Statement Oracle)
- [`lean-enforcement`](../lean-enforcement/SKILL.md) — CI gates triggered by council vote
- [`lean-zettelkasten`](../lean-zettelkasten/SKILL.md) — Knowledge synthesis target
