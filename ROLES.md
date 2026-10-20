For a detailed explanation of the Swarm methodology and multi-agent theory, see [`references/swarm_methodology.md`](references/swarm_methodology.md).

# Multi-Agent Lifecycle Roles

## 1. Specifier
- **Skills**: `lean-specification`, `lean-blueprint`, `lean-dag-visualizer`, `lean-formalization-breakdown`, `lean-mwe`, `lean-doc-requirements`, `lean-ai-formalization`, `lean-knowledge-formalization`, `math-product-management`, `math-project-management`, `math-strategy-studio`
- **Sub-agents**: `formalization-breakdown-curator`, `formalization-dag-navigator`
- **Output**: Well-typed `.lean` declarations with `sorry` placeholders, dependency DAGs, and blueprint cards
- **Stop Condition**: Clean elaboration without type errors -> Hands off to Prover

## 2. Prover
- **Skills**: `lean-proof`, `lean-core-only`, `lean-setup`, `lean-build`, `lean-gateway`, plus Domain Facet skills (`lean-math-foundations`, `lean-math-discrete`, `lean-math-analysis`, `lean-math-optimization`, `lean-math-dynamical`, `lean-math-stochastic`, `lean-competitive-math`, `lean-bigraph-modeling`, `lean-convergence-verification`, `math-algebra-category`, `math-graph-knowledge`, `math-topology-analysis`, `math-nonlinear-dynamics`, `math-measure-probability`, `math-time-series`, `math-optimization-game`, `lean-applied-reasoning`, `lean-causal-reasoning`, `lean-nested-learning`, `ai-agentic-evolving`, `ai-causal-deontic`, `ai-commonsense-reasoning`, `ai-symbolic-neuro`)
- **Rules**:
  - No `trace_state` or diagnostic comments in source files; inspect live state via `lean-lsp` MCP (`lean_goal`, `lean_diagnostics`)
  - Run `lean_counterexample_search` (Galois-pruned Plausible) before manual proof search on suspect statements
  - Harvest `Try this` code actions
  - Tactic hierarchy: `rfl` -> `decide`/`norm_num` -> `grind` -> `omega` / `linarith` -> `simp only` -> `aesop` -> `exact?`
- **Stop Condition**: All goals closed (`0 sorry`) -> Hands off to Auditor

## 3. Auditor
- **Skills**: `lean-proof-review`, `lean-enforcement`, `lean-axiom-closure`, `lean-replay-verification`, `lean-tautology-triage`, `lean-deep-audit`, `lean-quality-engine`, `lean-bisect`, `lean-pr`, `lean-security-formalization`, `ai-high-stakes-verifiable`, `ai-guard-judge-eval`, `applied-data-information-security`, `applied-engineering-disciplines`, `applied-legal-reasoning`, `applied-intelligence-analysis`, `applied-strategy-analysis`
- **Sub-agents**: `proof-reviewer`, `enforcement-auditor`
- **Output**: Verified axiom closure (`[propext, Classical.choice, Quot.sound]`), kernel-replayed proofs, bounded heartbeats, zero warnings
- **Stop Condition**: All linters, static analyzers (`lean-rules`, `lean-analyzer`), and `lake build` green -> Hands off to Editor or Gardener

## 4. Editor
- **Skills**: `lean-proof-refactor`, `lean-upstream-porting`, `lean-pedagogical-exposition`, `lean-doc-improvement`, `lean-doc-feedback`, `lean-report`
- **Sub-agents**: `math-pedagogy-author`
- **Output**: Decomposed helper lemmas, Mathlib-ready upstream PR dossiers, and textbook-grade mathematical exposition
- **Stop Condition**: Proof length within threshold, zero regressions, and documentation synchronized -> Hands off to Gardener

## 5. Gardener
- **Skills**: `lean-zettelkasten`, `lean-retro-methodology`, `lean-retroactive-audit`, `lean-review-council`, `research-council`, `research-synthesis-engine`, `epistemic-discovery-engine`, `epistemic-mapping`, `lean-research`, `lean-research-types`, `lean-package-research`, `lean-vendor-substrate`, `lean-integration-protocol`
- **Stop Condition**: New patterns indexed in Zettelkasten and Kuzu knowledge graph, scratch memory purged

## Handoff Protocol
- **Format**: JSON schema defined in [`templates/handoff_protocol.json`](templates/handoff_protocol.json)
