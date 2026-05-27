---
title: "Applied Legal Reasoning Handbook"
status: "reference"
extracted_from: "skills/applied-legal-reasoning/SKILL.md"
extracted_on: "2026-05-27"
scope: "Part 1 — Legal Reasoning Paradigms; Part 2 — Argumentation Frameworks; Part 3 — Defeasible Legal Rules; Part 4 — Statutory Interpretation; Part 5 — Case-Based Reasoning (CBR); Part 6 — Regulatory Compliance Formalization; Part 7 — AI & Legal Reasoning; Part 8 — Cross-References"
loader_hint: "Load when @applied-legal-reasoning routes here for details; not needed for the dispatch decision."
---

# Applied Legal Reasoning Handbook

> **Layering note.** This file holds the deep content previously
> embedded in [`skills/applied-legal-reasoning/SKILL.md`](../skills/applied-legal-reasoning/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow /
> Recovery / Handoffs) + a parts index. This file holds the full
> encyclopaedia. Zero fidelity loss vs the pre-layering revision.

---

## Part 1 — Legal Reasoning Paradigms

### 1.1 Core Methods

| Method | Description | Formal Model |
|---|---|---|
| **Rule-based** | Apply statutory rules to facts | Deductive logic + exception handling |
| **Case-based** | Reason by analogy to precedent | CBR: similarity metrics + factor analysis |
| **Argumentation** | Construct/attack/defend arguments | Abstract argumentation frameworks (Dung) |
| **Defeasible** | Rules with exceptions and priorities | Defeasible logic programming |
| **Teleological** | Interpret law by purpose/intent | Goal-directed reasoning |
| **Textual** | Strict reading of statutory text | Formal language interpretation |

### 1.2 Project Connections

| Legal Concept | Project Analog | Module |
|---|---|---|
| Chain of custody | Provenance chain | ProvenanceChain |
| Burden of proof | Quality gate thresholds | QualityGates |
| Due process | Pipeline stages (ordered, documented) | PipelineAdaptive |
| Regulatory compliance | Safety envelopes | AgenticSafety |
| Audit trail | Trust composition + timestamps | ProvenanceChain, AgenticSafety |
| Standard of care | Quality gate minimum thresholds | QualityGates |

---

## Part 2 — Argumentation Frameworks

### 2.1 Dung's Abstract Argumentation

```
AF = (Args, Attacks)
- Args: finite set of arguments
- Attacks ⊆ Args × Args: binary attack relation

Semantics:
- Conflict-free: S attacks no member of S
- Admissible: S conflict-free and defends all its members
- Complete: admissible + includes all arguments it defends
- Preferred: maximal complete extension
- Grounded: minimal complete extension
- Stable: conflict-free + attacks all non-members
```

### 2.2 Lean 4 Encoding

```lean
structure ArgFramework where
  args : Finset String
  attacks : String → String → Prop
  attacks_dec : ∀ a b, Decidable (attacks a b)

def conflictFree (af : ArgFramework) (s : Finset String) : Prop :=
  ∀ a ∈ s, ∀ b ∈ s, ¬af.attacks a b

def defends (af : ArgFramework) (s : Finset String) (a : String) : Prop :=
  ∀ b, af.attacks b a → ∃ c ∈ s, af.attacks c b

def admissible (af : ArgFramework) (s : Finset String) : Prop :=
  conflictFree af s ∧ ∀ a ∈ s, defends af s a
```

### 2.3 Structured Argumentation (ASPIC+)

Extends abstract argumentation with:
- Strict rules (non-defeasible): `a₁, ..., aₙ → b`
- Defeasible rules: `a₁, ..., aₙ ⇒ b` (can be defeated)
- Rule priorities and last-link/weakest-link defeat
- Burden of proof allocation

---

## Part 3 — Defeasible Legal Rules

### 3.1 Legal Rule Structure

```
IF conditions AND NOT exceptions THEN conclusion
  UNLESS higher-priority competing rule applies
  SUBJECT TO burden of proof allocation
```

### 3.2 Priority Mechanisms

| Mechanism | Description | Example |
|---|---|---|
| **Lex specialis** | Specific rule overrides general | Contract clause > general law |
| **Lex posterior** | Later rule overrides earlier | Amendment supersedes original |
| **Lex superior** | Higher authority overrides lower | Constitutional > statutory |
| **Explicit override** | Rule states it overrides another | "Notwithstanding Section 12..." |

### 3.3 Formalization Pattern

```lean
structure LegalRule where
  id : String
  conditions : List Prop
  exceptions : List Prop
  conclusion : Prop
  authority : Nat      -- Higher = more authoritative
  enactedDate : Nat    -- Later = more recent
  specificity : Nat    -- Higher = more specific

def ruleApplies (r : LegalRule) (facts : List Prop) : Prop :=
  (∀ c ∈ r.conditions, c) ∧ (∀ e ∈ r.exceptions, ¬e)

def defeats (r1 r2 : LegalRule) : Prop :=
  r1.authority > r2.authority ∨
  (r1.authority = r2.authority ∧ r1.enactedDate > r2.enactedDate) ∨
  (r1.authority = r2.authority ∧ r1.enactedDate = r2.enactedDate ∧
   r1.specificity > r2.specificity)
```

---

## Part 4 — Statutory Interpretation

### 4.1 Canons of Construction

| Canon | Method | Formalization |
|---|---|---|
| Plain meaning | Words have ordinary meaning | String matching + dictionary lookup |
| Contextual | Words interpreted in context | Scoped interpretation function |
| Purpose (teleological) | Interpret to fulfill legislative purpose | Goal-directed inference |
| Harmonization | Avoid contradictions between sections | Consistency checking |
| Ejusdem generis | General terms limited by specific context | Type restriction |
| Expressio unius | Expression of one excludes others | Closed-world assumption |
| Noscitur a sociis | Words known by company they keep | Contextual co-occurrence |

### 4.2 Project application

the project's formal specification process is analogous to statutory interpretation:
- Paper claims = "legislation" (authoritative text)
- Lean formalization = "court interpretation" (precise meaning)
- Errata = "judicial corrections" (fixing imprecise text)
- Coverage matrix = "annotated code" (linking text to interpretation)

---

## Part 5 — Case-Based Reasoning (CBR)

### 5.1 Factor-Based Analysis

| Factor | Direction | Description |
|---|---|---|
| Factor F₁ | Pro-plaintiff | Supports one side |
| Factor F₂ | Pro-defendant | Supports other side |
| Dimension D₁ | Continuous | Degree of relevant property |

### 5.2 Similarity Metrics

```
sim(case₁, case₂) = Σᵢ wᵢ · match(factor_i(case₁), factor_i(case₂))

Where match returns:
  1.0 if both present with same direction
  0.5 if both present with different magnitude
  0.0 if one missing
```

### 5.3 Project Proof CBR

Within Project, "case-based reasoning" means:
- Similar theorems in different modules (analogy)
- Reusing proof strategies from Tactics.lean (precedent)
- ZK permanent notes capturing successful patterns (jurisprudence)

---

## Part 6 — Regulatory Compliance Formalization

### 6.1 Compliance Rules as Formal Constraints

```lean
-- Regulatory compliance as safety envelope
structure ComplianceRegime where
  rules : List LegalRule
  applicability : Context → LegalRule → Prop
  penalties : LegalRule → Nat → Prop  -- violation severity
  
def isCompliant (regime : ComplianceRegime) (state : SystemState) : Prop :=
  ∀ r ∈ regime.rules,
    regime.applicability currentContext r →
    ruleApplies r (extractFacts state)
```

### 6.2 Connection to Project Safety Envelopes

The safety envelope in `AgenticSafety.lean` can be viewed as regulatory compliance:
- Safety conditions = mandatory regulations
- `allHold` = full regulatory compliance
- `envelope_monotone_conjunction` = regulations compose conjunctively
- `action_preserves_envelope` = actions must maintain compliance

---

## Part 7 — AI & Legal Reasoning

### 7.1 Legal AI Applications

| Application | Reasoning Type | Project Component |
|---|---|---|
| Contract analysis | Rule-based + NLP | Knowledge graph extraction |
| Legal research | Case-based retrieval | Research skill (Type L) |
| Compliance checking | Constraint satisfaction | Quality gates + safety envelopes |
| Verdict prediction | Statistical + factor-based | Stochastic CCV |
| Document review | Classification + extraction | Pipeline stages |

### 7.2 Ethical Considerations

- Bias in training data → biased legal AI
- Accountability for AI-assisted legal decisions
- Right to human review (GDPR Art 22)
- Transparency of AI reasoning in legal contexts

---

## Part 8 — Cross-References

| If working on... | Also consult... |
|---|---|
| Deontic logic (obligation/permission) | `ai-causal-deontic` |
| Argumentation attack graphs | `math-graph-knowledge` |
| Defeasible reasoning | `ai-commonsense-reasoning` (default logic) |
| Regulatory AI | `ai-high-stakes-verifiable` |
| Provenance as audit trail | `lean-knowledge-formalization` |
| Trust in legal contexts | `ai-agentic-evolving` (trust dynamics) |
