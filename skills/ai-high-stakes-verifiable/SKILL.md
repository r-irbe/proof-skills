---
name: ai-high-stakes-verifiable
description: |
  USE FOR: Formally verifiable AI, high-stakes AI systems, safety-critical deployment, certification, and regulatory compliance. Use for reasoning about AI systems that must be provably correct, auditable, or certifiable — medical AI, autonomous vehicles, legal decision support, military/intelligence systems, and the project's approach to making AI governance mathematically rigorous.
  DO NOT USE FOR: formal verification proofs in Lean (use @lean-ai-formalization); agentic AI dynamics (use @ai-agentic-evolving); causal/deontic reasoning (use @ai-causal-deontic).
  TRIGGERS: high stakes, verifiable AI, safety critical, certification, regulatory compliance, AI assurance.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-ai-formalization', 'skill:lean-security-formalization', 'skill:applied-data-information-security']
metadata:
  version: "0.2.0"
  source_spec: "skills/ai-high-stakes-verifiable/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# High-Stakes & Formally Verifiable AI

Mathematical frameworks for AI systems where correctness, safety, and auditability are non-negotiable.


## Routing

- **USE FOR:** Formally verifiable AI, high-stakes AI systems, safety-critical deployment, certification, and regulatory compliance. Use for reasoning about AI systems that must be provably correct, auditable, or certifiable — medical AI, autonomous vehicles, legal decision support, military/intelligence systems, and the project's approach to making AI governance mathematically rigorous.
- **DO NOT USE FOR:** formal verification proofs in Lean (use @lean-ai-formalization); agentic AI dynamics (use @ai-agentic-evolving); causal/deontic reasoning (use @ai-causal-deontic).
- **TRIGGERS:** high stakes, verifiable AI, safety critical, certification, regulatory compliance, AI assurance.

## Workflow

1. Confirm the question / task is in scope by checking the **USE FOR** clause above; if any of the **DO NOT USE FOR** redirects apply, hand off and stop.
2. Consult the body of this skill (the existing Parts below) for the domain content; pick the smallest relevant section.
3. Execute the section's procedure; emit an output suitable for the listed successor skill(s). Belief floor: 0.90 before publishing.
4. On handoff, attach: scope, key findings, recommended next-skill call. Leave a Zettel breadcrumb when permanent.

## Recovery & STOP

- STOP if the task hits a topic redirected by **DO NOT USE FOR** — hand off to that skill rather than expanding scope here.
- STOP if belief is below 0.90 on a key claim — request HITL or escalate to `@lean-research` for evidence widening.
- STOP if the domain content below is insufficient for the question — log the gap as a research request and hand off to `@research-council` (or `@lean-research` for a single question).

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-ai-formalization`, `skill:lean-security-formalization`, `skill:applied-data-information-security`.

---

## Part 1 — Verification Hierarchy

### 1.1 Levels of Assurance

| Level | Assurance | Method | Cost | Project Analog |
|---|---|---|---|---|
| 0 | None | Trust the developer | Low | No gates |
| 1 | Testing | Test cases | Medium | Unit tests |
| 2 | Static analysis | Automated checking | Medium | Enforcement scripts |
| 3 | Model checking | Exhaustive finite-state | High | `decide` proofs |
| 4 | Theorem proving | Universal mathematical proof | Very high | Lean 4 proofs |
| 5 | Certified compilation | Proof carried to runtime | Extreme | Future work |

### 1.2 What Can Be Formally Verified?

| Property Type | Verifiable? | Method | Example |
|---|---|---|---|
| Type safety | Yes | Type system | Lean kernel checking |
| Functional correctness | Yes (with spec) | Theorem proving | Gate monotonicity |
| Termination | Semi-decidable | Well-founded recursion | Lean's termination checker |
| Safety invariants | Yes | Inductive invariants | Safety envelope preservation |
| Liveness | Yes (for finite) | Temporal logic | Eventually converges |
| Fairness | Partially | Probabilistic proofs | Unbiased trust allocation |
| Alignment | Research frontier | Utility alignment proofs | AlignedReward in Tactics.lean |

### 1.3 What Cannot Be Formally Verified?

- **Specification correctness**: Is the spec what we actually want? (faithfulness gap)
- **Environmental assumptions**: Does the environment match our model?
- **Distributional robustness**: Will it work on data unlike training data?
- **Emergent properties**: Properties arising from composition, not design

→ These are precisely where the Review Council (Φ member) and epistemic mapping provide value.

---

## Part 2 — Safety Standards & Certification

### 2.1 Relevant Standards

| Standard | Domain | Key Requirement | Formalization Relevance |
|---|---|---|---|
| DO-178C | Aviation software | Verification objectives per criticality level | Lean proofs as verification evidence |
| ISO 26262 | Automotive | ASIL levels (A-D), safety goals | Safety envelope as ASIL artifact |
| IEC 61508 | Industrial | SIL levels (1-4), safety functions | Quantitative safety metrics |
| ISO/IEC 42001 | AI management | AI risk assessment, governance | Project framework as compliance tool |
| EU AI Act | Regulatory | Risk categories, conformity assessment | Quality gates as compliance gates |
| NIST AI RMF | US framework | Govern, Map, Measure, Manage | Maps to Project phases |

### 2.2 Project as Compliance Framework

```
EU AI Act category    →  Project mapping
───────────────────────────────────────
Unacceptable risk     →  Safety envelope FORBIDS
High risk             →  Full Project pipeline + Lean verification
Limited risk          →  Project with reduced gate thresholds  
Minimal risk          →  Light Project monitoring only
```

### 2.3 Certification Evidence from Lean

Lean proofs produce certification artifacts:
- **Machine-checked proofs** — independent of developer trust
- **Axiom audit** — what foundational assumptions are used
- **Coverage matrix** — which claims have been verified
- **Review records** — council review documentation

---

## Part 3 — Formal Safety Analysis

### 3.1 Hazard Analysis Methods

| Method | Description | Formalization Potential |
|---|---|---|
| FMEA | Failure modes and effects | Enumerate failure states in Lean |
| FTA | Fault tree analysis | Boolean algebra proofs |
| STPA | Systems-theoretic process analysis | Control structure verification |
| HAZOP | Deviation analysis | Property negation testing |

### 3.2 Safety Cases

A safety case is a structured argument that a system is safe.

**GSN (Goal Structuring Notation):**
```
Top claim: "System is acceptably safe"
  └─ Strategy: "Argument over identified hazards"
      ├─ Sub-claim: "Hazard H1 is mitigated"
      │   └─ Evidence: Lean proof of safety_envelope_preserved
      ├─ Sub-claim: "Hazard H2 is mitigated"
      │   └─ Evidence: Lean proof of trust_convergence_bound
      └─ Sub-claim: "All hazards identified"
          └─ Evidence: Epistemic mapping shows no UU in safety domain
```

### 3.3 Assurance Argument Patterns

| Pattern | Description | Project Implementation |
|---|---|---|
| Monotonic safety | Safety always increases with quality | Gate monotonicity proofs |
| Bounded degradation | Performance degrades gracefully | Lyapunov bounds |
| Fail-safe | System enters safe state on failure | Safety envelope default |
| Defense in depth | Multiple independent safety layers | Nested learning hierarchy |

---

## Part 4 — Provably Robust AI

### 4.1 Adversarial Robustness

- **$\epsilon$-ball robustness**: $\forall x' \in B(x, \epsilon): f(x') = f(x)$
- **Certified robustness**: Provable bound on maximum perturbation
- **Randomized smoothing**: Probabilistic robustness certificate

### 4.2 Distributional Robustness

- **Worst-case over uncertainty set**: $\min_\theta \max_{P \in \mathcal{P}} \mathbb{E}_P[\ell(\theta)]$
- **Wasserstein balls**: Robustness over distributions within Wasserstein distance
- **Project**: OKD dynamics robust under perturbation of transition matrix

### 4.3 Causal Robustness

-  **Invariant prediction**: Properties stable under interventions
- **Transportability**: Results transfer across environments
- **Project**: Causal DAG formalization ensures structural invariance

---

## Part 5 — Decision Support in High-Stakes Domains

### 5.1 Medical AI

| Requirement | Verification Method |
|---|---|
| Diagnostic accuracy | Statistical validation + formal bounds |
| Explanation quality | Causal reasoning formalization |
| Bias absence | Fairness proofs on decision boundary |
| Privacy preservation | Information-theoretic bounds |

### 5.2 Legal Decision Support

| Requirement | Verification Method |
|---|---|
| Rule application correctness | Deontic logic formalization |
| Precedent consistency | Knowledge graph reasoning |
| Procedural fairness | Access control formalization |
| Transparency | Provenance chain verification |

### 5.3 Intelligence Analysis

| Requirement | Verification Method |
|---|---|
| Evidence chain integrity | Provenance DAG verification |
| Hypothesis consistency | Satisfiability checking |
| Bias mitigation | Epistemic mapping (UU detection) |
| Confidence calibration | Probabilistic bounds |

---

## Part 6 — Connection to Project Lean Modules

| Project Module | High-Stakes Aspect |
|---|---|
| QualityGates.lean | Compliance gates with formal thresholds |
| AgenticSafety.lean | Safety envelopes, trust certification |
| ProvenanceChain.lean | Audit trail, evidence chain |
| LyapunovStability.lean | Stability certificates |
| ReinforcementLearning.lean | Bounded regret, safe exploration |
| All modules | Zero sorry = complete verification |

---

## Part 7 — Research Directions

### 7.1 Open Problems

| Problem | Impact | Approach |
|---|---|---|
| Specification completeness | Are we verifying the right thing? | Epistemic mapping + council review |
| Runtime monitoring | Online verification | Lean-verified monitors |
| Continuous certification | Re-certify after updates | RETRO audit protocol |
| Multi-system composition | Verified subsystems → verified system? | Compositional verification |

### 7.2 Epistemic Mapping

| KK | KU | UU |
|---|---|---|
| Gate monotonicity proven | Full FMEA formalization | Novel failure modes from composition |
| Axiom cleanliness | Certified compilation pipeline | Runtime verification gaps |
| Safety envelope algebra | Regulatory mapping completeness | Cross-jurisdictional requirements |
