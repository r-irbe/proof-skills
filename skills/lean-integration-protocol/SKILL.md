---
name: lean-integration-protocol
description: Cross-skill integration protocol defining how all 39 skills work together. Covers the complete lifecycle from document to proof to document, inter-cluster communication, workflow templates for common tasks, and the master orchestration patterns. Use when coordinating multi-skill workflows or diagnosing cross-skill issues.
---

# SK-40: Integration Protocol

Defines how all skills in the project ecosystem work together as a coherent system.

---

## Part 1 — The Three Lifecycles

### 1.1 Forward Lifecycle (Document → Lean)

```
PAPER → doc-requirements (SK-09) → specification (SK-05) → 
  proof (SK-01) → review-council (SK-03) → 
    zettelkasten (SK-04) → [done]
```

Skills involved: SK-01, SK-03, SK-04, SK-05, SK-09, SK-11, SK-38

### 1.2 Backward Lifecycle (Lean → Document)

```
PROOF RESULT → doc-feedback (SK-37) → doc-improvement (SK-10) →
  PAPER UPDATE → doc-requirements (SK-09) → [loop back if new claims]
```

Skills involved: SK-10, SK-37, SK-09

### 1.3 Quality Lifecycle (Continuous)

```
ENFORCEMENT (SK-36) → quality-engine (SK-39) → 
  quality-score → gateway (SK-07) → 
    [dispatch fixes if score dropped]
```

Skills involved: SK-07, SK-36, SK-39

---

## Part 2 — Standard Workflow Templates

### 2.1 Prove a New Theorem (end-to-end)

```
1. [SK-09] Extract claim from paper        → Claim ID
2. [SK-05] Create specification             → Spec ID
3. [SK-38/M] Research proof strategy        → Strategy
4. [SK-01] Implement proof                  → Theorem in .lean
5. [SK-36] Run council_precheck.sh          → Build OK
6. [SK-03] Council review (Star topology)   → Votes
7. [SK-04] Create ZK note if novel          → ZK note
8. [SK-37] Update coverage matrix           → Coverage matrix
9. [SK-10] Update paper if needed           → Paper patch
```

### 2.2 Retroactive Audit (existing module)

```
1. [SK-36] Run retro_recon.py              → Recon report
2. [SK-35] Establish baseline (Phase E)     → Baseline report
3. [SK-35] Triage findings (Phase T)        → Triage report
4. FOR EACH wave:
   a. [SK-03] Council review per theorem    → Findings
   b. [SK-01] Fix P0/P1 findings           → Patches
   c. [SK-05] Backfill specifications      → Specs
   d. [SK-37] Update coverage matrix       → Coverage
5. [SK-39] Quality gate check              → Score
6. [SK-35] Onboard to steady state (Phase O)
```

### 2.3 Paper Revision Sync

```
1. [SK-09] Re-extract claims from changed sections  → Delta claims
2. [SK-37] Compare with existing coverage matrix     → Gaps
3. FOR EACH gap:
   a. [SK-05] Update specification if claim changed  → Updated spec
   b. [SK-01] Re-prove if necessary                  → Updated proof
   c. [SK-03] Re-review affected theorems            → Updated votes
4. [SK-36] Run metric_sync.py                       → Sync status
5. [SK-10] Generate paper patches                   → LaTeX diffs
```

### 2.4 Research Deep Dive

```
1. [SK-38] Classify research type (M/T/L/S/D/X/E)
2. [SK-23] Check epistemic map for existing knowledge
3. [SK-11] Execute research protocol for chosen type
4. IF multi-domain: [SK-22] Research council session
5. [SK-04] Create ZK notes for findings
6. [SK-23] Update epistemic map with transitions
7. Return results to calling skill
```

---

## Part 3 — Inter-Cluster Communication Protocols

### 3.1 Review ↔ Quality

```
Review cluster produces: findings, votes, specifications
Quality cluster consumes: findings → quality score, votes → review coverage
Quality cluster produces: gate decisions, quality trends
Review cluster consumes: gate decisions → schedule adjustments
```

### 3.2 Research ↔ Document

```
Research cluster produces: literature findings, API cards, domain insights
Document cluster consumes: findings → paper improvements, new claims
Document cluster produces: extracted claims, paper changes
Research cluster consumes: claims → research triggers, changes → re-extraction triggers
```

### 3.3 Quality ↔ Infrastructure

```
Quality cluster produces: enforcement results, health metrics
Infrastructure cluster consumes: results → CI configuration, health → build monitoring
Infrastructure cluster produces: build status, nightly results
Quality cluster consumes: build status → quality score, nightly results → regression alerts
```

---

## Part 4 — Feedback Loop Inventory

Complete list of all feedback loops in the ecosystem:

| # | Loop Name | Source → Target | Frequency |
|---|---|---|---|
| F1 | Review → Spec | Council finding → spec revision | Per finding |
| F2 | Review → Proof | Vote reject → re-implementation | Per vote |
| F3 | ZK → Review | Pattern cluster → checklist update | Per 3+ patterns |
| F4 | Doc-req → Spec | New claim → new specification | Per extraction |
| F5 | Research → ZK | Finding → literature/permanent note | Per finding |
| F6 | Doc-improve → Gateway | Metric update → project state refresh | Per update |
| F7 | Doc-feedback → Doc-improve | Erratum → paper correction | Per erratum |
| F8 | Doc-feedback → Doc-req | Coverage gap → claim extraction | Per gap |
| F9 | Retro → Council | Module report → fix schedule | Per wave |
| F10 | RETRO → QA | Wave complete → gate check | Per wave |
| F11 | Enforcement → Gateway | Violation → P0 todo | Per violation |
| F12 | Enforcement → QA | Script result → score update | Per run |
| F13 | QA → Gateway | Gate blocked → pause/remediate | Per gate |
| F14 | QA → Gateway | Score regression → improvement plan | Per check |
| F15 | Research-types → Enforcement | Type S finding → soundness check | Per finding |
| F16 | Research-types → Spec | Type D recommendation → design update | Per reco |
| F17 | Epistemic → Research | Gap discovery → research dispatch | Per gap |
| F18 | Strategy → Research | Brainstorm idea → literature search | Per idea |

### 4.1 Loop Health Rules

- Every loop must complete within 2 RALPH iterations (else: stale signal)
- No loop may have > 10 queued signals (else: backlog alert)
- Every loop must be exercised at least once per project phase (else: starvation)

---

## Part 5 — Personas and Roles (Complete)

| # | Role | Symbol | Primary Skills | Focus |
|---|---|---|---|---|
| 1 | Gateway Orchestrator | GO | SK-07 | Route, coordinate, monitor |
| 2 | Soundness Guardian | Σ | SK-02, SK-03 | Axioms, sorry, kernel-checkability |
| 3 | Statement Oracle | Φ | SK-02, SK-03, SK-09 | Faithfulness, paper alignment |
| 4 | Novelty Scout | Ν | SK-02, SK-03, SK-11 | Deduplication, simplification |
| 5 | Quality Architect | Λ | SK-02, SK-03, SK-05 | Elegance, refactoring |
| 6 | Integration Sentinel | Ω | SK-02, SK-03, SK-10 | Naming, cross-refs, consistency |
| 7 | Implementer | — | SK-01, SK-05 | Write proofs |
| 8 | Specifier | — | SK-05, SK-09 | Write specifications |
| 9 | Researcher | — | SK-11, SK-38, SK-22 | Find knowledge |
| 10 | Synthesizer | — | SK-04, SK-23 | Knowledge management |
| 11 | Documenter | — | SK-10, SK-37 | Paper updates |
| 12 | RETRO Architect | RA | SK-35, SK-08 | Retroactive audit |
| 13 | Enforcement Engine | EE | SK-36, SK-39 | Run scripts, enforce gates |
| 14 | Domain Experts | DE | SK-12..21, 32, 33 | Domain-specific guidance |
| 15 | Census Agent | CA | SK-35 | Automated discovery |
| 16 | Triage Coordinator | TC | SK-35 | Priority assignment |
| 17 | Foundations Architect | Α | SK-22 | Research: axioms, definitions |
| 18 | Structure Strategist | Β | SK-22 | Research: proof architecture |
| 19 | Methods Scholar | Γ | SK-22 | Research: tactics, patterns |
| 20 | Bounds Analyst | Δ | SK-22 | Research: rates, complexity |
| 21 | Applications Bridge | Ε | SK-22 | Research: domain connections |

---

## Part 6 — Conflict Resolution

When skills produce conflicting recommendations:

### 6.1 Priority Rules

```
1. Soundness (Σ) always wins over elegance (Λ)
2. Faithfulness (Φ) always wins over naming (Ω)
3. Gateway (SK-07) breaks ties between clusters
4. QA gates (SK-39) override schedule (SK-24)
5. Enforcement violations (SK-36) override "this works" claims
```

### 6.2 Dispute Flow

```
Skill A recommends X, Skill B recommends Y
  → Gateway identifies conflict
  → Classify: which quality dimension (Q1-Q7)?
  → Higher-weighted dimension wins
  → If same dimension: council vote
  → If tie: Ω (Integration Sentinel) breaks tie
  → Record decision in ZK note
```

---

## Part 7 — Bootstrapping a New Project

To apply this ecosystem to a brand new Lean 4 project:

```
1. [SK-06] Set up project (lakefile.lean, toolchain, deps)
2. [SK-07] Initialize gateway (create tracking docs directory)
3. [SK-09] Extract claims from source documents
4. [SK-05] Create specifications for top-priority claims
5. [SK-01] Implement first proofs
6. [SK-03] Review first proofs (establish council rhythm)
7. [SK-04] Create first ZK notes
8. [SK-36] Set up enforcement scripts
9. [SK-39] Establish quality baseline
10. Iterate: feedforward (claims → specs → proofs) + feedback (proofs → docs)
```

---

## Part 8 — Retrofitting an Existing Project (RETRO Protocol Summary)

```
1. [SK-35] Phase R: retro_recon.py → census + dep graph + coverage
2. [SK-35] Phase E: council_precheck.sh per wave → baseline reports
3. [SK-35] Phase T: proof_quality.py → triage priorities
4. [SK-35] Phase R (review): per-wave council audit → findings + fixes
5. [SK-35] Phase O: enforce_all.sh --strict → steady-state graduation
6. [SK-39] Ongoing quality monitoring
```

---

## Part 9 — Integration Anti-Patterns

| Anti-Pattern | Why Harmful | Fix |
|---|---|---|
| Skill island | One skill operates without feeding back | Audit feedback loops F1-F18 |
| Gateway bypass | Skills calling each other directly without gateway knowledge | All cross-cluster comms via gateway |
| Cluster monologue | One cluster produces without consuming | Check inter-cluster protocols (Part 3) |
| Loop starvation | A feedback loop never fires | Verify loop health rules (Part 4.1) |
| Role confusion | Agent takes on multiple persona roles | One role per agent per session |
| Missing lifecycle | Only forward path, no backward | Always run both directions |
| Quality debt accumulation | Skip QA gates "just this once" | Hard gates are HARD — no exceptions |
