---
name: lean-doc-sync-handbook
description: Unified reference handbook for @lean-doc-sync (requirement extraction,
  blueprint-to-LaTeX report compilation, paper metric sync, and doc review).
extracted_from: skills/lean-doc-sync/SKILL.md
---

## Quick-Lookup Indexing Tables (`mathcomp-skills` Three-Entry-Point Pattern)

### Table 1: Goal-Shape-First (`templates` Entry Point)

| Goal / Term Shape | Primary Tactic / Pattern | Canonical Recipe / Notes |
| :--- | :--- | :--- |
| Informal paper theorem `\begin{theorem}` | `requirements` mode -> 3-part spec | Extract Preconditions, Postconditions, and Witness for `@lean-specification` |
| Completed `@[blueprint]` graph | `scripts/lean/blueprint_to_report.py` | Compile dependency-ordered LaTeX report sections |
| Paper appendix theorem/module table | `scripts/lean/metric_sync.py` | Re-derive exact counts from compiled `.olean` census |
| Conference paper + Lean 4 concordance | `Concordance.lean` + `paper_supplement_audit.py` | Pair every numbered claim & walkthrough arithmetic check with `#check` + `#print axioms` |
| Double-blind CMT/HotCRP Lean supplement | `altproof tree-shake --anonymize --verify-build` | Emit declaration-shaken slice + metadata-scrubbed `.tar.gz` + root `LICENSE` |

### Table 2: Intent-First (`phrasebook` Entry Point)

| User / Engineer Intent | Recommended Tool / Idiom | Actionable Recipe |
| :--- | :--- | :--- |
| Verify every Lean name cited in LaTeX exists | `scripts/lean/check_citations.py` | Check `file:line` and identifier parity against compiled tree |
| Review documentation draft for undefined terms | `feedback` mode readability pass | Flag forward references, missing assumptions, and scope overclaims |
| Audit `.bib`, terminology, `INV-001` & supplement | `scripts/lean/paper_supplement_audit.py --strict` | Verify `filecontents*` `.bib` parity, 0 BibTeX/Overfull warnings, 0 misnomers, and 0 `@[deprecated]` shims |
| Document honest proof provenance & novelty | Three-Tier Provenance Section | Partition credit into Tier 1 (`Mathlib`/`Cslib`), Tier 2 (adapted/newly proved classical), and Tier 3 (novel domain results) |

### Table 3: Error / Bottleneck-First (`errors` Entry Point)

| Symptom / Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Broken `foo.lean:123` citation in docs | Line numbers shifted after refactoring | Prefer declaration-anchored references and re-run `check_citations.py` |
| Prose claims theorem proved while `sorry` or facade stub remains | Premature paper sync before `@lean-verification-gate` | Strengthen upstream Lean theorem or calibrate paper statement to exact proved hypotheses |
| Coined/spliced mathematical misnomer (`Polyak-Doob`, `Presburger` on squares) | Unverified eponymous naming | Cross-check primary literature, delete `@[deprecated]` shims (`GT-66`), and run `paper_supplement_audit.py` |
| Embedded `filecontents*` `.bib` drifts from standalone `.bib` | Manual edit applied to only one file | Synchronize byte-for-byte and gate with `paper_supplement_audit.py --tex ... --bib ...` |
| Paper cites external checker (`nanoda_lib`) never run on final slice | Unverified boilerplate copied from prior prose | Cite only tools physically executed (`Lean.Kernel.Environment.replay` via `cold_kernel_replay.lean`, `GT-67`) |

---

<!-- Merged from lean-report-handbook.md -->

# Blueprint-to-Report Pipeline Handbook (Lean 4)

> **Layering note.** This file holds the deep pipeline content previously
> embedded in [`skills/lean-report/SKILL.md`](../../skills/lean-doc-sync/SKILL.md).
> The SKILL.md keeps the dispatch contract, the Execution Checklist (Part 12),
> the Troubleshooting table (Part 13), and the Output Artifacts summary (Part 14).
> This file holds the full encyclopaedia of pipeline stages, agent-driven
> narration rules, Lean 4.28 feature integration, audit hooks, and gateway
> wiring. Zero fidelity loss vs the pre-layering revision.

---

## Part 1 -- Inputs and Outputs

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

## Part 2 -- Pipeline Architecture

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
| COMPILE | lean-enforcement (SK-36) | -- | build logs |

---

## Part 3 -- Stage 1: INGEST

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

## Part 4 -- Stage 2: PLAN

### 4.1 Report Outline Template

```
Project Formal Verification Report
═════════════════════════════════

Front Matter:
  - Abstract (auto-generated from project overview + metrics)
  - Table of Contents
  - List of Definitions, Theorems, and Lemmas
  - Notation Table

Part I -- Foundations
  Ch 1: Mathematical Preliminaries (Tactics.lean)
  Ch 2: State Gate Formalization (StateGates.lean)
  Ch 3: Regime Classification (RegimeClass.lean)

Part II -- Core Models
  Ch 4: Simplex Vector Gating (SimplexGating.lean)
  Ch 5: Bifurcation Potential Model (BifurcationModel.lean)
  Ch 6: State Portrait Dynamics (StatePortrait.lean)
  Ch 7: Provenance DAG (ProvenanceDAG.lean)

Part III -- Adaptive Infrastructure
  Ch 8: Threshold Adaptation (ThresholdAdapt.lean)
  Ch 9: Markov Kernel Core (MarkovChain/Core.lean)
  Ch 10: Markov Information Bounds (MarkovChain/Information.lean)
  Ch 11: Guarded Bypass Semantics (GuardedBypass.lean)

Part IV -- Multi-Agent Systems
  Ch 12: Markov Decision Processes (MDPControl.lean)
  Ch 13: Capability Guard Core (CapabilityGuard/Core.lean)
  Ch 14: Quorum Consensus (CapabilityGuard/Consensus.lean)
  Ch 15: Role Policy Extensions (CapabilityGuard/Roles.lean)

Part V -- Convergence Theory
  Ch 16: Lyapunov Stability Analysis (LyapunovStability.lean)
  Ch 17: Contraction Mapping Bounds (ContractionBounds.lean)

Part VI -- Verification & Synthesis
  Ch 18: End-to-End Trace Soundness (TraceSoundness.lean)
  Ch 19: Transition Graph Topology (TransitionTopology.lean)

Note: Several modules may be split into subdirectories:
  - CapabilityGuard -> Core/, Consensus/, Roles/
  - MarkovChain -> Core/, Information/
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
| I -- Foundations | Set up the mathematical stage: what are quality gates, how do we classify knowledge phases, what automation do we use? |
| II -- Core Models | Construct the building blocks: how expert knowledge is categorized, how stress creates catastrophe, how the phase portrait captures system state |
| III -- Infrastructure | Show how the system adapts: pipeline thresholds shift with phases, CCV drifts stochastically toward stationarity |
| IV -- Governance | Introduce agency: MDP-based decision-making, trust envelopes, safety bounds |
| V -- Convergence | Tie it all together: the entire system converges under Lyapunov analysis |

---

## Part 5 -- Stage 3: NARRATE

### 5.1 Natural Language Generation Rules

Each chapter-writer agent follows these rules:

**R1 -- Audience**: Write for a mathematically literate reader who may not know Lean 4. All Lean-specific syntax must be translated to standard mathematical notation.

**R2 -- Definition introduction pattern**:
```latex
\begin{definition}[{name}]\label{def:label}
  {Natural language statement using standard math notation.}
\end{definition}

{1-2 paragraphs explaining motivation, intuition, and relationship
to preceding definitions. Include domain context (what this means
for knowledge transfer in the public sector).}
```

**R3 -- Theorem presentation pattern**:
```latex
\begin{theorem}[{name}]\label{thm:label}
  {Natural language statement of the mathematical claim.}
\end{theorem}

\begin{proof}[Proof sketch]
  {High-level proof strategy in natural language. Reference
  key lemmas by \cref. Do NOT reproduce full Lean tactic
  scripts -- instead describe the mathematical argument.}
\end{proof}

{1 paragraph explaining significance: why this result matters,
what it guarantees for the system, how it connects to other
chapters.}
```

**R4 -- Lean-to-LaTeX Translation Table**:

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
| `@[simp]` | (Omit from report -- internal automation detail) |
| `grind` | "by automated SMT-based reasoning" |
| `fun_prop` | "by function property inference (continuity, measurability)" |
| `push_cast` | "by coercion normalization" |
| `field_simp` | "by field-algebraic simplification" |
| `native_decide` -> `decide` / `kernel_decide` | "by kernel-checked finite-domain evaluation (`0` `Lean.ofReduceBool`)" |
| `ContractingWith K f` | "$f$ is a $K$-Lipschitz contraction ($K < 1$)" |
| `NNReal` / `ℝ≥0` | "$\mathbb{R}_{\geq 0}$" |

**R5 -- Nat-scaled arithmetic convention**: The Project formalization uses `Nat` scaled by 100 (or 10000) to avoid noncomputable reals. The report must:
1. State this convention once in the Preliminaries chapter
2. Convert back to real-valued notation in theorem statements
3. Note where the scaling introduces floor/ceiling effects
4. Use the notation "$q_{100} = \lfloor 100q \rfloor$" for explicit scaled values

**R6 -- Proof sketch depth**: Provide enough detail that a reader could reconstruct the proof in a different theorem prover, but do not include Lean-specific tactic names. Map:

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
| `grind` | "by automated SMT-based reasoning" |
| `decide +kernel` | "by kernel-reduced finite-domain evaluation (`GT-30`: `native_decide` is banned)" |
| `fun_prop` | "by function property inference" |
| `push_cast` | "by coercion normalization" |
| `field_simp` | "by field-algebraic simplification" |

**R7 -- Cross-references**: Every theorem that appears in the blueprint with a `\lean{name}` declaration should have:
- A `\label{thm:prefix-short-name}` for internal cross-referencing
- A margin note: `\marginpar{\texttt{name} {\footnotesize (Module.lean:L$n$)}}`
- A hyperlink to the blueprint web version (if deployed)

**R8 -- No fabrication**: Every mathematical statement in the report MUST correspond to a proven theorem in Lean (no `sorry`). If a result is only conjectured, label it explicitly as a conjecture.

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
  regardless of the initial knowledge state -- provided the
  contraction parameter $\alpha$ satisfies $0 \leq \alpha < 1$.
\end{remark}
```

---

## Part 5B -- Lean 4.28 Features for Report Generation

The Project formalization uses Lean v4.34.1 and Mathlib v4.34.1. Report narration should acknowledge the following Lean 4.28 features that heavily influence proof style:

### 5B.1 `grind` -- Primary Tactic (776 uses)

`grind` is now the dominant proof-closing tactic in the codebase (776 uses, up from ~30 in earlier versions). It combines congruence closure, E-matching, and case splitting into an SMT-style decision procedure. Report prose should translate `grind` as "by automated SMT-based reasoning" rather than enumerating sub-steps.

Variants used in the codebase:
| Annotation | Meaning | Report Translation |
|---|---|---|
| `@[grind =]` | Register equality lemma | (omit -- internal automation) |
| `@[grind →]` | Register forward-chaining rule | (omit -- internal automation) |
| `@[grind ←]` | Register backward-chaining rule | (omit -- internal automation) |
| `@[grind norm]` | Register normalization simp lemma | (omit -- internal automation) |
| `@[grind unfold]` | Register definition for unfolding | (omit -- internal automation) |

### 5B.2 Kernel-Reduced Finite Computation (`decide` / `kernel_decide`, `GT-30`)

Use kernel-reduced `decide` (`decide +kernel`) or `kernel_decide` (`first | rfl | decide +kernel | omega`) for finite-domain decidability proofs. Do NOT use `native_decide`, which introduces `Lean.ofReduceBool` / `Lean.trustCompiler` (`GT-30`). Report prose: "by Lean 4 kernel reduction."

### 5B.3 Module System Features

- Module system is no longer experimental in Lean 4.28
- `assert_not_exists` / `assert_not_imported` used for dependency hygiene -- ensures modules do not accidentally pull in heavy dependencies
- `lake shake` available for unused import detection (report should note if run during CI)

### 5B.4 `first_par` (Parser Exists, Not Yet Implemented)

The `first_par` combinator has a parser but no runtime implementation in Lean 4.28. Do not reference it as a parallelism feature in the report.

---

## Part 6 -- Stage 4: ILLUSTRATE

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

## Part 7 -- Stage 5: ASSEMBLE

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

%% Part I -- Foundations
\part{Foundations}
\input{chapters/ch_01_tactics}
\input{chapters/ch_02_qualitygates}
\input{chapters/ch_03_phaseclassification}

%% Part II -- Core Models
\part{Core Models}
\input{chapters/ch_04_ccvgating}
\input{chapters/ch_05_cuspcatastrophe}
\input{chapters/ch_06_phaseportrait}
\input{chapters/ch_07_provenancechain}

%% Part III -- Adaptive Infrastructure
\part{Adaptive Infrastructure}
\input{chapters/ch_08_pipelineadaptive}
\input{chapters/ch_09_stochasticccv_core}
\input{chapters/ch_10_stochasticccv_information}
\input{chapters/ch_11_pipelinebypass}

%% Part IV -- Agent Governance
\part{Agent Governance}
\input{chapters/ch_12_reinforcementlearning}
\input{chapters/ch_13_agenticsafety_core}
\input{chapters/ch_14_agenticsafety_consensus}
\input{chapters/ch_15_agenticsafety_gaps}

%% Part V -- Convergence Theory
\part{Convergence Theory}
\input{chapters/ch_16_lyapunov}
\input{chapters/ch_17_ccvecontraction}

%% Part VI -- Evaluation & Feedback
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
ExampleProject multi-stage state-machine and stability framework.
The formalization comprises \textbf{31} Lean~4 files across
\textbf{17} logical modules totaling \textbf{37,693} lines of
code, containing \textbf{2,186} theorems and lemmas,
all verified by the Lean~4 kernel (v4.34.1) with \textbf{zero}
uses of \texttt{sorry}, \textbf{zero} uses of \texttt{native\_decide},
and \textbf{zero} custom axioms beyond standard classical logic
(\texttt{propext}, \texttt{Classical.choice}, \texttt{Quot.sound}).

The development establishes: (1)~monotone decidable acceptance
gates across stage transitions, (2)~approximate forward simulation
onto bounded integer grids, (3)~stationary existence and Doeblin
$\ell^1$ contraction for finite Markov kernels, (4)~Bellman operator
contraction and martingale-difference partial-sum convergence, and
(5)~Byzantine quorum intersection and two-sided Boolean reflection
for end-to-end execution traces.

\medskip\noindent
\textbf{Keywords:} Formal verification, Lean~4, state-machine
invariants, Lyapunov stability, Markov chains, proper scoring,
Boolean reflection.
\end{abstract}
```

---

## Part 8 -- Stage 6: COMPILE

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
| PDF page count reasonable | `pdfinfo project-report.pdf` | 50--200 pages expected |
| No sorry-marked theorems | `grep -c '\\sorrymark' project-report.tex` | 0 |

---

## Part 9 -- Audit Integration Template (Example Corpus)

The report should incorporate findings from the project's codebase audit. Use a structured table to link audit artifacts to report sections:

### 9.1 Audit Reference Documents (Example)

| Document | Content | Report Integration |
|---|---|---|
| `AUDIT-RECOMMENDATIONS.md` | Cross-module audit findings and open items | Acknowledge addressed items; flag open items in appendix |
| `STATISTICS-RECONCILIATION.md` | Verified codebase metrics (`lake build` + census) | Use as authoritative source for all statistics |
| `ROADMAP.md` | Multi-phase formalization plan | Reference in "Future Work" section |

### 9.2 Critical Scope & Fidelity Caveats (Must Acknowledge in Report)

Every formalization report MUST explicitly distinguish proved claims from modeling hypotheses:

1. **Existence vs. uniqueness**: When uniqueness of a fixed point or stationary distribution is proved under an `[Inhabited X]` or existence hypothesis, state explicitly: "Uniqueness is mechanically proved; constructive existence remains an explicit hypothesis."
2. **Linearized vs. nonlinear scope**: When Lyapunov or contraction bounds apply to a linearized step function rather than the full nonlinear transition, state the exact domain of the formal guarantee.
3. **Exhaustive pattern matching**: Flag any classifier or transition function that uses a catch-all `| _ =>` branch rather than exhaustive constructor matching.
4. **Zero unbacked quantitative claims**: Remove any numerical suitability or speedup figure from earlier drafts that lacks either a formal bound or a reproducible benchmark artifact.

### 9.3 Verified Codebase Statistics Table

Include a machine-verified metrics block in the report appendix:

| Metric | Source of Truth | Gate |
|---|---|---|
| Lean files | `find <Root> -name '*.lean' \| wc -l` | Re-derived per build |
| Theorems + lemmas | `lean_metrics(action: "census")` | Within 100% of compiled `.olean` |
| `sorry` count | `check_sorry.sh` / `lean-rules` | Hard `0` |
| Custom `axiom` count | `axiom_audit.py` / `lean_axiom_closure` | Hard `0` (`propext`, `Classical.choice`, `Quot.sound` only) |
| `native_decide` count | `lean-rules` (`rule-lean-no-native-decide`) | Hard `0` |
| Lean & Mathlib version | `lean-toolchain` + `lake-manifest.json` | Pinned (`v4.34.1`) |

---

## Part 10 -- Project-Specific Configuration (`lean-project.toml` & `skills-overrides/`)

Keep project-specific module-to-chapter mappings and notation tables in the project's local `skills-overrides/` overlay (`subst_table.json` and `*-domain-deltas.md`) rather than hardcoding them in shared skill handbooks:

### 10.1 Module-to-Chapter Mapping Schema

| Module | Chapter | Part | Key Narrative Focus |
|---|---|---|---|
| `Core.Foundations` | Ch 1 | I | Foundational definitions, algebraic structures, custom tactics (`decide +kernel`, `omega`, `grind`) |
| `Core.Invariants` | Ch 2 | I | Monotonicity, preservation biconditionals, lattice bounds |
| `Dynamics.Stability` | Ch 3 | II | Lyapunov functions, contraction mappings, fixed-point convergence |
| `Stochastic.Markov` | Ch 4 | II | Row-stochastic kernels, stationary distributions, ergodic bounds |
| `Optimization.Control` | Ch 5 | III | Bellman operators, policy improvement, safety envelopes |
| `Verification.Soundness` | Ch 6 | III | End-to-end soundness theorems and non-vacuity witnesses |

### 10.2 Cross-Chapter Narrative Arcs

1. **Foundations to Invariants**: Definitions (Ch 1) -> Preservation lemmas (Ch 2) -> End-to-end soundness (Ch 6).
2. **Dynamics to Control**: Deterministic stability (Ch 3) -> Stochastic kernels (Ch 4) -> Optimal control (Ch 5).

Call out these threads explicitly in transition paragraphs between chapters.

### 10.3 Notation Consistency Table

Maintain a single bidirectional symbol dictionary between the primary LaTeX paper (`docs/paper.tex`) and Lean identifiers:

| LaTeX Symbol | Meaning | Lean Identifier | Module |
|---|---|---|---|
| $S$ | State space | `StateSpace` | `Core.Foundations` |
| $V(x)$ | Lyapunov candidate | `lyapunovVal` | `Dynamics.Stability` |
| $P$ | Markov transition kernel | `TransitionKernel` | `Stochastic.Markov` |
| $\mathcal{T}$ | Bellman operator | `bellmanOp` | `Optimization.Control` |
| $\gamma \in [0, 1)$ | Discount factor | `discountFactor` | `Optimization.Control` |

---

## Part 11 -- Integration with Gateway (SK-07)

### 11.1 Gateway Routing

The gateway registers this skill as `SK-62`:

```
| `SK-62` | `lean-report` | Blueprint-to-report (LaTeX with NL text) | Report Author |
```

### 11.2 Trigger Events

| Trigger | Action | Skills Involved |
|---|---|---|
| `generate report` | Full pipeline (stages 1--6) | SK-62, SK-61, SK-07, SK-60, SK-39 |
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


---

<!-- Merged from lean-doc-improvement-handbook.md -->

# Lean Doc Improvement Handbook

> **Layering note.** This file holds the deep content previously
> embedded in [`skills/lean-doc-improvement/SKILL.md`](../../skills/lean-doc-sync/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow /
> Recovery / Handoffs) + a parts index. This file holds the full
> encyclopaedia. Zero fidelity loss vs the pre-layering revision.

---

## Part 1 -- Trigger Events

| Trigger | Action | Priority |
|---|---|---|
| `sorry` removed (new proof completed) | Update coverage metrics | P2 |
| Hypothesis added to theorem | Check if paper claim needs corresponding condition | P1 |
| Hypothesis removed (stronger result) | Update paper to state stronger result | P1 |
| Counter-example found during review | Erratum entry + paper correction | P0 |
| Statement corrected (Φ finding) | Erratum entry + paper correction | P0 |
| New bridge theorem proven | Add to paper's formalization appendix | P2 |
| Duplicate detected by Ν | Note in appendix if paper references both | P3 |
| Quality improvement (Λ refactoring) | No paper change needed (internal) | -- |
| Convention change (Ω finding) | No paper change usually (internal) | -- |
| New Zettelkasten permanent note | Consider for paper discussion section | P3 |
| Axiom issue detected by Σ | Critical erratum if affects paper claims | P0 |

---

## Part 2 -- Document Update Types

### 2.1 Metric Synchronization

The paper's appendix contains formalization metrics that must stay in sync:

```markdown
## Metrics to Synchronize
- Total lines of Lean code: [from `wc -l Project/*.lean`]
- Total theorems: [from `grep -c "^theorem\|^lemma" Project/*.lean`]
- Total definitions: [from `grep -c "^def\|^structure\|^inductive\|^class" Project/*.lean`]
- Sorry count: [from `grep -c "sorry" Project/*.lean`]
- Module count: [from `ls Project/*.lean | wc -l`]
- Lean version: [from `lean --version`]
- Mathlib version: [from lakefile.lean]
- Build status: [from `lake build` exit code]
- Axiom cleanliness: [all/not-all modules pass `#print axioms` check]
```

### 2.2 Verification Table

The paper should contain (or be updated with) a verification mapping:

```latex
\begin{table}[h]
\caption{Formal Verification Mapping}
\begin{tabular}{llll}
Paper Claim & Lean Theorem & Module & Status \\
\hline
Thm 3.1 & \texttt{quality\_gate\_monotone} & QualityGates & \checkmark \\
Prop 4.2 & \texttt{phase\_classification\_complete} & PhaseClassification & \checkmark \\
% ... generated from coverage matrix
\end{tabular}
\end{table}
```

### 2.3 Erratum Entries

When formalization reveals a paper error:

```markdown
## Erratum: [ERR-YYYYMMDD-NNN]
- Paper location: §N.M, [Theorem/Equation] N
- Original claim: [verbatim from paper]
- Issue: [missing hypothesis / incorrect bound / wrong quantifier order / ...]
- Corrected claim: [corrected version]
- Evidence: Project/[Module].lean:[theorem_name] -- [brief explanation]
- Discovered by: [council member] during [Phase N audit / review session ID]
- Impact: [minor wording fix / substantive correction / invalidates downstream claim]
```

### 2.4 Insight Notes

When formalization yields positive insights (not corrections):

```markdown
## Insight: [INS-YYYYMMDD-NNN]
- Source: Project/[Module].lean:[theorem_name]
- Type: [sharper bound | simpler proof | unexpected connection | generalization]
- Description: [what was discovered]
- Paper action: [add to discussion / add remark / extend result / no action]
```

---

## Part 3 -- Update Workflow

### 3.1 Individual Theorem Completion

When a theorem is proven and council-reviewed:

```
1. Check coverage matrix → find corresponding paper claim
2. IF claim status was "uncovered" → update to "covered"
3. IF proof required additional hypotheses not in paper:
   a. Create erratum entry
   b. Draft LaTeX correction
   c. Route to Φ for validation
   d. Apply to paper source
4. IF proof achieved stronger result than paper claimed:
   a. Create insight note
   b. Draft LaTeX improvement
   c. Route to Ω for consistency check
   d. Apply to paper source
5. Update metrics (theorem count, sorry count, coverage %)
6. Update verification table
```

### 3.2 Batch Update After Audit Wave

After completing a retroactive audit wave:

```
1. Run metric sync script → generate diffs
2. Regenerate verification table from coverage matrix
3. Collect all erratum entries from the wave → batch review
4. Collect all insight notes → assess for paper inclusion
5. Update paper appendix with new metrics
6. Update paper body with corrections (P0/P1 errata)
7. Create Zettelkasten permanent note summarizing the wave's findings
```

### 3.3 Paper Revision Protocol

For non-trivial paper changes:

```
1. Draft the change (LaTeX diff)
2. Route through council:
   - Φ: Does the new text accurately reflect the formal result?
   - Ν: Is the change consistent with other paper claims?
   - Λ: Is the exposition clear?
   - Ω: Do cross-references and numbering still work?
3. Apply change
4. Verify paper compiles (LaTeX build)
5. Update traceability records
```

---

## Part 4 -- LaTeX Integration Patterns

### 4.1 Auto-Generated Content Markers

Place markers in the LaTeX source for auto-updatable sections:

```latex
% AUTO-GENERATED: DO NOT EDIT MANUALLY
% Source: docs/tracking/coverage_matrix.md
% Last sync: [ISO-8601]
\begin{table}[h]
...
\end{table}
% END AUTO-GENERATED
```

### 4.2 Conditional Formatting

For claims whose formal status changed:

```latex
% UPDATED per ERR-20250718-001: added hypothesis (q > 0)
\begin{theorem}[Quality Gate Monotonicity]
For all quality scores $q \in (0, 1]$ ... % was $q \in [0, 1]$
\end{theorem}
```

### 4.3 Verification Badges

In the paper appendix, each claim can carry a status:

```latex
\newcommand{\verified}{\textcolor{green}{\checkmark}}
\newcommand{\partial}{\textcolor{orange}{$\sim$}}
\newcommand{\unverified}{\textcolor{red}{$\times$}}

Theorem 3.1 \verified{} % quality_gate_monotone in QualityGates.lean
```

---

## Part 5 -- Feedback to Other Skills

### 5.1 To lean-doc-requirements

When updating the paper reveals:
- New claims that were added during revision → extract as new requirements
- Claims that were split or merged → update corresponding specifications
- Sections restructured → re-run extraction on affected sections

### 5.2 To lean-zettelkasten

Each erratum and insight becomes a Zettelkasten entry:
- Erratum → fleeting note tagged `#erratum #[module]`
- Insight → literature note or permanent note depending on significance
- Pattern of errata (e.g., "paper consistently omits positivity hypotheses") → permanent note

### 5.3 To lean-review-council

Findings during document update may trigger:
- Re-review of related theorems (if paper context changes interpretation)
- Specification update (if paper claim was the source of truth and it changed)
- Convention updates (if paper naming differs from Lean naming)

---

## Part 6 -- Metric Dashboard

### 6.1 Sync Status Template

```markdown
# Metric Sync Dashboard
## Last sync: [ISO-8601]

| Metric | Paper Value | Lean Value | Status |
|---|---|---|---|
| Total lines | 8,994 | [computed] | [match/stale] |
| Theorems | 611 | [computed] | [match/stale] |
| Sorry count | 0 | [computed] | [match/stale] |
| Modules | 12 | [computed] | [match/stale] |
| Coverage % | [N]% | [computed] | [match/stale] |
| Lean version | 4.34.1 | [computed] | [match/stale] |
| Mathlib version | 4.34.1 | [computed] | [match/stale] |

## Stale Metrics: [N]
## Errata Pending Paper Update: [N]
## Insights Pending Assessment: [N]
```

### 6.2 Automation

The `metric_sync.py` enforcement script (see lean-gateway SK-06 enforcement scripts) automates:
1. Extract current Lean metrics
2. Parse paper appendix for stated metrics
3. Diff and report mismatches
4. Generate PR-ready LaTeX patch if mismatches found


---

<!-- Merged from lean-doc-requirements-handbook.md -->

# Lean Doc Requirements Handbook

> **Layering note.** This file holds the deep content previously
> embedded in [`skills/lean-doc-requirements/SKILL.md`](../../skills/lean-doc-sync/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow /
> Recovery / Handoffs) + a parts index. This file holds the full
> encyclopaedia. Zero fidelity loss vs the pre-layering revision.

---

## Part 1 -- Extraction Pipeline

```
Document → Section scan → Claim extraction → Formalization →
  Specification → Cross-reference back to document
```

### Input Sources (priority order)

1. **Primary paper** (`docs/paper.tex`) -- mathematical claims, theorems, equations
2. **Technical reports** (`docs/technical-report.md`) -- extended proofs, design rationale
3. **System requirements** (`docs/requirements.md`) -- functional properties to verify
4. **Blueprint & specs** (`blueprint/`, `specs/`) -- verification targets

---

## Part 2 -- Claim Extraction Protocol

### 2.1 LaTeX Claim Types

| LaTeX Environment | Claim Type | Extraction Action |
|---|---|---|
| `\begin{theorem}` | Formal theorem | Direct extraction -- highest priority |
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

- Classification:
  - Type: [theorem | definition | bound | identity | monotonicity | convergence | safety | other]
  - Domain: [foundations | discrete | stochastic | dynamical | optimization | analysis | ai-safety | knowledge | security]
  - Complexity: [trivial | routine | moderate | hard | research-level]

## Informal Statement
[One-paragraph plain English interpretation]

## Hypotheses (inferred)
1. [h₁ -- e.g., "quality score is in [0,1]"]
2. [h₂ -- e.g., "decision function is continuous"]
3. [h₃ -- e.g., "convergence parameter ε > 0"]

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

## Part 3 -- Hypothesis Inference

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
| "Under mild regularity conditions" | CHECK CAREFULLY -- need to identify exact conditions |

### 3.2 Domain-Specific Defaults (Project)

When project-specific terms appear without qualification:

| Domain term | Default Hypothesis |
|---|---|
| Normalized score | `in Set.Icc 0 1` |
| Discrete regime | Member of finite inductive type |
| Configuration | Explicit `Config` structure |
| Simplex vector | Non-negative coordinates summing to `1` (or scaled integer simplex) |
| Decision boundary | Defined on `Real^n` with explicit metric |
| Convergence | With respect to explicit metric or norm |
| Safety bound | Via Lyapunov function or contraction mapping |

### 3.3 Red Flags in Hypothesis Inference

- **"Obviously" / "Clearly"** -- these hide non-trivial hypotheses, flag for Φ review
- **"Without loss of generality"** -- may hide symmetry argument needing separate lemma
- **"By a standard argument"** -- may require Mathlib search for the standard result
- **Universally quantified with no bound** -- check if domain restriction is implied
- **Conditional/existential mix** -- verify quantifier order carefully

---

## Part 4 -- Batch Extraction Workflow

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
| DOC-5-001 | §5.1 | convergence | PipelineAdaptive | uncovered | -- |
```

### 4.3 Output Artifacts

Per extraction batch:
1. `docs/tracking/claims_[section].md` -- all extracted claims for that section
2. Updated coverage matrix in `docs/tracking/coverage_matrix.md`
3. For uncovered claims: retroactive specifications via lean-specification skill
4. For partial claims: gap analysis notes
5. Zettelkasten literature notes for key insights discovered during extraction

---

## Part 5 -- Council Integration

### 5.1 Claim Review

After extraction, route claims through the council:

| Member | Role in Claim Review |
|---|---|
| Σ | Verify that the draft Lean signature type-checks (or explain why not) |
| Φ | Validate that the Lean signature faithfully represents the paper claim |
| Ν | Check if Mathlib already has a version of this claim |
| Λ | Assess specification quality -- clear, testable, well-scoped |
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

## Part 6 -- Requirements Traceability

### 6.1 Bidirectional Trace

Every formal requirement must trace in both directions:

```
Document claim ←→ Specification ←→ Lean theorem
```

The traceability record:

```markdown
## Trace: [claim_id]
- Forward: DOC-3-001 → SPEC-20250718-001 → quality_gate_monotone (QualityGates.lean:L45)
- Backward: quality_gate_monotone -> SPEC-20250718-001 -> DOC-3-001 (paper.tex §3.1)
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


---

<!-- Merged from lean-doc-feedback-handbook.md -->

# lean-doc-feedback

## Routing

- **USE FOR:** reviewing a Lean documentation draft; flagging undefined terms; suggesting cross-links to blueprint nodes; scoring readability against the
  project rubric.
- **DO NOT USE FOR:** rewriting prose end-to-end (use `@lean-doc-improvement`); generating new blueprints (use `@lean-blueprint`).
- **TRIGGERS:** doc-review, readability, doc-feedback.

## Behavioural rules (G-*)

- **G-1** (MUST): Feedback MUST be line-anchored to the draft. [Trace: AC-01]
- **G-2** (SHOULD): Feedback SHOULD prefer minimal-diff suggestions over rewrites. [Trace: AC-02]
- **G-3** (MUST NOT): The skill MUST NOT silently edit the draft. [Trace: AC-03]
- **G-4** (SHOULD): The skill SHOULD link each finding to a rubric criterion. [Trace: AC-04]

## Workflow

1. **Discover** [discover] -- read draft, locate rubric, list scope boundaries.
2. **Review** [execute] -- emit line-anchored findings.
3. **Score** [validate] -- apply rubric; max 3 attempts then escalate.
4. **Persist** [persist] -- write `feedback.md`, tick `tasks.md`.

## Recovery & STOP

- Draft missing rubric reference → STOP, escalate.
- Scope drift (silent edit) → immediate STOP, restore.
- Confidence < 80 % on rubric criterion → STOP, ask.

## Handoffs

- **Predecessors / successors**: see FM `handoffs`.
- **Source spec**: `specs/lean/doc-feedback/requirements.md`.

## Common failure modes

> AI agents commonly: rewrite instead of annotating; omit rubric anchors;
> bundle many findings into one comment. Full registry:
> GUARDRAILS.md §Agent failure taxonomy.

---

# Double-Blind Paper, Three-Tier Provenance & Shaken Supplement Synchronization

For conference and journal submissions accompanied by a standalone anonymized Lean 4 supplementary archive, follow [`../protocols/double-blind-paper-and-supplement-release.md`](../protocols/double-blind-paper-and-supplement-release.md) and execute these five mandatory gates:

1. **1-to-1 `Concordance.lean` Anchoring (Combined Option 1 + Option 2)**:
   - Every numbered proposition, theorem, corollary, table row, and numerical walkthrough constant in `.tex` must map to an explicit `#check` and `#print axioms` anchor in a single `Concordance.lean` entry module.
   - When a Lean declaration proves a weaker special case than the paper states (e.g., uniform player sets instead of heterogeneous `Fin (k i)`, or taking a fixed point as an input hypothesis instead of composing Brouwer existence + contraction uniqueness), strengthen the upstream Lean theorem first; when full generalization lies outside scope, calibrate the paper statement to match the exact proved hypotheses.
2. **Skeptical Primary-Literature Terminology & `.bib` Verification**:
   - Audit every DOI, volume, issue, article number, and author list against publisher records (`0` BibTeX warnings, `100%` `.bib` entries cited, embedded `filecontents*` `.bib` byte-for-byte identical to standalone `.bib`).
   - Eliminate coined/spliced mathematical misnomers (`Presburger` on quadratic expressions, `Polyak step-size` for Robbins-Monro schedules, `Little's law` for closed renewal cycle rates, `Awareness` for Aumann partition measurability, political slogans for quota inequalities).
3. **Zero `@[deprecated]` Shims & Standalone Rename Ledger (`GT-66`)**:
   - Delete retired identifiers cleanly across `.lean` source files (`0` `@[deprecated]` attributes) and record historical mappings in an external Markdown ledger (`docs/tracking/terminology-rename-ledger.md`).
4. **Three-Tier Proof Provenance & Executed-Tool Honesty (`GT-67`)**:
   - Explicitly partition formal credit across (i) upstream foundations (`Mathlib`, `Cslib`), (ii) adapted third-party ports (preserving SPDX/`LICENSE` notices) and newly proved classical bridges, and (iii) novel domain models and synthesis theorems.
   - Cite only verification tools physically executed on the final supplement (`Lean.Kernel.Environment.replay` via `scripts/lean/cold_kernel_replay.lean`).
5. **Automated Pre-Submission Gate**:
   ```bash
   python3 scripts/lean/paper_supplement_audit.py \
     --tex path/to/paper.tex \
     --bib path/to/paper.bib \
     --lean-dir path/to/lean4-supplement \
     --supplement-mode \
     --max-content-pages 9 \
     --forbid-first-person \
     --strict
   ```

