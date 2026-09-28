---
name: "lean-dag-visualizer"
description: |
  USE FOR: launching interactive standalone Lean 4 formalization DAG visualizers, extracting topological dependency graphs, inspecting Tufte proof-walk marginalia for Lean 4 projects, domain subpackages (packages/), and research formalizations (docs/easci/lean/EASCI).
  DO NOT USE FOR: authoring new Lean proofs (use @lean-proof), compiling PlasTeX LaTeX PDFs (use @lean-blueprint).
  TRIGGERS: dag-visualizer, proof-walk, visualize-formalization, lean-visualizer, show-dag, formalization-dag.
tier: "hot"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ["skill:lean-formalization-breakdown", "skill:lean-blueprint"]
  successors: ["skill:lean-pedagogical-exposition", "skill:lean-enforcement"]
metadata:
  version: "0.1.0"
  source_spec: "references/formalization_breakdown_guide.md"
  last_reviewed: "2026-09-28"
---

# lean-dag-visualizer

> Authoritative protocol for generating, extracting, and interactively inspecting
> Lean 4 formalization DAGs and Tufte proof-walk cards across projects, subpackages,
> and monumental mathematical codebases.

## Routing

- **USE FOR:**
  - Launching the standalone zero-dependency HTML5/SVG formalization DAG visualizer for any Lean 4 project or directory.
  - Inspecting topological layer depth, longest dependency paths, and landmark proof milestones.
  - Visualizing mathematical engines for domain subpackages (`packages/stochastic-ccv`, `packages/agentic-safety`, `packages/cusp-catastrophe`, etc.).
  - Visualizing primary formalization repositories (`docs/easci/lean/EASCI`, `docs/easci/lean/fermats-last-theorem`, `docs/easci/lean/NavierStokesAndEuler`).
  - Generating and caching visualizer-compatible graph JSONs (`nodes` and `edges`) via `formalization_breakdown.py --json-graph`.
  - Autonomous AI session configuration: serving graphs headlessly via `--no-browser` and retrieving network metrics without GUI dependencies.
- **DO NOT USE FOR:**
  - Interactive Lean 4 tactic theorem proving (use `@lean-proof`).
  - Compiling PlasTeX LaTeX blueprints into PDF or static web books (use `@lean-blueprint`).
  - Authoring human-readable mathematical narratives and pedagogy (use `@lean-pedagogical-exposition`).
- **TRIGGERS:** `dag-visualizer`, `proof-walk`, `visualize-formalization`, `lean-visualizer`, `show-dag`.

## Behavioural Rules (G-*)

- **G-1** (MUST): The visualizer application MUST remain 100% self-contained and zero-dependency (no Node.js runtime, no npm packages, no external CDN requests). It must function completely offline and adhere strictly to 7-bit ASCII (`INV-001`).
- **G-2** (MUST): Graph extraction MUST verify Directed Acyclic Graph (DAG) topology. Cycles must be reported as critical structural failures before rendering.
- **G-3** (MUST): When blueprint LaTeX exists (`blueprint/src/content.tex`), declaration-level graph extraction MUST be prioritized over module-level import graphs.
- **G-4** (SHOULD): AI sessions running headlessly MUST supply `--no-browser` to avoid GUI process hangs on headless hosts or remote SSH terminals.
- **G-5** (MUST): The two-phase DAG lifecycle MUST be respected: on-demand graph generation during orientation/discovery, and authoritative cache ratification during the verification phase.
- **G-6** (MUST): Every declaration node MUST link its formal signature, module file path, line number, mathematical intuition narrative, proof milestones, and bidirectional premise/dependent tags.

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
   python3 tools/visualizer/launch.py packages/stochastic-ccv
   ```
2. **Interact**:
   - The launcher automatically builds the graph, starts the local server, and opens the default browser to `http://127.0.0.1:8088/`.
   - The operator inspects nodes, selects declarations to read Tufte cards, and navigates premise tags.
3. **Export**: Click **"Export SVG"** to capture vector diagrams for papers, slides, or reports.

## Tooling Commands

```bash
# 1. Launch visualizer for any package
python3 tools/visualizer/launch.py packages/stochastic-ccv

# 2. Launch visualizer for EASCI formalization
python3 tools/visualizer/launch.py docs/easci/lean/EASCI

# 3. Launch preloaded corpus presets
python3 tools/visualizer/launch.py --preset flt
python3 tools/visualizer/launch.py --preset nse
python3 tools/visualizer/launch.py --preset easci

# 4. Extract graph JSON without launching server
python3 scripts/lean/formalization_breakdown.py <path> --json-graph graph.json

# 5. Run headless server for SSH port forwarding
python3 tools/visualizer/serve_visualizer.py --graph graph.json --port 8090 --no-browser
```

## Handoffs

- **Predecessors**: `skill:lean-formalization-breakdown` (static census and topological depth), `skill:lean-blueprint` (declaration LaTeX scaffolding).
- **Successors**: `skill:lean-pedagogical-exposition` (authoring mathematical narrative for nodes), `skill:lean-enforcement` (ratifying acyclicity in CI).
- **Tool Location**: [`docs/easci/lean/skills/tools/visualizer/`](../../tools/visualizer/)
