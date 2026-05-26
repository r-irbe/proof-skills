---
name: math-project-management
description: Project and product management for mathematical formalization projects. Covers dependency-aware scheduling, risk management for unprovable theorems, progress tracking, milestone planning, resource allocation across proof workstreams, technical debt management, and stakeholder communication. Use when planning formalization campaigns, tracking multi-module efforts, or managing the intersection of research and engineering in formal mathematics.
---

# Mathematical Project & Product Management

Methodology for managing large-scale formal mathematics projects as engineering endeavors.

---

## Part 1 — Formalization Project Structure

### 1.1 Work Breakdown Structure

```
Level 0: Project (Project Formalization)
Level 1: Domain (e.g., Stability Theory)
Level 2: Module (e.g., LyapunovStability.lean)
Level 3: Section (e.g., §14 Quadratic Lyapunov)
Level 4: Theorem (e.g., lyap_quadratic_nonneg)
Level 5: Proof task (e.g., "close case 3 using nlinarith")
```

### 1.2 Dependency-Aware Scheduling

```
1. Extract theorem dependency graph (imports + cross-references)
2. Compute topological sort → build order
3. Identify critical path (longest dependency chain)
4. Identify parallel opportunities (independent theorems/modules)
5. Schedule: critical path first, parallelize the rest
```

### 1.3 Critical Path Analysis

```markdown
# Critical Path: Project Formalization
## Longest dependency chain:

Tactics (shared infrastructure)
  → QualityGates (gate definitions referenced everywhere)
    → PhaseClassification (phases used in CCV, Pipeline)
      → CCVGating (CCV used in Phase Portrait, Stochastic)
        → PhasePortrait (connects quality + CCV + velocity)
          → LyapunovStability (stability uses phase/CCV/quality)
            → ReinforcementLearning (RL references Lyapunov)
              → AgenticSafety (safety builds on RL + Lyapunov)
                → StochasticCCV (stochastic extension)

## Critical path length: 9 modules (sequential)
## Parallelizable: CuspCatastrophe, ProvenanceChain, PipelineAdaptive (off critical path)
```

---

## Part 2 — Risk Management

### 2.1 Theorem-Level Risk Assessment

| Risk Factor | Weight | Assessment |
|---|---|---|
| **Difficulty** | 30% | 1 (trivial) to 5 (research-level) |
| **Dependency count** | 25% | How many downstream theorems need this? |
| **Alternative approaches** | 20% | 0 = no alternatives, 5 = many fallbacks |
| **Mathlib coverage** | 15% | Does Mathlib have relevant infrastructure? |
| **Precedent** | 10% | Has this been formalized before (any ITP)? |

```
Risk score = difficulty × dep_weight - alternatives × alt_weight - mathlib × ml_weight - precedent × prec_weight
```

### 2.2 Module-Level Risk Register

```markdown
# Risk Register: Project/CuspCatastrophe.lean

| Risk | Probability | Impact | Score | Mitigation |
|---|---|---|---|---|
| Cubic root analysis requires heavy real analysis | 0.7 | High | 7 | Use numeric verification as fallback |
| Cusp bifurcation set topology not in Mathlib | 0.9 | Medium | 5.4 | Define locally, contribute to Mathlib later |
| Discriminant classification requires `polyrith` | 0.5 | Low | 2 | Manual polynomial manipulation |
| Lean version update breaks calculus tactics | 0.2 | High | 2 | Pin version, test before upgrading |
```

### 2.3 Risk Mitigation Strategies

| Strategy | When to use |
|---|---|
| **Accept** | Low risk, low impact — document and monitor |
| **Weaken statement** | Theorem too hard — prove a weaker version that still serves the paper |
| **Alternative proof** | Primary approach stuck — try different proof strategy |
| **Upstream PR** | Needed Mathlib lemma missing — contribute it |
| **Table** | Research-level difficulty — defer to future work, document knowledge |
| **Decompose** | Large theorem — break into smaller lemmas that are individually provable |

---

## Part 3 — Progress Tracking

### 3.1 Key Metrics

| Metric | Formula | Cadence | Target |
|---|---|---|---|
| **Theorem velocity** | Theorems proved / week | Weekly | Positive trend |
| **Sorry burn-down** | Remaining sorries / initial sorries | Daily | → 0 |
| **Coverage rate** | Paper claims formalized / total claims | Weekly | → 100% |
| **Build health** | Days since last broken build | Continuous | → ∞ |
| **Review coverage** | Theorems reviewed / theorems proved | Weekly | → 100% |
| **Epistemic score** | From epistemic-mapping | Per research session | → 0.9 |
| **Technical debt** | Known quality issues deferred | Weekly | Stable or decreasing |

### 3.2 Sprint Planning (2-week cycles)

```markdown
# Sprint N: [dates]
## Goals
- [ ] Complete Project/[Module] deep audit
- [ ] Prove [N] theorems from specification backlog
- [ ] Resolve [N] P0/P1 issues from review council

## Capacity
- Available agent-hours: [N]
- Carry-over from last sprint: [N] items
- New items this sprint: [N] items

## Sprint Retrospective Template
- Theorems completed: [N] / [N planned]
- Blockers encountered: [list]
- Lessons learned: [list]
- Process improvements: [list]
```

### 3.3 Milestone Definitions

| Milestone | Criteria | Coverage |
|---|---|---|
| **M0: Scaffold** | All modules created, imports correct, build passes | Structure |
| **M1: Definitions** | All structures, types, and constants defined | 0% proofs |
| **M2: Key Theorems** | Critical path theorems proved | ~30% |
| **M3: Full Draft** | All paper claims have theorem stubs (may have sorry) | ~70% |
| **M4: Sorry-Free** | Zero sorry across all modules | 100% proofs |
| **M5: Reviewed** | All theorems passed council review | 100% reviewed |
| **M6: Documented** | Paper metrics synced, ZK populated, specs complete | 100% documented |

---

## Part 4 — Technical Debt Management

### 4.1 Debt Categories

| Category | Example | Impact | Priority |
|---|---|---|---|
| **Proof debt** | Long proof that works but should be shorter | Maintenance | P3 |
| **Architecture debt** | Wrong module for a theorem | Confusion | P2 |
| **Convention debt** | Missing docstrings, wrong naming | Consistency | P3 |
| **Automation debt** | Manual proof where tactic should work | Future speed | P2 |
| **Bridge debt** | Missing Nat ↔ ℝ coercion | Cross-module | P1 |
| **Test debt** | Theorem with no specification | Traceability | P2 |
| **Knowledge debt** | Proof technique used but not documented | Knowledge loss | P2 |

### 4.2 Debt Budget

Technical debt must not exceed 20% of total items at any milestone:
- At M4 (sorry-free): up to 20% may have P2/P3 debt
- At M5 (reviewed): debt for reviewed theorems resolved
- At M6 (documented): all debt documented or resolved

---

## Part 5 — Stakeholder Communication

### 5.1 Status Report Template

```markdown
# Project Formalization: Status Report [Date]

## Executive Summary
[1-2 sentences: milestone status, key achievement, main risk]

## Progress
| Module | Theorems | Sorry | Reviewed | Status |
|---|---|---|---|---|
| Tactics | 44/44 | 0 | 44 | ✅ Complete |
| QualityGates | 39/39 | 0 | 39 | ✅ Complete |
| ... | ... | ... | ... | ... |
| **Total** | **611/[target]** | **0** | **[N]** | |

## Key Achievements This Period
1. [Achievement 1]
2. [Achievement 2]

## Key Risks and Mitigations
1. [Risk 1] — [Mitigation]

## Next Period Plan
1. [Plan item 1]
2. [Plan item 2]
```

### 5.2 Paper Synchronization Checklist

Before any paper submission:
- [ ] `lake build` succeeds with 0 errors
- [ ] Theorem counts in paper match `grep` output
- [ ] `metric_sync.py` reports all green
- [ ] `review_coverage.py` reports 100%
- [ ] `axiom_audit.py` reports no forbidden axioms
- [ ] All P0/P1 issues resolved
- [ ] Epistemic score > 0.8

---

## Part 6 — Research Council Integration

| PM Topic | Research Council Member |
|---|---|
| Difficulty estimation | Γ (Methods Scholar) + Δ (Bounds Analyst) |
| Risk assessment | All (each for their domain) |
| Alternative approach planning | Γ (Methods Scholar) |
| Priority setting | Ε (Applications Bridge) — real-world impact |
| Milestone criteria review | All (consensus) |
| Technical debt classification | Β (Structure Strategist) |
| Sprint goal selection | All (weighted vote) |
