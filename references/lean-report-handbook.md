---
title: "Blueprint-to-Report Pipeline Handbook (Lean 4)"
status: "reference"
extracted_from: "skills/lean-report/SKILL.md"
extracted_on: "2026-05-27"
scope: "Parts 1-11 (inputs/outputs, pipeline architecture, six pipeline stages INGEST → PLAN → NARRATE → ILLUSTRATE → ASSEMBLE → COMPILE, Lean 4.28 features, audit integration, project configuration, gateway integration). Parts 12-14 (execution checklist, troubleshooting, output artifacts summary) are kept inline in the SKILL.md as workflow + quick reference."
loader_hint: "Load when @lean-report routes here for pipeline details; not needed for the dispatch decision or one-off Part 12 execution."
---

# Blueprint-to-Report Pipeline Handbook (Lean 4)

> **Layering note.** This file holds the deep pipeline content previously
> embedded in [`skills/lean-report/SKILL.md`](../skills/lean-report/SKILL.md).
> The SKILL.md keeps the dispatch contract, the Execution Checklist (Part 12),
> the Troubleshooting table (Part 13), and the Output Artifacts summary (Part 14).
> This file holds the full encyclopaedia of pipeline stages, agent-driven
> narration rules, Lean 4.28 feature integration, audit hooks, and gateway
> wiring. Zero fidelity loss vs the pre-layering revision.

---

## Part 1 — Inputs and Outputs

### 1.1 Required Inputs (from SK-61 Blueprint Pipeline)

| Artifact | Location | Format |
|---|---|---|
| Extracted LaTeX node files | `.lake/build/blueprint/library/*.tex` | One `.tex` per module with `\leannode` blocks |
| Node metadata JSON | `.lake/build/blueprint/nodes.json` | JSON array of `{name, label, statement, status, deps}` |
| Blueprint web build | `blueprint/web/` | HTML with `dep_graph.html` |
| Blueprint source | `blueprint/src/content.tex` + `chapter_*.tex` | Authored chapter LaTeX |
| Coverage matrix | `docs/tracking/coverage_matrix.md` | Markdown table mapping paper claims → Lean theorems |
| Quality scores | Per-module quality reports from SK-39 | JSON or markdown |

### 1.2 Produced Outputs

| Artifact | Location | Format |
|---|---|---|
| LaTeX report source | `report/project-report.tex` | Standalone compilable LaTeX |
| Per-chapter files | `report/chapters/ch_*.tex` | One file per Project module |
| Front matter | `report/front/abstract.tex`, `report/front/intro.tex` | Abstract + introduction |
| Back matter | `report/back/appendix.tex`, `report/back/bibliography.bib` | Appendices + bibliography |
| Figures | `report/figures/` | TikZ source + pre-rendered PDF |
| Compiled PDF | `report/build/project-report.pdf` | Final document |

---

## Part 2 — Pipeline Architecture

The report generation pipeline has 6 stages:

```
┌───────────────────────────────────────────────────────────────────────────┐
│                    REPORT GENERATION PIPELINE                             │
│                                                                           │
│  Stage 1: INGEST     (load blueprint artifacts + JSON metadata)           │
│       │                                                                   │
│       ▼                                                                   │
│  Stage 2: PLAN       (outline report structure, assign chapter scope)     │
│       │                                                                   │
│       ▼                                                                   │
│  Stage 3: NARRATE    (generate natural language text per chapter)         │
│       │                                                                   │
│       ▼                                                                   │
│  Stage 4: ILLUSTRATE (generate TikZ figures, tables, dependency maps)    │
│       │                                                                   │
│       ▼                                                                   │
│  Stage 5: ASSEMBLE   (combine chapters + front/back matter into report)  │
│       │                                                                   │
│       ▼                                                                   │
│  Stage 6: COMPILE    (latexmk → PDF, verify cross-references)            │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Agent Topology: Pipeline with Fan-Out at NARRATE

```
Gateway (SK-07)
  │
  ├── INGEST ── Single agent (reads all blueprint artifacts)
  │     │
  │     ▼ (produces: report_plan.json with chapter outlines)
  │
  ├── PLAN ── Single agent (Research Synthesis Ε role)
  │     │     Assigns: scope, narrative arc, key results per chapter
  │     ▼ (produces: report_plan.json updated with section outlines)
  │
  ├── NARRATE ── 17 parallel chapter-writer agents (fan-out)
  │     │         Each agent:
  │     │         1. Reads blueprint nodes for its module
  │     │         2. Reads the module's Lean source for proof context
  │     │         3. Generates natural language exposition
  │     │         4. Embeds formal statements with surrounding prose
  │     ▼ (produces: report/chapters/ch_*.tex)
  │
  ├── ILLUSTRATE ── Single agent (generates all figures)
  │     │
  │     ▼ (produces: report/figures/*.tex, report/figures/*.pdf)
  │
  ├── ASSEMBLE ── Single agent (merges all chapters + matter)
  │     │
  │     ▼ (produces: report/project-report.tex)
  │
  └── COMPILE ── Terminal command (latexmk)
        │
        ▼ (produces: report/build/project-report.pdf)
```

### 2.2 Skill Integration Map

| Stage | Primary Skill | Supporting Skills | Feedback To |
|---|---|---|---|
| INGEST | lean-blueprint (SK-61) | lean-enforcement (SK-36) | Validates artifacts exist |
| PLAN | research-synthesis-engine (SK-60) | lean-specification (SK-05), lean-doc-requirements (SK-09) | report_plan.json |
| NARRATE | lean-report (SK-62, this skill) | Domain skills (SK-12..21), lean-doc-improvement (SK-10) | chapter files |
| ILLUSTRATE | lean-report (SK-62) | lean-quality-engine (SK-39) | figures |
| ASSEMBLE | lean-report (SK-62) | lean-doc-improvement (SK-10) | merged document |
| COMPILE | lean-enforcement (SK-36) | — | build logs |

---

## Part 3 — Stage 1: INGEST

### 3.1 Blueprint Artifact Loading

```python
# Pseudocode for ingestion
def ingest_blueprint():
    # 1. Load all extracted LaTeX nodes
    nodes = {}
    for tex_file in glob(".lake/build/blueprint/library/Project.*.tex"):
        module_name = extract_module_name(tex_file)
        nodes[module_name] = parse_lean_nodes(tex_file)

    # 2. Load JSON metadata (if available)
    if exists(".lake/build/blueprint/nodes.json"):
        metadata = json.load(open(".lake/build/blueprint/nodes.json"))
    else:
        metadata = infer_metadata_from_tex(nodes)

    # 3. Load dependency graph
    dep_graph = extract_dependency_graph(metadata)

    # 4. Load coverage matrix
    coverage = parse_coverage_matrix("docs/tracking/coverage_matrix.md")

    # 5. Load quality scores
    quality = load_quality_scores()

    return ReportContext(nodes, metadata, dep_graph, coverage, quality)
```

### 3.2 Node Classification

Each blueprint node is classified for report treatment:

| Node Kind | Report Treatment |
|---|---|
| `structure` / `inductive` | Full formal definition + prose explanation |
| Key `def` (appears in paper) | Definition box + motivation paragraph |
| Internal `def` (helper) | Mentioned in narrative, not boxed |
| Main theorem (paper claim) | Theorem box + proof sketch + significance |
| Bridge theorem (cross-module) | Theorem box + connection narrative |
| `@[simp]` lemma | Listed in module summary, brief note |
| Instance (Decidable, etc.) | Mentioned in "computing with" subsection |
| Tactic / automation | Described in methodology chapter |

### 3.3 Dependency Graph Extraction

Build a directed graph `G = (V, E)` where:
- `V` = blueprint nodes
- `E` = dependency edges (from `uses`, `proofUses`, auto-inferred)

Compute:
- **Topological sort** → chapter ordering
- **Connected components** → functional groups within a chapter
- **Critical path** → the longest dependency chain (highlighted in report)
- **Fan-in / fan-out hubs** → most-depended-upon theorems (featured prominently)

---

## Part 4 — Stage 2: PLAN

### 4.1 Report Outline Template

```
Project Formal Verification Report
═════════════════════════════════

Front Matter:
  - Abstract (auto-generated from project overview + metrics)
  - Table of Contents
  - List of Definitions, Theorems, and Lemmas
  - Notation Table

Part I — Foundations
  Ch 1: Mathematical Preliminaries (Tactics.lean)
  Ch 2: Quality Gate Formalization (QualityGates.lean)
  Ch 3: Phase Classification (PhaseClassification.lean)

Part II — Core Models
  Ch 4: Collins Category Vector (CCVGating.lean)
  Ch 5: Cusp Catastrophe Model (CuspCatastrophe.lean)
  Ch 6: Phase Portrait Dynamics (PhasePortrait.lean)
  Ch 7: Provenance Chain (ProvenanceChain.lean)

Part III — Adaptive Infrastructure
  Ch 8: Pipeline Adaptation (PipelineAdaptive.lean)
  Ch 9: Stochastic CCV Core (StochasticCCV/Core.lean)
  Ch 10: Stochastic CCV Information Theory (StochasticCCV/Information.lean)
  Ch 11: Pipeline Bypass Semantics (PipelineBypass.lean)

Part IV — Agent Governance
  Ch 12: Reinforcement Learning (ReinforcementLearning.lean)
  Ch 13: Agentic Safety Core (AgenticSafety/Core.lean)
  Ch 14: Agentic Safety Consensus (AgenticSafety/Consensus.lean)
  Ch 15: Agentic Safety Gaps (AgenticSafety/Gaps.lean)

Part V — Convergence Theory
  Ch 16: Lyapunov Stability Analysis (LyapunovStability.lean)
  Ch 17: CCVE Contraction (CCVEContraction.lean)

Part VI — Evaluation & Feedback
  Ch 18: Evaluation Gaps (EvaluationGaps.lean)
  Ch 19: Feedback Semantics (FeedbackSemantics.lean)

Note: Several modules have been split into subdirectories:
  - AgenticSafety → Core/, Consensus/, Gaps/
  - StochasticCCV → Core/, Information/
  The chapter outline reflects these splits as separate chapters.

Back Matter:
  - Appendix A: Full Theorem Index with Status
  - Appendix B: Dependency Graph (full)
  - Appendix C: Formalization Metrics Summary
  - Appendix D: Tool Chain and Build Configuration
  - Bibliography
```

### 4.2 Chapter Scope Assignment

Each chapter is assigned:

```json
{
  "chapter": 12,
  "module": "Project.LyapunovStability",
  "title": "Lyapunov Stability Analysis",
  "sections": [
    {
      "heading": "Quadratic Lyapunov Function",
      "nodes": ["def:lyap-phasepoint", "def:lyap-lyapunov-quadratic",
                "thm:lyap-zero-at-eq", "thm:lyap-pos-def"],
      "narrative_arc": "Introduce V(φ) as squared distance, prove positive definiteness"
    },
    {
      "heading": "Governance Orbit Convergence",
      "nodes": ["def:lyap-governance-orbit", "thm:lyap-exponential-decay",
                "thm:lyap-governance-convergence"],
      "narrative_arc": "Show orbit contracts geometrically, prove convergence to equilibrium"
    }
  ],
  "key_results": ["governance_convergence", "lyapunov_component_bound"],
  "connections_to": ["PhasePortrait (phase space)", "CuspCatastrophe (cusp Lyapunov)",
                     "RL (reward shaping)", "AgenticSafety (safety bounds)"]
}
```

### 4.3 Narrative Arc per Part

| Part | Narrative Arc |
|---|---|
| I — Foundations | Set up the mathematical stage: what are quality gates, how do we classify knowledge phases, what automation do we use? |
| II — Core Models | Construct the building blocks: how expert knowledge is categorized, how stress creates catastrophe, how the phase portrait captures system state |
| III — Infrastructure | Show how the system adapts: pipeline thresholds shift with phases, CCV drifts stochastically toward stationarity |
| IV — Governance | Introduce agency: MDP-based decision-making, trust envelopes, safety bounds |
| V — Convergence | Tie it all together: the entire system converges under Lyapunov analysis |

---

## Part 5 — Stage 3: NARRATE

### 5.1 Natural Language Generation Rules

Each chapter-writer agent follows these rules:

**R1 — Audience**: Write for a mathematically literate reader who may not know Lean 4. All Lean-specific syntax must be translated to standard mathematical notation.

**R2 — Definition introduction pattern**:
```latex
\begin{definition}[{name}]\label{def:label}
  {Natural language statement using standard math notation.}
\end{definition}

{1-2 paragraphs explaining motivation, intuition, and relationship
to preceding definitions. Include domain context (what this means
for knowledge transfer in the public sector).}
```

**R3 — Theorem presentation pattern**:
```latex
\begin{theorem}[{name}]\label{thm:label}
  {Natural language statement of the mathematical claim.}
\end{theorem}

\begin{proof}[Proof sketch]
  {High-level proof strategy in natural language. Reference
  key lemmas by \cref. Do NOT reproduce full Lean tactic
  scripts — instead describe the mathematical argument.}
\end{proof}

{1 paragraph explaining significance: why this result matters,
what it guarantees for the system, how it connects to other
chapters.}
```

**R4 — Lean-to-LaTeX Translation Table**:

| Lean | LaTeX |
|---|---|
| `Nat` | $\mathbb{N}$ |
| `Int` | $\mathbb{Z}$ |
| `ℝ` (noncomputable) | $\mathbb{R}$ |
| `Fin n` | $\{0, 1, \ldots, n-1\}$ |
| `× 100` scaling | Convert back: $q/100$ or state "$q$ (scaled $\times 100$)" |
| `Bool` | true/false (state semantics in context) |
| `structure` | Define as a tuple or record type |
| `∀ (x : T), P x` | For all $x \in T$, $P(x)$ holds |
| `∃ (x : T), P x` | There exists $x \in T$ such that $P(x)$ |
| `h₁ ∧ h₂` | $h_1$ and $h_2$ |
| `h₁ ∨ h₂` | $h_1$ or $h_2$ |
| `h₁ → h₂` | If $h_1$ then $h_2$ |
| `h₁ ↔ h₂` | $h_1$ if and only if $h_2$ |
| `¬ P` | $\lnot P$ |
| `a ≤ b` | $a \leq b$ |
| `a < b` | $a < b$ |
| `Set.Icc a b` | $[a, b]$ |
| `List T` | A finite sequence of elements in $T$ |
| `Decidable` | Computationally decidable |
| `@[simp]` | (Omit from report — internal automation detail) |
| `grind` | "by automated SMT-based reasoning" |
| `fun_prop` | "by function property inference (continuity, measurability)" |
| `push_cast` | "by coercion normalization" |
| `field_simp` | "by field-algebraic simplification" |
| `native_decide` | "by compiled finite-domain computation" |
| `ContractingWith K f` | "$f$ is a $K$-Lipschitz contraction ($K < 1$)" |
| `NNReal` / `ℝ≥0` | "$\mathbb{R}_{\geq 0}$" |

**R5 — Nat-scaled arithmetic convention**: The Project formalization uses `Nat` scaled by 100 (or 10000) to avoid noncomputable reals. The report must:
1. State this convention once in the Preliminaries chapter
2. Convert back to real-valued notation in theorem statements
3. Note where the scaling introduces floor/ceiling effects
4. Use the notation "$q_{100} = \lfloor 100q \rfloor$" for explicit scaled values

**R6 — Proof sketch depth**: Provide enough detail that a reader could reconstruct the proof in a different theorem prover, but do not include Lean-specific tactic names. Map:

| Lean Tactic | Report Language |
|---|---|
| `simp` / `simp_all` | "simplifies by definitional equalities" |
| `omega` | "by linear arithmetic over integers" |
| `nlinarith` | "by nonlinear arithmetic" |
| `linarith` | "by linear arithmetic" |
| `ring` | "by the ring axioms" |
| `positivity` | "since all terms are non-negative" |
| `decide` | "by exhaustive case analysis (finite domain)" |
| `cases` | "by case analysis on ..." |
| `induction` | "by structural induction on ..." |
| `constructor` | "we prove each direction separately" (for ↔) |
| `unfold` | "expanding the definition of ..." |
| `norm_num` | "by numerical computation" |
| `aesop` | "by automated reasoning" |
| `grind` | "by automated SMT-based reasoning (primary tactic, 776 uses)" |
| `native_decide` | "by compiled finite-domain computation (68 uses)" |
| `fun_prop` | "by function property inference" |
| `push_cast` | "by coercion normalization" |
| `field_simp` | "by field-algebraic simplification" |

**R7 — Cross-references**: Every theorem that appears in the blueprint with a `\lean{name}` declaration should have:
- A `\label{thm:prefix-short-name}` for internal cross-referencing
- A margin note: `\marginpar{\texttt{name} {\footnotesize (Module.lean:L$n$)}}`
- A hyperlink to the blueprint web version (if deployed)

**R8 — No fabrication**: Every mathematical statement in the report MUST correspond to a proven theorem in Lean (no `sorry`). If a result is only conjectured, label it explicitly as a conjecture.

### 5.2 Chapter Template

```latex
% report/chapters/ch_12_lyapunov.tex
\chapter{Lyapunov Stability Analysis}\label{ch:lyapunov}

This chapter formalizes stability analysis for the project Knowledge
Phase Portrait. We construct a quadratic Lyapunov function
$V\colon \mathcal{P} \times \mathcal{P} \to \mathbb{R}_{\geq 0}$
on the four-dimensional phase space $\mathcal{P} = (R, D, C, V)$
and prove that the governance orbit converges exponentially to
the equilibrium $\phi^*$ under contraction ($\alpha \in [0,1)$).

The results in this chapter depend on the phase space structure
(\cref{ch:phaseportrait}), the cusp catastrophe model
(\cref{ch:cusp}), the MDP governance policy
(\cref{ch:rl}), and the agentic safety framework
(\cref{ch:agenticsafety}).

\section{The Phase Space}\label{sec:lyap-phase-space}

\begin{definition}[Phase Point]\label{def:lyap-phasepoint}
  A \emph{phase point} $\phi = (R, D, C, V) \in \mathbb{N}^4$ is
  a four-tuple of non-negative integer-valued coordinates
  representing the knowledge state along four dimensions:
  Richness ($R$), Diversity ($D$), Coherence ($C$), and
  Volatility ($V$).
\end{definition}
\marginpar{\texttt{PhasePoint} {\footnotesize (LyapunovStability.lean:L56)}}

The coordinates are Nat-scaled by $\times 100$ from their real-valued
counterparts (see \cref{sec:scaling-convention}).

\section{Quadratic Lyapunov Function}\label{sec:lyap-quadratic}

\begin{definition}[Quadratic Lyapunov Function]\label{def:lyap-V}
  For phase points $\phi, \phi^* \in \mathcal{P}$, the
  \emph{quadratic Lyapunov function} is
  \[
    V(\phi, \phi^*) \;=\;
      (R - R^*)^2 + (D - D^*)^2 + (C - C^*)^2 + (V_0 - V_0^*)^2
  \]
  where $(R^*, D^*, C^*, V_0^*)$ are the equilibrium coordinates.
\end{definition}
\marginpar{\texttt{lyapunovQuadratic} {\footnotesize (LyapunovStability.lean:L62)}}

This is the squared Euclidean distance in $\mathbb{N}^4$, serving
as an energy function that is zero exactly at equilibrium and
positive elsewhere.

\begin{theorem}[Positive Definiteness]\label{thm:lyap-pos-def}
  $V(\phi, \phi^*) = 0$ if and only if $\phi = \phi^*$
  (coordinate-wise equality).
\end{theorem}
\marginpar{\texttt{lyapunovQuadratic\_eq\_zero\_iff} {\footnotesize (LyapunovStability.lean:L108)}}

\begin{proof}[Proof sketch]
  Forward: if $V = 0$, then each squared difference
  $(R - R^*)^2 = 0$, etc., forcing coordinate-wise equality
  since squares of integers vanish only at zero.
  Backward: substituting $\phi = \phi^*$ yields
  $V = 0 + 0 + 0 + 0 = 0$ by direct computation.
\end{proof}

% ... [continues with remaining sections]
```

### 5.3 Narrative Connectors

Between sections, use transition paragraphs that explain the mathematical story:

| Transition Type | Template |
|---|---|
| Definition → Theorem | "With $X$ defined, we can now establish its key properties." |
| Theorem → Corollary | "An immediate consequence of \cref{thm:X} is:" |
| Section → Section | "Having established $X$, we turn to $Y$, which extends the analysis to ..." |
| Chapter → Chapter | "The constructions in this chapter provide the foundation for $Y$ (\cref{ch:next}), where we ..." |
| Module bridge | "This result connects to the $X$ framework (established in \cref{ch:other}), via the bridge theorem:" |

### 5.4 Domain Context Integration

For each key result, include a paragraph contextualizing it within the project application domain:

```latex
\begin{remark}[Application context]
  In the tacit knowledge transfer setting, \cref{thm:lyap-convergence}
  guarantees that the governance agent's policy drives the knowledge
  system toward a target operating point. Practically, this means
  that as the agent applies its MDP-derived actions, the knowledge
  pipeline's quality metrics converge to their desired values,
  regardless of the initial knowledge state — provided the
  contraction parameter $\alpha$ satisfies $0 \leq \alpha < 1$.
\end{remark}
```

---

## Part 5B — Lean 4.28 Features for Report Generation

The Project formalization uses Lean v4.28.0 and Mathlib v4.28.0. Report narration should acknowledge the following Lean 4.28 features that heavily influence proof style:

### 5B.1 `grind` — Primary Tactic (776 uses)

`grind` is now the dominant proof-closing tactic in the codebase (776 uses, up from ~30 in earlier versions). It combines congruence closure, E-matching, and case splitting into an SMT-style decision procedure. Report prose should translate `grind` as "by automated SMT-based reasoning" rather than enumerating sub-steps.

Variants used in the codebase:
| Annotation | Meaning | Report Translation |
|---|---|---|
| `@[grind =]` | Register equality lemma | (omit — internal automation) |
| `@[grind →]` | Register forward-chaining rule | (omit — internal automation) |
| `@[grind ←]` | Register backward-chaining rule | (omit — internal automation) |
| `@[grind norm]` | Register normalization simp lemma | (omit — internal automation) |
| `@[grind unfold]` | Register definition for unfolding | (omit — internal automation) |

### 5B.2 `native_decide` — Compiled Finite Computation (68 uses)

Used for large finite-domain decidability proofs where `decide` would timeout. Compiles the decision procedure to native code. Report prose: "by compiled finite-domain computation."

### 5B.3 Module System Features

- Module system is no longer experimental in Lean 4.28
- `assert_not_exists` / `assert_not_imported` used for dependency hygiene — ensures modules do not accidentally pull in heavy dependencies
- `lake shake` available for unused import detection (report should note if run during CI)

### 5B.4 `first_par` (Parser Exists, Not Yet Implemented)

The `first_par` combinator has a parser but no runtime implementation in Lean 4.28. Do not reference it as a parallelism feature in the report.

---

## Part 6 — Stage 4: ILLUSTRATE

### 6.1 Required Figures

| Figure | Source | Technique | Location |
|---|---|---|---|
| Module dependency DAG | `nodes.json` + imports | TikZ `graph` | Introduction |
| Theorem dependency graph (full) | Blueprint `dep_graph.html` | Dot → TikZ via `dot2tex` | Appendix B |
| Per-chapter mini-DAG | Subgraph of full DAG | TikZ | Each chapter opening |
| CCV simplex | CCVGating definitions | TikZ ternary plot | Ch 4 |
| Phase portrait regions | PhaseClassification boundaries | TikZ | Ch 3 / Ch 6 |
| Cusp catastrophe surface | CuspCatastrophe potential | PGFPlots 3D | Ch 5 |
| Governance orbit convergence | LyapunovStability orbit | PGFPlots 2D | Ch 12 |
| Coverage heatmap | `coverage_matrix.md` | TikZ matrix | Appendix A |
| Quality score spider chart | Quality engine scores | PGFPlots radar | Appendix C |

### 6.2 Module Dependency DAG (TikZ)

```latex
% report/figures/module_dag.tex
\begin{tikzpicture}[
  module/.style={draw, rounded corners, minimum width=2.8cm,
                 minimum height=0.7cm, font=\small},
  dep/.style={-stealth, thick},
  foundation/.style={module, fill=blue!10},
  core/.style={module, fill=green!10},
  infra/.style={module, fill=orange!10},
  govern/.style={module, fill=red!10},
  converge/.style={module, fill=purple!10}
]
  % Layer 0: Foundation
  \node[foundation] (tac) at (0,0) {Tactics};

  % Layer 1: Base models
  \node[foundation] (qg)  at (-3,-1.5) {QualityGates};
  \node[foundation] (pc)  at (0,-1.5) {PhaseClassif.};

  % Layer 2: Core
  \node[core] (ccv)  at (-4,-3) {CCVGating};
  \node[core] (pp)   at (-1,-3) {PhasePortrait};
  \node[core] (prov) at (2,-3)  {Provenance};
  \node[core] (cusp) at (5,-3)  {CuspCatastrophe};

  % Layer 3: Infrastructure
  \node[infra] (pa)   at (-3,-4.5) {PipelineAdaptive};
  \node[infra] (sccv) at (1,-4.5)  {StochasticCCV};

  % Layer 4: Governance
  \node[govern] (rl) at (-2,-6) {RL};
  \node[govern] (as) at (2,-6)  {AgenticSafety};

  % Layer 5: Convergence
  \node[converge] (lyap) at (0,-7.5) {LyapunovStability};

  % Edges (selected key imports)
  \draw[dep] (tac) -- (qg);
  \draw[dep] (tac) -- (pc);
  \draw[dep] (qg) -- (ccv);
  \draw[dep] (pc) -- (pp);
  \draw[dep] (qg) -- (pp);
  \draw[dep] (tac) -- (prov);
  \draw[dep] (tac) -- (cusp);
  \draw[dep] (ccv) -- (pa);
  \draw[dep] (pc) -- (pa);
  \draw[dep] (cusp) -- (pa);
  \draw[dep] (ccv) -- (sccv);
  \draw[dep] (pc) -- (rl);
  \draw[dep] (qg) -- (rl);
  \draw[dep] (ccv) -- (as);
  \draw[dep] (qg) -- (as);
  \draw[dep] (pp) -- (lyap);
  \draw[dep] (cusp) -- (lyap);
  \draw[dep] (rl) -- (lyap);
  \draw[dep] (as) -- (lyap);
\end{tikzpicture}
```

### 6.3 Coverage Heatmap

```latex
% Auto-generated from coverage_matrix.md
\begin{figure}[htbp]
\centering
\begin{tikzpicture}[
  cell/.style={minimum width=1.2cm, minimum height=0.6cm, font=\tiny},
  covered/.style={cell, fill=green!30},
  partial/.style={cell, fill=yellow!30},
  missing/.style={cell, fill=red!20}
]
  % Generated programmatically:
  % rows = paper claims, cols = modules
  % color = formalization status
\end{tikzpicture}
\caption{Coverage heatmap: paper claims (rows) vs.\ Lean modules
  (columns). Green = fully formalized, yellow = partial,
  red = not yet covered.}
\label{fig:coverage-heatmap}
\end{figure}
```

### 6.4 Figure Generation Command

```bash
# Convert dot dependency graph to TikZ:
dot2tex --figonly --format tikz blueprint/web/dep_graph.dot \
  > report/figures/dep_graph_full.tex

# Or generate from JSON:
python3 scripts/blueprint_to_tikz.py \
  --input .lake/build/blueprint/nodes.json \
  --output report/figures/
```

---

## Part 7 — Stage 5: ASSEMBLE

### 7.1 Master Document Structure

```latex
% report/project-report.tex
\documentclass[11pt,a4paper,twoside]{report}

%% ── Packages ────────────────────────────────────────────────
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath,amssymb,amsthm}
\usepackage{mathtools}
\usepackage{thmtools}
\usepackage{tikz}
\usetikzlibrary{arrows.meta, positioning, calc, graphs, shapes}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{hyperref}
\usepackage{cleveref}
\usepackage{marginnote}
\usepackage{xcolor}
\usepackage{listings}           % for Lean code snippets (rare)
\usepackage{environ}            % for proof environments
\usepackage[backend=biber]{biblatex}
\addbibresource{back/bibliography.bib}

%% ── Theorem Environments ────────────────────────────────────
\declaretheorem[numberwithin=chapter]{theorem}
\declaretheorem[sibling=theorem]{lemma}
\declaretheorem[sibling=theorem]{proposition}
\declaretheorem[sibling=theorem]{corollary}
\declaretheorem[style=definition, sibling=theorem]{definition}
\declaretheorem[style=remark, numbered=no]{remark}

%% ── Custom Commands ─────────────────────────────────────────
\input{macros/common}

%% ── Lean Reference Margin Note ──────────────────────────────
\newcommand{\leanref}[2]{%
  \marginpar{\texttt{#1} {\scriptsize (#2)}}%
}

%% ── Metadata ────────────────────────────────────────────────
\title{%
  Project: Formal Verification of a Knowledge Phase-Adaptive
  Governance Framework in Lean~4 \\[6pt]
  \large A Machine-Checked Mathematical Report
}
\author{Generated from Lean 4 Formalization \\ via SK-62 Report Pipeline}
\date{\today}

%% ── Document ────────────────────────────────────────────────
\begin{document}

\maketitle
\input{front/abstract}
\tableofcontents
\listoftheorems[title={List of Definitions and Theorems}]

%% Part I — Foundations
\part{Foundations}
\input{chapters/ch_01_tactics}
\input{chapters/ch_02_qualitygates}
\input{chapters/ch_03_phaseclassification}

%% Part II — Core Models
\part{Core Models}
\input{chapters/ch_04_ccvgating}
\input{chapters/ch_05_cuspcatastrophe}
\input{chapters/ch_06_phaseportrait}
\input{chapters/ch_07_provenancechain}

%% Part III — Adaptive Infrastructure
\part{Adaptive Infrastructure}
\input{chapters/ch_08_pipelineadaptive}
\input{chapters/ch_09_stochasticccv_core}
\input{chapters/ch_10_stochasticccv_information}
\input{chapters/ch_11_pipelinebypass}

%% Part IV — Agent Governance
\part{Agent Governance}
\input{chapters/ch_12_reinforcementlearning}
\input{chapters/ch_13_agenticsafety_core}
\input{chapters/ch_14_agenticsafety_consensus}
\input{chapters/ch_15_agenticsafety_gaps}

%% Part V — Convergence Theory
\part{Convergence Theory}
\input{chapters/ch_16_lyapunov}
\input{chapters/ch_17_ccvecontraction}

%% Part VI — Evaluation & Feedback
\part{Evaluation and Feedback}
\input{chapters/ch_18_evaluationgaps}
\input{chapters/ch_19_feedbacksemantics}

%% Appendices
\appendix
\input{back/appendix_A_theorem_index}
\input{back/appendix_B_dep_graph}
\input{back/appendix_C_metrics}
\input{back/appendix_D_toolchain}

\printbibliography
\end{document}
```

### 7.2 Shared Macros

```latex
% report/macros/common.tex

% Phase space
\newcommand{\phasepoint}{\phi}
\newcommand{\phaseeq}{\phi^*}
\newcommand{\phasespace}{\mathcal{P}}
\newcommand{\lyapV}{V}

% CCV
\newcommand{\ccvphi}{\varphi_{\mathrm{CCV}}}
\newcommand{\ccvr}{r}
\newcommand{\ccvs}{s}
\newcommand{\ccvk}{k}

% Stochastic
\newcommand{\stresssq}{\sigma^2}
\newcommand{\stochM}{\mathbf{M}}

% MDP
\newcommand{\govaction}{\mathbf{a}}
\newcommand{\valueV}{V^{\pi}}
\newcommand{\bellmanop}{\mathcal{B}_{\pi}}

% Quality gates
\newcommand{\gate}[1]{\mathrm{G}_{#1}}

% Scaling
\newcommand{\scaled}[1]{#1_{100}}
\newcommand{\bscaled}[1]{#1_{10000}}

% Status indicators (for appendix tables)
\newcommand{\proved}{\textcolor{green!60!black}{\checkmark}}
\newcommand{\sorrymark}{\textcolor{red}{\texttimes}}
\newcommand{\partialmark}{\textcolor{orange!80!black}{$\sim$}}

% Lean reference formatting
\newcommand{\leanname}[1]{\texttt{#1}}
```

### 7.3 Abstract Template

```latex
% report/front/abstract.tex
\begin{abstract}
This report presents a machine-checked formalization of the
Project (Experience, Articulation, Structuring, Consolidation,
Innovation) framework for knowledge phase-adaptive governance.
The formalization comprises \textbf{31} Lean~4 files across
\textbf{17} logical modules totaling \textbf{37,693} lines of
code, containing \textbf{2,186} theorems and lemmas,
all verified by the Lean~4 kernel (v4.28.0) with \textbf{zero}
uses of \texttt{sorry} and \textbf{zero} custom axioms beyond
those in Mathlib~v4.28.0.

The framework models organizational knowledge transfer through
seven interlocking components: (1)~quality gates controlling
information flow, (2)~phase classification via stress-driven
regime detection, (3)~Collins Category Vector (CCV) gating for
domain-aware filtering, (4)~cusp catastrophe theory for modeling
regime transitions, (5)~Doeblin contraction and stochastic CCV
convergence to stationary distributions, (6)~an end-to-end L1
contraction bridge (\texttt{okdStep\_L1\_contraction}) connecting
pipeline steps to distributional convergence, and (7)~BFT
consensus for multi-agent safety governance.

Key results include: monotonicity of quality gates under CCV
modulation, completeness of the three-regime phase classification,
exponential convergence of the governance orbit under contraction
mapping, Bellman operator monotonicity for the MDP-based
governance policy, safety envelope decomposition for agentic
trust management, and PROV-O provenance formalization ensuring
chain-of-custody invariants for knowledge artifacts.

All proofs are constructive where possible and use Mathlib~v4.28.0
as the mathematical library. A navigable dependency graph and
interactive web blueprint accompany this report.

\medskip\noindent
\textbf{Keywords:} Formal verification, Lean~4, knowledge management,
phase-adaptive governance, Lyapunov stability, cusp catastrophe,
reinforcement learning, safety envelopes.
\end{abstract}
```

---

## Part 8 — Stage 6: COMPILE

### 8.1 Build Commands

```bash
# Navigate to report directory
cd report/

# Full build with bibliography:
latexmk -pdf -interaction=nonstopmode project-report.tex

# Quick build (no bibliography):
pdflatex project-report.tex

# Clean intermediate files:
latexmk -c
```

### 8.2 CI Integration

```yaml
# .github/workflows/report.yml
name: Build Report
on:
  push:
    branches: [release/beta, main]
    paths:
      - 'report/**'
      - 'Project/**'

jobs:
  report:
    runs-on: ubuntu-latest
    env:
      LEAN_THREAD_STACK_SIZE: "33554432"
      LEAN_MAX_MEMORY: "4294967296"
    steps:
      - uses: actions/checkout@v4

      - name: Setup Lean
        uses: leanprover/lean-action@v1

      - name: Fetch Mathlib cache
        run: lake exe cache get

      - name: Build Lean project
        run: lake build -j$(nproc)

      - name: Install TeX Live
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            texlive-full biber latexmk

      - name: Build report
        run: |
          cd docs/project/lean/report
          latexmk -pdf -interaction=nonstopmode project-report.tex

      - name: Upload PDF artifact
        uses: actions/upload-artifact@v4
        with:
          name: project-report
          path: docs/project/lean/report/build/project-report.pdf
```

### 8.3 Validation Checks

| Check | Command | Pass Criterion |
|---|---|---|
| LaTeX compiles | `latexmk -pdf` | Exit 0 |
| No undefined references | `grep -c 'undefined' project-report.log` | 0 |
| No missing citations | `grep -c 'Citation.*undefined' project-report.log` | 0 |
| All cross-refs resolve | `grep -c 'multiply defined' project-report.log` | 0 |
| Theorem count matches Lean | Compare list-of-theorems vs Lean `grep` count | Within 5% |
| PDF page count reasonable | `pdfinfo project-report.pdf` | 50–200 pages expected |
| No sorry-marked theorems | `grep -c '\\sorrymark' project-report.tex` | 0 |

---

## Part 9 — Audit Integration

The report must incorporate findings from the comprehensive Project codebase audit. The following audit artifacts should be referenced and their findings reflected in the report narrative.

### 9.1 Audit Reference Documents

| Document | Content | Report Integration |
|---|---|---|
| `RECOMMENDATIONS-V3-FINAL.md` | 66 recommendations across all modules | Acknowledge addressed items; flag open items in appendix |
| `STATISTICS-RECONCILIATION.md` | Verified codebase metrics (31 files, 37,693 lines, 2,186 theorems) | Use as authoritative source for all statistics |
| `IMPLEMENTATION-SEQUENCE.md` | 6-phase implementation plan | Reference in "Future Work" section |

### 9.2 P0 Critical Items (Must Acknowledge in Report)

The report MUST explicitly acknowledge these four critical findings:

1. **Perron-Frobenius existence gap**: Uniqueness of the stationary distribution is proved, but existence is assumed (via `Inhabited` instance). The report should state: "We prove uniqueness of the stationary distribution; existence is assumed as a hypothesis and represents a formalization gap to be closed with a constructive Perron-Frobenius proof."

2. **Lyapunov bridge scope**: The Lyapunov stability analysis applies to the affine `govStep` function, not the full Project dynamics. The report should clarify: "The convergence guarantee applies to the linearized governance step; extending to the full nonlinear Project dynamics remains future work."

3. **`classifyFull` catch-all**: The current `classifyFull` function uses a catch-all `| _ =>` branch. The report should note the recommended migration to `classifyFullStrict` with exhaustive pattern matching. Do not present the classifier as total without this caveat.

4. **Remove 92.3% suitability figure**: This figure appeared in earlier drafts but has no formal backing. The report must NOT cite it.

### 9.3 Semantic Fidelity Caveats

The following semantic caveats must be noted in the relevant chapters:

- **CCV simplex is the project's operationalization** (CN-7): The CCV simplex formalized here is the project's operationalization of Collins' Category Vector, not Collins' original construction. State this clearly in Ch 4.
- **phiCCV excludes somatic tacit knowledge**: The `phiCCV` function operates on the explicit (r, s, k) triple and does not capture somatic/embodied TK. Note that a `CCVWeighted` extension exists for future integration.
- **Birkhoff misnomer**: Six theorems in StochasticCCV reference "Birkhoff" but actually prove Doeblin contraction or stationary distribution properties. The report should use "Doeblin contraction" or "stationary distribution" terminology, not "Birkhoff ergodic theorem."

### 9.4 Verified Codebase Statistics

Use these audit-verified statistics throughout the report:

| Metric | Value |
|---|---|
| Lean files | 31 |
| Total lines | 37,693 |
| Theorems + lemmas | 2,186 |
| `sorry` count | 0 |
| `axiom` count | 0 |
| Lean version | v4.28.0 |
| Mathlib version | v4.28.0 |
| `grind` uses | 776 |
| `native_decide` uses | 68 |
| Logical modules | 17 |

---

## Part 10 — Project-specific Configuration

### 10.1 Module-to-Chapter Mapping

| Module | Chapter | Part | Key Narrative Focus |
|---|---|---|---|
| Tactics | Ch 1 | I | Automation: grind (776 uses), native\_decide, custom tactics |
| QualityGates | Ch 2 | I | G1–G5 gate monotonicity, pipeline pass biconditionals |
| PhaseClassification | Ch 3 | I | 3-regime σ²-based classification, completeness |
| CCVGating | Ch 4 | II | CCV simplex (Project operationalization, not Collins original), φ\_CCV modulation |
| CuspCatastrophe | Ch 5 | II | A₃ singularity, hysteresis, bistable equilibria |
| PhasePortrait | Ch 6 | II | 4D phase space, TKS detection, entropy bounds |
| ProvenanceChain | Ch 7 | II | PROV-O DAG, stage monotonicity, depth invariants |
| PipelineAdaptive | Ch 8 | III | DGD adaptive thresholds, fixed-point convergence |
| StochasticCCV/Core | Ch 9 | III | 3×3 row-stochastic matrices, stationary distribution, Doeblin contraction |
| StochasticCCV/Information | Ch 10 | III | Information-theoretic CCV properties |
| PipelineBypass | Ch 11 | III | Bypass path semantics, safety-preserving shortcuts |
| ReinforcementLearning | Ch 12 | IV | MDP governance, Bellman monotonicity, reward shaping |
| AgenticSafety | Ch 11 | IV | Trust simplex, safety envelopes, autonomy bounds |

### 10.2 Key Narrative Arcs

**Thread 1 — Quality Flow**: G1–G5 gates (Ch 2) → CCV modulation (Ch 4) → Pipeline adaptation (Ch 8) → Final convergence (Ch 12)

**Thread 2 — Phase Dynamics**: σ² classification (Ch 3) → Full portrait (Ch 6) → Stochastic drift (Ch 9) → MDP control (Ch 10)

**Thread 3 — Safety Assurance**: Cusp catastrophe (Ch 5) → Safety envelopes (Ch 11) → Lyapunov bounds (Ch 12)

**Thread 4 — Provenance**: Chain invariants (Ch 7) → Stage monotonicity → Pipeline completeness (Ch 8)

These threads should be explicitly called out in transition paragraphs between chapters.

### 10.3 Notation Conventions

Ensure consistency with the primary paper (`docs/project-tufte.tex`):

| Symbol | Meaning | Lean Name | Module |
|---|---|---|---|
| $\phi = (R, D, C, V)$ | Phase point | `PhasePoint` | LyapunovStability |
| $\sigma^2$ | Stress squared | `StressSq` | PhaseClassification |
| $\varphi_{\mathrm{CCV}}(r,s,k)$ | CCV gate function | `phiCCV` | CCVGating |
| $V(\phi, \phi^*)$ | Lyapunov function | `lyapunovQuadratic` | LyapunovStability |
| $\mathbf{M}$ | Stochastic matrix | `StochMatrix3` | StochasticCCV |
| $\pi : S \to A$ | MDP policy | `MDPPolicy` | ReinforcementLearning |
| $\gamma$ | Discount factor (×100) | `γ100` | ReinforcementLearning |
| $(t_r, t_s, t_k)$ | Agent trust triple | `AgentTrust` | AgenticSafety |
| $\mathrm{G}_i(\cdot, \tau_i)$ | Quality gate $i$ | `G1`..`G5` | QualityGates |
| $U(a,b,x) = x^4/4 + ax^2/2 + bx$ | Cusp potential | `cuspPotential` | CuspCatastrophe |
| $4a^3 + 27b^2$ | Cusp discriminant | `cuspDiscriminant` | CuspCatastrophe |

---

## Part 11 — Integration with Gateway (SK-07)

### 11.1 Gateway Routing

The gateway registers this skill as `SK-62`:

```
| `SK-62` | `lean-report` | Blueprint-to-report (LaTeX with NL text) | Report Author |
```

### 11.2 Trigger Events

| Trigger | Action | Skills Involved |
|---|---|---|
| `generate report` | Full pipeline (stages 1–6) | SK-62, SK-61, SK-07, SK-60, SK-39 |
| `update report` | Re-narrate changed chapters + recompile | SK-62 |
| `report status` | Report coverage and staleness metrics | SK-62, SK-39 |
| `narrate chapter X` | Stage 3 for one module only | SK-62, domain skill |
| `compile report` | Stage 6 only (LaTeX → PDF) | SK-62 |

### 11.3 Feedback Loops

```
Report narration ──► Reveals unclear theorem statements ──► lean-specification (SK-05)
Report compilation ──► Missing cross-refs ──► lean-blueprint (SK-61)
Report figures ──► Dependency graph anomalies ──► lean-retro-methodology (SK-35)
Report coverage ──► Unnarrated theorems ──► lean-doc-improvement (SK-10)
Report draft ──► Paper inconsistencies ──► lean-doc-requirements (SK-09)
```

### 11.4 Quality Engine Integration (SK-39)

Report readiness adds a new quality dimension:

```
Q9 (Report):  weight = 3
  score = (narrated_theorems / blueprint_theorems) × 100
  gate = soft (advisory, does not block milestones)
```

### 11.5 Upstream Dependency

The report pipeline REQUIRES a completed blueprint (SK-61) run. If blueprint artifacts do not exist, the gateway must first trigger `generate blueprint` before `generate report`.

```
Gateway routing:
  IF trigger == "generate report" AND NOT exists(".lake/build/blueprint/nodes.json"):
    route → SK-61 (generate blueprint) THEN SK-62 (generate report)
  ELSE:
    route → SK-62 directly
```

---

