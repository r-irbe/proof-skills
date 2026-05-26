---
name: lean-specification
description: Design theorem specifications for Lean 4 proofs. Use when planning new theorems, lemmas, definitions, or tactics. Covers the three-part specification (requirements, design, documentation), lifecycle management, dependency analysis, and integration with the review council.
---

# Lean 4 Theorem Specification

Structured process for specifying theorems before implementation. Every theorem passes through Specify → Design → Implement → Review → Merge, with each stage tracked by document templates.

## Specification Structure

Every specification has three mandatory parts:

### Part 1: Requirement

Defines *what* needs to be proved and *why*.

```markdown
# Requirement: [REQ-YYYYMMDD-NNN]
## Status: [proposed / approved / implemented / merged]
## Priority: [P0-blocker / P1-critical / P2-important / P3-enhancement]

### Paper Claim
- Source: §[section] of project-tufte.tex
- Equation/Proposition: [reference]
- Quote: "[exact text from paper]"

### English Statement
"[Plain English translation of what the theorem asserts]"

### Preconditions
- [List of hypotheses the theorem needs]
- [Including type constraints, bounds, simplex membership]

### Domain
- Module: Project/[Module].lean
- Section: §[N]
- Related theorems: [existing theorems this depends on or extends]

### Acceptance Criteria
- [ ] `#print axioms` shows only standard axioms
- [ ] Statement matches the paper claim
- [ ] Not a duplicate of existing Mathlib/Tactics.lean result
- [ ] Proof closes without `sorry`
- [ ] `lake build` passes
```

### Part 2: Design

Defines *how* the theorem will be proved.

```markdown
# Design: [DES-YYYYMMDD-NNN] for [REQ-ID]

### Lean Signature
```lean
theorem [name] {params : Types}
    (hyp₁ : condition₁) (hyp₂ : condition₂) :
    conclusion := by
  sorry -- placeholder
```

### Proof Strategy
1. [High-level step 1 — which tactic or approach]
2. [High-level step 2]
3. [High-level step 3]

### Tactic Candidates
| Step | Primary tactic | Fallback | Project custom tactic |
|---|---|---|---|
| 0 | grind | grind | grind |
| 1 | omega | linarith | proj_simplex **(DEPRECATED)** |
| 2 | nlinarith | ring | proj_lyapunov **(DEPRECATED)** |
| 3 | simp [lemma] | unfold + omega | proj_exhaust **(DEPRECATED — prefer direct tactic calls)** |

### Dependencies
- Upstream lemmas: [from Tactics.lean or other modules]
- Upstream definitions: [structures, defs used in the statement]
- Upstream modules: [imports needed]

### Difficulty Assessment
- Estimated: [trivial / moderate / hard / research]
- Rationale: [why this difficulty level]
- Known obstacles: [any anticipated issues]

### Fallback Strategy
If the primary approach fails:
1. [Alternative proof strategy]
2. [Decomposition into sub-lemmas]
3. [Escalation criteria]
```

### Part 3: Documentation

Defines *what documentation* accompanies the theorem.

```markdown
# Documentation: [DOC-YYYYMMDD-NNN] for [REQ-ID]

### Docstring
```lean
/-- [Description of the mathematical content.
    Paper reference: §X.Y of project-tufte.tex.] -/
```

### Module Placement
- File: `Project/[Module].lean`
- Section: `§[N] [Section Title]`
- Position: After [preceding theorem name], before [following theorem name]

### Paper Update
- Appendix theorem count: [module] +1 → [new total]
- Total metrics: [new total lines / theorems / defs]
- Verification mapping table: [add row if new paper claim covered]

### Zettelkasten Notes
- Create: [[ZK-ID]] documenting the design rationale
- Link to: [[ZK-IDs]] of related patterns and insights

### Impact
- Downstream theorems enabled: [list]
- Paper coverage gap closed: [yes/no, which claim]
- New reusable lemma introduced: [yes/no]
```

## Specification Lifecycle

```
PROPOSED → [Φ reviews statement] → APPROVED → [Λ reviews design]
    → DESIGNED → [I_impl implements] → IMPLEMENTED
    → [Council reviews] → MERGED or REVISE
```

### State Transitions

| From | To | Condition | Agent |
|---|---|---|---|
| Proposed | Approved | Φ confirms statement matches paper; Σ confirms no axiom risks | Φ + Σ |
| Approved | Designed | Λ approves proof strategy and tactic selection | Λ |
| Designed | Implemented | Implementer completes proof, `lake build` passes | I_impl |
| Implemented | Merged | Council approves (voting protocol) | Full council |
| Implemented | Revise | Council finds issues (any 🔴 or majority 🟠) | Assigned member |
| Revise | Implemented | Fixes applied, retested | I_impl |

## Specification for Tactics

> **Note:** All `proj_*` custom tactics are DEPRECATED (0 cross-module uses). Prefer direct Mathlib tactics (`grind`, `omega`, `nlinarith`, `positivity`, etc.). This template is retained for historical reference only.

When designing a new tactic (use direct Mathlib names, not `proj_*` prefix):

```markdown
# Tactic Specification: [TAC-YYYYMMDD-NNN]
## Status: [proposed / designed / implemented / tested / deployed]

### Purpose
[What class of goals this tactic closes]

### Motivation
- Theorems that share this pattern: [list with theorem names]
- Current workaround: [existing tactic sequence being replaced]
- Improvement: [fewer steps / more readable / catches more cases]

### Cascade Design
| Priority | Sub-tactic | Handles |
|---|---|---|
| 1 | [first tactic] | [case description] |
| 2 | [second tactic] | [case description] |
| ... | ... | ... |
| N | throwError "[name]: all tactics failed" | Error case |

### Implementation
- Language: Lean 4 (Qq + Lean.Elab.Tactic.Meta)
- Location: Project/Tactics.lean §[next section number]
- Name: `proj_[descriptive_name]`

### Test Cases
```lean
-- Must pass:
example : [typical_goal_1] := by proj_[name]
example : [typical_goal_2] := by proj_[name]
-- Should fail gracefully:
-- example : [out_of_scope_goal] := by proj_[name]
```

### Review Criteria
- [ ] Cascade terminates (no infinite loops)
- [ ] Error messages name the failing tactic
- [ ] Does not shadow existing Mathlib tactics
- [ ] `#print axioms` clean on all test cases
- [ ] Performance: < 5s for typical Project goals
- [ ] Documented in lean-proof-review skill tactic table
- [ ] Documented in AGENT.md proof search strategy
```

## Specification for Definitions and Structures

```markdown
# Definition Specification: [DEF-YYYYMMDD-NNN]

### Lean Signature
```lean
structure [Name] where
  [fields]
```
-- or
```lean
def [name] {params} (args) : ReturnType := [body]
```

### Mathematical Meaning
[Plain English description of what this represents]

### Paper Reference
§[section], [equation/definition] in project-tufte.tex

### Naming Convention
- Structure → PascalCase
- Definition → camelCase
- Follows Project domain prefix convention

### Usage
- Used by theorems: [list]
- Used in modules: [list]

### Alternatives Considered
- [Alternative design 1 and why rejected]
- [Alternative design 2 and why rejected]
```

## Batch Specification (Multiple Related Theorems)

When specifying a group of related theorems (e.g., all lemmas for a paper section):

```markdown
# Batch Specification: [BATCH-YYYYMMDD-NNN]
## Paper Section: §[N] [Title]
## Module: Project/[Module].lean

### Coverage Plan
| Paper claim | REQ-ID | Status | Theorem name |
|---|---|---|---|
| Eq. (N) | REQ-...-001 | proposed | [name] |
| Prop. M | REQ-...-002 | proposed | [name] |
| Cor. K | REQ-...-003 | proposed | [name] |

### Dependency Order
[Which specs must be completed first]

### Parallelization
[Which specs can be implemented in parallel]

### Estimated Impact
- New theorems: [N]
- New definitions: [N]
- New lines: ~[N]
- Paper claims covered: [N]
```

## Integration with Council

| Specification event | Council action |
|---|---|
| Requirement proposed | Φ reviews English statement; Σ assesses axiom risk |
| Design proposed | Λ reviews tactic strategy; Ν checks for duplicates |
| Implementation complete | Full council review (Star topology RALPH) |
| Revision needed | Planner creates todos; assigned agent implements fixes |
| Specification merged | Ω updates AGENT.md metrics; DOC updates paper appendix |
