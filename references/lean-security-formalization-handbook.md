---
title: "Lean Security Formalization Handbook"
status: "reference"
extracted_from: "skills/lean-security-formalization/SKILL.md"
extracted_on: "2026-05-27"
scope: "Part 1 — Security Properties; Part 2 — Access Control Models; Part 3 — Information Flow; Part 4 — Privacy and Data Protection; Part 5 — Cryptographic Properties; Part 6 — Trust Models; Part 7 — Research Council Integration"
loader_hint: "Load when @lean-security-formalization routes here for details; not needed for the dispatch decision."
---

# Lean Security Formalization Handbook

> **Layering note.** This file holds the deep content previously
> embedded in [`skills/lean-security-formalization/SKILL.md`](../skills/lean-security-formalization/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow /
> Recovery / Handoffs) + a parts index. This file holds the full
> encyclopaedia. Zero fidelity loss vs the pre-layering revision.

---

## Part 1 — Security Properties

### 1.1 CIA Triad

| Property | Formal Statement | Project Relevance |
|---|---|---|
| **Confidentiality** | Unauthorized agents cannot read protected data | Tacit knowledge protection, LED compliance |
| **Integrity** | Unauthorized agents cannot modify data | Provenance immutability, quality gate tamper-resistance |
| **Availability** | Authorized agents can always access data | Pipeline liveness, knowledge retrieval |

### 1.2 Formal Security Properties

```lean
-- Noninterference: high-security inputs don't affect low-security outputs
def Noninterference (f : Input → Output) (sec : Input → SecurityLevel) 
    (obs : SecurityLevel) : Prop :=
  ∀ i₁ i₂, (∀ x, sec x ≤ obs → i₁ x = i₂ x) → 
    observe obs (f i₁) = observe obs (f i₂)

-- Integrity (Biba model): information flows upward
-- No write-up: low integrity cannot modify high integrity
def Integrity (write : Agent → Object → Prop) (level : Agent → ℕ) 
    (objLevel : Object → ℕ) : Prop :=
  ∀ a o, write a o → level a ≥ objLevel o
```

---

## Part 2 — Access Control Models

### 2.1 Lattice-Based Access Control (BLP)

```lean
-- Bell-LaPadula: information flows down (confidentiality)
-- No read-up: subject cannot read object above its clearance
-- No write-down: subject cannot write to object below its clearance

structure BLPState where
  subjects : Finset Subject
  objects : Finset Object
  clearance : Subject → SecurityLevel
  classification : Object → SecurityLevel
  currentAccess : Subject → Object → AccessMode → Prop

-- Simple security (no read-up):
def SimpleSecure (st : BLPState) : Prop :=
  ∀ s o, st.currentAccess s o .Read → st.clearance s ≥ st.classification o

-- Star property (no write-down):
def StarSecure (st : BLPState) : Prop :=
  ∀ s o, st.currentAccess s o .Write → st.clearance s ≤ st.classification o
```

### 2.2 Role-Based Access Control (RBAC)

```lean
-- RBAC: permissions assigned to roles, roles assigned to users
structure RBAC where
  users : Finset User
  roles : Finset Role
  permissions : Finset Permission
  userRoles : User → Finset Role
  rolePerms : Role → Finset Permission

-- Authorization: user has permission if any of their roles grants it
def authorized (rbac : RBAC) (u : User) (p : Permission) : Prop :=
  ∃ r ∈ rbac.userRoles u, p ∈ rbac.rolePerms r

-- Project: role-based access to pipeline stages
-- E.g., only ConsolidationReviewer role can approve at Consolidation stage
```

### 2.3 Project Access Control Model

```lean
-- Project stage-based access:
-- Experience: practitioner (capture) + system (context enrichment)
-- Articulation: practitioner (edit) + AI (elicitation scaffolding, read-only knowledge)
-- Structuring: practitioner (organize) + AI (suggestion, no write)
-- Consolidation: reviewer (approve/reject) + practitioner (read)
-- Innovation: administrator (version, retire) + all (read)

-- Key property: AI never has write access to validated knowledge
-- (Design Principles DP6, DP7)
theorem ai_no_write_to_validated (agent : Agent) (artifact : Artifact)
    (h_ai : agent.isAI) (h_val : artifact.stage = .Consolidation ∨ artifact.stage = .Innovation) :
    ¬ hasWriteAccess agent artifact := by
  sorry -- enforce by construction in the access model
```

---

## Part 3 — Information Flow

### 3.1 Information Flow Control

```lean
-- Security lattice: (levels, ≤) where ≤ is the "can flow to" relation
-- Top = most secret, Bottom = most public

-- Project information flow:
-- Tacit knowledge flows: practitioner → system (E → A → S)
-- Validated knowledge flows: system → organization (C → I)
-- AI-generated content: tagged, bounded, never auto-promoted

-- No flow violations:
def NoFlowViolation (flow : Artifact → Artifact → Prop) 
    (level : Artifact → SecurityLevel) : Prop :=
  ∀ a b, flow a b → level a ≤ level b
```

### 3.2 Provenance Integrity

```lean
-- PROV-O provenance chain must be tamper-evident:
-- 1. Each node has a content hash
-- 2. Each derivation references the parent hash
-- 3. Chain verification: recompute hashes and compare

-- Formal property: no undetectable modification
theorem provenance_tamper_evident (chain : ProvChain) (h_wf : WellFormed chain) :
    ∀ modification, detectable chain modification := by
  -- Follows from hash chain integrity
  sorry
```

### 3.3 Covert Channels

```lean
-- Covert channel: information flow not intended by the security policy
-- In Project: AI model could leak training data through generated text
-- Mitigation: provenance tagging + output filtering

-- Formal bound: mutual information between secret and observable is bounded
-- I(Secret; Observable) ≤ ε
```

---

## Part 4 — Privacy and Data Protection

### 4.1 GDPR-Relevant Properties

```lean
-- Data minimization: only necessary data collected
-- Purpose limitation: data used only for stated purpose
-- Storage limitation: data deleted after retention period

-- Formal data lifecycle:
structure DataLifecycle where
  collected : Nat  -- timestamp
  purpose : String
  retentionDays : Nat
  deleted : Option Nat  -- deletion timestamp

-- Compliance: data deleted by deadline
def gdprCompliant (dl : DataLifecycle) (now : Nat) : Prop :=
  dl.deleted.isSome ∨ (now - dl.collected) ≤ dl.retentionDays * 86400
```

### 4.2 LED-Specific Properties (Law Enforcement)

```lean
-- Law Enforcement Directive (2016/680):
-- Article 4: lawful processing principles
-- Article 10: processing of special categories (biometric, genetic)
-- Article 11: automated individual decisions (requires human review)

-- Project compliance: Consolidation stage = Article 11 human review
-- Every AI-assisted analysis must be reviewed by a human before
-- it can influence law enforcement decisions
```

### 4.3 Differential Privacy

```lean
-- ε-differential privacy:
-- P(M(D₁) ∈ S) ≤ e^ε * P(M(D₂) ∈ S)
-- for neighboring datasets D₁, D₂ (differing in one record)

-- Project: if the system stores knowledge from multiple practitioners,
-- differential privacy bounds information leakage about individuals
-- (Relevant for organizational knowledge base, not individual capture)
```

---

## Part 5 — Cryptographic Properties

### 5.1 Hash Functions

```lean
-- Collision resistance: hard to find x ≠ y with H(x) = H(y)
-- Pre-image resistance: given h, hard to find x with H(x) = h
-- Second pre-image resistance: given x, hard to find y ≠ x with H(y) = H(x)

-- Project provenance uses content hashes:
-- Not modeling computational hardness (that's complexity theory)
-- But modeling: if hashes are different, content is different
axiom hash_injective_model : ∀ x y, hash x = hash y → x = y
-- (This is the idealized model; real hashes have negligible collision probability)
```

### 5.2 Digital Signatures

```lean
-- Authenticity: signature proves authorship
-- Non-repudiation: author cannot deny signing

-- Project: practitioner signs their contributions
-- AI-generated content signed differently (different key/tag)
-- Verification: any party can verify signature
```

### 5.3 Secure Multi-Party Computation

```lean
-- Multiple parties compute f(x₁, ..., xₙ) without revealing inputs
-- Project: multiple practitioners contribute knowledge
-- without revealing sensitive operational details
-- (Relevant for cross-organizational knowledge sharing)
```

---

## Part 6 — Trust Models

### 6.1 Computational Trust

```lean
-- Trust as a value in [0,1] (or Nat ×100 in the project):
-- Updated based on evidence: positive → increase, negative → decrease
-- Project trust vector: (recognition, structuring, knowledge)

-- Trust composition: agent A trusts B, B trusts C → A trusts C?
-- Not transitive in general! Discount: trust(A,C) ≤ trust(A,B) * trust(B,C)
-- Project: trust contraction bounds composition
```

### 6.2 Delegation and Authority

```lean
-- Delegation: A grants B some of A's authority
-- Bounded: B's delegated authority ≤ A's authority
-- Revocable: A can revoke at any time

-- Project: AI agents have delegated authority from practitioners
-- Trust vector determines delegation bounds
-- Human override = immediate revocation
```

---

## Part 7 — Research Council Integration

| Security Topic | Research Council Member |
|---|---|
| Access control model design | Β (Structure Strategist) |
| Information flow analysis | Α (Foundations Architect) + Δ (Bounds Analyst) |
| Privacy property formulation | Ε (Applications Bridge) |
| Cryptographic modeling | Α (Foundations Architect) |
| Trust model mathematics | Δ (Bounds Analyst) + Γ (Methods Scholar) |
| Legal compliance mapping | Ε (Applications Bridge) |
| Provenance security | Β (Structure Strategist) + Ε (Applications Bridge) |
