---
title: Research Council Handbook
status: reference
extracted_from: skills/research-council/SKILL.md
extracted_on: '2026-05-27'
scope: Parts 1-9 (The Five Research Members; The RESEARCH Loop (Dual to RALPH); Epistemic
  Mapping (Rumsfeld Matrix); Cross-Disciplinary Research Domains; Research Session
  Protocol; Literature Synthesis Protocol; Integration with Other Skills; Self-Improvement;
  Project Current State & Proven Methodology).
loader_hint: Load when @research-council routes here for methodology details; not
  needed for the dispatch decision.
---

## Quick-Lookup Indexing Tables (`mathcomp-skills` Three-Entry-Point Pattern)

### Table 1: Goal-Shape-First (`templates` Entry Point)

| Goal / Term Shape | Primary Tactic / Pattern | Canonical Recipe / Notes |
| :--- | :--- | :--- |
| Open-ended formalization frontier or unknown unknowns | 5-Member Research Council (`Α, Β, Γ, Δ, Ε`) + RESEARCH loop | Parallelize across Foundations, Dynamics, Epistemics, Discrete, and Bridge |
| Multi-paper / multi-repo literature corpus | 5-Role Synthesis Engine (`Scanner -> Clusterer -> Distiller -> Verifier -> Publisher`) | Emit citation-verified concept graph and `@lean-specification` backlog |

### Table 2: Intent-First (`phrasebook` Entry Point)

| User / Engineer Intent | Recommended Tool / Idiom | Actionable Recipe |
| :--- | :--- | :--- |
| Discover missing bridge theorems across modules | Dependency & gap mode discovery | Compare domain concept lattice against compiled `.ilean` declarations |
| Synthesize conflicting definitions across papers | Chair `Ε` (`research-epsilon-bridge`) concordance table | Record explicit ADR choosing the canonical Lean carrier |

### Table 3: Error / Bottleneck-First (`errors` Entry Point)

| Symptom / Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Literature synthesis cites unverified AI-generated claims | Missing trust-tier tagging (`T-HV` vs `T-AI`) | Quarantine unverified conjectures and screen via `@counterexample-first-proving` |
| Research report produces prose without actionable Lean specs | Missing handoff to `specifier` | Emit concrete 3-part candidate signatures at end of council synthesis |

---

# Research Council Handbook

> **Layering note.** This file holds the deep methodology content
> previously embedded in [`skills/research-council/SKILL.md`](../skills/research-council/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow /
> Recovery / Handoffs) + the parts index. This file holds the full
> encyclopaedia of the five research members; the research loop (dual to ralph); epistemic mapping (rumsfeld matrix); cross-disciplinary research domains, etc.
> Zero fidelity loss vs the pre-layering revision.

---

## Part 1 -- The Five Research Members

### 1.1 Α -- Foundations Architect

**Greek letter:** Alpha (Α)
**Soul:** "What are the foundational assumptions, and do they hold?"
**Domain:** Logic, type theory, axiomatic foundations, universe levels, constructive/classical choices, Lean meta-theory

**RALPH specialization:**
- **Review:** Audit foundational assumptions in existing work
- **Analyze:** Identify which axioms/foundations a domain requires
- **Learn:** Study foundation-level connections across domains
- **Plan:** Design the type-theoretic architecture for new formalization
- **Handle:** Resolve foundational inconsistencies or level-universe issues

**Competencies:**
- Mathlib typeclass hierarchy navigation
- Universe polymorphism decisions
- Classical vs constructive strategic choices
- Axiom minimality analysis
- Cross-domain foundational bridges

### 1.2 Β -- Structure Strategist

**Greek letter:** Beta (Β)
**Soul:** "What is the right mathematical structure for this domain?"
**Domain:** Algebraic structures, category theory, lattice design, representation choices, data structure selection

**RALPH specialization:**
- **Review:** Evaluate structural choices in existing formalizations
- **Analyze:** Map a domain's natural algebraic/categorical structure
- **Learn:** Study how similar domains are structured in Mathlib
- **Plan:** Design the typeclasses, structures, and hierarchies for new work
- **Handle:** Restructure when initial choices prove suboptimal

**Competencies:**
- Algebraic hierarchy design
- Category-theoretic modeling
- Lattice and order structure selection
- Representation theorem identification
- Isomorphism and equivalence detection

### 1.3 Γ -- Methods Scholar

**Greek letter:** Gamma (Γ)
**Soul:** "What proof techniques and methods will work here?"
**Domain:** Proof strategies, tactic selection, mathematical methodology, proof patterns, automation assessment

**RALPH specialization:**
- **Review:** Evaluate proof technique choices in existing work
- **Analyze:** Classify a goal by proof method (induction, contradiction, construction, ...)
- **Learn:** Study successful proof patterns in similar Mathlib proofs
- **Plan:** Design the proof strategy for theorem specifications
- **Handle:** Find alternative strategies when primary approach fails

**Competencies:**
- Tactic selection and sequencing
- Induction schema selection (natural, strong, well-founded, structural)
- Proof by contradiction vs direct proof decisions
- Automation boundary assessment (tactic priority: `grind` > `omega` > `norm_num` > `simp only` > `nlinarith` > `linarith` > `ring` > `positivity` > `field_simp` > `decide` > `aesop`; `grind` is priority #1 and replaced all deprecated `proj_*` tactics)
- Proof architecture (calc blocks, suffices, have chains)

### 1.4 Δ -- Bounds Analyst

**Greek letter:** Delta (Δ)
**Soul:** "How tight are the bounds, and can we do better?"
**Domain:** Quantitative analysis, convergence rates, error estimates, complexity bounds, numerical precision

**RALPH specialization:**
- **Review:** Audit numerical claims, convergence rates, bounds
- **Analyze:** Compute or estimate key quantities (Lipschitz constants, spectral gaps, ...)
- **Learn:** Study optimal bounds in the literature
- **Plan:** Design proof strategies that yield the tightest possible bounds
- **Handle:** Tighten loose bounds or prove they cannot be tightened

**Competencies:**
- Convergence rate analysis
- Spectral analysis
- Perturbation bounds
- Complexity analysis (computational and proof)
- Optimality certificates

### 1.5 Ε -- Applications Bridge

**Greek letter:** Epsilon (Ε)
**Soul:** "Does this matter for the real world, and are we formalizing the right thing?"
**Domain:** Domain expertise, requirements engineering, paper-to-spec translation, cross-disciplinary connections, stakeholder needs

**RALPH specialization:**
- **Review:** Verify that formal claims match real-world requirements
- **Analyze:** Map between informal domain concepts and formal structures
- **Learn:** Study application-domain literature (KM, AI governance, law, intelligence)
- **Plan:** Prioritize formalization targets by real-world impact
- **Handle:** Bridge gaps between mathematical abstraction and practical meaning

**Competencies:**
- Project paper claim extraction
- EU AI Act / LED compliance interpretation
- Intelligence analysis methodology
- Knowledge management theory
- Cross-disciplinary vocabulary translation

---

## Part 2 -- The RESEARCH Loop (Dual to RALPH)

Where the Review Council uses **RALPH** (Review-Analyze-Learn-Plan-Handle), the Research Council uses **RESEARCH**:

```
R -- Reconnaissance: survey the landscape (literature, Mathlib, community)
E -- Explore: deep-dive into promising areas
S -- Synthesize: combine findings into coherent understanding
E -- Evaluate: assess our epistemic position (Rumsfeld matrix)
A -- Architect: design the formal approach
R -- Review: peer-review the research plan with all 5 members
C -- Commit: produce specification documents
H -- Handoff: transfer to Review Council / Implementation
```

### 2.1 Anti-Collapse Safeguards

| Safeguard | Mechanism | Threshold |
|---|---|---|
| Depth cap | Max 5 RESEARCH iterations per topic | Hard limit |
| Breadth cap | Max 7 sub-topics per exploration | Requires justification to exceed |
| Time budget | Each depth level has time allocation | Quick/Standard/Deep/Exhaustive |
| Diminishing returns | If iteration N yields < 2 new insights, stop | Auto-detect |
| Scope drift | Every finding must map to an Project module or extension | Mandatory check |
| Redundancy | Check ZK before researching -- may already be answered | Mandatory first step |

### 2.2 Consensus Protocol

Research Council decisions use weighted consensus:

| Decision type | Α weight | Β weight | Γ weight | Δ weight | Ε weight | Threshold |
|---|---|---|---|---|---|---|
| Foundational choice | 3 | 2 | 1 | 1 | 1 | ≥ 5/8 |
| Structure design | 1 | 3 | 2 | 1 | 1 | ≥ 5/8 |
| Method selection | 1 | 1 | 3 | 2 | 1 | ≥ 5/8 |
| Bound assessment | 1 | 1 | 1 | 3 | 2 | ≥ 5/8 |
| Relevance/priority | 1 | 1 | 1 | 1 | 3 | ≥ 4/7 |

**Veto power:** Α can veto any foundational choice; Ε can veto any relevance claim.

---

## Part 3 -- Epistemic Mapping (Rumsfeld Matrix)

The Research Council systematically maps the knowledge landscape using the Johari-Rumsfeld matrix:

### 3.1 The Four Quadrants

```
                    KNOWN to us          UNKNOWN to us
                 ┌──────────────────┬──────────────────┐
  KNOWN to       │  KNOWN KNOWNS    │  UNKNOWN KNOWNS  │
  exist          │  (Verified)      │  (Blind spots)   │
                 │  We know it and  │  Others know it   │
                 │  have formalized │  but we missed it │
                 ├──────────────────┼──────────────────┤
  UNKNOWN if     │  KNOWN UNKNOWNS  │  UNKNOWN UNKNOWNS│
  it exists      │  (Research gaps)  │  (Black swans)   │
                 │  We know we       │  We don't know   │
                 │  don't know this  │  it exists        │
                 └──────────────────┴──────────────────┘
```

### 3.2 Quadrant Detection Methods

| Quadrant | Detection Method | Research Council Lead |
|---|---|---|
| **Known Knowns** | Census of existing theorems + coverage matrix | All (automated) |
| **Known Unknowns** | Gap analysis: paper claims - formalized theorems | Ε → Β |
| **Unknown Knowns** | Literature search: what have others formalized that we missed? | Γ → Α |
| **Unknown Unknowns** | Cross-disciplinary survey, expert consultation, adversarial red-teaming | Ε → all |

### 3.3 Reducing Unknown Unknowns

Strategies for converting unknown unknowns to known categories:

1. **Cross-disciplinary survey** -- Check if adjacent fields (control theory, economics, cognitive science) have formalizations that cover our blind spots
2. **Red team session** -- Ε plays adversary: "What assumption are we making that we haven't questioned?"
3. **Failure mode analysis** -- "What could go wrong with our formalization that we haven't considered?"
4. **External review** -- Submit to Lean Zulip or Mathlib community for feedback
5. **Historical case study** -- Study where similar formalization projects discovered late surprises
6. **Completeness audit** -- For every definition, ask: "What properties does this NOT capture?"

### 3.4 Epistemic Map Template

```markdown
# Epistemic Map: [Domain/Module]
## Date: [ISO-8601]
## Council: Α, Β, Γ, Δ, Ε

### Known Knowns (Formalized & Verified)
| Item | Module | Theorem | Confidence |
|---|---|---|---|
| Gate monotonicity | QualityGates | quality_gate_monotone | High |
| Trust contraction | AgenticSafety | trust_tR_contraction_raw | High |
| ... | ... | ... | ... |

### Known Unknowns (Identified Gaps)
| Gap | Expected difficulty | Priority | Assigned to |
|---|---|---|---|
| Cusp bifurcation set topology | Research-level | P2 | Γ, Δ |
| Multi-agent trust composition | Hard | P1 | Β, Δ |
| ... | ... | ... | ... |

### Unknown Knowns (Blind Spots Discovered)
| Item | Source | Our gap | Action |
|---|---|---|---|
| Mathlib has ContractingWith.fixedPoint | Mathlib docs | We proved manually | Refactor to use Mathlib |
| ... | ... | ... | ... |

### Unknown Unknowns (Risks & Black Swans)
| Risk area | Detection method | Mitigation |
|---|---|---|
| Hidden axiom dependency | Axiom audit | Run #print axioms regularly |
| Lean version breaking change | Version pinning | CI + lockfile |
| ... | ... | ... |

### Coverage Metrics
- Known Knowns: [N] / [M] paper claims formalized ([X]%)
- Known Unknowns: [N] identified gaps
- Unknown Knowns: [N] blind spots found this cycle
- Unknown Unknowns: [N] risk areas monitored
- Epistemic Score: [weighted composite]
```

---

## Part 4 -- Cross-Disciplinary Research Domains

The Research Council covers all domains relevant to Project formalization:

### 4.1 Mathematical Disciplines

| Domain | Relevance to Project | Primary RC Member |
|---|---|---|
| Real analysis | Lyapunov, cusp, contraction | Γ (methods) + Δ (bounds) |
| Topology | Phase space, convergence | Β (structure) |
| Measure theory | Stochastic CCV, probability | Α (foundations) |
| Linear algebra | Stochastic matrices, spectral | Γ (methods) |
| Combinatorics | Provenance chains, DAGs | Γ (methods) |
| Order theory | Lattices, gates, phases | Β (structure) |
| Category theory | Functorial structure | Α (foundations) |
| Dynamical systems | Stability, bifurcation, chaos | Γ + Δ |
| Game theory | Multi-agent, mechanism design | Ε (applications) |
| Optimization | Bellman, convex, variational | Γ + Δ |

### 4.2 Applied Domains

| Domain | Relevance to Project | Primary RC Member |
|---|---|---|
| Knowledge management | SECI, tacit knowledge, organizational learning | Ε |
| Cognitive science | Cognitive load, expertise, dual process | Ε |
| AI safety | Alignment, envelopes, trust | Ε + Δ |
| AI governance | EU AI Act, LED, compliance | Ε |
| Information security | Provenance, access control, privacy | Β + Ε |
| Legal reasoning | Deontic logic, evidence, chain of custody | Ε + Α |
| Intelligence analysis | SATs, ACH, indicators | Ε |
| Software engineering | Formal methods, verification, testing | Γ + Β |
| Process philosophy | Whitehead, process ontology | Α + Ε |

### 4.3 Engineering Disciplines

| Domain | Relevance to Project | Primary RC Member |
|---|---|---|
| Control engineering | Lyapunov, feedback, PID | Γ + Δ |
| Systems engineering | Requirements, V&V, MBSE | Ε + Β |
| Reliability engineering | Failure modes, safety margins | Δ + Ε |
| Signal processing | Time series, filtering, EWS | Γ + Δ |
| Network science | Graph metrics, centrality, flow | Β + Γ |

---

## Part 5 -- Research Session Protocol

### 5.1 Session Types

| Session Type | Duration | Scope | Output |
|---|---|---|---|
| **Quick scan** | 1 RESEARCH iteration | Single question | Answer + 1 ZK note |
| **Standard survey** | 2-3 iterations | One Project module | Literature synthesis + epistemic map section |
| **Deep exploration** | 3-5 iterations | Cross-module domain | Full epistemic map + strategy document |
| **Exhaustive review** | 5+ iterations (max) | Entire project domain | Comprehensive literature review + epistemic map + specification bundle |

### 5.2 Session Launch Protocol

```
1. Check Zettelkasten: do we already know this? → If yes, update rather than restart
2. Check epistemic map: which quadrant does the question fall in?
3. Assign lead member based on domain
4. Launch RESEARCH loop:
   R: Survey → literature search, Mathlib, community forums
   E: Explore → deep-dive into top 3-5 findings
   S: Synthesize → combine into coherent understanding
   E: Evaluate → update epistemic map (all 4 quadrants)
   A: Architect → propose formal approach
   R: Review → all 5 members critique the proposal
   C: Commit → produce specifications
   H: Handoff → to lean-specification / lean-review-council
```

### 5.3 Inter-Council Handoff

```
Research Council (produces)          Review Council (consumes)
  ├─ Epistemic map        ──────────── Context for review
  ├─ Strategy document     ──────────── Proof architecture guidance
  ├─ Literature synthesis  ──────────── Evidence for Φ (Statement Oracle)
  ├─ Specifications        ──────────── Input for implementation
  └─ Research ZK notes     ──────────── Knowledge base for Ν (Novelty Scout)

Review Council (feeds back)          Research Council (updates)
  ├─ Statement corrections ──────────── Revise specifications
  ├─ Missing lemma reports ──────────── New known unknowns
  ├─ Duplicate detection   ──────────── Unknown knowns discovered
  └─ Quality patterns      ──────────── Update proof strategy guidance
```

---

## Part 6 -- Literature Synthesis Protocol

### 6.1 Source Hierarchy

| Priority | Source Type | Trust Level | Treatment |
|---|---|---|---|
| 1 | Mathlib source code | Authoritative | Definitive for Lean formalization |
| 2 | Lean Zulip / community | High | Verified by practitioners |
| 3 | Peer-reviewed papers | High | But may differ from Lean formalization |
| 4 | Textbooks | Medium-High | Canonical but may use different conventions |
| 5 | Preprints (arXiv) | Medium | Unchecked but often cutting-edge |
| 6 | Blog posts / tutorials | Low-Medium | May be outdated or incorrect |
| 7 | AI-generated content | Low | Must be independently verified |

### 6.2 Synthesis Template

```markdown
# Literature Synthesis: [Topic]
## Date: [ISO-8601]
## RC Lead: [Α/Β/Γ/Δ/Ε]

### Sources Reviewed
1. [Source 1] -- [1-sentence summary]
2. [Source 2] -- [1-sentence summary]
...

### Key Findings
1. [Finding 1] -- supported by [sources]
2. [Finding 2] -- supported by [sources]
...

### Contradictions / Disagreements
- [Source A] says X, [Source B] says Y -- resolution: [...]

### Gaps in Literature
- [Gap 1] -- no formalization exists for [...]
- [Gap 2] -- existing work assumes [assumption we don't have]

### Recommendations
- Primary approach: [...]
- Alternative approach: [...]
- Research needed: [...]

### Zettelkasten Notes
- [ZK-YYYYMMDD-NNN] -- [type: literature/permanent]
```

---

## Part 7 -- Integration with Other Skills

### 7.1 Skill Interaction Matrix

| Research Council → | Target Skill | Interface |
|---|---|---|
| → lean-specification | Theorem specs from research | Specification documents |
| → lean-zettelkasten | Literature/permanent notes | ZK notes |
| → lean-research | Delegate specific searches | Research requests |
| → lean-doc-requirements | Extracted claims | Claim documents |
| → epistemic-mapping | Updated quadrant data | Epistemic map updates |
| → math-strategy-studio | Problem decomposition guidance | Strategy briefs |
| → lean-review-council | Context for review | Handoff package |
| → lean-gateway | Status reports, research requests | Gateway protocol |

### 7.2 Review Council ↔ Research Council Duality

| Aspect | Review Council (Σ,Φ,Ν,Λ,Ω) | Research Council (Α,Β,Γ,Δ,Ε) |
|---|---|---|
| Focus | Proof quality (post-hoc) | Knowledge acquisition (pre-hoc) |
| Input | Completed proofs | Open questions |
| Output | Verdicts + fixes | Strategies + specifications |
| Loop | RALPH | RESEARCH |
| Topology | Star, Pipeline, Mesh | Survey, Deep-dive, Cross-disciplinary |
| Voting | Pass/Warn/Fail/Reject | Consensus on approach |
| Iteration cap | 7 | 5 |
| Primary ZK output | Permanent notes (patterns) | Literature notes (findings) |

---

## Part 8 -- Self-Improvement

### 8.1 Research Retrospective

After each research session:
1. What did we learn that we didn't know before?
2. What blind spots did we discover?
3. What research methods worked / failed?
4. Should any RC member's competencies be updated?
5. Are there emerging domains we need to add?

### 8.2 Skill Updates from Research

When research reveals patterns that should be encoded in skills:
1. Create permanent ZK note with the pattern
2. Propose skill update (RC consensus vote)
3. Draft the update
4. Review by Review Council (Σ approval for structural, Ω for convention)
5. Apply update
6. Update skill version registry (lean-gateway Part 9)

---

## Part 9 -- Project Current State & Proven Methodology

### 9.1 Module Metrics

> **Module counts are in `AGENT.md §Module Inventory` (authoritative).** Current totals: 22,312 lines, ≥1,255 theorems, 12 modules, zero sorry.
### 9.2 Tactic Modernization (completed)

All 8 `proj_*` tactics are **DEPRECATED** -- zero cross-module uses remaining. Current priority:

| Priority | Tactic | Use case |
|---|---|---|
| 1 | `grind` | General goal closing; replaced all `proj_*` |
| 2 | `omega` | Pure Nat/Int arithmetic |
| 3 | `norm_num` | Numeric computation |
| 4 | `simp only [...]` | Targeted rewriting |
| 5 | `nlinarith` / `linarith` | Linear/nonlinear arithmetic |
| 6 | `ring` | Ring identities |
| 7 | `positivity` | Non-negativity goals |
| 8 | `field_simp` | Nat→ℝ division / coercion |
| 9 | `decide` | Decidable propositions |
| 10 | `aesop` | Last resort |

Zero `sorry` -- all ≥1,255 theorems fully closed.

### 9.3 CuspCatastrophe: Equilibrium Existence via IVT

Key findings from bifurcation formalization establishing templates for all dynamical systems work:

- **`fold_curve_iff_discriminant_zero`** (C4): The fold curve is fully characterized by `discriminant = 0` -- a purely algebraic condition; proof closes with `ring` / `nlinarith`, no IVT required.
- **`asymmetric_three_roots_ivt`**: Three equilibria proven for a=-3, b=1 using `IsPreconnected.intermediate_value₂` with sign-change witnesses. **Finding:** Lean 4 Mathlib's IVT machinery is sufficient for equilibrium existence proofs -- no external bifurcation library is needed.

**Equilibrium exhibition pattern:**
1. Exhibit `x₁ < x₂ < x₃` with alternating sign of the polynomial at each point
2. Apply `IsPreconnected.intermediate_value₂` on each adjacent pair
3. `fun_prop` discharges polynomial continuity (after `unfold`)
4. `norm_num` closes numeric evaluations

### 9.4 Stochastic Systems: Perron-Frobenius Gap and Workaround

**Status (Mathlib 4.28):** The general Perron-Frobenius theorem for non-negative matrices is **NOT** in Mathlib.

**Project workaround** (proven in `StochasticCCV.uniformQ_stationary_doubly_stochastic`):
- Prove stationarity directly from column sum = 100 hypothesis
- Key tactic: `linear_combination (1/300 : ℚ) * col_sum_hypothesis`
- More elementary than spectral theory; fully kernel-checkable; robust to Mathlib version changes

**Research planning note (Γ member):** Any proof that would otherwise require Perron-Frobenius should use the column-sum / row-sum arithmetic pattern instead. Flag as **Known Unknown** in the epistemic map until Perron-Frobenius is available in Mathlib.

---

## Annex: Epistemic Discovery Modes (Census / Dependency / Literature / Cross-Domain)

# Epistemic Discovery Engine Handbook

> **Layering note.** This file holds the deep methodology content
> previously embedded in [`skills/epistemic-discovery-engine/SKILL.md`](../skills/epistemic-discovery-engine/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow /
> Recovery / Handoffs) + the parts index. This file holds the full
> encyclopaedia of discovery modes; uu hunting protocols; reporting and outputs; integration architecture, etc.
> Zero fidelity loss vs the pre-layering revision.

---

## Part 1 -- Discovery Modes

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
2. Diff against last census -- detect new defs without lemmas, lemmas without usage
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
4. **Compare:** Diff against what Project has -- catalog exact gaps
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

## Part 2 -- UU Hunting Protocols

The core mission: systematically reduce the unknown-unknown zone.

### 2.1 The Eight UU-Shrinking Methods

Each method targets a different class of blind spot:

#### Method 1 -- Red Team Adversarial Probing
**Lead:** Ε (Applications Bridge)
**Protocol:** Assume adversarial intent -- what could go wrong that nobody mentioned?
- Step 1: Select a formalization claim (e.g., "trust monotonically decreases under violation")
- Step 2: Generate 5 counterarguments or edge cases
- Step 3: For each, check if the formalization handles it
- Step 4: Unhandled cases → new KU items

#### Method 2 -- Cross-Disciplinary Survey
**Lead:** Α (Foundations Architect)
**Protocol:** Check what adjacent fields know that we might have missed.
- Map: Project domain → 3-5 adjacent fields (e.g., Lyapunov → control theory + mathematical biology + economics)
- For each field: What are their core theorems? Do we have equivalents?
- New theorems found → UK items (they exist, we missed them)

#### Method 3 -- Failure Mode Enumeration
**Lead:** Δ (Bounds Analyst)
**Protocol:** Enumerate failure modes of each major theorem.
- For each theorem: What assumptions does it require?
- For each assumption: Under what conditions could it fail?
- For each failure condition: Is this addressed anywhere?
- Unaddressed failure modes → new UU→KU

#### Method 4 -- External Review Solicitation
**Lead:** Γ (Methods Scholar)
**Protocol:** Show formalization to external experts.
- Prepare review package: key definitions, theorem statements (no proofs)
- Submit to: Lean Zulip, domain experts, Mathlib reviewers
- Catalogue feedback: surprises, missed connections, alternative approaches

#### Method 5 -- Adversarial Query Generation
**Lead:** Ε (Applications Bridge)
**Protocol:** Generate questions that the formalization SHOULD answer but might not.
- From each paper section: extract implicit questions
- From each definition: "What is NOT a [defined concept]?"
- From each theorem: "What happens when the hypothesis fails?"
- Unanswerable queries → new KU items

#### Method 6 -- Analogy Check
**Lead:** Β (Structure Strategist)
**Protocol:** Find analogies in other formalization projects.
- Identify 3-5 comparable Lean projects (Mathlib four, lean-liquid, sphere-eversion, etc.)
- For each: What did they formalize that we haven't considered?
- Structural parallels → potential UK items

#### Method 7 -- Completeness Challenge
**Lead:** Α (Foundations Architect) + Β (Structure Strategist)
**Protocol:** For each algebraic structure, systematically check standard properties.
- Is it associative? Commutative? Has identity? Has inverse?
- Is the functor faithful? Full? Essentially surjective?
- Does the space satisfy separation axioms? Compactness? Completeness?
- Missing standard properties → new KU items

#### Method 8 -- Edge Case Generation
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

## Part 3 -- Reporting and Outputs

### 3.1 Sweep Report Template

```markdown
# Discovery Engine -- Sweep Report
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
- [ ] [action 1 -- assigned to [member]]
- [ ] [action 2 -- priority P[N]]
...
```

### 3.2 Probe Report Template

```markdown
# Discovery Engine -- Probe Report
## Target: [concept/gap being probed]
## Level: [Shallow|Standard|Deep|Exhaustive]
## Lead member: [Α/Β/Γ/Δ/Ε]
## Date: [ISO-8601]

### Scope Definition
[1-sentence precise scope]

### Sources Consulted
1. [source] -- [relevance]
2. [source] -- [relevance]
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
# Discovery Engine -- Alert
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

## Part 4 -- Integration Architecture

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
| math-nonlinear-dynamics | -- | -- | -- | -- |
| math-time-series | -- | -- | -- | -- |
| math-graph-knowledge | -- | -- | -- | -- |
| math-measure-probability | -- | -- | -- | -- |
| math-algebra-category | -- | -- | -- | -- |
| math-optimization-game | -- | -- | -- | -- |
| math-topology-analysis | -- | -- | -- | -- |
| ai-symbolic-neuro | -- | -- | -- | -- |
| ai-agentic-evolving | -- | -- | -- | -- |
| ai-high-stakes-verifiable | -- | -- | -- | -- |
| ai-causal-deontic | -- | -- | -- | -- |
| ai-commonsense-reasoning | -- | -- | -- | -- |
| applied-legal-reasoning | -- | -- | -- | -- |
| applied-intelligence-analysis | -- | -- | -- | -- |
| applied-strategy-analysis | -- | -- | -- | -- |
| applied-data-information-security | -- | -- | -- | -- |
| applied-engineering-disciplines | -- | -- | -- | -- |

---

## Part 5 -- Anti-Stagnation Mechanisms

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

## Part 6 -- Project Relevance

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

## Part 7 -- Cross-References

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

---

## Annex: 5-Role Research Synthesis Engine (Scanner / Clusterer / Distiller / Verifier / Publisher)

# Research Synthesis Engine Handbook

> **Layering note.** This file holds the deep methodology content
> previously embedded in [`skills/research-synthesis-engine/SKILL.md`](../skills/research-synthesis-engine/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow /
> Recovery / Handoffs) + the parts index. This file holds the full
> encyclopaedia of the five synthesis roles; the synthesize loop; synthesis products; duality with review council, etc.
> Zero fidelity loss vs the pre-layering revision.

---

## Part 1 -- The Five Synthesis Roles

Each role mirrors a Research Council member but operates in **synthesis mode** -- combining, fusing, and producing rather than surveying and exploring.

### 1.1 Α-Synth -- Foundational Synthesizer

**Source role:** Α (Foundations Architect) from Research Council
**Synthesis focus:** Combine foundational findings into coherent axiomatic frameworks
**Produces:**
- Axiom packages: minimal, consistent, sufficient
- Foundation selection rationale (classical vs constructive, universe levels)
- Cross-foundation compatibility assessments

**Key questions:**
- From all surveyed foundations, which is the RIGHT one for this formalization?
- Are there foundational conflicts between domains we need to bridge?
- What is the minimal axiom set that supports the full specification?

### 1.2 Β-Synth -- Structural Synthesizer

**Source role:** Β (Structure Strategist) from Research Council
**Synthesis focus:** Fuse structural insights into typeclass hierarchies and algebraic designs
**Produces:**
- Typeclass hierarchy proposals
- Structure selection rationale (why this algebraic structure, not that one)
- Representation choice documents with trade-off analysis

**Key questions:**
- From all surveyed structures, which captures the domain most faithfully?
- How does the chosen structure interact with existing Project structures?
- What structural properties are we deliberately NOT encoding, and why?
- For ordered types: does a `Lattice` instance follow for free from `LinearOrder`? (Project pattern: `instance : Lattice MyType := inferInstance` works for any `LinearOrder MyType` -- `FullRegime` and `GateConfig` both use this; reduce lattice goals with `sup_eq_max` / `inf_eq_min`)

### 1.3 Γ-Synth -- Methods Synthesizer

**Source role:** Γ (Methods Scholar) from Research Council
**Synthesis focus:** Distill proof methodologies into proof strategy blueprints
**Produces:**
- Proof strategy documents (method selection, tactic sequences, automation boundaries)
- Technique comparison matrices (which method for which theorem class)
- Proof pattern catalogs extracted from literature
- **Proven Project patterns:** IVT via `IsPreconnected.intermediate_value₂` for equilibrium existence in polynomial systems; column-sum arithmetic for doubly-stochastic stationarity (Perron-Frobenius-free)

**Key questions:**
- From all surveyed techniques, which is most robust for Lean 4 formalization?
- What proof patterns from the literature can we reuse vs must we invent?
- Where should we rely on automation (`grind` > `omega` > `norm_num` > `simp only` > `nlinarith` > `linarith` > `ring` > `positivity` > `field_simp` > `decide` > `aesop`) vs manual proof?
- For equilibrium existence: can we exhibit sign-change witnesses and apply `IsPreconnected.intermediate_value₂`? (`fun_prop` handles polynomial continuity after `unfold`; `norm_num` closes numeric evaluations)
- For stochastic stationarity: is column-sum arithmetic sufficient? (`linear_combination (1/300 : ℚ) * hColumn` avoids Perron-Frobenius, which is absent from Mathlib 4.28)

### 1.4 Δ-Synth -- Quantitative Synthesizer

**Source role:** Δ (Bounds Analyst) from Research Council
**Synthesis focus:** Compile quantitative results -- bounds, rates, constants -- into specification-ready claims
**Produces:**
- Bound catalogs: best known bounds from literature
- Convergence rate comparisons across sources
- Numerical precision requirements (how tight must our bounds be?)

**Key questions:**
- From all surveyed bounds, what is the tightest provable in Lean 4?
- Are our Nat-scaled ×100 arithmetic bounds competitive with real-valued originals?
- Where are the quantitative gaps between paper claims and formalizable statements?
- For convergence/contraction claims: use `AgenticSafety.trust_L1_contraction` as template -- state as `‖update x - update y‖₁ ≤ c * ‖x - y‖₁` with rational `c < 1`; close with `norm_num` + `linarith`

### 1.5 Ε-Synth -- Applications Synthesizer

**Source role:** Ε (Applications Bridge) from Research Council
**Synthesis focus:** Translate domain knowledge into formalization requirements
**Produces:**
- Requirements documents mapping informal claims to formal specifications
- Domain vocabulary → Lean term translation tables
- Relevance prioritization (which claims matter most for the project's goals?)

**Key questions:**
- From all surveyed applications, which formalization targets have the highest impact?
- How do the domain experts actually use these concepts, and does our formalization match?
- What real-world scenarios should drive our test cases?

---

## Part 2 -- The SYNTHESIZE Loop

The synthesis counterpart to RALPH (Review Council) and RESEARCH (Research Council):

```
S -- Survey:     Gather all inputs (discovery reports, literature, domain skill outputs)
Y -- Yield:      Extract key claims, theorems, definitions, and patterns
N -- Normalize:  Standardize notation, reconcile conflicting sources
T -- Triangulate: Cross-validate findings across ≥ 3 independent sources
H -- Harmonize:  Resolve conflicts, choose canonical representations
E -- Encode:     Translate findings into Lean-ready specification language
S -- Specify:    Produce formal specification documents
I -- Integrate:  Connect specifications to existing Project modules
Z -- Zettelkasten: Record synthesis products as permanent notes
E -- Export:     Package for handoff to implementation / Review Council
```

### 2.1 Loop Configuration

| Synthesis type | Iterations | Roles active | Output |
|---|---|---|---|
| Quick synthesis | 1 SYNTHESIZE pass | Ε-Synth lead | Requirements sketch |
| Standard synthesis | 2-3 passes | All 5 roles | Specification package |
| Deep synthesis | 3-5 passes | All 5 roles + RC | Full specification + strategy |
| Comprehensive synthesis | 5+ passes | All + external | Publication-grade survey + specs |

### 2.2 Anti-Collapse Safeguards

| Safeguard | Mechanism | Threshold |
|---|---|---|
| Iteration cap | Max 7 SYNTHESIZE loops per topic | Hard limit |
| Source saturation | If pass N yields < 1 new source vs pass N-1, stop surveying | Auto-detect |
| Conflict resolution deadline | Conflicts unresolved after 2 passes → vote (§2.3) | Mandatory |
| Scope anchor | Every synthesis product must trace to an Project module | Mandatory |
| Novelty filter | Claims already in KK quadrant are summarized, not re-synthesized | Efficiency |

### 2.3 Consensus Protocol (mirrors Research Council)

| Decision type | Α-S | Β-S | Γ-S | Δ-S | Ε-S | Threshold |
|---|---|---|---|---|---|---|
| Foundation choice | 3 | 2 | 1 | 1 | 1 | ≥ 5/8 |
| Structure design | 1 | 3 | 2 | 1 | 1 | ≥ 5/8 |
| Method selection | 1 | 1 | 3 | 2 | 1 | ≥ 5/8 |
| Bound selection | 1 | 1 | 1 | 3 | 2 | ≥ 5/8 |
| Priority ranking | 1 | 1 | 1 | 1 | 3 | ≥ 4/7 |

---

## Part 3 -- Synthesis Products

### 3.1 Specification Package

The primary output -- a complete, implementation-ready package:

```markdown
# Specification Package: [Domain/Topic]
## Date: [ISO-8601]
## Synthesis type: [Quick|Standard|Deep|Comprehensive]
## Lead: [Α-S/Β-S/Γ-S/Δ-S/Ε-S]

### 1. Context
- Project module(s): [target modules]
- Epistemic status: [KU item being resolved / new domain entry / extension]
- Priority: P[1-3]

### 2. Formal Specifications
#### Definitions
| Name | Type signature | Informal meaning | Source |
|---|---|---|---|
| [name] | [Lean 4 type] | [english] | [paper/Mathlib ref] |

#### Theorems
| Name | Statement (informal) | Expected difficulty | Proof strategy hint |
|---|---|---|---|
| [name] | [natural language] | [Easy/Medium/Hard/Research] | [brief hint] |

#### Instances
| Typeclass | Type | Justification |
|---|---|---|
| [class] | [type] | [why this instance] |

### 3. Dependencies
- Mathlib imports needed: [list]
- Project modules depended on: [list]
- New definitions required first: [ordered list]

### 4. Proof Strategy Brief (from Γ-Synth)
- Primary approach: [description]
- Fallback approach: [description]
- Automation opportunities: [what simp/omega/aesop can handle]
- Manual proof areas: [what requires hand proof]

### 5. Quantitative Targets (from Δ-Synth)
- Bounds to achieve: [list with sources]
- Precision requirements: [Nat-scaled ×100 implications]
- Convergence rates: [expected rates with literature comparison]

### 6. Relevance Justification (from Ε-Synth)
- Paper claims addressed: [list with section references]
- Real-world impact: [brief description]
- Priority rationale: [why this, why now]

### 7. Epistemic Map Updates
- KU items being resolved: [list]
- New KU items identified during synthesis: [list]
- UU→KU transitions: [list from discovery engine]

### 8. Quality Criteria (acceptance conditions)
- [ ] All definitions compile
- [ ] All theorem statements type-check (sorry permitted for initial spec)
- [ ] No autoImplicit violations
- [ ] Nat-scaled arithmetic consistent with project conventions
- [ ] Cross-references to existing modules verified
```

### 3.1.1 Proven Specification Patterns (Project)

The following patterns have been established in the project theorems and are ready for direct use in specification packages:

**IVT sign-change package** -- equilibrium existence in ℝ-valued polynomial systems:
- Mathlib entry point: `IsPreconnected.intermediate_value₂`
- Pattern: exhibit `x₁ < x₂` with `f(x₁)` and `f(x₂)` of opposite sign; discharge continuity with `fun_prop` after `unfold`; close numeric goals with `norm_num`
- Specification package slot: §4 Proof Strategy Brief → Primary approach
- Template theorem: `CuspCatastrophe.asymmetric_three_roots_ivt`

**Column-sum uniqueness package** -- doubly-stochastic stationarity (Perron-Frobenius-free):
- Mathlib entry point: `linear_combination` tactic with rational coefficients
- Pattern: express stationarity as ℚ linear system; close each component with `linear_combination (1/300 : ℚ) * hColumn`
- Specification package slot: §4 Proof Strategy Brief; §5 Quantitative Targets
- Template theorem: `StochasticCCV.uniformQ_stationary_doubly_stochastic`
- **Note:** Perron-Frobenius is **NOT** in Mathlib 4.28 -- this elementary approach is the canonical Project substitute

**L¹ contraction package** -- trust/belief convergence:
- Mathlib entry point: `norm_num` + `linarith` after unfolding the update step
- Pattern: state as `‖update x - update y‖₁ ≤ c * ‖x - y‖₁` with rational `c < 1`; close arithmetic with `norm_num` + `linarith`
- Template theorem: `AgenticSafety.trust_L1_contraction`

**Lattice-from-LinearOrder package** -- ordered categorical types:
- Mathlib entry point: `instance : Lattice T := inferInstance` (requires `LinearOrder T`)
- Pattern: declare `LinearOrder` first; `inferInstance` yields `Lattice` for free; reduce lattice goals with `sup_eq_max`, `inf_eq_min`
- Template theorems: `PhasePortrait.FullRegime`, `QualityGates.GateConfig` (distributive)

### 3.2 Knowledge Fusion Document

When synthesizing across multiple domains:

```markdown
# Knowledge Fusion: [Domain A] × [Domain B]
## Date: [ISO-8601]
## Synthesizers: [roles involved]

### Shared Concepts
| Concept in A | Concept in B | Formal bridge | Project location |
|---|---|---|---|
| [term A] | [term B] | [how they connect] | [module.lean] |

### Structural Analogies
| Structure in A | Structure in B | Isomorphism type | Exploitable? |
|---|---|---|---|
| [structure] | [structure] | [iso/equiv/embed] | [yes/no + why] |

### Proof Transfer Opportunities
| Theorem in A | Potential analog in B | Transfer method | Effort |
|---|---|---|---|
| [thm] | [analog] | [specialization/generalization/analogy] | [est.] |

### Conflicts and Resolutions
| Conflict | Domain A says | Domain B says | Resolution |
|---|---|---|---|
| [point] | [claim] | [claim] | [chosen + rationale] |
```

### 3.3 Domain Coverage Audit

Systematic assessment of how well Project covers a domain:

```markdown
# Domain Coverage Audit: [Domain]
## Date: [ISO-8601]
## Auditor: [Ε-Synth + relevant domain skill]

### Standard Curriculum (what a textbook covers)
| Topic | Formalized? | Module | Completeness |
|---|---|---|---|
| [topic] | Yes/No/Partial | [module] | [%] |

### Key Theorems (from literature)
| Theorem | Formalized? | Our version | Generality gap |
|---|---|---|---|
| [thm name] | Yes/No | [our variant] | [what we miss] |

### Missing Foundations
| Foundation | Needed for | Available in Mathlib? | Effort to formalize |
|---|---|---|---|
| [concept] | [usage] | [yes/no/partial] | [est.] |

### Coverage Score
- Core coverage: [N/M] key results ([%])
- Extended coverage: [N/M] advanced results ([%])
- Application coverage: [N/M] applied claims ([%])
- Overall: [weighted %]
```

---

## Part 4 -- Duality with Review Council

### 4.1 Structural Duality

| Aspect | Research Synthesis Engine | Review Council |
|---|---|---|
| Direction | Knowledge → Specifications | Proofs → Verdicts |
| Members | Α-S, Β-S, Γ-S, Δ-S, Ε-S | Σ, Φ, Ν, Λ, Ω |
| Loop | SYNTHESIZE (10 steps) | RALPH (5 steps) |
| Input | Literature, discoveries, domain knowledge | Completed Lean proofs |
| Output | Specification packages | Pass/Warn/Fail verdicts |
| Iteration cap | 7 | 7 |
| Quality gate | Specification completeness ≥ 80% | Proof quality ≥ targets |
| ZK output | Literature notes + synthesis notes | Permanent pattern notes |
| Error focus | "Are we formalizing the RIGHT thing?" | "Is the formalization CORRECT?" |

### 4.2 Feedback Loop

```
Research Synthesis Engine
    │
    ├──produces──→ Specification Package
    │                    │
    │                    ▼
    │              Implementation
    │                    │
    │                    ▼
    │              Review Council
    │                    │
    │  ┌─────────────────┘
    │  │
    │  ├── Statement corrections → specification revision
    │  ├── Missing lemma reports → new KU items → new synthesis target
    │  ├── Duplicate detection → UK discovery → integration
    │  └── Quality patterns → proof strategy refinement
    │
    └──updated by←─ all feedback loops above
```

### 4.3 Joint Sessions

When synthesis and review must coordinate:

| Scenario | Joint action | Lead |
|---|---|---|
| Specification ambiguity | Synthesis clarifies intent, Review tests interpretations | Ε-S + Φ |
| Proof reveals spec gap | Review reports, Synthesis patches spec | Γ-S + Ν |
| Domain mismatch | Synthesis re-audits domain, Review re-checks proofs | Α-S + Σ |
| Bound disagreement | Synthesis provides literature bounds, Review verifies | Δ-S + Λ |

---

## Part 5 -- Domain Integration

### 5.1 Domain Skill → Synthesis Routing

Each domain skill feeds specific synthesis needs:

| Domain Skill | Synthesis Trigger | Primary Synth Role |
|---|---|---|
| math-nonlinear-dynamics | Dynamics formalization | Γ-Synth + Δ-Synth |
| math-time-series | Time series properties | Δ-Synth |
| math-graph-knowledge | Graph/KG formalization | Β-Synth |
| math-measure-probability | Measure-theoretic specs | Α-Synth |
| math-algebra-category | Algebraic structure specs | Α-Synth + Β-Synth |
| math-optimization-game | Optimization/game specs | Γ-Synth + Δ-Synth |
| math-topology-analysis | Topological specs | Α-Synth + Β-Synth |
| ai-symbolic-neuro | Neuro-symbolic integration | Ε-Synth |
| ai-agentic-evolving | Multi-agent specs | Ε-Synth + Β-Synth |
| ai-high-stakes-verifiable | Verification targets | Α-Synth + Ε-Synth |
| ai-causal-deontic | Causal/deontic specs | Α-Synth + Ε-Synth |
| ai-commonsense-reasoning | Commonsense formalization | Ε-Synth + Γ-Synth |
| applied-legal-reasoning | Legal spec translation | Ε-Synth |
| applied-intelligence-analysis | Intel formalization | Ε-Synth |
| applied-strategy-analysis | Strategy modeling | Ε-Synth + Γ-Synth |
| applied-data-information-security | Security property specs | Β-Synth + Ε-Synth |
| applied-engineering-disciplines | Engineering model specs | Γ-Synth + Δ-Synth |

### 5.2 Lean Formalization Skill Integration

| Lean Skill | Synthesis Interface |
|---|---|
| lean-math-foundations | Receives foundational specs from Α-Synth |
| lean-math-analysis | Receives analysis specs from Γ-Synth + Δ-Synth |
| lean-math-discrete | Receives discrete specs from Β-Synth |
| lean-math-dynamical | Receives dynamics specs from Γ-Synth |
| lean-math-stochastic | Receives stochastic specs from Δ-Synth |
| lean-math-optimization | Receives optimization specs from Γ-Synth + Δ-Synth |
| lean-specification | Receives all specification packages |
| lean-research | Receives targeted research requests |
| lean-zettelkasten | Receives all synthesis notes |

---

## Part 6 -- Synthesis Workflows

### 6.1 New Domain Entry Workflow

When Project enters a new mathematical or applied domain:

```
1. Ε-Synth: Scope the domain -- what does Project need from it?
2. epistemic-discovery-engine: Full sweep of the domain
3. Α-Synth: Assess foundational requirements
4. Β-Synth: Survey existing structures (Mathlib, community)
5. Γ-Synth: Catalog proof techniques
6. Δ-Synth: Compile key quantitative results
7. All: Run SYNTHESIZE loop (Deep level)
8. Output: Specification Package + Domain Coverage Audit
9. Handoff: lean-specification + Research Council for review
```

### 6.2 Gap Closure Workflow

When a KU item needs to be converted to KK:

```
1. Identify the KU item and its origin
2. Γ-Synth + Δ-Synth: Research proof strategies and bounds
3. Ε-Synth: Verify the gap is still relevant
4. Run SYNTHESIZE loop (Standard level)
5. Output: Focused Specification Package for the gap
6. Handoff: implementation team
```

### 6.3 Cross-Domain Fusion Workflow

When a formalization requires combining knowledge from multiple domains:

```
1. Identify the domains to fuse
2. Each: run domain-specific synthesis (Synth roles per §5.1)
3. All: identify shared concepts, analogies, conflicts
4. Knowledge Fusion Document production
5. Α-Synth: foundational compatibility check
6. SYNTHESIZE loop (Deep level)
7. Output: Fusion Specification Package
```

---

## Part 7 -- Quality Assurance

### 7.1 Synthesis Quality Metrics

| Metric | Target | Measurement |
|---|---|---|
| Source triangulation | ≥ 3 independent sources per claim | Count references |
| Specification completeness | ≥ 80% of identified claims have specs | Claims with specs / total |
| Notation consistency | 100% normalized across package | Automated check |
| Mathlib alignment | ≥ 90% of types match Mathlib conventions | Manual review |
| Conflict resolution | 100% of conflicts resolved | Zero open conflicts |
| Epistemic coverage | All quadrants addressed | Quadrant checklist |
| Handoff readiness | Specification compiles (with sorry) | lakecheck |

### 7.2 Synthesis Review Checklist

Before handoff, every specification package must pass:

- [ ] **Scope check:** Every item traces to an Project module or justified extension
- [ ] **Foundation check:** Α-Synth has cleared foundational choices
- [ ] **Structure check:** Β-Synth has confirmed typeclass/structure design
- [ ] **Method check:** Γ-Synth has provided proof strategy
- [ ] **Bounds check:** Δ-Synth has compiled quantitative targets
- [ ] **Relevance check:** Ε-Synth has justified priority
- [ ] **Epistemic check:** Epistemic map updated with all quadrant transitions
- [ ] **ZK check:** Key findings recorded as Zettelkasten notes
- [ ] **Conflict check:** No unresolved source conflicts
- [ ] **Convention check:** Nat-scaled ×100, no autoImplicit, naming conventions

---

## Part 8 -- Cross-References

| Skill | Relationship | Interface |
|---|---|---|
| research-council | Synthesis operates under RC strategy | Strategy → synthesis targets |
| lean-review-council | Dual system (input vs output) | Specs → impl → verdicts → feedback |
| epistemic-discovery-engine | Receives discovery findings | Discovery reports → synthesis input |
| epistemic-mapping | Reads/updates quadrant state | Quadrant data + transitions |
| lean-specification | Primary output target | Specification packages |
| lean-zettelkasten | Records synthesis products | Literature + permanent notes |
| lean-research | Delegates targeted searches | Research requests |
| lean-gateway | Reports synthesis progress | Health dashboard metrics |
| lean-quality-engine | Quality gate coordination | Quality metrics |
| lean-doc-feedback | Bidirectional doc↔spec updates | Documentation alignment |
| math-strategy-studio | Proof strategy collaboration | Strategy briefs |
| math-project-management | Schedule coordination | Milestone integration |
| math-product-management | Portfolio prioritization | Value/priority input |
| All domain skills (math-*, ai-*, applied-*) | Domain knowledge input | Domain expertise → synthesis |
| All lean-math-* skills | Specification output targets | Specs → formalization |

---

## Part 9 -- Mathlib Coverage Status & Known Gaps (2026-04-06)

### 9.1 Confirmed Coverage (Found in Mathlib 4.28)

| Concept | Mathlib entry point | Project use |
|---|---|---|
| Intermediate Value Theorem | `IsPreconnected.intermediate_value₂` | Equilibrium existence (CuspCatastrophe) |
| Lattice from LinearOrder | `inferInstance` | `FullRegime`, `GateConfig` lattice instances |
| ℚ arithmetic + `linear_combination` | `field_simp` + `linear_combination` | Doubly-stochastic stationarity (StochasticCCV) |
| Contraction mappings | `ContractingWith.fixedPoint` | Trust convergence (AgenticSafety) |
| Nat-to-ℝ coercion | `field_simp` + `push_cast` | All ×100 scaled arithmetic bounds |
| Topological connectedness | `IsPreconnected` | Sign-change IVT proofs |

### 9.2 Confirmed Gaps (Still Missing in Mathlib 4.28)

| Gap | Affected area | Project workaround |
|---|---|---|
| General Perron-Frobenius theorem | Stochastic eigenvalue arguments | Column-sum arithmetic via `linear_combination` |
| Measure-theoretic basin boundaries | Precise basin-of-attraction area | Avoided; qualitative stability used |
| Continuous-time ODE trajectory theory | Time-parameterized orbit proofs | Discrete-time analogs only |
| Spectral gap for general Markov chains | Mixing time bounds | Not yet formalized in the project |

### 9.3 Module Metrics

> **Module counts are in `AGENT.md §Module Inventory` (authoritative).** Current totals: 22,312 lines, ≥1,255 theorems, 12 modules, zero sorry.

