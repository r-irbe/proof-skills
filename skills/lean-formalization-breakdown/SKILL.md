---
name: "lean-formalization-breakdown"
description: |
  USE FOR: multi-wave architectural deconstruction of monumental Lean 4 codebases, static/kernel censuses, DAG topology & depth analysis, landmark theorem extraction, mathematical engine decomposition, substrate mapping, and dual-kernel verification audits.
  DO NOT USE FOR: authoring new Lean proofs (use @lean-proof), simple typo fixes (use @lean-doc-improvement).
  TRIGGERS: formalization-breakdown, proof-breakdown, census, landmark-dag, flt-breakdown, nse-breakdown, blowup-breakdown, lean-breakdown.
tier: "hot"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-blueprint"]
  successors: ["skill:lean-pedagogical-exposition", "skill:lean-zettelkasten", "skill:lean-enforcement"]
metadata:
  version: "0.1.0"
  source_spec: "references/formalization_breakdown_guide.md"
  last_reviewed: "2026-09-28"
---

# lean-formalization-breakdown

> Authoritative protocol for architectural deconstruction and multi-wave analysis
> of monumental Lean 4 formalizations (derived from the Fermat's Last Theorem
> 28-wave and Navier-Stokes & Euler 8-wave campaigns).

## Routing

- **USE FOR:**
  - Deconstructing monumental Lean 4 codebases (100 to 60,000+ modules) into structured, human-navigable mathematical layers.
  - Running automated static and kernel censuses (modules, lines, theorems, lemmas, definitions, structures, axioms, sorries).
  - Verifying import DAG topology, detecting cycles, computing topological layer depth and longest dependency paths.
  - Identifying landmark theorems, boundary adapters, and comparator challenge interfaces.
  - Decomposing mathematical proof engines into sequential multi-stage pipelines.
  - Mapping formal mathematical substrates into downstream packages and domain libraries.
  - Scaffolding master investigation plans, Lean Blueprint LaTeX outlines, and zettelkasten notes.
- **DO NOT USE FOR:**
  - Interactive tactic proof closing (use `@lean-proof`).
  - Small localized bugfixes or typo correction (use `@lean-doc-improvement`).
  - Simple git bisection across toolchains (use `@lean-bisect`).
- **TRIGGERS:** `formalization-breakdown`, `proof-breakdown`, `census`, `landmark-dag`, `flt-breakdown`, `nse-breakdown`.

## Behavioural Rules (G-*)

- **G-1** (MUST): Always run an automated static census (`scripts/lean/formalization_breakdown.py`) before formulating qualitative claims or estimates. Never cite declaration counts from memory or stale documentation.
- **G-2** (MUST): Verify strict Directed Acyclic Graph (DAG) topology. Report cycle violations immediately as hard blockers. Measure topological depth and identify the critical dependency path.
- **G-3** (MUST): Audit the complete axiom profile. Implementation modules must have zero `sorry` and rely exclusively on foundational Lean 4 axioms (`propext`, `Quot.sound`, `Classical.choice`). Any custom axiom must be flagged.
- **G-4** (MUST): Formulate the mathematical proof engine in a clear multi-stage architecture (e.g., Incompressible coordinate deformation -> Anisotropic packet scaling -> BKM logarithmic Gronwall reduction).
- **G-5** (MUST): Map extracted substrates into downstream modules using standardized proof templates and domain substitution tables (`subst_table.json`).
- **G-6** (MUST): Generate dual-kernel verification contracts and automated pytest / shell test gates for every transferred substrate.
- **G-7** (MUST): Preserve strict 7-bit ASCII throughout all generated documentation and markdown plans (INV-001). Mathematical symbols in markdown must use standard LaTeX math syntax (`$ ... $` or `$$ ... $$`).
- **G-8** (MUST): Resolve and verify all cited file paths against the physical filesystem before citing them (AOR-2 / INV-014).

## 8-Wave Deconstruction Workflow

```
+-----------------------------------------------------------------------------+
| Wave 1: Static Census & Macro Architecture                                  |
|   - scripts/lean/formalization_breakdown.py                                 |
|   - Module inventory, lines of code, declaration counts, DAG depth          |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Wave 2: Dual-Kernel Verification & Axiom Audit                              |
|   - Zero-sorry validation, comparator challenge verification                |
|   - Nanoda / independent kernel export check, permitted axioms whitelist    |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Wave 3: Landmark DAG & Critical Proof Path                                  |
|   - Identify terminal theorems (e.g. euler_singularity, breakdown_R3)       |
|   - Extract backward transitive dependency cones and intermediate milestones|
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Wave 4: Mathematical Engine Decomposition                                   |
|   - Isolate core mathematical innovations (Piola geometry, Gronwall, etc.)  |
|   - Structure 3-stage proof engine diagrams and formal theorem statements   |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Wave 5: Substrate Abstraction & Domain Transfer                             |
|   - Abstract specialized lemmas into reusable domain templates              |
|   - Deploy into target subpackages with clean lake compilation              |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Wave 6: Static AST Linter Rules                                             |
|   - Deploy ast-grep rules guarding against unanchored unfolding and drift   |
|   - Register rules in .pi-lens/rules/                                       |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Wave 7: Lean Blueprint & Pedagogical Exposition                             |
|   - Scaffold leanblueprint LaTeX structure with @[blueprint] alignment      |
|   - Hand off to @lean-pedagogical-exposition for human-readable math prose  |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Wave 8: Verification Gate & Knowledge Graph Ingestion                       |
|   - Pytest contract test suite, CI ladder integration                       |
|   - Zettelkasten permanent notes, MOC registration, Kuzu semantic graph     |
+-----------------------------------------------------------------------------+
```

## Tooling Commands

```bash
# 1. Run automated census and DAG topology analysis
python3 scripts/lean/formalization_breakdown.py <path/to/formalization>

# 2. Emit scaffolded master investigation plan
python3 scripts/lean/formalization_breakdown.py <path/to/formalization> --scaffold-plan -o docs/investigation-garden/plans/PLAN-<NAME>.md

# 3. Emit Lean Blueprint LaTeX skeleton
python3 scripts/lean/formalization_breakdown.py <path/to/formalization> --scaffold-blueprint -o blueprint/src/content.tex

# 4. Export JSON metrics for knowledge graph ingestion
python3 scripts/lean/formalization_breakdown.py <path/to/formalization> --format json -o breakdown-metrics.json
```

## Handoffs

- **Predecessors**: `agent:gateway`, `skill:lean-blueprint`
- **Successors**: `skill:lean-pedagogical-exposition` (human-readable math and pedagogical synthesis), `skill:lean-zettelkasten` (knowledge graph storage), `skill:lean-enforcement` (CI gate enforcement).
- **Source Guide**: [`references/formalization_breakdown_guide.md`](../../references/formalization_breakdown_guide.md)
