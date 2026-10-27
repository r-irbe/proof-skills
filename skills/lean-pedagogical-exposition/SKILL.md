---
name: "lean-pedagogical-exposition"
description: |
  USE FOR: translating Lean 4 formal proofs into human-readable textbook-grade mathematical descriptions.
  DO NOT USE FOR: closing open goals in Lean (@lean-proof).
  TRIGGERS: pedagogical-math, math-exposition, proof-narrative.
tier: "hot"
runtime_targets: [copilot-cli, claude-code, antigravity, pi, cursor, gemini-cli]
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
  - Converting proof scripts (towers of `have`, `calc`, `obtain`, `rcases`) into structured narrative proofs
  with clear
  motivation.
  - Authoring Lean Blueprint LaTeX chapters with `\begin{theorem}`, `\uses`, `\lean`, `\leanok`, and informal
  proof sketches.
  - Designing pedagogical diagrams, flowcharts, and intuition pumps for complex formal proofs.
  - Producing learning zettels and concept cards for the knowledge garden.
- **DO NOT USE FOR:**
## Workflow
1. **Select Landmark**: Identify target theorem or definition from `@lean-formalization-breakdown`.
2. **Extract Dependencies**: Query `lean-lsp-mcp` or `dep_graph.sh` to obtain the transitive premise set.
3. **Draft Math Formulation**: Translate Lean types and hypotheses into standard mathematical notation ($L^2$,
  $H^s$, $\nabla
  \times u$).
4. **Decompose Proof Skeleton**: Identify the major intermediate lemmas (`have` milestones) and draft the
  narrative proof.
5. **Format Blueprint Block**: Write the LaTeX snippet with `\begin{theorem}[Name] \label{...} \lean{...}
  \uses{...} \leanok ...
   \end{theorem}`.
6. **Synthesize Zettel**: Emit permanent concept note or reference zettel for the knowledge garden.
## Recovery & STOP
- If an informal translation appears weaker or stronger than the formal Lean signature, re-check the exact
  binder and hypothesis
  types via
  `@lean-proof-review` before publishing the exposition.
- If dependency extraction is incomplete because `.ilean` artifacts are missing, run a targeted build via
  `@lean-build` first.
## Handoffs
- **Predecessors**: `skill:lean-formalization-breakdown`, `skill:lean-blueprint`
- **Successors**: `skill:lean-zettelkasten` (saving to knowledge graph), `skill:lean-doc-improvement`
  (documentation polishing).
- **Reference Catalog**:
  [`references/lean_to_math_exposition_patterns.md`](../../references/lean_to_math_exposition_patterns.md)
## Detailed reference
Full encyclopedic reference, decision trees, and lookup tables live in
[`references/lean-pedagogical-exposition-handbook.md`](../../references/lean-pedagogical-exposition-handbook.md)
.
## See also
- [`../../references/lean-pedagogical-exposition-handbook.md`](../../references/lean-pedagogical-exposition-handbook.md)
  --
  Complete `lean-pedagogical-exposition` Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
