---
name: epistemic-mapping
description: Systematic knowledge-state mapping using the Johari-Rumsfeld matrix. Tracks known knowns, known unknowns, unknown knowns, and unknown unknowns across all domains. Use when assessing completeness of formalization knowledge, identifying blind spots, planning research priorities, or auditing epistemic coverage of a mathematical domain. Integrates with Research Council for discovery and Review Council for verification.
---

# Epistemic Mapping — Rumsfeld Matrix Methodology

Systematic methodology for mapping the knowledge landscape at project, module, and theorem levels.

---

## Part 1 — The Four Quadrants

### 1.1 Definitions

| Quadrant | Code | Definition | Example |
|---|---|---|---|
| **Known Knowns** | KK | Facts we are aware of and have verified/formalized | "Quality gates are monotone" — theorem proven |
| **Known Unknowns** | KU | Questions we know we need to answer but haven't yet | "Is the cusp bifurcation set connected?" — paper claims, not yet proven |
| **Unknown Knowns** | UK | Knowledge that exists (in Mathlib, literature, community) but we haven't found/used | Mathlib already has `ContractingWith.fixedPoint` — we wrote our own |
| **Unknown Unknowns** | UU | Risks and gaps we aren't even aware of | A Lean version update breaks a key tactic pattern |

### 1.2 Quadrant Dynamics

```
UU → KU (discovery: "we found a gap we didn't know about")
KU → KK (research + formalization: "we proved the thing we needed")
UK → KK (awareness: "we found Mathlib already has this")
UU → UK → KK (gradual discovery: surfaced, then recognized, then integrated)
KK → KU (obsolescence: "Lean version changed, our proof broke")
```

### 1.3 Epistemic Health Score

```
Score = (|KK| / (|KK| + |KU| + |UK| + estimated|UU|)) × coverage_factor

Where:
  |KK| = number of verified items
  |KU| = number of identified gaps
  |UK| = number of discovered blind spots (should decrease over time)
  estimated|UU| = heuristic estimate based on domain complexity
  coverage_factor = paper_claims_covered / total_paper_claims
```

Target: Epistemic Score > 0.8 before declaring module "research-complete"

---

## Part 2 — Discovery Methods per Quadrant

### 2.1 Growing Known Knowns (KK)

| Method | Description | Frequency |
|---|---|---|
| Theorem census | Count formalized theorems per module | Every audit wave |
| Coverage matrix | Map paper claims to Lean theorems | Continuous |
| Axiom audit | Verify all proofs are axiom-clean | Weekly |
| Build verification | `lake build` succeeds | Every change |
| Review Council pass | Theorem passed 5-member review | Per theorem |

### 2.2 Finding Known Unknowns (KU → KK)

| Method | Description | Frequency |
|---|---|---|
| Gap analysis | paper claims − formalized theorems | After each section extraction |
| sorry census | Count and categorize sorries | Every build |
| Specification backlog | Specs without proofs | Weekly review |
| Research Council survey | Open questions from RESEARCH loop | Per session |
| Dependency analysis | Required but missing lemmas | Per module |

### 2.3 Revealing Unknown Knowns (UK → KK)

| Method | Description | Frequency |
|---|---|---|
| Loogle sweep | Search Mathlib by type signature for every custom lemma | Per module |
| `exact?` sweep | Run exact? on every goal to find existing solutions | Per proof |
| Literature review | Search for existing formalizations of our claims | Per domain survey |
| Reservoir check | Search Lean packages for relevant libraries | Quarterly |
| Zulip search | Search community discussions for our problem patterns | Per stuck point |
| Cross-project scan | Check Archive of Formal Proofs (Isabelle), MathComp (Coq) | Per domain |

### 2.4 Shrinking Unknown Unknowns (UU → KU or UK)

| Method | Description | Frequency |
|---|---|---|
| **Red team** | Ε (Applications Bridge) challenges all assumptions | Per module |
| **Cross-disciplinary survey** | Check adjacent fields for relevant results | Per research session |
| **Failure mode analysis** | "What could go wrong that we haven't thought of?" | Per specification |
| **External review** | Submit to Zulip, Mathlib, or domain experts | Per milestone |
| **Adversarial queries** | "What if [assumption] is wrong?" for each assumption | Per design session |
| **Analogy check** | "Have other projects like ours hit unexpected problems?" | Quarterly |
| **Completeness challenge** | "For every def, what property does it NOT capture?" | Per module |
| **Edge case generation** | "What inputs/states did we not consider?" | Per theorem |

---

## Part 3 — Epistemic Map Structure

### 3.1 Project-Level Map

```markdown
# Epistemic Map: Project Formalization
## Last updated: [ISO-8601]
## Research Council session: [N]

### Summary
| Quadrant | Count | Δ since last | Status |
|---|---|---|---|
| Known Knowns (KK) | 611 | +15 | Growing ✓ |
| Known Unknowns (KU) | 23 | -5 | Shrinking ✓ |
| Unknown Knowns (UK) | 4 | -2 | Shrinking ✓ |
| Unknown Unknowns (UU) | ~8 (est.) | -1 | Shrinking ✓ |
| **Epistemic Score** | **0.87** | +0.03 | |
```

### 3.2 Module-Level Map

For each Project module, a focused epistemic map:

```markdown
# Epistemic Map: Project/LyapunovStability.lean
## Theorems: 108 | Defs: 29 | Sorry: 0

### KK (Verified)
- Quadratic Lyapunov non-negativity — lyap_nonneg
- Governance contraction — governance_contraction_factor
- ... [full list]

### KU (Gaps)
- Cusp Lyapunov function construction for general (a,b) parameters
- Connection to Mathlib's ContractingWith for trust dynamics
- Spectral gap bound for governance Markov chain

### UK (Blind Spots Found)
- Mathlib.Topology.MetricSpace.Contracting has ContractingWith — 
  we proved contraction manually in 15 lines when 3 would suffice

### UU (Monitored Risks)
- Lean 4.29 may change simp behavior on sq_nonneg lemmas
- The NL bridge may not scale to higher dimensions
```

### 3.3 Domain-Level Map

For each mathematical domain used in the project:

```markdown
# Epistemic Map: Dynamical Systems
## Used in: LyapunovStability, CuspCatastrophe, PhasePortrait, AgenticSafety

### KK: What we've formalized
- Discrete-time Lyapunov stability (quadratic V)
- Geometric contraction bounds
- Cusp potential and derivative

### KU: What we know we need
- General Lyapunov theorem (not just quadratic)
- Bifurcation set as a manifold
- Basin of attraction boundaries

### UK: What we're probably missing
- [Check: does Mathlib have LaSalle's invariance principle?]
- [Check: does lean4-dynamics package exist?]

### UU: What might surprise us
- [Risk: our cusp formalization assumes smoothness — what if paper needs C^k?]
```

---

## Part 4 — Tracking and Lifecycle

### 4.1 Quadrant Transitions

Every item has a lifecycle through the quadrants:

```
Created (in one quadrant) → Investigated → Migrated → Resolved

UU → KU: "We discovered we don't know X"
KU → KK: "We proved X" (or: "We found X in Mathlib")
UK → KK: "We integrated X from Mathlib/literature"
UU → UK: "We found that X exists but hasn't been integrated"
KK → KU: "X broke due to dependency update" (regression)
```

### 4.2 Transition Log

```markdown
# Epistemic Transition Log
## [ISO-8601] UU → KU: Discovered that we lack a spectral gap bound for OKD
   - Found by: Δ during Deep survey of StochasticCCV
   - Priority: P2
   - Assigned to: Γ + Δ

## [ISO-8601] KU → KK: Proved cusp_bistable_roots_distinct
   - Was KU since: [date]
   - Duration in KU: 12 days
   - Proof by: implementation team
   - Review: Council approved 5/5
```

### 4.3 Freshness and Staleness

| Item age in quadrant | KK | KU | UK | UU |
|---|---|---|---|---|
| < 7 days | Fresh | Active | Urgent | Fresh |
| 7-30 days | Current | Stale (investigate) | Very stale (integrate or dismiss) | Aging |
| 30+ days | Verified | Blocked (escalate) | Neglected (mandatory action) | Forgotten (mandatory red team) |

---

## Part 5 — Integration Points

### 5.1 With Research Council

- Every RESEARCH loop iteration produces quadrant updates
- Epistemic Score is a key health metric in gateway dashboard
- Research sessions target KU items (to convert to KK) and UU detection

### 5.2 With Review Council

- Review findings may add to KU (new gaps found during review)
- Ν (Novelty Scout) discoveries may reveal UK items
- Post-review, theorem moves from KU to KK

### 5.3 With lean-gateway

- Epistemic Score reported in health dashboard
- KU count contributes to "Yellow" health if > threshold
- UU detection triggers automatic research dispatch

### 5.4 With lean-zettelkasten

- Every quadrant item that warrants explanation gets a ZK note
- Synthesis across multiple UK discoveries → permanent note
- KK-verified patterns → permanent methodology notes

### 5.5 With lean-retroactive-audit

- First audit action: populate initial epistemic map from census
- Each audit wave updates all four quadrants
- Transition to steady state requires Epistemic Score > 0.8

---

## Part 6 — Automation

### 6.1 Automated KK Growth

```bash
# Count KK items from theorem census
grep -c "^theorem\|^lemma" Project/*.lean

# Count KU items from sorry census
grep -c "sorry" Project/*.lean

# Count specifications without proofs
# (requires structured spec documents)
```

### 6.2 Automated UK Detection

```python
# For each custom lemma in the project, check if Mathlib has an equivalent:
# 1. Extract lemma type signatures
# 2. Query Loogle for matches
# 3. Flag matches as potential UK items
```

### 6.3 Staleness Alerts

```python
# Flag KU items older than 30 days
# Flag UK items older than 7 days (should be integrated quickly)
# Flag UU items not reviewed in 90 days
```
