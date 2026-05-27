---
title: "Lean Doc Requirements Handbook"
status: "reference"
extracted_from: "skills/lean-doc-requirements/SKILL.md"
extracted_on: "2026-05-27"
scope: "Part 1 — Extraction Pipeline; Part 2 — Claim Extraction Protocol; Part 3 — Hypothesis Inference; Part 4 — Batch Extraction Workflow; Part 5 — Council Integration; Part 6 — Requirements Traceability"
loader_hint: "Load when @lean-doc-requirements routes here for details; not needed for the dispatch decision."
---

# Lean Doc Requirements Handbook

> **Layering note.** This file holds the deep content previously
> embedded in [`skills/lean-doc-requirements/SKILL.md`](../skills/lean-doc-requirements/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow /
> Recovery / Handoffs) + a parts index. This file holds the full
> encyclopaedia. Zero fidelity loss vs the pre-layering revision.

---

## Part 1 — Extraction Pipeline

```
Document → Section scan → Claim extraction → Formalization →
  Specification → Cross-reference back to document
```

### Input Sources (priority order)

1. **Primary paper** (`docs/project-tufte.tex`) — mathematical claims, theorems, equations
2. **Technical reports** (`docs/tech_report_copy1.txt`, `docs/theory-report-copy-2.txt`) — extended proofs, design rationale
3. **System requirements** (`docs/system_requirements_final.md`) — functional properties to verify
4. **Analysis documents** (`docs/analysis-plan/`) — verification targets

---

## Part 2 — Claim Extraction Protocol

### 2.1 LaTeX Claim Types

| LaTeX Environment | Claim Type | Extraction Action |
|---|---|---|
| `\begin{theorem}` | Formal theorem | Direct extraction — highest priority |
| `\begin{proposition}` | Proposition | Direct extraction |
| `\begin{corollary}` | Corollary | Extract with parent theorem reference |
| `\begin{lemma}` | Supporting lemma | Extract with usage context |
| `\begin{definition}` | Formal definition | Extract for `structure`/`def` in Lean |
| `\begin{equation}` | Numbered equation | Extract if involves a verifiable identity or bound |
| Inline `$...$` | Inline claim | Extract only if it asserts a property (e.g., "$f$ is monotone") |
| Prose assertion | Informal claim | Extract if it makes a mathematical claim that can be formalized |

### 2.2 Extraction Template

For each extracted claim:

```markdown
# Claim: [DOC-SECT-NNN]
## Source
- Document: [filename]
- Section: [§N.M]
- Page/Line: [reference]
- LaTeX environment: [theorem/equation/prose]
- Verbatim text: [exact quote, max 200 chars]

## Classification
- Type: [theorem | definition | bound | identity | monotonicity | convergence | safety | other]
- Domain: [quality-gates | phase-classification | pipeline | CCV | cusp | provenance | lyapunov | RL | agentic-safety | stochastic]
- Complexity: [trivial | routine | moderate | hard | research-level]

## Informal Statement
[One-paragraph plain English interpretation]

## Hypotheses (inferred)
1. [h₁ — e.g., "quality score is in [0,1]"]
2. [h₂ — e.g., "decision function is continuous"]
3. [h₃ — e.g., "convergence parameter ε > 0"]

## Target Lean Signature (draft)
```lean
theorem claim_name
    (h₁ : ...)
    (h₂ : ...)
    : [conclusion] := by
  sorry -- to be proven
```

## Dependencies
- Requires definitions: [list of Lean definitions needed]
- Requires prior claims: [list of claim IDs this depends on]
- Target module: Project/[Module].lean

## Traceability
- Claim ID: DOC-SECT-NNN
- Specification ID: [SPEC-YYYYMMDD-NNN when created]
- Theorem name: [final Lean name when implemented]
```

---

## Part 3 — Hypothesis Inference

Informal text rarely states all hypotheses explicitly. Infer from:

### 3.1 Context Clues

| Document Signal | Inferred Hypothesis |
|---|---|
| "For all quality scores q" | `(q : ℝ) (hq : q ∈ Set.Icc 0 1)` |
| "Given a continuous function f" | `(hf : Continuous f)` |
| "Under standard assumptions" | Check paper §2 for assumption block |
| "As shown in Theorem 3.2" | Dependency on claim DOC-3-002 |
| "In the limit" | `(n : ℕ)` or `Filter.Tendsto` |
| "For sufficiently large n" | `(N : ℕ) (hn : n ≥ N)` or `Filter.Eventually` |
| "Almost surely" | Measurability + `MeasureTheory.ae` |
| "Under mild regularity conditions" | CHECK CAREFULLY — need to identify exact conditions |

### 3.2 Domain-Specific Defaults (Project)

When project-specific terms appear without qualification:

| Term | Default Hypothesis |
|---|---|
| Quality score | `∈ Set.Icc 0 1` |
| Phase | Member of `PhaseType` enum |
| Pipeline | `PipelineConfig` structure |
| CCV values | Non-negative real |
| Decision boundary | Defined on `ℝⁿ` with appropriate topology |
| Convergence | With respect to explicit metric or norm |
| Safety bound | Via Lyapunov function or contraction mapping |

### 3.3 Red Flags in Hypothesis Inference

- **"Obviously" / "Clearly"** — these hide non-trivial hypotheses, flag for Φ review
- **"Without loss of generality"** — may hide symmetry argument needing separate lemma
- **"By a standard argument"** — may require Mathlib search for the standard result
- **Universally quantified with no bound** — check if domain restriction is implied
- **Conditional/existential mix** — verify quantifier order carefully

---

## Part 4 — Batch Extraction Workflow

### 4.1 Section-by-Section Scan

```
FOR EACH section in paper:
  1. Read section completely
  2. List all mathematical environments
  3. List all prose assertions with mathematical content
  4. For each item:
     a. Fill extraction template
     b. Classify complexity
     c. Assign target module
  5. Cross-reference with existing theorems in target module
  6. Record: covered / partial / uncovered
```

### 4.2 Coverage Matrix Update

After extraction, update the project coverage matrix:

```markdown
| Claim ID | Section | Type | Target Module | Status | Lean Name |
|---|---|---|---|---|---|
| DOC-3-001 | §3.1 | theorem | QualityGates | covered | quality_gate_monotone |
| DOC-3-002 | §3.2 | bound | QualityGates | partial | quality_upper_bound |
| DOC-4-001 | §4.1 | definition | PhaseClassification | covered | PhaseType |
| DOC-5-001 | §5.1 | convergence | PipelineAdaptive | uncovered | — |
```

### 4.3 Output Artifacts

Per extraction batch:
1. `docs/tracking/claims_[section].md` — all extracted claims for that section
2. Updated coverage matrix in `docs/tracking/coverage_matrix.md`
3. For uncovered claims: retroactive specifications via lean-specification skill
4. For partial claims: gap analysis notes
5. Zettelkasten literature notes for key insights discovered during extraction

---

## Part 5 — Council Integration

### 5.1 Claim Review

After extraction, route claims through the council:

| Member | Role in Claim Review |
|---|---|
| Σ | Verify that the draft Lean signature type-checks (or explain why not) |
| Φ | Validate that the Lean signature faithfully represents the paper claim |
| Ν | Check if Mathlib already has a version of this claim |
| Λ | Assess specification quality — clear, testable, well-scoped |
| Ω | Verify naming convention, module placement, cross-references |

### 5.2 Handoff Chain

```
doc-requirements extracts claim
  → lean-specification creates formal spec
    → lean-review-council reviews spec
      → implementer proves theorem
        → lean-review-council reviews proof
          → lean-doc-improvement updates paper
```

### 5.3 Dispute Resolution

When Φ and the document disagree (Lean formalization reveals paper imprecision):
1. Record the discrepancy in a fleeting Zettelkasten note
2. Flag for Φ + Ν joint review
3. If confirmed: create a paper erratum entry
4. Update the claim to reflect correct formalization
5. Route to lean-doc-improvement for paper update

---

## Part 6 — Requirements Traceability

### 6.1 Bidirectional Trace

Every formal requirement must trace in both directions:

```
Document claim ←→ Specification ←→ Lean theorem
```

The traceability record:

```markdown
## Trace: [claim_id]
- Forward: DOC-3-001 → SPEC-20250718-001 → quality_gate_monotone (QualityGates.lean:L45)
- Backward: quality_gate_monotone → SPEC-20250718-001 → DOC-3-001 (project-tufte.tex §3.1)
- Status: verified (all links valid, theorem compiles, matches claim)
```

### 6.2 Orphan Detection

- **Orphan claims**: Document claims with no Lean theorem → create specification
- **Orphan theorems**: Lean theorems with no document claim → add to "infrastructure lemmas" or flag for paper inclusion
- **Broken traces**: Claim references a Lean name that no longer exists → repair or update

### 6.3 Stale Trace Detection

Trigger re-extraction when:
- Paper section is substantially revised
- Lean theorem signature changes (hypotheses added/removed)
- Module reorganization moves theorems
- New document is added to the project
