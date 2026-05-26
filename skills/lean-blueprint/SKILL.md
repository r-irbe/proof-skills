---
name: lean-blueprint
description: "Generate a formal project blueprint from a Lean 4 codebase using LeanArchitect and leanblueprint. Orchestrates: (1) dependency analysis of all modules, (2) annotation of key theorems/definitions with @[blueprint], (3) LaTeX generation via LeanArchitect, (4) dependency graph and web rendering via leanblueprint. Use when producing a navigable, publishable overview of the formalization — dependency DAGs, theorem status, proof summaries — from the Lean source. Integrates with lean-gateway (SK-07), lean-retro-methodology (SK-35), lean-quality-engine (SK-39), lean-enforcement (SK-36), lean-doc-improvement (SK-10), research-synthesis-engine (SK-60), and lean-specification (SK-05)."
---

# SK-61: Lean Blueprint Generator

Convert a large Lean 4 formalization into a navigable, publishable blueprint with dependency graphs, theorem status tracking, and LaTeX/web output.

---

## Part 1 — Tool Stack

| Tool | Role | Source |
|---|---|---|
| **LeanArchitect** | Extract `@[blueprint]` annotations → LaTeX node files | `https://github.com/hanwenzhu/LeanArchitect` |
| **leanblueprint** | plasTeX plugin: LaTeX → web + pdf + dependency graph | `https://github.com/PatrickMassot/leanblueprint` |
| **graphviz** | Render dependency DAGs (required by leanblueprint) | System package |
| **lake** | Build Lean project + `:blueprint` target | Lean toolchain |

### 1.1 Version Compatibility

| Component | Minimum Version | Notes |
|---|---|---|
| Lean 4 | v4.26.0+ | LeanArchitect tracks Lean releases |
| Mathlib | Compatible with Lean version | Must build cleanly first |
| Python | 3.9+ | For leanblueprint CLI |
| graphviz | System package | `brew install graphviz` (macOS) or `apt install graphviz libgraphviz-dev` (Linux) |
| leanblueprint | latest pip | `pip install leanblueprint` |
| LeanArchitect | `main` branch or tagged release | Add to lakefile.lean |

---

## Part 2 — Pipeline Architecture

The blueprint generation pipeline has 5 stages, orchestrated by the gateway (SK-07):

```
┌──────────────────────────────────────────────────────────────────────┐
│                    BLUEPRINT GENERATION PIPELINE                     │
│                                                                      │
│  Stage 1: ANALYZE    (read-only: module census + dependency DAG)     │
│       │                                                              │
│       ▼                                                              │
│  Stage 2: ANNOTATE   (add @[blueprint] attrs + LaTeX statements)     │
│       │                                                              │
│       ▼                                                              │
│  Stage 3: SCAFFOLD   (leanblueprint new + content.tex structure)     │
│       │                                                              │
│       ▼                                                              │
│  Stage 4: EXTRACT    (lake build :blueprint → .lake/build/blueprint) │
│       │                                                              │
│       ▼                                                              │
│  Stage 5: RENDER     (leanblueprint pdf + leanblueprint web)         │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 2.1 Agent Topology: Pipeline with Fan-Out

```
Gateway (SK-07)
  │
  ├── ANALYZE ── Explore agent (read-only scan of all modules)
  │     │
  │     ▼ (produces: module_inventory.json, dependency_edges.json)
  │
  ├── ANNOTATE ── 12 parallel module-annotator agents (fan-out)
  │     │         Each agent handles one Project module
  │     ▼ (produces: annotated .lean files with @[blueprint])
  │
  ├── SCAFFOLD ── Single scaffolder agent
  │     │         Creates blueprint/ directory, content.tex, macros
  │     ▼ (produces: blueprint/src/content.tex)
  │
  ├── EXTRACT ── lake build :blueprint (terminal command)
  │     │
  │     ▼ (produces: .lake/build/blueprint/library/*.tex)
  │
  └── RENDER ── leanblueprint pdf + web (terminal commands)
        │
        ▼ (produces: blueprint/web/, blueprint.pdf)
```

### 2.2 Skill Integration Map

| Stage | Primary Skill | Supporting Skills | Feedback To |
|---|---|---|---|
| ANALYZE | lean-retro-methodology (SK-35) | lean-enforcement (SK-36), lean-quality-engine (SK-39) | coverage_matrix.md |
| ANNOTATE | lean-specification (SK-05) | research-synthesis-engine (SK-60), domain skills (SK-12..21) | Zettelkasten |
| SCAFFOLD | lean-doc-improvement (SK-10) | lean-doc-requirements (SK-09) | content.tex |
| EXTRACT | lean-enforcement (SK-36) | mathlib-build (SK-29) | build logs |
| RENDER | lean-doc-improvement (SK-10) | — | deployed site |

---

## Part 3 — Stage 1: ANALYZE

### 3.1 Module Inventory

For each `.lean` module, collect:

```json
{
  "module": "Project.LyapunovStability",
  "file": "Project/LyapunovStability.lean",
  "lines": 2007,
  "imports": ["Project.PhasePortrait", "Project.CuspCatastrophe", ...],
  "theorems": [
    {"name": "lyapunov_zero_at_eq", "line": 76, "simp": true, "sorry": false},
    {"name": "lyapunovQuadratic_eq_zero_iff", "line": 108, "simp": true, "sorry": false}
  ],
  "definitions": [
    {"name": "PhasePoint", "line": 56, "kind": "structure"},
    {"name": "lyapunovQuadratic", "line": 62, "kind": "def"}
  ],
  "sections": ["§1 Quadratic Lyapunov", "§2 Time derivative", ...],
  "sorry_count": 0,
  "simp_count": 9
}
```

### 3.2 Dependency DAG Construction

Build the full project dependency graph at three granularities:

| Level | Nodes | Edges | Purpose |
|---|---|---|---|
| **Module-level** | 12 Project modules | `import` statements | High-level overview |
| **Section-level** | ~60 sections | Cross-references within modules | Mid-level structure |
| **Theorem-level** | ≥1,255 theorems/defs | `uses` in proofs (inferred by LeanArchitect) | Full dependency graph |

### 3.3 Blueprint Candidate Selection

Not every theorem needs `@[blueprint]`. Select candidates using these criteria:

| Category | Selection Rule | Priority |
|---|---|---|
| **Core definitions** | All `structure`, `inductive`, `class`, key `def` | Must include |
| **Main theorems** | Theorems referenced in the paper (coverage matrix) | Must include |
| **Bridge theorems** | Cross-module bridges (Ω-level integration) | Must include |
| **@[simp] lemmas** | Definitional equalities and biconditionals | Should include |
| **Instances** | `MetricSpace`, `Decidable`, `Inhabited`, `Fintype` | Should include |
| **Helper lemmas** | Internal module lemmas used only locally | May exclude |
| **Computational checks** | `decide` proofs, `#eval` | Exclude |

**Selection heuristic (automated):**
```
INCLUDE if:
  - referenced in coverage_matrix.md  OR
  - has docstring                      OR
  - is @[simp]                         OR
  - is an instance / structure / class OR
  - is imported by 2+ other theorems   OR
  - is a cross-module bridge (uses defs from imported module)

EXCLUDE if:
  - name starts with `_` or `aux`      AND
  - no docstring                        AND
  - used only within 10 lines of definition
```

---

## Part 4 — Stage 2: ANNOTATE

### 4.1 Annotation Strategy

For each selected theorem/definition, add `@[blueprint]` with appropriate options:

```lean
-- BEFORE (existing code):
/-- The quadratic Lyapunov function measures distance to equilibrium. -/
def lyapunovQuadratic (ϕ ϕstar : PhasePoint) : ℝ :=
  (ϕ.R - ϕstar.R) ^ 2 + (ϕ.D - ϕstar.D) ^ 2 +
  (ϕ.C - ϕstar.C) ^ 2 + (ϕ.V - ϕstar.V) ^ 2

-- AFTER (annotated for blueprint):
@[blueprint "def:lyapunov-quadratic"
  (statement := /-- The quadratic Lyapunov function
    $V(\phi, \phi^*) = \|\phi - \phi^*\|^2
    = \sum_{i \in \{R,D,C,V\}} (\phi_i - \phi^*_i)^2$
    measures the squared Euclidean distance from the
    equilibrium point $\phi^*$ in the 4-dimensional
    phase space. -/)]
def lyapunovQuadratic (ϕ ϕstar : PhasePoint) : ℝ :=
  (ϕ.R - ϕstar.R) ^ 2 + (ϕ.D - ϕstar.D) ^ 2 +
  (ϕ.C - ϕstar.C) ^ 2 + (ϕ.V - ϕstar.V) ^ 2
```

### 4.2 LaTeX Label Conventions

```
def:module-name            (definitions)
thm:module-theorem-name    (theorems)
lem:module-lemma-name      (lemmas)
inst:module-instance-name  (instances)
str:module-struct-name     (structures)
```

Module prefix mapping:

| Module | Prefix | Example |
|---|---|---|
| Tactics | `tac` | `thm:tac-geometric-decay` |
| QualityGates | `qg` | `thm:qg-pipeline-pass-iff` |
| CCVGating | `ccv` | `def:ccv-phiCCV` |
| PhaseClassification | `pc` | `thm:pc-classify-total` |
| PhasePortrait | `pp` | `def:pp-phaseState` |
| ProvenanceChain | `prov` | `thm:prov-link-preserves-root` |
| CuspCatastrophe | `cusp` | `thm:cusp-bistable-equilibria` |
| PipelineAdaptive | `pa` | `thm:pa-dgdUpdate-fixedpoint` |
| StochasticCCV | `sccv` | `thm:sccv-doeblin-contraction` |
| ReinforcementLearning | `rl` | `thm:rl-bellman-contraction` |
| AgenticSafety | `as` | `thm:as-allHold-iff` |
| LyapunovStability | `lyap` | `thm:lyap-governance-convergence` |

### 4.3 Statement Generation Rules

The `(statement := /-- ... -/)` LaTeX must:

1. Use standard LaTeX math mode (`$...$` for inline, `$$...$$` for display)
2. Reference other blueprint nodes via `\cref{label}` (not Lean names)
3. State the mathematical content, not the Lean encoding details
4. Use notation consistent with the paper (project-tufte.tex)
5. Be self-contained: a reader unfamiliar with Lean should understand the claim

### 4.4 Proof Documentation

For theorems with non-trivial proofs, add `blueprint_comment` or proof docstrings:

```lean
@[blueprint "thm:lyap-pos-def"
  (statement := /-- $V(\phi, \phi^*) = 0$ if and only if
    $\phi = \phi^*$ (positive definiteness). -/)]
theorem lyapunovQuadratic_eq_zero_iff (ϕ ϕstar : PhasePoint) :
    lyapunovQuadratic ϕ ϕstar = 0 ↔
    ϕ.R = ϕstar.R ∧ ϕ.D = ϕstar.D ∧ ϕ.C = ϕstar.C ∧ ϕ.V = ϕstar.V := by
  constructor
  · /-- Forward: $V = 0$ implies each squared
      difference is zero, hence coordinates agree. -/
    exact lyapunov_zero_iff_eq ϕ ϕstar
  · /-- Backward: equal coordinates yield
      $V = 0$ by direct computation. -/
    intro ⟨hR, hD, hC, hV⟩
    unfold lyapunovQuadratic
    rw [hR, hD, hC, hV]; ring
```

### 4.5 Dependency Override

LeanArchitect auto-infers dependencies from the proof. Override when:

- A `sorry` masks the real dependency → use `(proofUses := [dep1, dep2])`
- An internal helper should not appear in the graph → use `(proofUses := [-helper_lemma])`
- A cross-module bridge is semantically important but not syntactically used → add explicit `(uses := [bridge])`

---

## Part 5 — Stage 3: SCAFFOLD

### 5.1 Blueprint Directory Structure

```
blueprint/
├── src/
│   ├── content.tex          -- Main content (imports all chapters)
│   ├── chapter_tactics.tex  -- §1 Tactics
│   ├── chapter_qg.tex       -- §2 Quality Gates
│   ├── chapter_ccv.tex      -- §3 CCV Gating
│   ├── chapter_pc.tex       -- §4 Phase Classification
│   ├── chapter_pp.tex       -- §5 Phase Portrait
│   ├── chapter_prov.tex     -- §6 Provenance Chain
│   ├── chapter_cusp.tex     -- §7 Cusp Catastrophe
│   ├── chapter_pa.tex       -- §8 Pipeline Adaptive
│   ├── chapter_sccv.tex     -- §9 Stochastic CCV
│   ├── chapter_rl.tex       -- §10 Reinforcement Learning
│   ├── chapter_as.tex       -- §11 Agentic Safety
│   ├── chapter_lyap.tex     -- §12 Lyapunov Stability
│   ├── macros/
│   │   ├── common.tex       -- Shared LaTeX macros
│   │   ├── web.tex          -- Web-specific macros
│   │   └── print.tex        -- Print-specific macros
│   ├── web.tex              -- plasTeX driver
│   └── print.tex            -- PDF driver
└── references.bib           -- Bibliography
```

### 5.2 Content Template

Each chapter file (`chapter_*.tex`) follows this pattern:

```latex
% chapter_lyap.tex — Lyapunov Stability Analysis
\chapter{Lyapunov Stability Analysis}\label{ch:lyapunov}

This module formalizes stability analysis for the project Knowledge
Phase Portrait, constructing Lyapunov functions and proving
convergence of the governance orbit.

% Import the full module (alternative: individual \inputleannode)
\inputleanmodule{Project.LyapunovStability}
```

OR for finer control:

```latex
\chapter{Lyapunov Stability Analysis}\label{ch:lyapunov}

\section{Quadratic Lyapunov Function}

The quadratic Lyapunov function $V(\phi) = \|\phi - \phi^*\|^2$
is the standard energy function for linear stability analysis.

\inputleannode{def:lyap-phasepoint}
\inputleannode{def:lyap-lyapunov-quadratic}
\inputleannode{thm:lyap-zero-at-eq}
\inputleannode{thm:lyap-pos-def}
\inputleannode{thm:lyap-pos-away}

\section{Cusp Potential as Lyapunov Function}
% ...
```

### 5.3 Macros

```latex
% macros/common.tex
\newcommand{\phasepoint}{\phi}
\newcommand{\phaseeq}{\phi^*}
\newcommand{\lyapV}{V}
\newcommand{\ccvphi}{\varphi_{\mathrm{CCV}}}
\newcommand{\stresssq}{\sigma^2}
\newcommand{\govaction}{\mathbf{a}}
\newcommand{\valueV}{V^{\pi}}
\newcommand{\bellman}{\mathcal{B}_{\pi}}
```

---

## Part 6 — Stage 4: EXTRACT

### 6.1 lakefile Integration

Add LeanArchitect as a dependency:

```lean
-- In lakefile.lean (or lakefile.toml):
require LeanArchitect from git
  "https://github.com/hanwenzhu/LeanArchitect.git" @ "v4.28.0"
```

**TOML alternative:**
```toml
[[require]]
name = "LeanArchitect"
git = "https://github.com/hanwenzhu/LeanArchitect.git"
rev = "v4.28.0"
```

### 6.2 Module Import

Every annotated module must import `Architect`:

```lean
import Architect
import Project.PhasePortrait
-- ... rest of imports
```

### 6.3 Build Command

```bash
# Full build (Lean + blueprint extraction):
lake build :blueprint

# Build just one module's blueprint:
lake build Project.LyapunovStability

# JSON output for tooling:
lake build :blueprintJson
```

### 6.4 Output Location

```
.lake/build/blueprint/
├── library/
│   ├── Project.Tactics.tex
│   ├── Project.QualityGates.tex
│   ├── Project.CCVGating.tex
│   ├── Project.PhaseClassification.tex
│   ├── Project.PhasePortrait.tex
│   ├── Project.ProvenanceChain.tex
│   ├── Project.CuspCatastrophe.tex
│   ├── Project.PipelineAdaptive.tex
│   ├── Project.StochasticCCV.tex
│   ├── Project.ReinforcementLearning.tex
│   ├── Project.AgenticSafety.tex
│   └── Project.LyapunovStability.tex
└── nodes.json  (if :blueprintJson built)
```

---

## Part 7 — Stage 5: RENDER

### 7.1 Local Build Commands

```bash
# Prerequisite: leanblueprint installed
pip install leanblueprint

# Initialize (first time only):
leanblueprint new

# Build PDF:
leanblueprint pdf

# Build web:
leanblueprint web

# Serve locally (for development):
leanblueprint serve
# Opens http://0.0.0.0:8000/

# Check all \lean declarations exist:
leanblueprint checkdecls

# Build everything:
leanblueprint all
```

### 7.2 CI Integration

Add to `.github/workflows/blueprint.yml`:

```yaml
name: Build Blueprint
on:
  push:
    branches: [release/beta, main]

jobs:
  blueprint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Lean
        uses: leanprover/lean-action@v1
        with:
          use-github-cache: true
          build-args: ":blueprint"

      - name: Install Python deps
        run: |
          pip install leanblueprint

      - name: Install graphviz
        run: sudo apt-get install -y graphviz libgraphviz-dev

      - name: Build blueprint
        run: |
          leanblueprint checkdecls
          leanblueprint pdf
          leanblueprint web

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./blueprint/web
```

### 7.3 Output Structure

```
blueprint/
├── web/                     -- Static site (deploy to GitHub Pages)
│   ├── index.html           -- Main page with all theorems
│   ├── dep_graph.html       -- Interactive dependency graph
│   ├── dep_graph_full.html  -- Full dependency graph
│   └── ...
└── print/
    └── print.pdf            -- PDF version
```

---

## Part 8 — Project-specific Configuration

### 8.1 Module Ordering

The blueprint chapters follow the project dependency order (topological sort):

```
1. Tactics          (no Project imports — foundation)
2. QualityGates     (imports: Tactics)
3. CCVGating        (imports: Tactics)
4. PhaseClassification (imports: Tactics)
5. PhasePortrait    (imports: QualityGates, PhaseClassification, Tactics)
6. ProvenanceChain  (imports: Tactics)
7. CuspCatastrophe  (imports: Tactics)
8. PipelineAdaptive (imports: CCVGating, PhaseClassification, CuspCatastrophe, Tactics)
9. StochasticCCV    (imports: CCVGating, Tactics)
10. ReinforcementLearning (imports: PhaseClassification, QualityGates, Tactics)
11. AgenticSafety   (imports: CCVGating, QualityGates, Tactics)
12. LyapunovStability (imports: PhasePortrait, CuspCatastrophe, RL, AgenticSafety, Tactics)
```

### 8.2 Key Cross-Module Bridges to Highlight

These deserve special emphasis in the dependency graph:

| Bridge | From → To | Blueprint Label |
|---|---|---|
| CCV → Trust | CCVGating → AgenticSafety | `thm:as-toCCV-toAgentTrust` |
| Trust → CCV | AgenticSafety → CCVGating | `thm:as-agentAutonomy-plus-phiCCV` |
| Cusp → Lyapunov | CuspCatastrophe → LyapunovStability | `thm:lyap-cuspLyapunov-eq` |
| Phase → RL Reward | PhaseClassification → RL | `thm:rl-reward-eq` |
| Drift → Gates | StochasticCCV → CCVGating | `thm:ccv-positive-drift-relaxes` |
| Governance → Lyapunov | RL → LyapunovStability | `thm:lyap-governance-convergence` |
| Quality → Pipeline | QualityGates → PipelineAdaptive | via gate thresholds |

### 8.3 Color Coding

Configure node colors in `blueprint/src/web.tex`:

```latex
% Status colors matching Project quality dimensions
\graphcolor{stated}{green}{Stated (has Lean signature)}
\graphcolor{proved}{#9CEC8B}{Proved (sorry-free)}
\graphcolor{fully_proved}{#1CAC78}{Fully proved + reviewed}
\graphcolor{not_ready}{#FFAA33}{Not ready (informal only)}
\graphcolor{can_prove}{#A3D6FF}{Can formalize (deps ready)}
```

---

## Part 9 — Execution Checklist

### 9.1 First-Time Setup

```bash
# 1. Verify prerequisites
which graphviz dot python3 pip lake lean
pip install leanblueprint

# 2. Add LeanArchitect to lakefile
# (edit lakefile.lean or lakefile.toml — see §6.1)

# 3. Run lake update
lake update LeanArchitect

# 4. Verify base project still builds
lake build

# 5. Initialize blueprint directory
leanblueprint new
# Answer configuration questions:
#   Project name: Project
#   GitHub URL: https://github.com/r-irbe/tacit-mui
#   Blueprint path: blueprint  (default)

# 6. Add `import Architect` to each module that needs annotation
# 7. Add @[blueprint] attributes to selected theorems/definitions
# 8. Build blueprint extraction
lake build :blueprint

# 9. Write content.tex with \inputleanmodule or \inputleannode
# 10. Build final output
leanblueprint all
```

### 9.2 Incremental Updates

After adding new theorems:

```bash
# Annotate new theorems with @[blueprint]
# Then:
lake build :blueprint
leanblueprint all
```

### 9.3 Validation Checks

| Check | Command | Pass Criterion |
|---|---|---|
| Lean builds clean | `lake build` | Exit 0, 0 errors |
| Blueprint extracts | `lake build :blueprint` | Exit 0 |
| All `\lean` decls exist | `leanblueprint checkdecls` | Exit 0, no missing decls |
| PDF compiles | `leanblueprint pdf` | Exit 0, valid PDF |
| Web builds | `leanblueprint web` | Exit 0, valid HTML |
| Dependency graph renders | Open `dep_graph.html` | Non-empty, all nodes colored |

---

## Part 10 — Integration with Gateway (SK-07)

### 10.1 Gateway Routing

The gateway registers this skill as `SK-61`:

```
| `SK-61` | `lean-blueprint` | Blueprint generation | Blueprint Architect |
```

### 10.2 Trigger Events

| Trigger | Action | Skills Involved |
|---|---|---|
| `generate blueprint` | Full pipeline (stages 1–5) | SK-61, SK-07, SK-35, SK-36 |
| `update blueprint` | Incremental (stages 2, 4, 5) | SK-61 |
| `blueprint status` | Report annotation coverage | SK-61, SK-39 |
| `annotate module X` | Stage 2 for one module | SK-61, SK-05 |
| `deploy blueprint` | CI push to GitHub Pages | SK-61, SK-34 |

### 10.3 Feedback Loops

```
Blueprint generation ──► Reveals undocumented theorems ──► lean-doc-improvement (SK-10)
Blueprint checkdecls ──► Missing declaration errors ──► lean-enforcement (SK-36)
Dependency graph ──► Reveals circular or missing deps ──► lean-retro-methodology (SK-35)
Blueprint coverage ──► Gaps vs paper claims ──► lean-doc-requirements (SK-09)
Rendered blueprint ──► Paper appendix updates ──► lean-doc-improvement (SK-10)
```

### 10.4 Quality Engine Integration (SK-39)

Blueprint readiness is an additional quality dimension:

```
Q8 (Blueprint):  weight = 5
  score = (annotated_theorems / selected_theorems) × 100
  gate = soft (advisory, does not block milestones)
```

---

## Part 11 — Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| `import Architect` fails | LeanArchitect not in lakefile | Add `require LeanArchitect` to lakefile, run `lake update` |
| `lake build :blueprint` fails | Lean build error (not blueprint-specific) | Fix the underlying `lake build` error first |
| `leanblueprint checkdecls` reports missing | `\lean{name}` in LaTeX doesn't match Lean | Check namespaces — use fully qualified names |
| Dependency graph is empty | No `@[blueprint]` annotations | Add annotations to key theorems |
| Dependency graph has too many edges | LeanArchitect infers ALL constant usages | Use `(proofUses := [-internal_helper])` to suppress |
| LaTeX errors in plasTeX | Unsupported LaTeX in `(statement := /-- ... -/)` | Simplify LaTeX; plasTeX has limited macro support |
| VS Code syntax highlighting broken | `<` in LaTeX comment parsed as HTML | Replace `<a` with `< a` in LaTeX strings |
| Circular dependency in graph | Module A imports B imports A | Fix module import graph (should be DAG) |
| Heartbeat timeout after adding `import Architect` | LeanArchitect adds simp lemmas | Use `set_option maxHeartbeats 400000` if needed |

---

## Part 12 — Output Artifacts

The complete blueprint generation produces:

| Artifact | Location | Purpose |
|---|---|---|
| Annotated `.lean` files | `Project/*.lean` | Source with `@[blueprint]` |
| Extracted LaTeX per module | `.lake/build/blueprint/library/` | Generated node files |
| Blueprint source | `blueprint/src/` | Authored LaTeX content |
| PDF blueprint | `blueprint/print/print.pdf` | Printable document |
| Web blueprint | `blueprint/web/` | Navigable HTML site |
| Dependency graph | `blueprint/web/dep_graph.html` | Interactive DAG |
| JSON node data | `.lake/build/blueprint/nodes.json` | Machine-readable |
| Coverage report | `docs/tracking/blueprint_coverage.md` | % annotated |

---

## See also

- [`../../templates/Template_Index.md`](../../templates/Template_Index.md) — Template: Umbrella re-export modules
