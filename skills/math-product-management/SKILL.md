---
name: math-product-management
description: Product management for mathematical formalization projects — roadmap creation, stakeholder management, feature prioritization for formal verification artifacts, theorem portfolio management, release planning, and the business/academic value analysis of formal proofs. Complements math-project-management (scheduling/execution) with strategic product thinking.
---

# Math Product Management

Strategic product thinking applied to formal verification projects. While math-project-management handles execution (schedules, tasks, milestones), this skill handles strategy (what to build, for whom, why, and in what order).

---

## Part 1 — Product vs. Project Management

| Dimension | Project Management (SK-24) | Product Management (this skill) |
|---|---|---|
| Question | HOW and WHEN? | WHAT and WHY? |
| Focus | Execution, scheduling, risk | Strategy, value, stakeholders |
| Output | Gantt chart, task list, milestones | Roadmap, prioritized backlog, value analysis |
| Horizon | Current phase/milestone | Multi-release, long-term vision |
| Success | On time, on scope | Right theorems, right impact |

---

## Part 2 — Theorem Portfolio Management

### 2.1 Value Taxonomy

Not all theorems are equally valuable. Categorize by:

| Value Type | Description | Example |
|---|---|---|
| **Foundational** | Enables many downstream results | Contraction mapping lemma in Tactics.lean |
| **Novel** | New result not in Mathlib or literature | project-specific convergence bounds |
| **Spectacular** | Impressive, quotable, paper-worthy | "≥1,255 theorems, zero sorry, kernel-checked" |
| **Defensive** | Prevents errors, catches flawed reasoning | Axiom audits, vacuity checks |
| **Bridge** | Connects two domains or modules | Lyapunov ↔ RL governance convergence |
| **Utility** | Used frequently, reduces proof effort | Reusable simplex arithmetic lemmas |

### 2.2 Prioritization Framework (RICE for Theorems)

```
Score = (Reach × Impact × Confidence) / Effort

Where:
  Reach = How many other theorems/claims depend on this? (1-10)
  Impact = {3: foundational, 2: novel/bridge, 1: utility, 0.5: defensive}
  Confidence = How sure are we it's provable? (0.5-1.0)
  Effort = Estimated proof complexity (1: trivial, 5: hard, 10: research-level)
```

### 2.3 Portfolio Health Metrics

| Metric | Healthy Range | Project Current |
|---|---|---|
| Foundational coverage | >80% of paper foundations proven | Track per coverage matrix |
| Novel theorem ratio | 10-30% of total | Count project-specific results |
| Bridge density | ≥1 bridge per module pair used together | Count cross-module theorems |
| Utility reuse rate | Each utility used ≥3 times | `grep` usage counts |
| Technical debt (sorry) | 0 | 0 ✓ |

---

## Part 3 — Stakeholder Analysis

### 3.1 Stakeholder Map for Project

| Stakeholder | Interest | Needs from formalization |
|---|---|---|
| **Paper reviewers** | Correctness, credibility | Zero sorry, clean axioms, coverage % |
| **Domain experts** | Faithfulness to intended meaning | Φ review, specification traces |
| **Future developers** | Maintainability, extensibility | Documentation, ZK notes, conventions |
| **CI/Build system** | Reliability, reproducibility | Clean builds, nightly tests |
| **The team** | Productivity, satisfaction | Tooling, automation, clear process |
| **Academic community** | Reproducibility, novelty | Open source, documentation, Mathlib contributions |

### 3.2 Stakeholder Communication Plan

| Stakeholder | Artifact | Frequency |
|---|---|---|
| Paper reviewers | Coverage matrix + verification table | Per submission |
| Domain experts | Erratum/insight reports | Per milestone |
| Future developers | AGENT.md + ZK index + skill docs | Continuously |
| CI/Build | enforce_all.sh reports | Per commit/nightly |
| Academic community | README + technical report | Per release |

---

## Part 4 — Roadmap Planning

### 4.1 Release Cadence for Formal Verification

| Phase | Duration | Goal |
|---|---|---|
| **Alpha** | Initial | Core structures, key theorems, some sorry |
| **Beta** | Iterative | Zero sorry, all core theorems, basic review |
| **RC** | Stabilization | Full coverage, council review, enforcement passing |
| **Release** | Final | Publication-ready, all gates green |
| **Maintenance** | Ongoing | Mathlib version bumps, new paper revisions |

### 4.2 Feature Backlog Categories

| Category | Examples |
|---|---|
| **Must Have** | Zero sorry, clean axioms, build passes |
| **Should Have** | >90% coverage, all modules reviewed, errata resolved |
| **Could Have** | Tactic diversity metrics, full ZK index, Mathlib contribution |
| **Won't Have (now)** | Mechanized paper generation, interactive visualizations |

### 4.3 Roadmap Template

```markdown
# the project's Lean Formalization Roadmap

## v1.0 — Paper Submission
- [x] All 12 modules exist and build
- [x] Zero sorry
- [ ] Coverage matrix >90%
- [ ] All modules council-reviewed (at least Pipeline baseline)
- [ ] Paper verification table generated

## v1.1 — Post-Review
- [ ] Address reviewer feedback
- [ ] Close any coverage gaps reviewers identify
- [ ] Strengthen results where possible

## v2.0 — Extended Framework
- [ ] Generalize beyond project-specific claims
- [ ] Contribute reusable lemmas to Mathlib
- [ ] Support additional paper sections
```

---

## Part 5 — Value Analysis

### 5.1 Value of Formal Verification

| Value Driver | Measurement | Compounding Effect |
|---|---|---|
| **Error detection** | Errata found / paper claims | Early detection prevents downstream errors |
| **Precision forcing** | Hypotheses made explicit | Clarifies informal reasoning |
| **Reuse enablement** | Lemmas reused across modules | Each reuse saves future proof effort |
| **Credibility** | "≥1,255 theorems, zero sorry" | Competitive advantage in publication |
| **Knowledge capture** | ZK notes, specifications | Survives team changes |

### 5.2 Cost of NOT Formalizing

| Risk | Impact | Probability if unformalised |
|---|---|---|
| Hidden flaw in main theorem | Paper retraction | Low but catastrophic |
| Missing hypothesis | Incorrect theorem statement | Medium |
| Subtle type error | Proof of wrong thing | Medium |
| Reviewer doubt | Paper rejection | High for formal claims |
| Knowledge loss | Can't extend/maintain | High over time |

---

## Part 6 — Decision Frameworks

### 6.1 Build vs. Reuse

When deciding whether to prove a theorem from scratch or reuse Mathlib:

```
IF exact Mathlib theorem exists:
  REUSE (zero effort, maximum credibility)
ELIF Mathlib has 80%+ of what's needed:
  WRAP (small adaptation, good credibility)
ELIF result is project-specific:
  BUILD from scratch with Mathlib foundations
ELIF result is general mathematical knowledge:
  CONSIDER Mathlib PR (community benefit)
```

### 6.2 Depth vs. Breadth Trade-off

```
Depth: Prove one result completely, with all edge cases
Breadth: Prove many results at basic level

For paper submission: Breadth first (coverage), then depth (strength)
For long-term: Depth on foundational results (they compound)
```

---

## Part 7 — Metrics and Analytics

### 7.1 Product Health Dashboard

```markdown
# Product Health
| Metric | Value | Trend | Target |
|---|---|---|---|
| Total theorems | ≥1,255 | ↑ | ≥1,000 |
| Coverage % | 82% | ↑ | ≥90% |
| Sorry count | 0 | → | 0 |
| Reuse rate (Tactics.lean) | 3.2 uses/lemma | ↑ | ≥3 |
| Bridge theorems | 14 | ↑ | ≥12 |
| Novel results | 45 | ↑ | ≥30 |
| Errata found | 3 | → | track |
| Build time | 12 min | → | <15 min |
```

### 7.2 Velocity Tracking

```
Theorems proven per session (velocity)
Coverage points gained per session (acceleration)
Errata resolved per session (quality)
ZK notes created per session (knowledge capture)
```

---

## Part 8 — Cross-References

| If working on... | Also consult... |
|---|---|
| Project scheduling | `math-project-management` (SK-24) |
| Quality gates | `lean-quality-engine` (SK-39) |
| Stakeholder communication | `lean-doc-improvement` (SK-10) |
| Roadmap prioritization | `lean-integration-protocol` (SK-40) |
| Coverage tracking | `lean-doc-feedback` (SK-37) |
| Team process | `lean-review-council` (SK-03) |
