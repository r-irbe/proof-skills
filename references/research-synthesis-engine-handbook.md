---
title: "Research Synthesis Engine Handbook"
status: "reference"
extracted_from: "skills/research-synthesis-engine/SKILL.md"
extracted_on: "2026-05-27"
scope: "Parts 1-9 (The Five Synthesis Roles; The SYNTHESIZE Loop; Synthesis Products; Duality with Review Council; Domain Integration; Synthesis Workflows; Quality Assurance; Cross-References; Mathlib Coverage Status & Known Gaps)."
loader_hint: "Load when @research-synthesis-engine routes here for methodology details; not needed for the dispatch decision."
---

# Research Synthesis Engine Handbook

> **Layering note.** This file holds the deep methodology content
> previously embedded in [`skills/research-synthesis-engine/SKILL.md`](../skills/research-synthesis-engine/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow /
> Recovery / Handoffs) + the parts index. This file holds the full
> encyclopaedia of the five synthesis roles; the synthesize loop; synthesis products; duality with review council, etc.
> Zero fidelity loss vs the pre-layering revision.

---

## Part 1 — The Five Synthesis Roles

Each role mirrors a Research Council member but operates in **synthesis mode** — combining, fusing, and producing rather than surveying and exploring.

### 1.1 Α-Synth — Foundational Synthesizer

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

### 1.2 Β-Synth — Structural Synthesizer

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
- For ordered types: does a `Lattice` instance follow for free from `LinearOrder`? (Project pattern: `instance : Lattice MyType := inferInstance` works for any `LinearOrder MyType` — `FullRegime` and `GateConfig` both use this; reduce lattice goals with `sup_eq_max` / `inf_eq_min`)

### 1.3 Γ-Synth — Methods Synthesizer

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

### 1.4 Δ-Synth — Quantitative Synthesizer

**Source role:** Δ (Bounds Analyst) from Research Council
**Synthesis focus:** Compile quantitative results — bounds, rates, constants — into specification-ready claims
**Produces:**
- Bound catalogs: best known bounds from literature
- Convergence rate comparisons across sources
- Numerical precision requirements (how tight must our bounds be?)

**Key questions:**
- From all surveyed bounds, what is the tightest provable in Lean 4?
- Are our Nat-scaled ×100 arithmetic bounds competitive with real-valued originals?
- Where are the quantitative gaps between paper claims and formalizable statements?
- For convergence/contraction claims: use `AgenticSafety.trust_L1_contraction` as template — state as `‖update x - update y‖₁ ≤ c * ‖x - y‖₁` with rational `c < 1`; close with `norm_num` + `linarith`

### 1.5 Ε-Synth — Applications Synthesizer

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

## Part 2 — The SYNTHESIZE Loop

The synthesis counterpart to RALPH (Review Council) and RESEARCH (Research Council):

```
S — Survey:     Gather all inputs (discovery reports, literature, domain skill outputs)
Y — Yield:      Extract key claims, theorems, definitions, and patterns
N — Normalize:  Standardize notation, reconcile conflicting sources
T — Triangulate: Cross-validate findings across ≥ 3 independent sources
H — Harmonize:  Resolve conflicts, choose canonical representations
E — Encode:     Translate findings into Lean-ready specification language
S — Specify:    Produce formal specification documents
I — Integrate:  Connect specifications to existing Project modules
Z — Zettelkasten: Record synthesis products as permanent notes
E — Export:     Package for handoff to implementation / Review Council
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

## Part 3 — Synthesis Products

### 3.1 Specification Package

The primary output — a complete, implementation-ready package:

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

**IVT sign-change package** — equilibrium existence in ℝ-valued polynomial systems:
- Mathlib entry point: `IsPreconnected.intermediate_value₂`
- Pattern: exhibit `x₁ < x₂` with `f(x₁)` and `f(x₂)` of opposite sign; discharge continuity with `fun_prop` after `unfold`; close numeric goals with `norm_num`
- Specification package slot: §4 Proof Strategy Brief → Primary approach
- Template theorem: `CuspCatastrophe.asymmetric_three_roots_ivt`

**Column-sum uniqueness package** — doubly-stochastic stationarity (Perron-Frobenius-free):
- Mathlib entry point: `linear_combination` tactic with rational coefficients
- Pattern: express stationarity as ℚ linear system; close each component with `linear_combination (1/300 : ℚ) * hColumn`
- Specification package slot: §4 Proof Strategy Brief; §5 Quantitative Targets
- Template theorem: `StochasticCCV.uniformQ_stationary_doubly_stochastic`
- **Note:** Perron-Frobenius is **NOT** in Mathlib 4.28 — this elementary approach is the canonical Project substitute

**L¹ contraction package** — trust/belief convergence:
- Mathlib entry point: `norm_num` + `linarith` after unfolding the update step
- Pattern: state as `‖update x - update y‖₁ ≤ c * ‖x - y‖₁` with rational `c < 1`; close arithmetic with `norm_num` + `linarith`
- Template theorem: `AgenticSafety.trust_L1_contraction`

**Lattice-from-LinearOrder package** — ordered categorical types:
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

## Part 4 — Duality with Review Council

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

## Part 5 — Domain Integration

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

## Part 6 — Synthesis Workflows

### 6.1 New Domain Entry Workflow

When Project enters a new mathematical or applied domain:

```
1. Ε-Synth: Scope the domain — what does Project need from it?
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

## Part 7 — Quality Assurance

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

## Part 8 — Cross-References

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

## Part 9 — Mathlib Coverage Status & Known Gaps (2026-04-06)

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
