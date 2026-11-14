---
name: lean-blueprint-handbook
description: Reference handbook for @lean-blueprint.
extracted_from: skills/lean-blueprint/SKILL.md
---

## Quick-Lookup Indexing Tables (`mathcomp-skills` Three-Entry-Point Pattern)

### Table 1: Goal-Shape-First (`templates` Entry Point)

| Goal / Term Shape | Primary Tactic / Pattern | Canonical Recipe / Notes |
| :--- | :--- | :--- |
| Declaration ready for dependency tracking | `@[blueprint "lem:foo" (statement := /-- ... -/)]` | Annotate lean declaration and link upstream lemma labels |
| Large multi-directory Lean codebase | 8-wave formalization breakdown + DAG census | Extract Layer 0..4 critical path via `lean_module_hierarchy` |

### Table 2: Intent-First (`phrasebook` Entry Point)

| User / Engineer Intent | Recommended Tool / Idiom | Actionable Recipe |
| :--- | :--- | :--- |
| Scaffold a LeanBlueprint / LeanArchitect tree | `lean_blueprint(action: "scaffold" | "skeleton")` | Verify acyclic label graph before batch proving |
| Launch interactive DAG / proof-walk visualizer | DAG export + marginalia mapping | Bind nodes to verified `.ilean` declarations |

### Table 3: Error / Bottleneck-First (`errors` Entry Point)

| Symptom / Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Cyclic dependency between blueprint nodes | Forward lemma reference contradicts Lean import order | Run `lean_module_hierarchy` and split shared definitions into `.Defs` |
| Orphan `@[blueprint]` tag not appearing in graph | Label omitted from chapter `\lean{...}` / root import | Ensure module is imported by root `<Project>.lean` |

---

# lean-blueprint

> ⚠️ **MANDATORY** (hot-tier): the gates in §Behavioural rules and the Persist
> step in §Workflow are CI-enforced. Skipping Persist = incomplete, regardless
> of artefact quality (FSIA-R-11-09).

## Routing

- **USE FOR:** generating a navigable formal blueprint from a Lean 4 codebase; annotating definitions and theorems with `@[blueprint]`; scaffolding
  `blueprint/` with `leanblueprint new`; building blueprint LaTeX via `lake build :blueprint`; rendering the dependency graph and web view.
- **DO NOT USE FOR:** authoring new Lean proofs (use `@lean-proof`); opening Lean/Mathlib PRs (use `@lean-pr`); editing prose docs (use
  `@lean-doc-improvement`).
- **TRIGGERS:** blueprint, leanblueprint, LeanArchitect, dependency-graph.

## Behavioural rules (G-*)

- **G-1** (MUST): The blueprint pipeline MUST run the five stages in order (analyze → annotate → scaffold → extract → render). [Trace: AC-01]
- **G-2** (MUST): Every `@[blueprint]` annotation MUST carry a matching LaTeX statement in `content.tex`. [Trace: AC-02]
- **G-3** (MUST NOT): The skill MUST NOT mutate files outside `blueprint/` and the annotated `.lean` modules. [Trace: AC-03]
- **G-4** (SHOULD): The skill SHOULD fan out per-module annotators when ≥6 modules are in scope. [Trace: AC-04]
- **G-5** (MUST): `lake build :blueprint` MUST succeed before render. [Trace: AC-05]
- **G-6** (MUST): `leanblueprint pdf` and `leanblueprint web` MUST both produce artefacts under `blueprint/`. [Trace: AC-06]
- **G-7** (SHOULD NOT): The skill SHOULD NOT re-annotate modules already carrying complete `@[blueprint]` coverage. [Trace: AC-07]
- **G-8** (MUST): On any guard failure the skill MUST escalate per §Recovery & STOP. [Trace: AC-08]

## Workflow

1. **Discover** [discover] -- read inputs, list Lean modules, locate `lakefile.lean` and prior `blueprint/`, and audit current coverage via `lean_blueprint`
   (`{"action": "status", "formalizationDir": "...", "blueprintDir": "..."}`).
2. **Plan** [discover] -- propose per-module annotator fan-out; generate proof outlines with `lean_blueprint` (`{"action": "skeleton", "symbol": "..."}`) or
   `lean_blueprint(action: "skeleton")`; STOP if confidence < 80 %.
3. **Annotate** [execute] -- scaffold LaTeX entries via `lean_blueprint` (`{"action": "scaffold", "symbol": "..."}`) or `lean_blueprint(action: "scaffold")`, and apply
   `@[blueprint]` annotations and LaTeX statements inside owned scope.
4. **Build** [execute] -- run `lake build :blueprint`.
5. **Verify** [validate] -- confirm artefacts exist and re-run `lean_blueprint(action: "status")` to verify 0 premature `\leanok` and 0 ghost nodes; max 3
   retries then escalate.
6. **Render** [execute] -- run `leanblueprint pdf` and `leanblueprint web`.
7. **Persist** [persist] *(MANDATORY, FSIA-R-11-09)* -- commit changes, update state tracker, tick `tasks.md`. Skipping Persist = incomplete.

## Recovery & STOP

- `lake build :blueprint` fails ×3 → STOP, escalate to human.
- Scope drift (touch outside `blueprint/` or annotated `.lean` files) → immediate STOP, re-anchor.
- Confidence < 80 % on annotation strategy → STOP, ask.
- Context degradation signals (≥2 from AGENTS.md) → recommend fresh session.

## Handoffs

- **Predecessors / successors**: see FM `handoffs` (grammar from ADR-0080).
- **Source spec**: `specs/lean/blueprint/requirements.md` -- every G-rule traces to an AC there.
- **Related ADRs**: ADR-0076, ADR-0080.

## Common failure modes

> AI agents commonly: skip the Persist step; over-annotate stable modules;
> re-run `lake build` instead of escalating on third failure.
> Full registry: GUARDRAILS.md §Agent failure taxonomy.

---

## Annex: Interactive Formalization DAG Visualizer & Proof-Walk Marginalia

# lean-dag-visualizer

> Authoritative protocol for generating, extracting, and interactively inspecting
> Lean 4 formalization DAGs and Tufte proof-walk cards across projects, subpackages,
> and monumental mathematical codebases.

## Routing

- **USE FOR:**
  - Launching the standalone zero-dependency HTML5/SVG formalization DAG visualizer for any Lean 4 project or directory.
  - Inspecting topological layer depth, longest dependency paths, and landmark proof milestones.
  - Visualizing mathematical engines for domain subpackages (`packages/stochastic-ccv`, `packages/agentic-safety`, `packages/cusp-catastrophe`, etc.).
  - Visualizing primary formalization repositories (`MyProject`, `fermats-last-theorem`, `NavierStokesAndEuler`).
  - Generating and caching visualizer-compatible graph JSONs (`nodes` and `edges`) via `formalization_breakdown.py --json-graph`.
  - Autonomous AI session configuration: serving graphs headlessly via `--no-browser` and retrieving network metrics without GUI dependencies.
- **DO NOT USE FOR:**
  - Interactive Lean 4 tactic theorem proving (use `@lean-proof`).
  - Compiling PlasTeX LaTeX blueprints into PDF or static web books (use `@lean-blueprint`).
  - Authoring human-readable mathematical narratives and pedagogy (use `@lean-pedagogical-exposition`).
- **TRIGGERS:** `dag-visualizer`, `proof-walk`, `visualize-formalization`, `lean-visualizer`, `show-dag`.

## Behavioural Rules (G-*)

- **G-1** (MUST): The visualizer application MUST remain 100% self-contained and zero-dependency (no Node.js runtime, no npm packages, no external CDN
  requests). It must function completely offline and follow the scoped Unicode policy (`INV-001`).
- **G-2** (MUST): Graph extraction MUST verify Directed Acyclic Graph (DAG) topology. Cycles must be reported as critical structural failures before rendering.
- **G-3** (MUST): When blueprint LaTeX exists (`blueprint/src/content.tex`), declaration-level graph extraction MUST be prioritized over module-level
  import graphs.
- **G-4** (SHOULD): AI sessions running headlessly MUST supply `--no-browser` to avoid GUI process hangs on headless hosts or remote SSH terminals.
- **G-5** (MUST): The two-phase DAG lifecycle MUST be respected: on-demand graph generation during orientation/discovery, and authoritative cache
  ratification during the verification phase.
- **G-6** (MUST): Every declaration node MUST link its formal signature, module file path, line number, mathematical intuition narrative, proof milestones,
  and bidirectional premise/dependent tags.

## Two-Phase Lifecycle: Entry Analysis vs. Verification Ratchet

Formalization DAGs serve two distinct operational purposes during the formalization lifecycle:

```
+-----------------------------------------------------------------------------+
| Phase 1: Entry Orientation & Discovery (Beginning of Task)                 |
|   - Trigger: Agent cold-starts or human researcher explores formalization.  |
|   - Action: Fast static scan via formalization_breakdown.py (<1s).          |
|   - Purpose: Maps the terrain, measures topological depth, pinpoints        |
|     critical paths, and highlights unproven sorries for sprint planning.     |
+-----------------------------------------------------------------------------+
                                       |
                                       v (Proof Implementation & Refactoring)
+-----------------------------------------------------------------------------+
| Phase 2: Verification Ratchet & Certified Cache (Verification Phase)        |
|   - Trigger: Running CI gates (verify_formalization_breakdowns.py).         |
|   - Action: Asserts strict acyclicity, 0 unauthorized sorries, and          |
|     blueprint declaration coverage across all registered formalizations.     |
|   - Purpose: Emits certified graph JSON to .cache/graphs/<target>.json.     |
|   - Result: Visualizer always displays the authoritative verified state.    |
+-----------------------------------------------------------------------------+
```

## Workflows

### Workflow A: Autonomous AI Session Inspection
1. **Analyze Target**: Run `python3 scripts/lean/formalization_breakdown.py <target_path> --format summary` to check module count, depth, and sorries.
2. **Generate Graph JSON**: Emit graph JSON to temporary or cached location:
   ```bash
   python3 scripts/lean/formalization_breakdown.py <target_path> --json-graph .cache/graphs/<slug>.json
   ```
3. **Headless Verification / Serving**: Start launcher with `--no-browser` if HTTP API interaction is needed, or inspect node topology directly from the JSON.
4. **Synthesize Findings**: Report topological depth, critical proof path, and key milestone declarations to the operator.

### Workflow B: Interactive Human-in-the-Loop Visual Walk
1. **Launch Target**:
   ```bash
   python3 scripts/lean/launch_visualizer.py packages/stochastic-ccv
   ```
2. **Interact**:
   - The launcher automatically builds the graph, starts the local server (`tools/visualizer/serve.py`), and opens the default browser to
     `http://127.0.0.1:8088/`.
   - The operator inspects nodes, selects declarations to read Tufte cards, and navigates premise tags.
3. **Export**: Click **"Export SVG"** to capture vector diagrams for papers, slides, or reports.

## Tooling Commands

```bash
# 1. Launch visualizer for any package
python3 scripts/lean/launch_visualizer.py packages/stochastic-ccv

# 2. Launch visualizer for a project formalization
python3 scripts/lean/launch_visualizer.py MyProject

# 3. Launch preloaded corpus presets
python3 tools/visualizer/serve.py --corpus flt
python3 tools/visualizer/serve.py --corpus nse
python3 tools/visualizer/serve.py --corpus markov

# 4. Extract graph JSON without launching server
python3 scripts/lean/formalization_breakdown.py <path> --json-graph graph.json

# 5. Run headless server for SSH port forwarding
python3 tools/visualizer/serve.py --graph graph.json --port 8090 --no-browser
```

## Recovery

- If graph extraction reports an import cycle, stop rendering and resolve the circular dependency before ratifying the DAG cache.
- On headless or SSH hosts without a display server, pass `--no-browser` and inspect `.cache/graphs/<slug>.json` directly.

## Handoffs

- **Predecessors**: `skill:lean-formalization-breakdown` (static census and topological depth), `skill:lean-blueprint` (declaration LaTeX scaffolding).
- **Successors**: `skill:lean-pedagogical-exposition` (authoring mathematical narrative for nodes), `skill:lean-enforcement` (ratifying acyclicity in CI).
- **Tool Location**: [`tools/visualizer/`](../../tools/visualizer/)

---

## Annex: Architectural Formalization Breakdown & Landmark Census

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

- **G-1** (MUST): Always run an automated static census (`scripts/lean/formalization_breakdown.py`) before formulating qualitative claims or estimates.
  Never cite declaration counts from memory or stale documentation.
- **G-2** (MUST): Verify strict Directed Acyclic Graph (DAG) topology. Report cycle violations immediately as hard blockers. Measure topological depth and
  identify the critical dependency path.
- **G-3** (MUST): Audit the complete axiom profile. Implementation modules must have zero `sorry` and rely exclusively on foundational Lean 4 axioms
  (`propext`, `Quot.sound`, `Classical.choice`). Any custom axiom must be flagged.
- **G-4** (MUST): Formulate the mathematical proof engine in a clear multi-stage architecture (e.g., Incompressible coordinate deformation -> Anisotropic
  packet scaling -> BKM logarithmic Gronwall reduction).
- **G-5** (MUST): Map extracted substrates into downstream modules using standardized proof templates and domain substitution tables (`subst_table.json`).
- **G-6** (MUST): Generate dual-kernel verification contracts and automated pytest / shell test gates for every transferred substrate.
- **G-7** (MUST): Follow the configured scoped Unicode policy (INV-001) in generated documentation and plans. Mathematical notation and scripts are allowed; reject dangerous carriers and configured substitutions.
- **G-8** (MUST): Resolve and verify all cited file paths against the physical filesystem before citing them (AOR-2 / INV-014).

## Workflow (8-Wave Deconstruction)

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
python3 scripts/lean/formalization_breakdown.py <path/to/formalization> --scaffold-plan -o docs/plans/PLAN-<NAME>.md

# 3. Emit Lean Blueprint LaTeX skeleton
python3 scripts/lean/formalization_breakdown.py <path/to/formalization> --scaffold-blueprint -o blueprint/src/content.tex

# 4. Export JSON metrics for knowledge graph ingestion
python3 scripts/lean/formalization_breakdown.py <path/to/formalization> --format json -o breakdown-metrics.json
```

## Recovery

- If `formalization_breakdown.py` detects an import cycle or unresolvable path, halt downstream wave scaffolding and report the structural blocker first.
- If `sorry` declarations appear in implementation modules, isolate them in Wave 2 before claiming substrate readiness.

## Handoffs

- **Predecessors**: `agent:gateway`, `skill:lean-blueprint`
- **Successors**: `skill:lean-pedagogical-exposition` (human-readable math and pedagogical synthesis), `skill:lean-zettelkasten` (knowledge graph storage),
  `skill:lean-enforcement` (CI gate enforcement).
- **Source Guide**: [`references/formalization_breakdown_guide.md`](../../references/formalization_breakdown_guide.md)

