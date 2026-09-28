# Template_PedagogicalProofWalkthrough.md -- Textbook-Quality Mathematical Exposition

> **Status:** Production template for translating monumental Lean 4 proofs into
> human-readable, textbook-grade pedagogical walkthroughs and learning materials.
> Compatible with Lean Blueprint, Investigation Garden Layer 4 Concept Zettels,
> and proof-skills `@lean-pedagogical-exposition`.

---

## 1. When to Use

- Translating a complex Lean 4 theorem and proof script into clear, pedagogical mathematical prose.
- Creating learning materials and companion guides for formal math codebases (e.g. FLT, Navier-Stokes, Sphere Eversion).
- Bridging formal verification artifacts with human mathematical intuition.

---

## 2. Template Structure

```markdown
# Pedagogical Proof Walkthrough: <Theorem Title>

> **Formal Declaration:** `<Namespace.theorem_name>`  
> **Source File:** [`<path/to/file.lean>`](file:///<path/to/file.lean>)  
> **Lean Blueprint Anchor:** `\lean{<Namespace.theorem_name>}`, `\label{thm:<label>}`  
> **Garden Concept Zettel:** [`zet-lean-<slug>`](file:///docs/investigation-garden/zettels/concepts/zet-lean-<slug>.md)  
> **MSC2020 Classification:** <Primary Code> (e.g. 11G05, 35Q30, 03B35)

---

## 1. Mathematical Statement & Intuitive Essence

### Informal Textbook Formulation

**Theorem (<Theorem Title>).**
*Let $X$ be a <domain space> satisfying <regularity conditions>. Suppose that <hypotheses>.
Then <conclusion mathematical assertion>.*

### Formal Lean 4 Declaration

```lean
theorem <theorem_name> (<args> : <types>) : <formal_assertion> := by
  ...
```

### Conceptual Executive Summary

<In 2-3 paragraphs, explain the mathematical intuition behind the theorem.
What makes this result deep or surprising? What is the fundamental obstruction
that prevents a trivial proof, and what core geometric or algebraic idea overcomes it?>

---

## 2. Notation & De-Formalization Dictionary

To bridge the formal code with conventional mathematical literature, we map the Lean 4 type signatures to standard notation:

| Formal Lean 4 Identifier | Conventional Math Symbol | Mathematical Description |
| :--- | :--- | :--- |
| `<LeanType1>` | $X$ | The underlying manifold or configuration space |
| `<LeanFunc2>` | $u \in C^\infty(X, \mathbb{R}^3)$ | Smooth velocity vector field |
| `<LeanNorm3>` | $\|u\|_{L^2}$ | Standard $L^2$ norm on spatial domain |
| `<LeanOperator4>` | $\nabla \times u$ | Vector curl / vorticity operator |
| `<LeanRelation5>` | $A \sim B$ | Isogeny or equivalence relation |

---

## 3. The Three-Stage Proof Engine

Monumental formal proofs are structured into three distinct mathematical phases:

```text
+-----------------------------------------------------------------------------+
| Stage 1: Geometric Setup & Invariant Conservation                          |
|   - Establish coordinates, symmetries, and conserved quantities             |
|   - Transform raw variables into normalized canonical representations       |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Stage 2: Energy Estimates, Asymptotics & Concentration                     |
|   - Bound growth rates via Gronwall inequalities or height bounds           |
|   - Localize singularities or Galois representations to critical scales     |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Stage 3: Topological / Analytic Contradiction & Conclusion                  |
|   - Demonstrate incompatibility between bounded capacity and infinite growth|
|   - Conclude finite-time breakdown or existence of non-trivial solution     |
+-----------------------------------------------------------------------------+
```

### Stage 1: Setup & Conserved Quantities
<Detailed narrative of the initial transformations and invariant preservation.>

### Stage 2: The Core Estimate
<Detailed narrative of the central inequality, spectral decomposition, or induction step.>

### Stage 3: The Contradiction / Resolution
<Detailed narrative of how the estimates culminate in the final theorem statement.>

---

## 4. Milestone Proof Walkthrough

Instead of reciting mechanical tactic sequences (`simp`, `intro`, `linarith`), we trace the essential milestones (`have`, `obtain`, `calc`):

### Milestone 1: <Name of First Lemma/Have Block>
- **Formal Anchor:** Line <N>, `have h1 : <type>`
- **Mathematical Rationale:** <Explain why this intermediate lemma is needed and how it is established.>

### Milestone 2: <Name of Second Lemma/Have Block>
- **Formal Anchor:** Line <M>, `obtain \<x, hx\> := <proof>`
- **Mathematical Rationale:** <Explain the extraction of the witness or decomposition.>

### Milestone 3: <Name of Key Calculation Block>
- **Formal Anchor:** Line <K>, `calc <lhs> = <mid> := by ... <= <rhs> := by ...`
- **Mathematical Rationale:** <Explain the algebraic cancellation or geometric inequality.>

---

## 5. Pedagogical Intuition Pumps & Pitfalls

### The Naive Approach and Why It Fails
<Describe the obvious or historical attempt to prove this theorem and explain exactly where it breaks down.>

### The "Aha!" Insight
<Explain the non-obvious shift in perspective that allows the formal proof to go through (e.g. change of coordinates, dual representation, auxiliary Lyapunov functional).>

### Potential Formalization Traps
- **Trap 1:** <e.g. Direct definition vs inductive construction.>
- **Trap 2:** <e.g. Non-computable classical choice vs constructive witnesses.>

---

## 6. Lean Blueprint & Knowledge Garden Integration

### Lean Blueprint Environment (PlasTeX)

```latex
\begin{theorem}[<Theorem Title>]
\label{thm:<label>}
\uses{def:<dep1>, lem:<dep2>}
\lean{<Namespace.theorem_name>}
\leanok
<Informal LaTeX theorem statement.>
\end{theorem}

\begin{proof}
\uses{lem:<dep2>}
\leanok
<Textbook-quality proof sketch summarizing the 3-stage engine.>
\end{proof}
```

### Knowledge Garden Concept Zettel

- **Zettel ID:** `zet-lean-<slug>`
- **Layer:** 4 (Concept)
- **MOC Index:** `MOC-lean-and-easci`, `MOC-itp-master-ontology`
- **Related Notes:** `zet-lean-<related1>`, `zet-lean-<related2>`
```
