---
title: "Applied Data Information Security Handbook"
status: "reference"
extracted_from: "skills/applied-data-information-security/SKILL.md"
extracted_on: "2026-05-27"
scope: "Part 1 — Security Properties; Part 2 — Access Control Models; Part 3 — Information Flow Control; Part 4 — Cryptographic Foundations; Part 5 — Privacy Formalization; Part 6 — Threat Modeling; Part 7 — Security Verification in Lean; Part 8 — Cross-References"
loader_hint: "Load when @applied-data-information-security routes here for details; not needed for the dispatch decision."
---

# Applied Data Information Security Handbook

> **Layering note.** This file holds the deep content previously
> embedded in [`skills/applied-data-information-security/SKILL.md`](../skills/applied-data-information-security/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow /
> Recovery / Handoffs) + a parts index. This file holds the full
> encyclopaedia. Zero fidelity loss vs the pre-layering revision.

---

## Part 1 — Security Properties

### 1.1 CIA Triad (Extended)

| Property | Definition | Formal Statement | Project Analog |
|---|---|---|---|
| **Confidentiality** | Only authorized access | `∀ s d, access s d → authorized s d` | Trust-gated knowledge flow |
| **Integrity** | No unauthorized modification | `∀ s d, modify s d → authorized s d ∧ valid d` | Provenance chain integrity |
| **Availability** | Resources accessible when needed | `∀ t, ∃ s, service_available s t` | Pipeline liveness |
| **Authenticity** | Source identity verified | `∀ m, received m → authentic_source m` | Source trust scores |
| **Non-repudiation** | Cannot deny actions | `∀ a s, performed a s → evidence a s` | Provenance audit trail |
| **Accountability** | Actions traceable to actors | `∀ a, ∃ s, responsible a s` | Agent trust composition |

### 1.2 Lean 4 Security Property Encoding

```lean
-- Security properties as decidable predicates
structure SecurityPolicy where
  subjects : Finset Subject
  objects : Finset Object
  privileges : Finset Privilege
  authorized : Subject → Object → Privilege → Prop
  authorized_dec : ∀ s o p, Decidable (authorized s o p)

-- CIA as structural properties
def confidential (pol : SecurityPolicy) : Prop :=
  ∀ s o, ¬pol.authorized s o .read → ¬canAccess s o

def integrityPreserved (pol : SecurityPolicy) : Prop :=
  ∀ s o, ¬pol.authorized s o .write → ¬canModify s o
```

---

## Part 2 — Access Control Models

### 2.1 Bell-LaPadula (BLP) — Confidentiality

```
Properties:
  Simple Security: No read up (s ≤ o for reading)
  Star Property (*): No write down (o ≤ s for writing)
  Discretionary: Access matrix check

Formal:
  ∀ s o, read_access s o → clearance(s) ≥ classification(o)
  ∀ s o, write_access s o → clearance(s) ≤ classification(o)
```

### 2.2 Biba — Integrity

```
Dual of BLP:
  Simple Integrity: No read down (s ≥ o for reading)
  Star Integrity (*): No write up (o ≥ s for writing)

Formal:
  ∀ s o, read_access s o → integrity(s) ≤ integrity(o)
  ∀ s o, write_access s o → integrity(s) ≥ integrity(o)
```

### 2.3 RBAC — Role-Based

```
Roles R, Permissions P, Users U
- User-Role assignment: UA ⊆ U × R
- Permission-Role assignment: PA ⊆ P × R
- Session: user activates subset of assigned roles

Access: user u has permission p ↔ ∃ r, (u,r) ∈ UA ∧ (p,r) ∈ PA
```

### 2.4 ABAC — Attribute-Based

```
Access decision = f(subject_attributes, object_attributes, 
                    action_attributes, environment_attributes)

More flexible than RBAC: attributes can be any property
Policies: XACML-style rules combining attributes
```

### 2.5 Project Access Control Analog

| Project Component | Security Model Analog |
|---|---|
| Quality gate (pass/fail) | Access control decision |
| Trust threshold | Clearance level (BLP) |
| Phase classification | Security classification level |
| Safety envelope | Mandatory access control constraint |
| Pipeline stage | Permission scope (context-based) |

---

## Part 3 — Information Flow Control

### 3.1 Denning's Lattice Model

```
Information flows from low to high (never high to low):
  L = (SC, ≤, ⊕)
  - SC: security classes
  - ≤: partial order (can-flow-to)
  - ⊕: join operation (least upper bound)

Non-interference: low inputs alone determine low outputs
  low_equiv(s₁, s₂) → low_equiv(exec(s₁), exec(s₂))
```

### 3.2 Lean Formalization Pattern

```lean
structure InfoFlowLattice where
  levels : Type
  le : levels → levels → Prop
  join : levels → levels → levels
  le_refl : ∀ l, le l l
  le_trans : ∀ a b c, le a b → le b c → le a c
  le_antisymm : ∀ a b, le a b → le b a → a = b
  join_lub : ∀ a b, le a (join a b) ∧ le b (join a b)
```

### 3.3 Project Pipeline as Information Flow

The Project pipeline has an implicit information flow:
- Raw data → processed knowledge → validated insights
- Each stage adds structure (increases information value)
- Quality gates prevent low-quality information from flowing upstream
- This is analogous to lattice-based information flow control

---

## Part 4 — Cryptographic Foundations

### 4.1 Primitives (Formalization Targets)

| Primitive | Security Property | Lean Approach |
|---|---|---|
| Hash function | Collision resistance | Abstract: `∀ x y, hash x = hash y → x = y` (ideal) |
| Symmetric encryption | IND-CPA | Game-based: advantage negligible |
| Public-key encryption | IND-CCA | Game-based: advantage negligible |
| Digital signature | EUF-CMA | Existential unforgeability |
| MAC | Unforgeability | Correct verification implies honest creation |
| Zero-knowledge proof | Soundness + ZK | Simulation-based |

### 4.2 Connection to Lean Proofs

Lean proof verification is analogous to zero-knowledge proofs:
- **Soundness**: If the proof verifies, the theorem is true (no false positives)
- **Completeness**: If the theorem is true, a proof exists (in principle)
- **Zero-knowledge**: The proof reveals nothing beyond the truth of the statement (the kernel doesn't need to understand the proof strategy)

---

## Part 5 — Privacy Formalization

### 5.1 Privacy Models

| Model | Definition | Guarantee |
|---|---|---|
| **k-Anonymity** | Each record indistinguishable from k-1 others | Re-identification probability ≤ 1/k |
| **l-Diversity** | Each group has l distinct sensitive values | Attribute disclosure protection |
| **t-Closeness** | Distribution in group ≈ overall distribution | Statistical disclosure protection |
| **Differential privacy** | Output ≈ same with/without any individual | `P[A(D)] / P[A(D')] ≤ eᵋ` |

### 5.2 Differential Privacy Formalization

```lean
-- ε-differential privacy
def differentially_private (ε : ℝ) (mechanism : Database → Distribution) : Prop :=
  ∀ (d₁ d₂ : Database), neighboring d₁ d₂ →
    ∀ (S : Set Output),
      probability (mechanism d₁) S ≤ Real.exp ε * probability (mechanism d₂) S
```

### 5.3 Project Privacy Relevance

- Knowledge externalization involves private/sensitive knowledge
- Pipeline stages may need to anonymize before sharing
- Multi-agent trust = sharing information selectively
- Provenance chains may reveal sensitive attributes

---

## Part 6 — Threat Modeling

### 6.1 STRIDE Framework

| Threat | Property Violated | Mitigation |
|---|---|---|
| **Spoofing** | Authenticity | Authentication, certificates |
| **Tampering** | Integrity | MACs, digital signatures, hashing |
| **Repudiation** | Non-repudiation | Audit logs, digital signatures |
| **Information disclosure** | Confidentiality | Encryption, access control |
| **Denial of service** | Availability | Rate limiting, redundancy |
| **Elevation of privilege** | Authorization | Least privilege, RBAC |

### 6.2 Attack Trees

```
Root: Compromise system integrity
├── Attack via external interface
│   ├── SQL injection → input validation
│   └── Authentication bypass → MFA
├── Attack via insider
│   ├── Privileged abuse → separation of duties
│   └── Social engineering → security awareness
└── Attack via supply chain
    ├── Compromised dependency → SBOM + verification
    └── Build process tampering → reproducible builds
```

### 6.3 Formal Verification of the project Security

| Project Security Property | Formalization Target | Module |
|---|---|---|
| Provenance chain integrity | Hash chain verification | ProvenanceChain |
| Trust composition soundness | Trust algebra correctness | AgenticSafety |
| Quality gate enforcement | Access control correctness | QualityGates |
| Pipeline stage ordering | Information flow ordering | PipelineAdaptive |
| Axiom cleanliness | No unauthorized axioms | axiom_audit.py |

---

## Part 7 — Security Verification in Lean

### 7.1 Security Property Proofs

Types of security theorems:
1. **Non-interference**: Information doesn't flow where it shouldn't
2. **Access control correctness**: Only authorized operations succeed
3. **Protocol correctness**: Security protocol achieves its goals
4. **Invariant preservation**: Security state maintained across operations

### 7.2 Adversarial Reasoning in Proofs

When proving security properties, think adversarially:
- What inputs could an adversary provide? (universally quantify)
- What prior knowledge might they have? (model as hypotheses)
- What is the worst-case behavior? (prove for all cases)
- Does the property degrade gracefully? (bound the damage)

This mirrors the review council's adversarial review methodology.

---

## Part 8 — Cross-References

| If working on... | Also consult... |
|---|---|
| Access control lattices | `math-algebra-category` (order theory) |
| Information flow | `math-graph-knowledge` (directed graphs) |
| Cryptographic proofs | `math-measure-probability` (probability) |
| Privacy formalization | `math-measure-probability` (distributions) |
| Threat modeling | `applied-intelligence-analysis` (adversarial thinking) |
| Security properties of agents | `ai-agentic-evolving` (trust dynamics) |
| Legal compliance | `applied-legal-reasoning` (regulatory) |
| Provenance verification | `lean-knowledge-formalization` |
| Formal security verification | `ai-high-stakes-verifiable` |
