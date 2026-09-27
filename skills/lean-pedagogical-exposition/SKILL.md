---
name: "lean-pedagogical-exposition"
description: |
  USE FOR: translating Lean 4 formal proofs into human-readable textbook-grade mathematical descriptions, creating learning materials, pedagogical proof walkthroughs, Lean Blueprint LaTeX chapters, and concept zettels.
  DO NOT USE FOR: closing open goals in Lean (use @lean-proof), automated static code census (use @lean-formalization-breakdown).
  TRIGGERS: pedagogical-math, math-exposition, proof-narrative, human-readable-proof, lean-learning-materials, blueprint-chapter.
tier: "hot"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ["skill:lean-formalization-breakdown", "skill:lean-blueprint"]
  successors: ["skill:lean-zettelkasten", "skill:lean-doc-improvement"]
metadata:
  version: "0.1.0"
  source_spec: "references/lean_to_math_exposition_patterns.md"
  last_reviewed: "2026-09-28"
---

# lean-pedagogical-exposition

> Protocol for translating Lean 4 formalizations into clear, beautiful,
> textbook-quality mathematical exposition, interactive Lean Blueprint chapters,
> and pedagogical learning materials.

## Routing

- **USE FOR:**
  - De-formalizing Lean 4 definitions and theorems into intuitive, elegant standard mathematical prose.
  - Converting proof scripts (towers of `have`, `calc`, `obtain`, `rcases`) into structured narrative proofs with clear motivation.
  - Authoring Lean Blueprint LaTeX chapters with `\begin{theorem}`, `\uses`, `\lean`, `\leanok`, and informal proof sketches.
  - Designing pedagogical diagrams, flowcharts, and intuition pumps for complex formal proofs.
  - Producing learning zettels and concept cards for the knowledge garden.
- **DO NOT USE FOR:**
  - Automated static metrics and DAG topological calculations (use `@lean-formalization-breakdown`).
  - Interactive tactic proof closing (use `@lean-proof`).
  - Git PR preparation (use `@lean-pr`).
- **TRIGGERS:** `pedagogical-math`, `math-exposition`, `proof-narrative`, `human-readable-proof`, `lean-learning-materials`, `blueprint-chapter`.

## Exposition Principles

1. **Focus on Ideas Over Implementation Details**:
   - Do not recite mechanical tactic sequences (such as 'then apply simp only and linarith').
   - Instead, state the mathematical reason: 'The divergence vanishes because the adjugate transformation is divergence-free under a unit Jacobian'.
2. **Standard Mathematical Notation**:
   - Translate Lean types to conventional mathematics: `SmoothL2Field Space` becomes $u \in C^\infty(\mathbb{R}^3) \cap L^2(\mathbb{R}^3)$; `fderiv R A.field x` becomes $\nabla u(x)$; `vectorCurl A.field x` becomes $\nabla \times u(x)$.
3. **Structured Proof Walkthroughs (Three-Stage Engine)**:
   - Break monumental arguments into three intuitive stages: Setup / Coordinate Geometry -> Energy Concentration / Asymptotics -> Contradiction / Conclusion.
4. **Lean Blueprint Tight Integration**:
   - Provide each result with its formal Lean identifier (`\lean{...}`), dependency labels (`\uses{...}`), and verification status (`\leanok`).

## Behavioural Rules (G-*)

- **G-1** (MUST): Every formal theorem cited must be accompanied by its standard informal mathematical statement and an intuitive explanation of why the theorem is true.
- **G-2** (MUST): Proof walkthroughs must identify the key invariant, Lyapunov function, or geometric transformation driving the proof.
- **G-3** (MUST): Keep mathematical exposition strictly 7-bit ASCII in Markdown files (INV-001); use standard LaTeX math syntax (`$ ... $` or `$$ ... $$`).
- **G-4** (SHOULD): Include a schematic ASCII or mermaid diagram showing data flow or scale interactions for proofs longer than 50 lines.
- **G-5** (MUST): Preserve fidelity with Lean formal semantics: never over-simplify a statement to the point where it asserts something different from the Lean signature.

## Workflow

1. **Select Landmark**: Identify target theorem or definition from `@lean-formalization-breakdown`.
2. **Extract Dependencies**: Query `lean-lsp-mcp` or `dep_graph.sh` to obtain the transitive premise set.
3. **Draft Math Formulation**: Translate Lean types and hypotheses into standard mathematical notation ($L^2$, $H^s$, $\nabla \times u$).
4. **Decompose Proof Skeleton**: Identify the major intermediate lemmas (`have` milestones) and draft the narrative proof.
5. **Format Blueprint Block**: Write the LaTeX snippet with `\begin{theorem}[Name] \label{...} \lean{...} \uses{...} \leanok ... \end{theorem}`.
6. **Synthesize Zettel**: Emit permanent concept note or reference zettel for the knowledge garden.

## Handoffs

- **Predecessors**: `skill:lean-formalization-breakdown`, `skill:lean-blueprint`
- **Successors**: `skill:lean-zettelkasten` (saving to knowledge graph), `skill:lean-doc-improvement` (documentation polishing).
- **Reference Catalog**: [`references/lean_to_math_exposition_patterns.md`](../../references/lean_to_math_exposition_patterns.md)
