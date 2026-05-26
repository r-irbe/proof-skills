---
name: research-council
description: The Research Council — a 5-member scholarly dual to the Review Council (lean-review-council). Where the Review Council evaluates existing proofs, the Research Council drives knowledge acquisition, literature synthesis, domain exploration, and epistemic mapping BEFORE formalization begins. Use when planning new formalization work, exploring unfamiliar mathematical domains, mapping known/unknown knowledge, synthesizing scholarship across disciplines, or ensuring no blind spots exist before proof engineering. Produces strategy documents, literature syntheses, epistemic maps, and research-grade Zettelkasten notes.
---

# Research Council — Scholarly Dual to the Review Council

The Research Council is a 5-member multi-agent system for systematic knowledge acquisition, domain exploration, and epistemic mapping. It is the **input side** of the formalization pipeline, while the Review Council is the **output side**.

```
Research Council → Specification → Implementation → Review Council
    (what to prove)                                    (is the proof good?)
```

---

## Part 1 — The Five Research Members

### 1.1 Α — Foundations Architect

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

### 1.2 Β — Structure Strategist

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

### 1.3 Γ — Methods Scholar

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

### 1.4 Δ — Bounds Analyst

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

### 1.5 Ε — Applications Bridge

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

## Part 2 — The RESEARCH Loop (Dual to RALPH)

Where the Review Council uses **RALPH** (Review-Analyze-Learn-Plan-Handle), the Research Council uses **RESEARCH**:

```
R — Reconnaissance: survey the landscape (literature, Mathlib, community)
E — Explore: deep-dive into promising areas
S — Synthesize: combine findings into coherent understanding
E — Evaluate: assess our epistemic position (Rumsfeld matrix)
A — Architect: design the formal approach
R — Review: peer-review the research plan with all 5 members
C — Commit: produce specification documents
H — Handoff: transfer to Review Council / Implementation
```

### 2.1 Anti-Collapse Safeguards

| Safeguard | Mechanism | Threshold |
|---|---|---|
| Depth cap | Max 5 RESEARCH iterations per topic | Hard limit |
| Breadth cap | Max 7 sub-topics per exploration | Requires justification to exceed |
| Time budget | Each depth level has time allocation | Quick/Standard/Deep/Exhaustive |
| Diminishing returns | If iteration N yields < 2 new insights, stop | Auto-detect |
| Scope drift | Every finding must map to an Project module or extension | Mandatory check |
| Redundancy | Check ZK before researching — may already be answered | Mandatory first step |

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

## Part 3 — Epistemic Mapping (Rumsfeld Matrix)

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

1. **Cross-disciplinary survey** — Check if adjacent fields (control theory, economics, cognitive science) have formalizations that cover our blind spots
2. **Red team session** — Ε plays adversary: "What assumption are we making that we haven't questioned?"
3. **Failure mode analysis** — "What could go wrong with our formalization that we haven't considered?"
4. **External review** — Submit to Lean Zulip or Mathlib community for feedback
5. **Historical case study** — Study where similar formalization projects discovered late surprises
6. **Completeness audit** — For every definition, ask: "What properties does this NOT capture?"

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

## Part 4 — Cross-Disciplinary Research Domains

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

## Part 5 — Research Session Protocol

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

## Part 6 — Literature Synthesis Protocol

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
1. [Source 1] — [1-sentence summary]
2. [Source 2] — [1-sentence summary]
...

### Key Findings
1. [Finding 1] — supported by [sources]
2. [Finding 2] — supported by [sources]
...

### Contradictions / Disagreements
- [Source A] says X, [Source B] says Y — resolution: [...]

### Gaps in Literature
- [Gap 1] — no formalization exists for [...]
- [Gap 2] — existing work assumes [assumption we don't have]

### Recommendations
- Primary approach: [...]
- Alternative approach: [...]
- Research needed: [...]

### Zettelkasten Notes
- [ZK-YYYYMMDD-NNN] — [type: literature/permanent]
```

---

## Part 7 — Integration with Other Skills

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

## Part 8 — Self-Improvement

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

## Part 9 — Project Current State & Proven Methodology

### 9.1 Module Metrics

> **Module counts are in `AGENT.md §Module Inventory` (authoritative).** Current totals: 22,312 lines, ≥1,255 theorems, 12 modules, zero sorry.
### 9.2 Tactic Modernization (completed)

All 8 `proj_*` tactics are **DEPRECATED** — zero cross-module uses remaining. Current priority:

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

Zero `sorry` — all ≥1,255 theorems fully closed.

### 9.3 CuspCatastrophe: Equilibrium Existence via IVT

Key findings from bifurcation formalization establishing templates for all dynamical systems work:

- **`fold_curve_iff_discriminant_zero`** (C4): The fold curve is fully characterized by `discriminant = 0` — a purely algebraic condition; proof closes with `ring` / `nlinarith`, no IVT required.
- **`asymmetric_three_roots_ivt`**: Three equilibria proven for a=-3, b=1 using `IsPreconnected.intermediate_value₂` with sign-change witnesses. **Finding:** Lean 4 Mathlib's IVT machinery is sufficient for equilibrium existence proofs — no external bifurcation library is needed.

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
