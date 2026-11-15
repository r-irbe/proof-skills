For a detailed explanation of the Swarm methodology and multi-agent theory, see [`references/protocols/swarm_methodology.md`](references/swarm_methodology.md).

# Multi-Agent Lifecycle Roles (5 Pure Role-Actor Containers + 24 Soul Overlays)

`proof-skills` `v0.5.0` enforces a strict separation between the **5 Pure Role-Actor Containers** (`agents/{specifier,prover,auditor,editor,gardener}.md`) and the **24 Specialist Soul Overlays** (`agents/souls/*.md`, bound via [`agents/facets/registry.json`](agents/facets/registry.json)), spanning all **21 `lean-lsp` MCP tools**.

## 1. Specifier (`agents/specifier.md` -- Role #1)
- **Role-Scoped `lean-lsp` MCP Allowlist (11 tools)**: `lean_search`, `lean_lookup_symbol`, `lean_decl_references`, `lean_module_hierarchy`, `lean_navigate`, `lean_diagnostics`, `lean_counterexample_search`, `lean_blueprint`, `lean_metrics`, `lean_theorem_preflight`, `lean_skill_dispatch`
- **Soul Overlays (`agents/souls/`)**: `lean-spec-architect`, `formalization-breakdown-curator`, `formalization-dag-navigator`, `premise-retrieval-specialist`, `research-alpha-foundations`, `research-beta-dynamics`, `research-gamma-epistemics`, `research-delta-systems`, `research-epsilon-bridge`
- **Skills**: `lean-gateway`, `lean-specification`, `lean-blueprint`, `lean-doc-sync`, `lean-research`, `research-council`
- **Output**: Three-part `.lean` theorem specifications with `sorry` skeletons, `@[blueprint]` DAG annotations, and counterexample-screened declarations
- **Stop Condition**: Clean elaboration without type errors and 0 Plausible counterexamples -> Hands off to `prover`

## 2. Prover (`agents/prover.md` -- Role #2)
- **Role-Scoped `lean-lsp` MCP Allowlist (15 tools)**: `lean_goal`, `lean_diagnostics`, `lean_server_status`, `lean_counterexample_search`, `lean_multi_attempt`, `lean_repair_proof`, `lean_lookup_symbol`, `lean_decl_references`, `lean_navigate`, `lean_search`, `lean_ffi`, `lean_exec`, `lean_theorem_preflight`, `lean_resync`, `lean_skill_dispatch`
- **Soul Overlays (`agents/souls/`)**: `lean-proof-builder`, `counterexample-falsification-hunter`, `sair-kernel-optimizer`, `cross-itp-porter`
- **Skills**: `lean-proof`, `lean-proof-repair`, `lean-core-only`, `lean-build`, `lean-setup`, `lean-bisect`, `lean-mwe`, `counterexample-first-proving`, `lean-sair-kernel-optimization`, `itp-cross-porting`, `rocq-proof-adapter`, `isabelle-isar-adapter`, `hol-metamath-adapter`, `lean-math-foundations`, `lean-math-discrete`, `lean-math-stochastic`, `lean-math-dynamical`, `lean-math-optimization`, `lean-math-analysis`, `lean-ai-formalization`, `lean-knowledge-formalization`, `lean-security-formalization`
- **Rules**:
  - No `trace_state` or diagnostic comments in source files; inspect live state via `lean-lsp` MCP (`lean_goal`, `lean_diagnostics`, `lean_multi_attempt`)
  - Run `lean_counterexample_search` (Galois-pruned Plausible) before manual proof search on suspect statements
  - Never alter theorem signatures or hypothesis types to make a proof pass; `native_decide` (`Lean.ofReduceBool`) is strictly banned
  - Unified `v0.5.0` Tactic Hierarchy: `rfl` -> `bv_decide` / `decide +kernel` / `sair_decide` / `norm_num` / `ring` -> `omega` / `linarith` / `positivity` -> `grind` / `eqsat_rw` -> `simp only [...]` -> `backchain` -> `aesop`
- **Stop Condition**: All goals closed (`0 sorry`) -> Hands off to `auditor`

## 3. Auditor (`agents/auditor.md` -- Role #3, Strictly Read-Only)
- **Role-Scoped `lean-lsp` MCP Allowlist (13 tools)**: `lean_axiom_closure`, `lean_metrics`, `lean_diagnostics`, `lean_server_status`, `lean_counterexample_search`, `lean_minimal_hypotheses`, `lean_profile_proof`, `lean_lookup_symbol`, `lean_decl_references`, `lean_module_hierarchy`, `lean_navigate`, `lean_ffi`, `lean_search`
- **Soul Overlays (`agents/souls/`)**: `proof-reviewer`, `enforcement-auditor`, `abstract-interp-vacuity-auditor`, `council-sigma-soundness`, `council-phi-faithfulness`, `council-nu-novelty`, `council-tau-tactics`, `council-omega-chair`
- **Skills**: `lean-proof-review`, `lean-verification-gate`, `lean-tautology-triage`, `lean-corpus-audit`, `lean-review-council`
- **Output**: Verified axiom closure (`[propext, Classical.choice, Quot.sound]`), 4-layer soundness/vacuity certificates, minimal-hypothesis checks (`lean_minimal_hypotheses`), kernel-replayed proofs, zero warnings
- **Stop Condition**: All linters (`lean-rules`), static analyzers (`lean-analyzer` WASM), and `lake build` green -> Hands off to `editor` or `gardener`

## 4. Editor (`agents/editor.md` -- Role #4)
- **Role-Scoped `lean-lsp` MCP Allowlist (12 tools)**: `lean_goal`, `lean_diagnostics`, `lean_multi_attempt`, `lean_minimal_hypotheses`, `lean_profile_proof`, `lean_lookup_symbol`, `lean_decl_references`, `lean_navigate`, `lean_search`, `lean_blueprint`, `lean_metrics`, `lean_resync`
- **Soul Overlays (`agents/souls/`)**: `math-pedagogy-author`, `abstraction-concrete-architect`
- **Skills**: `lean-proof-refactor`, `lean-pedagogical-exposition`, `lean-doc-sync`, `research-council`
- **Output**: Decomposed helper lemmas, `@[csimp]` Abstraction-Concrete Duality twins, synchronized LaTeX reports, and textbook-grade mathematical exposition
- **Stop Condition**: Proof length within threshold, zero regressions, and documentation synchronized -> Hands off to `gardener`

## 5. Gardener (`agents/gardener.md` -- Role #5)
- **Role-Scoped `lean-lsp` MCP Allowlist (10 tools)**: `lean_search`, `lean_lookup_symbol`, `lean_decl_references`, `lean_module_hierarchy`, `lean_navigate`, `lean_blueprint`, `lean_metrics`, `lean_axiom_closure`, `lean_server_status`, `lean_skill_dispatch`
- **Soul Overlays (`agents/souls/`)**: `lean-retro-facilitator`
- **Skills**: `lean-retro-methodology`, `lean-upstream-pr`, `lean-dependency-management`, `lean-gateway` (+ opt-in `packs/applied-strategy/skills/*`)
- **Stop Condition**: New patterns indexed in Zettelkasten (`zettelkasten/`) and Kuzu knowledge graph (`kuzu/prover_knowledge.kz`), upstream PR dossiers prepared

## Handoff Protocol
- **Format**: JSON schema v2.0 defined in [`templates/handoff_protocol.json`](templates/handoff_protocol.json), binding `from_role`, `to_role`, `soul_overlay`, and `facet_pack` via [`agents/facets/registry.json`](agents/facets/registry.json).
