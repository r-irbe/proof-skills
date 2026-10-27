# proof-skills Taxonomy -- 5-Tier Abstraction Hierarchy, 65 Unified Skills & 6-Prover Concordance

Classification of all **65 active v2 first-party skills**, **5 Role-Actor Containers** (`agents/*.md`), **23 Soul Overlays** (`agents/souls/*.md`), **200 Templates** (`59` core + `131` arithmetic-geometry pack + `10` fluid-pde pack), and **20 Cross-ITP Concordance Mechanisms (`CONC-01..20`)** across **6 Prover Families** (`lean4`, `coq_mathcomp`, `isabelle_hol`, `hol_light`, `agda`, `metamath`).

---

## 1. Five-Tier Abstraction Hierarchy

Every `skills/<slug>/SKILL.md` dispatch contract is strictly `<4,000` bytes (`<1,000` tokens), offloading encyclopedic content and `mathcomp-skills` 3-table lookups (`templates`, `phrasebook`, `errors`) to `references/<slug>-handbook.md`:

```text
+-------------------------------------------------------------------------------+
| L4: Governance, Audit & Review (Auditor / Gardener)                           |
|     lean-quality-engine, lean-review-council, lean-retroactive-audit,         |
|     lean-deep-audit, lean-axiom-closure, lean-replay-verification,            |
|     lean-security-formalization, Biba integrity lattices, invariant audits    |
+-------------------------------------------------------------------------------+
                                       ^
                                       |
+-------------------------------------------------------------------------------+
| L3: Knowledge, Blueprints & Multi-Prover Concordance (Specifier / Editor)     |
|     lean-blueprint, lean-dag-visualizer, lean-formalization-breakdown,        |
|     lean-pedagogical-exposition, lean-zettelkasten,                           |
|     100-concept ITP Ontology, 10 JSON book indexes / 42 Kuzu-indexed books,   |
|     20 Cross-ITP Concordance mechanisms (CONC-01..20) across 6 provers        |
+-------------------------------------------------------------------------------+
                                       ^
                                       |
+-------------------------------------------------------------------------------+
| L2: Unified Domain Formalization & Cross-ITP Adapters (Prover / Specifier)    |
|     lean-math-{foundations,discrete,stochastic,dynamical,optimization,        |
|     analysis}, lean-ai-formalization, lean-causal-reasoning,                  |
|     lean-knowledge-formalization, lean-applied-reasoning,                     |
|     itp-cross-porting, rocq-proof-adapter, isabelle-isar-adapter,             |
|     hol-metamath-adapter                                                      |
+-------------------------------------------------------------------------------+
                                       ^
                                       |
+-------------------------------------------------------------------------------+
| L1: Tactic Discipline, Proof Repair & SAIR Optimization (Prover / Auditor)    |
|     lean-proof, lean-proof-repair, lean-proof-review, lean-tautology-triage,  |
|     lean-core-only, counterexample-first-proving,                             |
|     lean-sair-kernel-optimization, lean-enforcement                           |
+-------------------------------------------------------------------------------+
                                       ^
                                       |
+-------------------------------------------------------------------------------+
| L0: Deterministic Infrastructure Substrate                                    |
|     lean-setup, lean-build, lean-mwe, lean-bisect,                            |
|     lean-serve-broker, lean4-lsp-mcp (14 consolidated MCP tools + WASM)       |
+-------------------------------------------------------------------------------+
```

---

## 2. Core & Multi-Prover Kernel Skills (29 Skills)

| Skill | Role Container | Profile | Primary Function |
| :--- | :--- | :--- | :--- |
| [lean-gateway](skills/lean-gateway/SKILL.md) | Specifier / Prover | `core` | Top-level dispatch router across all 65 skills. |
| [lean-setup](skills/lean-setup/SKILL.md) | Prover | `core` | Toolchain resolution, `elan`, `lean-toolchain` pins. |
| [lean-build](skills/lean-build/SKILL.md) | Prover | `core` | Lake compilation, `.olean` cache management, `lean-serve-broker`. |
| [lean-proof](skills/lean-proof/SKILL.md) | Prover | `core` | Interactive tactic proving via `lean_goal` and 3-table phrasebook. |
| [lean-proof-repair](skills/lean-proof-repair/SKILL.md) | Prover | `core` | Automated & interactive repair of broken proofs across toolchain/Mathlib bumps. |
| [lean-core-only](skills/lean-core-only/SKILL.md) | Prover | `core` | Core/Stdlib-only Lean 4 proving without Mathlib (`omega`, `grind`, `bv_decide`). |
| [counterexample-first-proving](skills/counterexample-first-proving/SKILL.md) | Prover / Specifier | `core` | Plausible property testing & boundary witness falsification prior to proving. |
| [lean-sair-kernel-optimization](skills/lean-sair-kernel-optimization/SKILL.md) | Prover | `core` | SAIR Middle-IR, kernel WHNF caching, ZDD, and GMP SWAR word-packing (`SAIR-LAW-01..25B`). |
| [lean-mwe](skills/lean-mwe/SKILL.md) | Prover | `core` | Minimal Working Example extraction and `#guard_msgs` reproducers. |
| [lean-bisect](skills/lean-bisect/SKILL.md) | Prover | `core` | Toolchain and commit bisection for regressions. |
| [lean-specification](skills/lean-specification/SKILL.md) | Specifier | `core` | Three-part theorem specification (Preconditions, Postconditions, Witness). |
| [lean-blueprint](skills/lean-blueprint/SKILL.md) | Specifier | `core` | `@[blueprint]` annotations and `lean_blueprint(action: "scaffold" \| "skeleton")`. |
| [itp-cross-porting](skills/itp-cross-porting/SKILL.md) | Prover | `multi-prover` | Cross-ITP concordance router (`CONC-01..20`) across all 6 prover families + Agda adapter. |
| [rocq-proof-adapter](skills/rocq-proof-adapter/SKILL.md) | Prover | `multi-prover` | Rocq / Coq (SSReflect, MathComp, Hierarchy Builder, `lia`/`lra`) -> Lean 4 adapter. |
| [isabelle-isar-adapter](skills/isabelle-isar-adapter/SKILL.md) | Prover | `multi-prover` | Isabelle/HOL (Isar, locales, Lifting/Transfer, `HOL-Analysis`) -> Lean 4 adapter. |
| [hol-metamath-adapter](skills/hol-metamath-adapter/SKILL.md) | Prover | `multi-prover` | HOL Light (`.ml` tactical scripts) and Metamath (`set.mm` ZFC proofs) -> Lean 4 adapter. |
| [lean-proof-review](skills/lean-proof-review/SKILL.md) | Auditor | `governance` | Read-only 4-layer proof review (Soundness, Faithfulness, Non-Vacuity, Hygiene). |
| [lean-enforcement](skills/lean-enforcement/SKILL.md) | Auditor | `governance` | Programmatic zero-`sorry`, zero-warning CI gatekeeper. |
| [lean-axiom-closure](skills/lean-axiom-closure/SKILL.md) | Auditor | `governance` | Transitive axiom-closure lockdown (`[propext, Classical.choice, Quot.sound]`). |
| [lean-replay-verification](skills/lean-replay-verification/SKILL.md) | Auditor | `governance` | Fresh kernel replay verification (`lean4checker --fresh`). |
| [lean-tautology-triage](skills/lean-tautology-triage/SKILL.md) | Auditor | `governance` | Vacuity, tautology, and `NatSubTruncation` / `NatDivModByZero` triage. |
| [lean-quality-engine](skills/lean-quality-engine/SKILL.md) | Auditor | `governance` | 7-dimension corpus quality assessment and heartbeat profiling. |
| [lean-deep-audit](skills/lean-deep-audit/SKILL.md) | Auditor | `governance` | Whole-corpus 7-lens quality audit. |
| [lean-proof-refactor](skills/lean-proof-refactor/SKILL.md) | Editor | `governance` | Long-proof decomposition into reusable helper lemmas. |
| [lean-upstream-porting](skills/lean-upstream-porting/SKILL.md) | Gardener | `governance` | Generalizing and porting corpus lemmas to Mathlib4/stdlib upstream. |
| [lean-pr](skills/lean-pr/SKILL.md) | Gardener | `governance` | Opening, labeling, and managing PRs against Lean ecosystem repositories. |
| [lean-dag-visualizer](skills/lean-dag-visualizer/SKILL.md) | Specifier | `governance` | Module/declaration dependency DAG analysis (`lean_module_hierarchy(direction: "subgraph")`). |
| [lean-formalization-breakdown](skills/lean-formalization-breakdown/SKILL.md) | Specifier | `governance` | Multi-wave theorem breakdown registries and fidelity tracking. |
| [lean-doc-requirements](skills/lean-doc-requirements/SKILL.md) | Specifier | `governance` | Requirement extraction from papers and technical specifications. |

---

## 3. Unified Mathematical Domain Facet (8 Skills)

The former standalone `math-*` companion skills have been unified into their canonical `lean-math-*` counterparts, with all domain theory and `mathcomp-skills` 3-table lookups (`templates`, `phrasebook`, `errors`) consolidated in `references/lean-math-*-handbook.md`:

| Canonical Skill | Unified Companion(s) Merged | Key Mathlib Theories & Handbook |
| :--- | :--- | :--- |
| [lean-math-foundations](skills/lean-math-foundations/SKILL.md) | `math-algebra-category` | Type universes, logic, `Algebra.Group`, `Algebra.Ring`, `Order.GaloisConnection`, `CategoryTheory` ([handbook](references/lean-math-foundations-handbook.md)) |
| [lean-math-discrete](skills/lean-math-discrete/SKILL.md) | `math-graph-knowledge` | `Data.Finset`, `BigOperators`, `Combinatorics.SimpleGraph`, posets, DAGs, provenance ([handbook](references/lean-math-discrete-handbook.md)) |
| [lean-math-stochastic](skills/lean-math-stochastic/SKILL.md) | `math-measure-probability`, `math-time-series` | `MeasureTheory`, Bochner/Lebesgue integration, Markov chains, martingales, time series, ergodic theory ([handbook](references/lean-math-stochastic-handbook.md)) |
| [lean-math-dynamical](skills/lean-math-dynamical/SKILL.md) | `math-nonlinear-dynamics` | Lyapunov functions, LaSalle invariance, bifurcations, cusp catastrophe, phase portraits ([handbook](references/lean-math-dynamical-handbook.md)) |
| [lean-math-optimization](skills/lean-math-optimization/SKILL.md) | `math-optimization-game` | `Analysis.Convex`, Bellman contractions, MDP value iteration, Nash equilibria, minimax duality ([handbook](references/lean-math-optimization-handbook.md)) |
| [lean-math-analysis](skills/lean-math-analysis/SKILL.md) | `math-topology-analysis` | `Filter.Tendsto`, `MetricSpace`, `NormedSpace`, `HasDerivAt`, compactness, functional analysis ([handbook](references/lean-math-analysis-handbook.md)) |
| [lean-competitive-math](skills/lean-competitive-math/SKILL.md) | *(self-contained)* | Project Euler, MiniF2F, Putnam, decidable number theory ([handbook](references/lean-competitive-math-handbook.md)) |
| [lean-convergence-verification](skills/lean-convergence-verification/SKILL.md) | *(self-contained)* | Discrete Lyapunov decay, ceiling-division loop bounds ([handbook](references/lean-convergence-verification-handbook.md)) |

---

## 4. Unified AI, Epistemic & Applied Reasoning Facet (8 Skills)

| Canonical Skill | Unified Companion(s) Merged | Focus Area & Handbook |
| :--- | :--- | :--- |
| [lean-ai-formalization](skills/lean-ai-formalization/SKILL.md) | `ai-agentic-evolving`, `ai-high-stakes-verifiable` | Agentic AI safety barriers, evolving agent invariants, high-stakes certification ([handbook](references/lean-ai-formalization-handbook.md)) |
| [lean-causal-reasoning](skills/lean-causal-reasoning/SKILL.md) | `ai-causal-deontic` | Pearl causal hierarchy, `do`-calculus, counterfactuals, deontic logic, provenance bridges ([handbook](references/lean-causal-reasoning-handbook.md)) |
| [lean-knowledge-formalization](skills/lean-knowledge-formalization/SKILL.md) | `ai-commonsense-reasoning`, `ai-symbolic-neuro` | Ontologies, description logics, Kripke epistemic frames, Allen interval algebra, neuro-symbolic KRR ([handbook](references/lean-knowledge-formalization-handbook.md)) |
| [lean-applied-reasoning](skills/lean-applied-reasoning/SKILL.md) | `applied-intelligence-analysis`, `applied-strategy-analysis` | Structured analytic techniques (ACH), Bayesian evidence scoring, game-theoretic wargaming ([handbook](references/lean-applied-reasoning-handbook.md)) |
| [lean-bigraph-modeling](skills/lean-bigraph-modeling/SKILL.md) | *(self-contained)* | Robin Milner Bigraphical Reactive Systems (place forests + link hypergraphs) ([handbook](references/lean-bigraph-modeling-handbook.md)) |
| [lean-nested-learning](skills/lean-nested-learning/SKILL.md) | *(self-contained)* | Multi-scale nested learning hierarchies and coupled Lyapunov certificates ([handbook](references/lean-nested-learning-handbook.md)) |
| [lean-security-formalization](skills/lean-security-formalization/SKILL.md) | *(self-contained)* | Non-interference, Bell-LaPadula / Biba lattices, cryptographic protocol invariants ([handbook](references/lean-security-formalization-handbook.md)) |
| [ai-guard-judge-eval](skills/ai-guard-judge-eval/SKILL.md) | *(self-contained)* | Stratified LLM safety-guard and judge calibration ([handbook](references/ai-guard-judge-eval-handbook.md)) |

---

## 5. Governance, Councils, Documentation & Gardening Facet (20 Skills)

| Category | Skills |
| :--- | :--- |
| **Councils & Discovery** | [lean-review-council](skills/lean-review-council/SKILL.md), [research-council](skills/research-council/SKILL.md), [research-synthesis-engine](skills/research-synthesis-engine/SKILL.md), [epistemic-discovery-engine](skills/epistemic-discovery-engine/SKILL.md), [epistemic-mapping](skills/epistemic-mapping/SKILL.md), [lean-research](skills/lean-research/SKILL.md), [lean-package-research](skills/lean-package-research/SKILL.md) |
| **Exposition & Reports** | [lean-pedagogical-exposition](skills/lean-pedagogical-exposition/SKILL.md), [lean-report](skills/lean-report/SKILL.md), [lean-doc-improvement](skills/lean-doc-improvement/SKILL.md), [lean-doc-feedback](skills/lean-doc-feedback/SKILL.md) |
| **Gardening & Substrate** | [lean-zettelkasten](skills/lean-zettelkasten/SKILL.md), [lean-retro-methodology](skills/lean-retro-methodology/SKILL.md), [lean-retroactive-audit](skills/lean-retroactive-audit/SKILL.md), [lean-vendor-substrate](skills/lean-vendor-substrate/SKILL.md), [lean-integration-protocol](skills/lean-integration-protocol/SKILL.md) |
| **Strategy, Systems & Legal** | [math-product-management](skills/math-product-management/SKILL.md), [math-project-management](skills/math-project-management/SKILL.md), [math-strategy-studio](skills/math-strategy-studio/SKILL.md), [applied-engineering-disciplines](skills/applied-engineering-disciplines/SKILL.md), [applied-legal-reasoning](skills/applied-legal-reasoning/SKILL.md), [applied-data-information-security](skills/applied-data-information-security/SKILL.md) |
