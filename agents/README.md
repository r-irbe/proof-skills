# `agents/` -- Pure 5 Role-Actor Containers + 23 `souls/` Overlays

`proof-skills` separates **structural role permissions** (`agents/*.md`) from **specialist persona overlays** (`agents/souls/*.md`) and **domain facet bindings** (`agents/facets/registry.json`).

## 1. The 5 Pure Role-Actor Containers (`agents/*.md`)

Every sub-agent dispatch instantiates one of the 5 canonical Role-Actor Containers (aligned 1-to-1 with `ROLES.md`):

| Role # | Container File | Tools | Role-Scoped `lean-lsp` MCP Allowlist | Primary Responsibility |
| :--- | :--- | :--- | :--- | :--- |
| **#1** | `agents/specifier.md` | `read, write, edit, bash, mcp:lean-lsp` | `lean_search`, `lean_lookup_symbol`, `lean_decl_references`, `lean_module_hierarchy`, `lean_diagnostics`, `lean_counterexample_search`, `lean_blueprint`, `lean_metrics` | Three-part theorem specifications, `@[blueprint]` scaffolding, DAG navigation, and pre-proof counterexample screening. |
| **#2** | `agents/prover.md` | `read, write, edit, bash, mcp:lean-lsp` | `lean_goal`, `lean_diagnostics`, `lean_counterexample_search`, `lean_lookup_symbol`, `lean_decl_references`, `lean_search`, `lean_exec`, `lean_resync` | Interactive tactic synthesis, proof repair (`@lean-proof-repair`), cross-ITP porting (`@itp-cross-porting`), and SAIR kernel optimization without altering theorem signatures. |
| **#3** | `agents/auditor.md` | `read, grep, find, ls, bash, mcp:lean-lsp` | `lean_diagnostics`, `lean_axiom_closure`, `lean_metrics`, `lean_counterexample_search`, `lean_lookup_symbol`, `lean_decl_references`, `lean_module_hierarchy`, `lean_search` | **Strictly read-only** 4-layer proof reviews, axiom-closure lockdowns, vacuity/truncation auditing, and 5-member Review Council gates. |
| **#4** | `agents/editor.md` | `read, write, edit, bash, mcp:lean-lsp` | `lean_goal`, `lean_diagnostics`, `lean_lookup_symbol`, `lean_decl_references`, `lean_search`, `lean_blueprint`, `lean_metrics` | Post-proof refactoring (`@lean-proof-refactor`), textbook-grade pedagogical exposition (`@lean-pedagogical-exposition`), and LaTeX report sync (`@lean-report`). |
| **#5** | `agents/gardener.md` | `read, write, edit, bash, mcp:lean-lsp` | `lean_search`, `lean_lookup_symbol`, `lean_decl_references`, `lean_module_hierarchy`, `lean_metrics`, `lean_axiom_closure` | Zettelkasten graph curation (`@lean-zettelkasten`), RETRO retrospectives (`@lean-retro-methodology`), substrate hygiene, and upstream Mathlib PR preparation (`@lean-upstream-porting`). |

## 2. The 23 Specialist `souls/` Overlays (`agents/souls/*.md`)

Rather than proliferating top-level agent containers, specialized personas live in `agents/souls/*.md` and bind to one of the 5 Role-Actor Containers via `agents/facets/registry.json`:

### A. 5 Migrated Analysts
1. `proof-reviewer` -> `auditor` (`@lean-proof-review`)
2. `enforcement-auditor` -> `auditor` (`@lean-enforcement`)
3. `formalization-breakdown-curator` -> `specifier` (`@lean-formalization-breakdown`)
4. `math-pedagogy-author` -> `editor` (`@lean-pedagogical-exposition`)
5. `formalization-dag-navigator` -> `specifier` (`@lean-dag-visualizer`)

### B. 8 Operational Specialists
6. `lean-proof-builder` -> `prover` (`@lean-proof`)
7. `lean-spec-architect` -> `specifier` (`@lean-specification`)
8. `counterexample-falsification-hunter` -> `prover` (`@counterexample-first-proving`)
9. `abstract-interp-vacuity-auditor` -> `auditor` (`@lean-tautology-triage`)
10. `sair-kernel-optimizer` -> `prover` (`@lean-sair-kernel-optimization`)
11. `premise-retrieval-specialist` -> `specifier` (`@lean-research`)
12. `cross-itp-porter` -> `prover` (`@itp-cross-porting`)
13. `lean-retro-facilitator` -> `gardener` (`@lean-retro-methodology`)

### C. 10 Review & Research Council Personas
14. `council-sigma-soundness` -> `auditor` (`@lean-review-council` Member Sigma)
15. `council-phi-faithfulness` -> `auditor` (`@lean-review-council` Member Phi)
16. `council-nu-novelty` -> `auditor` (`@lean-review-council` Member Nu)
17. `council-tau-tactics` -> `auditor` (`@lean-review-council` Member Tau)
18. `council-omega-chair` -> `auditor` (`@lean-review-council` Chair Omega)
19. `research-alpha-foundations` -> `specifier` (`@research-council` Member Alpha)
20. `research-beta-dynamics` -> `specifier` (`@research-council` Member Beta)
21. `research-gamma-epistemics` -> `specifier` (`@research-council` Member Gamma)
22. `research-delta-systems` -> `specifier` (`@research-council` Member Delta)
23. `research-epsilon-bridge` -> `specifier` (`@research-council` Chair Epsilon)

## 3. Runtime Composition & Handoff Protocol

When dispatching a sub-agent, select the Role Container (`specifier`, `prover`, `auditor`, `editor`, or `gardener`) and attach the target `soul_overlay` and `facet_pack` in the `templates/handoff_protocol.json` envelope.
