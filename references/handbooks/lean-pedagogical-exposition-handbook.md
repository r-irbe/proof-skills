---
name: lean-pedagogical-exposition-handbook
description: Reference handbook for @lean-pedagogical-exposition.
extracted_from: skills/lean-pedagogical-exposition/SKILL.md
---

## Quick-Lookup Indexing Tables (`mathcomp-skills` Three-Entry-Point Pattern)

### Table 1: Goal-Shape-First (`templates` Entry Point)

| Goal / Term Shape | Primary Tactic / Pattern | Canonical Recipe / Notes |
| :--- | :--- | :--- |
| Verified Lean 4 proof with inscrutable tactic script | Structured Mathematical Proof Narrative | Map `have`/`calc`/`induction` landmarks to human mathematical intuition |
| Type-theoretic encoding (`Fin n -> ℝ`, `Subtype`) | Standard mathematical notation translation | Render clean LaTeX (`x \in \mathbb{R}^n`) with side-by-side Lean anchor |
| Pure-math conference manuscript over Lean corpus | Halmos + Knuth Ch. 18 Pure-Math Architecture | Zero `.lean` / `snake_case` in prose; bind all symbols inside theorem boxes; slash `$a/b$` inline |

### Table 2: Intent-First (`phrasebook` Entry Point)

| User / Engineer Intent | Recommended Tool / Idiom | Actionable Recipe |
| :--- | :--- | :--- |
| Turn a formal Lean module into a textbook chapter | `editor.md` + `math-pedagogy-author` overlay | Include motivation, geometric intuition, proof architecture diagram, and Lean table |
| Explain *why* a precondition is needed | Counterexample-driven exposition | Show concrete failure witness when hypothesis `h` is dropped |
| Credit upstream, classical, and novel proofs honestly | Three-Tier Proof Provenance Section | Separate Tier 1 (`Mathlib`/`Cslib`), Tier 2 (adapted/newly proved classical), and Tier 3 (novel domain) |

### Table 3: Error / Bottleneck-First (`errors` Entry Point)

| Symptom / Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Prose reads like line-by-line tactic transliteration ('First we `rw`...') | Tactic-level noise leaked into exposition | Summarize algebraic rewrites as conceptual equations (`calc` chain) |
| Exposition omits key technical hypothesis present in Lean | Silent simplification drift | List every Lean hypothesis explicitly in the theorem statement box |
| Bracketed titles stuffed onto routine propositions | Promotional naming clutter | Reserve `[...]` titles strictly for classical landmark theorems (Halmos §12) |

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
   - Translate Lean types to conventional mathematics: `SmoothL2Field Space` becomes $u \in C^\infty(\mathbb{R}^3) \cap L^2(\mathbb{R}^3)$; `fderiv R
     A.field x` becomes $\nabla u(x)$; `vectorCurl A.field x` becomes $\nabla \times u(x)$.
3. **Structured Proof Walkthroughs (Three-Stage Engine)**:
   - Break monumental arguments into three intuitive stages: Setup / Coordinate Geometry -> Energy Concentration / Asymptotics -> Contradiction / Conclusion.
4. **Lean Blueprint Tight Integration**:
   - Provide each result with its formal Lean identifier (`\lean{...}`), dependency labels (`\uses{...}`), and verification status (`\leanok`).

## Behavioural Rules (G-*)

- **G-1** (MUST): Every formal theorem cited must be accompanied by its standard informal mathematical statement and an intuitive explanation of why the
  theorem is true.
- **G-2** (MUST): Proof walkthroughs must identify the key invariant, Lyapunov function, or geometric transformation driving the proof.
- **G-3** (MUST): Follow scoped Unicode policy (INV-001) in Markdown exposition. Preserve mathematical notation and scripts; reject dangerous carriers and configured substitutions.
- **G-4** (SHOULD): Include a schematic ASCII or mermaid diagram showing data flow or scale interactions for proofs longer than 50 lines.
- **G-5** (MUST): Preserve fidelity with Lean formal semantics: never over-simplify a statement to the point where it asserts something different from the
  Lean signature.

## Workflow

1. **Select Landmark**: Identify target theorem or definition from `@lean-formalization-breakdown`.
2. **Extract Dependencies**: Query `lean-lsp-mcp` or `dep_graph.sh` to obtain the transitive premise set.
3. **Draft Math Formulation**: Translate Lean types and hypotheses into standard mathematical notation ($L^2$, $H^s$, $\nabla \times u$).
4. **Decompose Proof Skeleton**: Identify the major intermediate lemmas (`have` milestones) and draft the narrative proof.
5. **Format Blueprint Block**: Write the LaTeX snippet with `\begin{theorem}[Name] \label{...} \lean{...} \uses{...} \leanok ... \end{theorem}`.
6. **Synthesize Zettel**: Emit permanent concept note or reference zettel for the knowledge garden.

## Recovery

- If an informal translation appears weaker or stronger than the formal Lean signature, re-check the exact binder and hypothesis types via
  `@lean-proof-review` before publishing the exposition.
- If dependency extraction is incomplete because `.ilean` artifacts are missing, run a targeted build via `@lean-build` first.

## Handoffs

- **Predecessors**: `skill:lean-formalization-breakdown`, `skill:lean-blueprint`
- **Successors**: `skill:lean-zettelkasten` (saving to knowledge graph), `skill:lean-doc-improvement` (documentation polishing).
- **Reference Catalog**: [`references/lean_to_math_exposition_patterns.md`](../protocols/lean_to_math_exposition_patterns.md)
