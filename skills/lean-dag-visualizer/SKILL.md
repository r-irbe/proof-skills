---
name: "lean-dag-visualizer"
description: |
  USE FOR: launching interactive Lean 4 formalization DAG visualizers and Tufte proof-walk marginalia.
  DO NOT USE FOR: authoring new Lean proofs (@lean-proof), compiling PlasTeX PDFs (@lean-blueprint).
  TRIGGERS: dag-visualizer, proof-walk, visualize-formalization, lean-visualizer, show-dag.
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

# 1. Launch visualizer for any package
> Authoritative protocol for generating, extracting, and interactively inspecting
> Lean 4 formalization DAGs and Tufte proof-walk cards across projects, subpackages,
> and monumental mathematical codebases.
## Routing
- **USE FOR:**
  - Launching the standalone zero-dependency HTML5/SVG formalization DAG visualizer for any Lean 4 project or
  directory.
  - Inspecting topological layer depth, longest dependency paths, and landmark proof milestones.
  - Visualizing mathematical engines for domain subpackages (`packages/stochastic-ccv`,
  `packages/agentic-safety`,
    `packages/cusp-catastrophe`, etc.).
  - Visualizing primary formalization repositories (`MyProject`, `fermats-last-theorem`,
  `NavierStokesAndEuler`).
  - Generating and caching visualizer-compatible graph JSONs (`nodes` and `edges`) via
  `formalization_breakdown.py --json-graph`.
## Workflow
### Workflow A: Autonomous AI Session Inspection
1. **Analyze Target**: Run `python3 scripts/lean/formalization_breakdown.py <target_path> --format summary` to
  check module count,
  depth,
   and sorries.
2. **Generate Graph JSON**: Emit graph JSON to temporary or cached location:
   ```bash
   python3 scripts/lean/formalization_breakdown.py <target_path> --json-graph .cache/graphs/<slug>.json
   ```
3. **Headless Verification / Serving**: Start launcher with `--no-browser` if HTTP API interaction is needed,
  or inspect node
  topology
   directly from the JSON.
4. **Synthesize Findings**: Report topological depth, critical proof path, and key milestone declarations to
  the operator.
### Workflow B: Interactive Human-in-the-Loop Visual Walk
1. **Launch Target**:
   ```bash

## Recovery & STOP

- If graph extraction reports an import cycle, stop rendering and resolve the circular dependency before ratifying the DAG cache.
- On headless or SSH hosts without a display server, pass `--no-browser` and inspect `.cache/graphs/<slug>.json` directly.

## Handoffs

- **Predecessors**: `skill:lean-formalization-breakdown` (static census and topological depth), `skill:lean-blueprint` (declaration LaTeX scaffolding).
- **Successors**: `skill:lean-pedagogical-exposition` (authoring mathematical narrative for nodes), `skill:lean-enforcement` (ratifying acyclicity in CI).
- **Tool Location**: [`tools/visualizer/`](../../tools/visualizer/)

## Detailed reference

Full reference and lookup tables:
[`references/lean-dag-visualizer-handbook.md`](../../references/lean-dag-visualizer-handbook.md).

## See also

- [`../../references/lean-dag-visualizer-handbook.md`](../../references/lean-dag-visualizer-handbook.md) -- Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
