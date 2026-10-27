---
name: "lean-formalization-breakdown"
description: |
  USE FOR: architectural deconstruction of Lean 4 codebases, censuses, DAG analysis, and verification audits.
  DO NOT USE FOR: authoring new Lean proofs (@lean-proof), simple typo fixes (@lean-doc-improvement).
  TRIGGERS: formalization-breakdown, proof-breakdown, census, landmark-dag, lean-breakdown.
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

# 1. Run automated census and DAG topology analysis
> Authoritative protocol for architectural deconstruction and multi-wave analysis
> of monumental Lean 4 formalizations (derived from the Fermat's Last Theorem
> 28-wave and Navier-Stokes & Euler 8-wave campaigns).
## Routing
- **USE FOR:**
  - Deconstructing monumental Lean 4 codebases (100 to 60,000+ modules) into structured, human-navigable
  mathematical layers.
  - Running automated static and kernel censuses (modules, lines, theorems, lemmas, definitions, structures,
  axioms, sorries).
  - Verifying import DAG topology, detecting cycles, computing topological layer depth and longest dependency
  paths.
  - Identifying landmark theorems, boundary adapters, and comparator challenge interfaces.
  - Decomposing mathematical proof engines into sequential multi-stage pipelines.
  - Mapping formal mathematical substrates into downstream packages and domain libraries.
## Workflow
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

## Recovery & STOP

- If `formalization_breakdown.py` detects an import cycle or unresolvable path, halt downstream wave scaffolding and report the structural blocker first.
- If `sorry` declarations appear in implementation modules, isolate them in Wave 2 before claiming substrate readiness.

## Handoffs

- **Predecessors**: `agent:gateway`, `skill:lean-blueprint`
- **Successors**: `skill:lean-pedagogical-exposition` (human-readable math and pedagogical synthesis), `skill:lean-zettelkasten` (knowledge graph storage),
  `skill:lean-enforcement` (CI gate enforcement).
- **Source Guide**: [`references/formalization_breakdown_guide.md`](../../references/formalization_breakdown_guide.md)

## Detailed reference

Full reference and lookup tables:
[`references/lean-formalization-breakdown-handbook.md`](../../references/lean-formalization-breakdown-handbook.md).

## See also

- [`../../references/lean-formalization-breakdown-handbook.md`](../../references/lean-formalization-breakdown-handbook.md) -- Handbook
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Top-level skill router
