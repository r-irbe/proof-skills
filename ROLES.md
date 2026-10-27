For a detailed explanation of the Swarm methodology and multi-agent theory, see [`references/swarm_methodology.md`](references/swarm_methodology.md).

# Multi-Agent Lifecycle Roles (5 Pure Role-Actor Containers + 23 Soul Overlays)

`proof-skills` enforces a strict separation between the **5 Pure Role-Actor Containers** (`agents/{specifier,prover,auditor,editor,gardener}.md`) and the **23 Specialist Soul Overlays** (`agents/souls/*.md`, bound via [`agents/facets/registry.json`](agents/facets/registry.json)).

## 1. Specifier (`agents/specifier.md` -- Role #1)
- **Role-Scoped `lean-lsp` MCP Allowlist**: `lean_search`, `lean_lookup_symbol`, `lean_decl_references`, `lean_module_hierarchy`, `lean_diagnostics`, `lean_counterexample_search`, `lean_blueprint`, `lean_metrics`
- **Soul Overlays (`agents/souls/`)**: `lean-spec-architect`, `formalization-breakdown-curator`, `formalization-dag-navigator`, `premise-retrieval-specialist`, `research-alpha-foundations`, `research-beta-dynamics`, `research-gamma-epistemics`, `research-delta-systems`, `research-epsilon-bridge`
- **Skills**: `lean-gateway`, `lean-specification`, `lean-blueprint`, `lean-formalization-breakdown`, `lean-dag-visualizer`, `lean-doc-requirements`, `lean-research`, `epistemic-discovery-engine`, `epistemic-mapping`, `research-council`
- **Output**: Three-part `.lean` theorem specifications with `sorry` skeletons, `@[blueprint]` DAG annotations, and counterexample-screened declarations
- **Stop Condition**: Clean elaboration without type errors and 0 Plausible counterexamples -> Hands off to `prover`

## 2. Prover (`agents/prover.md` -- Role #2)
- **Role-Scoped `lean-lsp` MCP Allowlist**: `lean_goal`, `lean_diagnostics`, `lean_counterexample_search`, `lean_lookup_symbol`, `lean_decl_references`, `lean_search`, `lean_exec`, `lean_resync`
- **Soul Overlays (`agents/souls/`)**: `lean-proof-builder`, `counterexample-falsification-hunter`, `sair-kernel-optimizer`, `cross-itp-porter`
- **Skills**: `lean-proof`, `lean-proof-repair`, `lean-core-only`, `lean-setup`, `lean-build`, `lean-bisect`, `lean-mwe`, `counterexample-first-proving`, `lean-sair-kernel-optimization`, Multi-Prover Adapters (`itp-cross-porting`, `rocq-proof-adapter`, `isabelle-isar-adapter`, `hol-metamath-adapter`), and Unified Domain Facet skills (`lean-math-foundations`, `lean-math-discrete`, `lean-math-analysis`, `lean-math-optimization`, `lean-math-dynamical`, `lean-math-stochastic`, `lean-competitive-math`, `lean-bigraph-modeling`, `lean-convergence-verification`, `lean-ai-formalization`, `lean-applied-reasoning`, `lean-causal-reasoning`, `lean-knowledge-formalization`, `lean-nested-learning`, `lean-security-formalization`)
- **Rules**:
  - No `trace_state` or diagnostic comments in source files; inspect live state via `lean-lsp` MCP (`lean_goal`, `lean_diagnostics`)
  - Run `lean_counterexample_search` (Galois-pruned Plausible) before manual proof search on suspect statements
  - Never alter theorem signatures or hypothesis types to make a proof pass
  - Tactic hierarchy: `rfl` -> `decide`/`norm_num` -> `grind` -> `omega` / `linarith` -> `simp only` -> `aesop` -> `exact?`
- **Stop Condition**: All goals closed (`0 sorry`) -> Hands off to `auditor`

## 3. Auditor (`agents/auditor.md` -- Role #3, Strictly Read-Only)
- **Role-Scoped `lean-lsp` MCP Allowlist**: `lean_diagnostics`, `lean_axiom_closure`, `lean_metrics`, `lean_counterexample_search`, `lean_lookup_symbol`, `lean_decl_references`, `lean_module_hierarchy`, `lean_search`
- **Soul Overlays (`agents/souls/`)**: `proof-reviewer`, `enforcement-auditor`, `abstract-interp-vacuity-auditor`, `council-sigma-soundness`, `council-phi-faithfulness`, `council-nu-novelty`, `council-tau-tactics`, `council-omega-chair`
- **Skills**: `lean-proof-review`, `lean-enforcement`, `lean-axiom-closure`, `lean-replay-verification`, `lean-tautology-triage`, `lean-deep-audit`, `lean-quality-engine`, `lean-review-council`, `lean-retroactive-audit`, `ai-guard-judge-eval`
- **Output**: Verified axiom closure (`[propext, Classical.choice, Quot.sound]`), 4-layer soundness/vacuity certificates, kernel-replayed proofs, zero warnings
- **Stop Condition**: All linters, static analyzers (`lean-analyzer` WASM), and `lake build` green -> Hands off to `editor` or `gardener`

## 4. Editor (`agents/editor.md` -- Role #4)
- **Role-Scoped `lean-lsp` MCP Allowlist**: `lean_goal`, `lean_diagnostics`, `lean_lookup_symbol`, `lean_decl_references`, `lean_search`, `lean_blueprint`, `lean_metrics`
- **Soul Overlays (`agents/souls/`)**: `math-pedagogy-author`
- **Skills**: `lean-proof-refactor`, `lean-pedagogical-exposition`, `lean-doc-improvement`, `lean-doc-feedback`, `lean-report`, `research-synthesis-engine`
- **Output**: Decomposed helper lemmas, synchronized LaTeX reports, and textbook-grade mathematical exposition
- **Stop Condition**: Proof length within threshold, zero regressions, and documentation synchronized -> Hands off to `gardener`

## 5. Gardener (`agents/gardener.md` -- Role #5)
- **Role-Scoped `lean-lsp` MCP Allowlist**: `lean_search`, `lean_lookup_symbol`, `lean_decl_references`, `lean_module_hierarchy`, `lean_metrics`, `lean_axiom_closure`
- **Soul Overlays (`agents/souls/`)**: `lean-retro-facilitator`
- **Skills**: `lean-zettelkasten`, `lean-retro-methodology`, `lean-upstream-porting`, `lean-pr`, `lean-package-research`, `lean-vendor-substrate`, `lean-integration-protocol`, `math-product-management`, `math-project-management`, `math-strategy-studio`, `applied-engineering-disciplines`, `applied-legal-reasoning`, `applied-data-information-security`
- **Stop Condition**: New patterns indexed in Zettelkasten (`zettelkasten/`) and Kuzu knowledge graph, upstream PR dossiers prepared

## Handoff Protocol
- **Format**: JSON schema v2.0 defined in [`templates/handoff_protocol.json`](templates/handoff_protocol.json), binding `from_role`, `to_role`, `soul_overlay`, and `facet_pack` via [`agents/facets/registry.json`](agents/facets/registry.json).
