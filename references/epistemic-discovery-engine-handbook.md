---
title: "Epistemic Discovery Engine Handbook"
status: "reference"
extracted_from: "skills/epistemic-discovery-engine/SKILL.md"
extracted_on: "2026-05-27"
scope: "Parts 1-7 (Discovery Modes; UU Hunting Protocols; Reporting and Outputs; Integration Architecture; Anti-Stagnation Mechanisms; Project Relevance; Cross-References)."
loader_hint: "Load when @epistemic-discovery-engine routes here for methodology details; not needed for the dispatch decision."
---

# Epistemic Discovery Engine Handbook

> **Layering note.** This file holds the deep methodology content
> previously embedded in [`skills/epistemic-discovery-engine/SKILL.md`](../skills/epistemic-discovery-engine/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow /
> Recovery / Handoffs) + the parts index. This file holds the full
> encyclopaedia of discovery modes; uu hunting protocols; reporting and outputs; integration architecture, etc.
> Zero fidelity loss vs the pre-layering revision.

---

## Part 1 — Discovery Modes

### 1.1 Sweep Mode (Scheduled, Breadth-First)

Systematic coverage sweeps across all Project modules and adjacent domains. Run periodically or at milestones.

| Sweep type | Scope | Frequency | Trigger |
|---|---|---|---|
| **Census sweep** | All 12 Project modules | Every 50 new theorems | Automated |
| **Dependency sweep** | Mathlib dependency surface | Every Mathlib bump | Automated |
| **Literature sweep** | arXiv, Lean Zulip, Mathlib PRs | Weekly | Scheduled |
| **Cross-domain sweep** | Adjacent fields (control, econ, cognitive) | Monthly | Research Council request |
| **Community sweep** | Lean community projects, ITP conferences | Quarterly | Manual |

**Census sweep protocol:**
1. `grep -c "^theorem\|^lemma\|^def\|^instance"` across all modules
2. Diff against last census — detect new defs without lemmas, lemmas without usage
3. For every new definition: "What properties does this NOT capture?"
4. For every new theorem: "What generalizations exist that we haven't stated?"
5. Update KK count, flag potential KU items

**Dependency sweep protocol:**
1. Extract all `import Mathlib.*` lines from Project
2. For each imported file, check Mathlib changelog since last sweep
3. Flag: new lemmas that could replace manual proofs (UK candidates)
4. Flag: deprecated APIs that may break existing proofs (KK→KU regression)
5. Flag: new files in adjacent Mathlib directories (potential UU→UK)

### 1.2 Probe Mode (Targeted, Depth-First)

Deep investigation into a specific area flagged by sweep mode or the Research Council.

**Probe protocol (per target):**
1. **Scope:** Define the target concept/gap precisely (≤ 1 sentence)
2. **Source:** Identify 3-5 authoritative references (Mathlib > papers > textbooks)
3. **Dig:** For each source, extract: definitions, key theorems, proof techniques, dependencies
4. **Compare:** Diff against what Project has — catalog exact gaps
5. **Classify:** Map every finding to a quadrant transition (UU→KU, UK→KK, etc.)
6. **Report:** Produce a probe report (see §3.2) and update the epistemic map

**Probe depth levels:**

| Level | Iterations | Output | When |
|---|---|---|---|
| Shallow | 1 pass through sources | Quick gap list | Triage |
| Standard | 2-3 passes with cross-referencing | Structured probe report | Normal ops |
| Deep | 4-5 passes with proof-of-concept | Full analysis + draft spec | Before major work |
| Exhaustive | 5+ with community engagement | Comprehensive survey + RFC | New domain entry |

### 1.3 Alert Mode (Reactive, Event-Driven)

Triggered by external events or anomalies detected during normal work.

| Alert trigger | Response | Urgency |
|---|---|---|
| Proof breaks after Lean/Mathlib update | Dependency sweep (targeted) | P1 |
| Review Council flags missing context | Probe the flagged area | P2 |
| New arXiv paper in the project-adjacent area | Quick literature probe | P3 |
| Lean community discussion about related topic | Community probe | P3 |
| Epistemic score drops | Full census sweep + targeted probes | P1 |
| KU item stale > 30 days | Investigate blockage | P2 |
| UU item stale > 90 days | Mandatory red team probe | P1 |

---

## Part 2 — UU Hunting Protocols

The core mission: systematically reduce the unknown-unknown zone.

### 2.1 The Eight UU-Shrinking Methods

Each method targets a different class of blind spot:

#### Method 1 — Red Team Adversarial Probing
**Lead:** Ε (Applications Bridge)
**Protocol:** Assume adversarial intent — what could go wrong that nobody mentioned?
- Step 1: Select a formalization claim (e.g., "trust monotonically decreases under violation")
- Step 2: Generate 5 counterarguments or edge cases
- Step 3: For each, check if the formalization handles it
- Step 4: Unhandled cases → new KU items

#### Method 2 — Cross-Disciplinary Survey
**Lead:** Α (Foundations Architect)
**Protocol:** Check what adjacent fields know that we might have missed.
- Map: Project domain → 3-5 adjacent fields (e.g., Lyapunov → control theory + mathematical biology + economics)
- For each field: What are their core theorems? Do we have equivalents?
- New theorems found → UK items (they exist, we missed them)

#### Method 3 — Failure Mode Enumeration
**Lead:** Δ (Bounds Analyst)
**Protocol:** Enumerate failure modes of each major theorem.
- For each theorem: What assumptions does it require?
- For each assumption: Under what conditions could it fail?
- For each failure condition: Is this addressed anywhere?
- Unaddressed failure modes → new UU→KU

#### Method 4 — External Review Solicitation
**Lead:** Γ (Methods Scholar)
**Protocol:** Show formalization to external experts.
- Prepare review package: key definitions, theorem statements (no proofs)
- Submit to: Lean Zulip, domain experts, Mathlib reviewers
- Catalogue feedback: surprises, missed connections, alternative approaches

#### Method 5 — Adversarial Query Generation
**Lead:** Ε (Applications Bridge)
**Protocol:** Generate questions that the formalization SHOULD answer but might not.
- From each paper section: extract implicit questions
- From each definition: "What is NOT a [defined concept]?"
- From each theorem: "What happens when the hypothesis fails?"
- Unanswerable queries → new KU items

#### Method 6 — Analogy Check
**Lead:** Β (Structure Strategist)
**Protocol:** Find analogies in other formalization projects.
- Identify 3-5 comparable Lean projects (Mathlib four, lean-liquid, sphere-eversion, etc.)
- For each: What did they formalize that we haven't considered?
- Structural parallels → potential UK items

#### Method 7 — Completeness Challenge
**Lead:** Α (Foundations Architect) + Β (Structure Strategist)
**Protocol:** For each algebraic structure, systematically check standard properties.
- Is it associative? Commutative? Has identity? Has inverse?
- Is the functor faithful? Full? Essentially surjective?
- Does the space satisfy separation axioms? Compactness? Completeness?
- Missing standard properties → new KU items

#### Method 8 — Edge Case Generation
**Lead:** Δ (Bounds Analyst) + Γ (Methods Scholar)
**Protocol:** What happens at the boundaries?
- For each bound: What happens at the exact bound value?
- For each convergence: What is the rate? Is it tight?
- For each "for all": What is the smallest/largest sensible domain?
- Untested edge cases → new KU items (or, if surprising: new UU→KU)

### 2.2 UU Hunting Schedule

| Cadence | Methods applied | Depth | Scope |
|---|---|---|---|
| Per-session | 5 (adversarial queries) on current work | Shallow | Current module |
| Weekly | 1, 3, 8 on recent changes | Standard | Changed modules |
| Monthly | 2, 6, 7 on all modules | Standard | All modules |
| Quarterly | All 8 methods | Deep | Full project + adjacencies |
| Pre-release | All 8 methods | Exhaustive | Full project |

### 2.3 UU Estimation Heuristic

Since UUs are by definition unknown, estimation uses proxies:

```
Estimated UU count ≈ max(
  0.1 × KU_count,                          # At least 10% of known gaps
  cross_domain_count × avg_new_findings,    # Adjacent-field projection
  historical_discovery_rate × months_ahead  # Trend extrapolation
)
```

Estimation refines over time as discovery rate data accumulates.

---

## Part 3 — Reporting and Outputs

### 3.1 Sweep Report Template

```markdown
# Discovery Engine — Sweep Report
## Type: [Census|Dependency|Literature|Cross-domain|Community]
## Date: [ISO-8601]
## Scope: [description]

### Summary
| Metric | Before | After | Δ |
|---|---|---|---|
| KK count | --- | --- | --- |
| KU count | --- | --- | --- |
| UK count | --- | --- | --- |
| UU estimate | --- | --- | --- |
| Epistemic Score | --- | --- | --- |

### Transitions Found
| Item | From | To | Method | Details |
|---|---|---|---|---|
| [item] | UU | KU | Red team | [description] |
| [item] | UK | KK | Dependency sweep | [Mathlib ref] |
| ... | ... | ... | ... | ... |

### Actions Required
- [ ] [action 1 — assigned to [member]]
- [ ] [action 2 — priority P[N]]
...
```

### 3.2 Probe Report Template

```markdown
# Discovery Engine — Probe Report
## Target: [concept/gap being probed]
## Level: [Shallow|Standard|Deep|Exhaustive]
## Lead member: [Α/Β/Γ/Δ/Ε]
## Date: [ISO-8601]

### Scope Definition
[1-sentence precise scope]

### Sources Consulted
1. [source] — [relevance]
2. [source] — [relevance]
...

### Findings
| Finding | Quadrant Impact | Confidence | Priority |
|---|---|---|---|
| [finding] | UU→KU | High | P2 |
| [finding] | UK→KK | Medium | P3 |

### Gap Analysis
- Project has: [what we have]
- Literature has: [what exists]
- Delta: [exact gap]

### Recommendation
[What to formalize / integrate / investigate further]

### Epistemic Map Update
[Specific updates to the epistemic-mapping quadrant data]
```

### 3.3 Alert Report Template

```markdown
# Discovery Engine — Alert
## Trigger: [event description]
## Urgency: P[1-3]
## Date: [ISO-8601]

### What happened
[Brief description]

### Epistemic impact
[Which quadrant is affected; potential KK→KU regression or new UU emergence]

### Recommended action
[Sweep type, probe target, or escalation to Research Council]
```

---

## Part 4 — Integration Architecture

### 4.1 Data Flow

```
epistemic-discovery-engine
    ├── reads ← epistemic-mapping (current quadrant state, scores)
    ├── reads ← lean-zettelkasten (existing knowledge, avoiding re-research)
    ├── reads ← lean-research (prior search results)
    ├── writes → epistemic-mapping (quadrant transitions, score updates)
    ├── writes → lean-zettelkasten (new literature/fleeting notes)
    ├── feeds → research-council (discovery findings for strategy)
    ├── feeds → research-synthesis-engine (raw material for synthesis)
    └── reports → lean-gateway (health metrics, alert flags)
```

### 4.2 Trigger → Skill Dispatch

| Trigger | Discovery Engine Action | Downstream Skill |
|---|---|---|
| New module added | Census sweep + cross-domain probe | research-council (strategy) |
| Mathlib bump | Dependency sweep | lean-build (build check) |
| Review Council flag | Targeted probe | lean-research (search execution) |
| Score stagnation | All 8 UU methods | research-synthesis-engine |
| Pre-release gate | Exhaustive sweep | lean-quality-engine (quality sign-off) |
| New domain skill created | Cross-domain sweep for the domain | [relevant domain skill] |

### 4.3 Domain Skill Coverage Matrix

The Discovery Engine checks all domain skills for epistemic coverage:

| Domain Skill | KK items | KU items | Last swept | Health |
|---|---|---|---|---|
| math-nonlinear-dynamics | — | — | — | — |
| math-time-series | — | — | — | — |
| math-graph-knowledge | — | — | — | — |
| math-measure-probability | — | — | — | — |
| math-algebra-category | — | — | — | — |
| math-optimization-game | — | — | — | — |
| math-topology-analysis | — | — | — | — |
| ai-symbolic-neuro | — | — | — | — |
| ai-agentic-evolving | — | — | — | — |
| ai-high-stakes-verifiable | — | — | — | — |
| ai-causal-deontic | — | — | — | — |
| ai-commonsense-reasoning | — | — | — | — |
| applied-legal-reasoning | — | — | — | — |
| applied-intelligence-analysis | — | — | — | — |
| applied-strategy-analysis | — | — | — | — |
| applied-data-information-security | — | — | — | — |
| applied-engineering-disciplines | — | — | — | — |

---

## Part 5 — Anti-Stagnation Mechanisms

### 5.1 Score Plateau Detection

If epistemic score does not improve for 3 consecutive sweeps:
1. Trigger **full UU hunt** (all 8 methods, deep level)
2. Rotate the lead member (fresh perspective)
3. Expand cross-domain scope by 2 additional fields
4. Mandatory external review solicitation

### 5.2 Comfort Zone Breaker

Periodically (monthly) select the 3 Project modules with the HIGHEST epistemic scores and probe them:
- "What are we confidently wrong about?"
- "What simplification did we make that might not hold?"
- "What adjacent theorem did we choose NOT to formalize, and why?"

High-confidence areas are the most dangerous for hidden UU items.

### 5.3 Novelty Budget

Allocate 20% of discovery effort to areas with NO current KU items. Rationale: if we have zero known unknowns in an area, either we truly know everything (unlikely) or our UU zone is large.

---

## Part 6 — Project Relevance

| Project Module | Primary Discovery Focus | Key Methods |
|---|---|---|
| Tactics.lean | Tactic completeness, missing automation | 7 (completeness), 5 (queries) |
| LyapunovStability.lean | General Lyapunov theory beyond quadratic | 2 (cross-domain), 3 (failure) |
| AgenticSafety.lean | Multi-agent scalability, trust composition | 1 (red team), 8 (edge cases) |
| ReinforcementLearning.lean | Beyond tabular, continuous state spaces | 2 (cross-domain), 6 (analogy) |
| StochasticCCV.lean | Mixing time tightness, ergodic universality | 3 (failure), 4 (external) |
| CuspCatastrophe.lean | Smoothness assumptions, higher-dim cusps | 5 (queries), 7 (completeness) |
| QualityGates.lean | Gate composability, lattice properties | 7 (completeness), 8 (edges) |
| PhasePortrait.lean | Phase landscape completeness | 2 (cross-domain), 7 (complete) |
| ProvenanceChains.lean | Chain integrity, graph-theoretic properties | 6 (analogy), 8 (edge cases) |
| OKDFormalization.lean | KM theory coverage | 2 (cross-domain), 5 (queries) |
| SCCExperiential.lean | SECI completeness, sociological grounding | 4 (external), 5 (queries) |
| AdaptivePolicies.lean | Policy composition, scalability | 1 (red team), 3 (failure) |

---

## Part 7 — Cross-References

| Skill | Relationship | Interface |
|---|---|---|
| epistemic-mapping | Reads/writes quadrant data | Quadrant state + transitions |
| research-council | Feeds findings; receives strategy | Discovery reports → RC sessions |
| research-synthesis-engine | Provides raw material | Discovery findings → synthesis |
| lean-research | Delegates specific searches | Research requests |
| lean-zettelkasten | Reads existing; writes new notes | ZK query/write |
| lean-gateway | Reports metrics; receives triggers | Health dashboard |
| lean-quality-engine | Pre-release gate coordination | Quality metrics |
| lean-review-council | Receives flags; feeds back findings | Alert/feedback loop |
| lean-retro-methodology | Retrospective findings feed sweeps | Retro insights → sweep targets |
| All domain skills (math-*, ai-*, applied-*) | Coverage matrix tracking | Domain coverage reports |
