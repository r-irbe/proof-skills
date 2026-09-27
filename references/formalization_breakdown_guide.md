# Formalization Breakdown Guide: Multi-Wave Archaeology, DAG Analysis, and Pedagogical Synthesis

<!-- Strict 7-bit ASCII only. Invariant per AGENTS.md (INV-001).
     Status: Authoritative Engineering Reference
     Authority: Systems Architecture Council / Formal Verification Lead
     Target Skills: lean-formalization-breakdown, lean-pedagogical-exposition, lean-blueprint -->

## 1. Overview and Operational Scope

This engineering reference establishes the canonical methodology for analyzing,
deconstructing, and synthesizing monumental Lean 4 formalizations (ranging from 100
modules to 60,000+ modules). The protocols documented here derive from our formal
investigations of:
1. The Fermat's Last Theorem formalization (60,475 modules, Anthropic PBC).
2. The Navier-Stokes & Euler finite-time blowup formalization (2,659 modules, OpenAI).

The objective of a formalization breakdown is threefold:
1. **Structural Truth**: Establishing an automated, machine-checked census of code lines,
   declarations, proof completeness (zero sorry), and foundational axiom dependency.
2. **Topological Navigation**: Mapping the import directed acyclic graph (DAG) to reveal
   critical dependency paths, topological layers, and landmark theorem hubs.
3. **Pedagogical and Substrate Extraction**: Translating formal types and proof scripts
   into human-readable mathematical narratives, interactive Lean Blueprints, and reusable
   substrates for downstream libraries.

---

## 2. The 8-Wave Deconstruction Protocol

Monumental codebases cannot be understood through ad-hoc inspection. Our protocol
executes eight sequential waves, each producing verified artifacts:

```
+-----------------------------------------------------------------------------+
| Wave 1: Automated Static Census and Physical Inventory                      |
|   Tool: scripts/lean/formalization_breakdown.py                             |
|   Outputs: Module counts, lines of code, theorems, defs, structures, sorries|
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Wave 2: Dual-Kernel Verification and Axiom Audit                            |
|   Tools: tools/verification/verify_comparator_protocol.sh, #print axioms   |
|   Checks: 0 sorry in implementation, Lean foundational axioms whitelist     |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Wave 3: Landmark DAG and Critical Dependency Path                           |
|   Metrics: Tarjan SCC cycle check, longest path, topological layer depth    |
|   Selection: Terminal theorems, boundary adapters, high-degree hubs         |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Wave 4: Three-Stage Mathematical Engine Decomposition                       |
|   Stage 1: Geometric setup, coordinate frames, algebraic invariants         |
|   Stage 2: Multi-scale concentration, scaling, asymptotic localization      |
|   Stage 3: Differential inequality, Gronwall reduction, contradiction       |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Wave 5: Substrate Abstraction and Downstream Transfer                       |
|   Mapping: Extract formal lemmas into clean domain packages                 |
|   Verification: lake build passes clean across all subpackages              |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Wave 6: Static AST Linter Rules                                             |
|   Rules: ast-grep patterns guarding unanchored unfolding and metric drift   |
|   Registration: .pi-lens/rules/                                             |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Wave 7: Lean Blueprint Generation and Mathematical Exposition               |
|   Scaffolding: Plastex blueprint with \begin{theorem}, \uses, \lean, \leanok|
|   Exposition: Textbook-grade mathematical descriptions without tactic noise |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Wave 8: Verification Gate Closeout and Knowledge Graph Ingestion            |
|   Gate: Automated pytest contract suite (100% assertions green)             |
|   Ingestion: Zettelkasten permanent notes, MOC registration, Kuzu graph     |
+-----------------------------------------------------------------------------+
```

---

## 3. Census and Graph Topology Metrics

A formalization breakdown must quantify four core topological dimensions:

### 3.1 Static Census
- **Code vs Non-Code Density**: Ratio of actual Lean code lines to comments and whitespace.
- **Declaration Taxonomy**: Distinguishing theorems and lemmas (asserted proofs) from
  definitions (`def`), structures, and typeclasses.
- **Typeclass Overhead**: Excessive typeclass instances cause exponential search slowdowns
  in large codebases. OpenAI's 2,659-module formalization achieved zero typeclasses by
  bundling properties into explicit structures (`structure ... : Prop`).

### 3.2 Topological Depth and Critical Path
- **DAG Acyclicity**: Verified using Tarjan's strongly connected components (SCC) algorithm.
  Any cycle constitutes an immediate fatal compilation defect.
- **Topological Layer Depth**: The maximum length of an internal import path from a leaf
  definition to the final top-level theorem.
  - FLT formalization: 49 layers across landmark theorems.
  - Navier-Stokes & Euler formalization: 96 layers.
- **Landmark Theorem Hubs**: Modules with high in-degree (frequently imported foundational
  results) or high out-degree (terminal synthesizers).

---

## 4. De-Formalization: Translating Lean to Human-Readable Mathematics

To create great learning materials, the formalization must be translated from
machine-checked terms into clear mathematical prose:

1. **Strip Tactic Scaffolding**: Eliminate operational commands (`simp only`, `rintro`,
   `linarith`, `ring`, `omega`). Focus on the mathematical identity being asserted.
2. **Standardize Mathematical Objects**:
   - `SmoothL2Field Space` -> $u \in C^\infty(\mathbb{R}^3) \cap L^2(\mathbb{R}^3)$.
   - `fderiv R A.field x` -> $\nabla u(x)$.
   - `vectorCurl A.field x` -> $\nabla \times u(x)$.
   - `divergence A.field x = 0` -> $\text{div}(u) = 0$.
3. **Structured Milestone Outlines**: Replace long proofs (> 50 lines) with a structured
   sequence of named intermediate lemmas corresponding to the major `have` and `obtain`
   milestones.

---

## 5. Lean Blueprint Integration

Patrick Massot's `leanblueprint` package provides the standard bridge between formal
Lean code and human-readable documentation:

- **Annotation**: Mark formal declarations with `@[blueprint]` in Lean 4.
- **Macro Pairing**: Every formal declaration maps to a corresponding LaTeX environment:
  ```latex
  \begin{theorem}[Beale-Kato-Majda Blowup]
  \label{thm:bkm-blowup}
  \uses{def:sobolev-space, lem:logarithmic-gradient}
  \lean{Euler.exists_compact_smooth_euler_singularity}
  \leanok
  There exists smooth compactly supported initial data on $\mathbb{R}^3$ with
  positive finite lifespan $T^* \in (0, 1]$ such that:
  \[
    \lim_{t \to T^*} \|u(\cdot, t)\|_{C^1} = \infty
    \quad\text{and}\quad
    \int_0^{T^*} \|\nabla \times u(\cdot, t)\|_{L^\infty} dt = \infty.
  \]
  \end{theorem}
  ```
- **Graph Generation**: `leanblueprint web` parses the `\uses{...}` directives to render
  the interactive dependency graph, color-coding verified nodes green (`\leanok`).
