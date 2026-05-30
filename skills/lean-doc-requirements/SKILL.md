---
name: "lean-doc-requirements"
description: |
  USE FOR: Extract formal requirements from academic papers, technical reports, and design documents. Use when converting informal mathematical claims into Lean 4 theorem specifications. Covers claim extraction from LaTeX sources, equation identification, proposition mapping, hypothesis inference, and requirement traceability from document to formal specification.
  DO NOT USE FOR: paper update post-Lean (use @lean-doc-improvement); specification design (use @lean-specification); blueprint generation (use @lean-blueprint).
  TRIGGERS: doc requirements, requirement extraction, informal-to-Lean, claim extraction, paper-to-spec.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-specification', 'skill:lean-proof', 'skill:lean-zettelkasten']
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-doc-requirements/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# Lean 4 Document-to-Requirements

Extract formal specification requirements from informal documents (papers, reports, specs) and map them to Lean 4 theorem statements.

---

## Routing

- **USE FOR:** Extract formal requirements from academic papers, technical reports, and design documents. Use when converting informal mathematical claims into Lean 4 theorem specifications. Covers claim extraction from LaTeX sources, equation identification, proposition mapping, hypothesis inference, and requirement traceability from document to formal specification.
- **DO NOT USE FOR:** paper update post-Lean (use @lean-doc-improvement); specification design (use @lean-specification); blueprint generation (use @lean-blueprint).
- **TRIGGERS:** doc requirements, requirement extraction, informal-to-Lean, claim extraction, paper-to-spec.

## Workflow

1. Read the source document; identify each informal mathematical claim, its scope, and implicit assumptions.
2. Pick the requirement template from the body matching the claim class (definition, theorem, lemma, tactic-rule).
3. Produce a draft Lean specification (signature only, no proof) with traceability back to the source.
4. Hand off: to `@lean-specification` for the formal spec design, to `@lean-proof` for the proof, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the document is being updated FROM Lean — delegate to `@lean-doc-improvement`.
- STOP if claims are too vague to formalise — request HITL clarification.
- STOP if a project-level blueprint is needed — delegate to `@lean-blueprint`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-specification`, `skill:lean-proof`, `skill:lean-zettelkasten`.

---

## Detailed reference

Full content for `lean-doc-requirements` lives in
[`references/lean-doc-requirements-handbook.md`](../../references/lean-doc-requirements-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

| Section | Topic |
|---|---|
| Part 1 | Extraction Pipeline |
| Part 2 | Claim Extraction Protocol |
| Part 3 | Hypothesis Inference |
| Part 4 | Batch Extraction Workflow |
| Part 5 | Council Integration |
| Part 6 | Requirements Traceability |

---

## See also

- [`../../references/lean-doc-requirements-handbook.md`](../../references/lean-doc-requirements-handbook.md) — Full handbook (extracted from this skill)
- [`../lean-specification/SKILL.md`](../lean-specification/SKILL.md) — Successor
- [`../_overrides/lean-proof/SKILL.md`](../_overrides/lean-proof/SKILL.md) — Successor
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor
