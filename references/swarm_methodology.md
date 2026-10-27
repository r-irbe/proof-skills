# Stanford ACE Prover Swarm Methodology (5 Role-Actor Containers)

## 1. Overview and Motivation

To prevent context collapse, persona drift, and proof degradation in long-running Lean 4 sessions, the formalization lifecycle in this repository adopts a 5-role multi-agent swarm architecture (`agents/{specifier,prover,auditor,editor,gardener}.md`) composed with 23 specialist soul overlays (`agents/souls/*.md`).

Agents operating on mathematical formalization face severe context limits when mixing specification design, interactive tactic proving, read-only soundness auditing, pedagogical refactoring, and long-term knowledge curation. By separating concerns across 5 Role-Actor Containers, agents transition sequentially and never mix generative proving with read-only auditing or memory curation in the same context window.

## 2. Theoretical Backing & Literature

*For full citations, refer to [`bibliography.md`](bibliography.md).*

1. **Multi-Agent Role Specialization**: Breaking complex reasoning tasks into the 5 canonical Role-Actor Containers (Specifier, Prover, Auditor, Editor, Gardener) prevents persona drift and enforces structural tool boundaries.
   - *Reference*: Wu et al. (2023)
   - *Application*: Ensures that Specifier agents focused on high-level blueprinting do not get bogged down in low-level `simp` tactics, and Auditor agents remain strictly read-only.
2. **Iterative Proof Refinement, Auditing, and Exposition**: Separating verification (Auditor) and pedagogical refactoring (Editor) from tactic synthesis (Prover) guarantees zero statement weakening.
   - *Reference*: Yang et al. (2023)
   - *Application*: The Auditor role acts as a read-only gatekeeper before the Editor refactors proof terms or the Gardener persists lemmas.
3. **Cross-Session Knowledge Retrieval (Zettelkasten & RETRO)**:
   - *Reference*: Lewis et al. (2020)
   - *Application*: The Gardener role persists verified tactics and 3-table phrasebook patterns to the Zettelkasten and Kuzu knowledge graph.

## 3. The Five Role-Actor Containers

The lifecycle is divided into five sequential Role-Actor Containers defined in [`ROLES.md`](../ROLES.md) and [`agents/facets/registry.json`](../agents/facets/registry.json):

- **Specifier (`agents/specifier.md` -- Role #1)**: Informal-to-formal 3-part specification, `@[blueprint]` scaffolding, and pre-proof counterexample screening.
- **Prover (`agents/prover.md` -- Role #2)**: Interactive tactic synthesis, proof repair (`@lean-proof-repair`), cross-ITP porting (`@itp-cross-porting`), and SAIR kernel optimization.
- **Auditor (`agents/auditor.md` -- Role #3)**: Strictly read-only 4-layer proof review, axiom-closure lockdown (`lean_axiom_closure`), vacuity/truncation auditing, and Review Council arbitration.
- **Editor (`agents/editor.md` -- Role #4)**: Post-proof helper-lemma extraction (`@lean-proof-refactor`), textbook-grade mathematical exposition (`@lean-pedagogical-exposition`), and LaTeX paper sync (`@lean-report`).
- **Gardener (`agents/gardener.md` -- Role #5)**: Zettelkasten curation (`@lean-zettelkasten`), RETRO retrospectives (`@lean-retro-methodology`), and Mathlib upstream porting (`@lean-upstream-porting`).

## 4. Handoff Protocol

Transitions between the 5 roles use structured handoff receipts binding the active `soul_overlay` (`agents/souls/*.md`) and `facet_pack` (`agents/facets/registry.json`).
- *See the exact JSON schema in [`templates/handoff_protocol.json`](../templates/handoff_protocol.json).*
