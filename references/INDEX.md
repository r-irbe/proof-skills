# Reference Index and Master Taxonomy

Authoritative catalog of background knowledge, theorem-proving guides, domain
handbooks, and operational protocols across the proof-skills corpus.

Strict 7-bit ASCII only.

---

## 1. Structure Overview

References in this repository support the Hybrid Architecture (Approach 1: Kernel
and Facets + Approach 2: Stanford ACE Prover Roles):

| Section | Scope | Primary Agent Role | Associated Facet |
| --- | --- | --- | --- |
| 1. Core Verification | LSP, tactic hierarchies, proof protocols, import DAGs | Prover / Specifier | Core |
| 2. Mathematical Domains | Analysis, algebra, topology, discrete, stochastics | Prover / Specifier | Math |
| 3. AI and Reasoning | Neuro-symbolic, causal deontic, verifiable AI | Specifier / Auditor | AI |
| 4. Governance & Strategy | Review council, research synthesis, legal reasoning | Auditor / Gardener | Governance |

---

## 2. Core Lean 4 Verification and Toolchain Guides

Authoritative engineering references for Lean 4 compiler interaction, proof state
inspection, tactic execution, and module hygiene.

| Reference File | Focus & Key Rules | Target Skills |
| --- | --- | --- |
| [lean4-lsp-guide.md](lean4-lsp-guide.md) | 12-point Lean 4 LSP interaction manual: Try this code action harvesting, watchdog recovery, diagnostic wait policy, plainGoal formatting. | lean-proof, lean-build, lean-setup |
| [lean4-lsp-proof-protocol.md](lean4-lsp-proof-protocol.md) | The 13 operational proof rules: prohibits trace_state file pollution, enforces live LSP goal queries, inaccessible dagger variable hygiene. | lean-proof, lean-proof-review |
| [lean4-tactic-hierarchy.md](lean4-tactic-hierarchy.md) | Canonical tactic dispatch order: rfl -> omega / linarith -> simp only -> aesop -> exact?. Reversibility and termination bounds. | lean-proof, lean-mwe |
| [lean4-proof-strategy.md](lean4-proof-strategy.md) | Proof decomposition: have / suffices subgoal cuts, forward vs backward reasoning, induction structuring. | lean-proof, lean-specification |
| [lean4-module-dependency-guide.md](lean4-module-dependency-guide.md) | Layer 0 to 4 DAG architecture, transitive import blast radius, forward and reverse module navigation. | lean-build, lean-blueprint |
| [mathlib4-conventions.md](mathlib4-conventions.md) | Mathlib4 style guide: snake_case for lemmas, camelCase for types, docstrings, binder hygiene, and implicit arguments. | lean-proof, lean-pr |
| [AUTHORING.md](AUTHORING.md) | Authoring standards for proof-skills SKILL.md contracts, frontmatter validation, and evaluation rubrics. | lean-quality-engine |

---

## 3. Mathematical Domain Handbooks and Pattern Catalogs

Domain-specific lemma patterns, formalization templates, and tactic idioms.

### 3.1 Foundations, Discrete Mathematics and Algebra
| Reference File | Domain Scope | Associated Skill |
| --- | --- | --- |
| [lean4-math-foundations.md](lean4-math-foundations.md) | Sets, functions, relations, type universes, equality and quotients. | lean-math-foundations |
| [lean4-math-discrete.md](lean4-math-discrete.md) | Combinatorics, discrete structures, graph coloring, recurrence relations. | lean-math-discrete |
| [math-algebra-category-handbook.md](math-algebra-category-handbook.md) | Monoids, groups, rings, modules, category theory, functors and limits. | math-algebra-category |
| [math-graph-knowledge-handbook.md](math-graph-knowledge-handbook.md) | Graph theory, hypergraphs, topological graphs, graph-theoretic invariants. | math-graph-knowledge |

### 3.2 Analysis and Optimization
| Reference File | Domain Scope | Associated Skill |
| --- | --- | --- |
| [lean4-math-analysis.md](lean4-math-analysis.md) | Real analysis, metric spaces, limits, continuity, differentiability. | lean-math-analysis |
| [lean4-math-optimization.md](lean4-math-optimization.md) | Convex optimization, Lagrange multipliers, duality, KKT conditions. | lean-math-optimization |
| [lean4-ivt-patterns.md](lean4-ivt-patterns.md) | Intermediate Value Theorem formalization idioms and continuity proofs. | lean-math-analysis |
| [lean4-contraction-catalog.md](lean4-contraction-catalog.md) | Banach fixed point theorem, contraction mappings, metric completions. | lean-math-analysis |

### 3.3 Topology and Dynamical Systems
| Reference File | Domain Scope | Associated Skill |
| --- | --- | --- |
| [math-topology-analysis-handbook.md](math-topology-analysis-handbook.md) | General topology, topological spaces, compactness, connected components. | math-topology-analysis |
| [lean4-math-dynamical.md](lean4-math-dynamical.md) | Dynamical systems, flow invariants, fixed points, stability analysis. | lean-math-dynamical |
| [math-nonlinear-dynamics-handbook.md](math-nonlinear-dynamics-handbook.md) | Nonlinear bifurcations, phase space portraits, Lyapunov stability. | math-nonlinear-dynamics |
| [lean4-ergodic-theory.md](lean4-ergodic-theory.md) | Measure-preserving transformations, Birkhoff ergodic theorem idioms. | lean-math-dynamical |

### 3.4 Measure Theory, Stochastics and Time Series
| Reference File | Domain Scope | Associated Skill |
| --- | --- | --- |
| [math-measure-probability-handbook.md](math-measure-probability-handbook.md) | Measure spaces, Lebesgue integration, probability spaces, expectation. | math-measure-probability |
| [lean4-math-stochastic.md](lean4-math-stochastic.md) | Martingales, stochastic processes, stopping times, Markov chains. | lean-math-stochastic |
| [math-time-series-handbook.md](math-time-series-handbook.md) | Discrete-time stochastic processes, stationarity, autocorrelation. | math-time-series |
| [lean4-time-series-patterns.md](lean4-time-series-patterns.md) | Time-series decomposition, lag operators, trend estimation idioms. | math-time-series |

---

## 4. AI and Neuro-Symbolic Handbooks

Formalization contracts bridging symbolic reasoning, agent architectures, and causal logic.

| Reference File | Domain Scope | Associated Skill |
| --- | --- | --- |
| [ai-agentic-evolving-handbook.md](ai-agentic-evolving-handbook.md) | Self-modifying and evolving agent loops, safety invariants. | ai-agentic-evolving |
| [ai-causal-deontic-handbook.md](ai-causal-deontic-handbook.md) | Causal inference, do-calculus, deontic logic, normative obligations. | ai-causal-deontic |
| [ai-commonsense-reasoning-handbook.md](ai-commonsense-reasoning-handbook.md) | Default reasoning, non-monotonic logic, commonsense knowledge frames. | ai-commonsense-reasoning |
| [ai-high-stakes-verifiable-handbook.md](ai-high-stakes-verifiable-handbook.md) | High-assurance verification, formal safety guarantees, fault trees. | ai-high-stakes-verifiable |
| [ai-symbolic-neuro-handbook.md](ai-symbolic-neuro-handbook.md) | Neuro-symbolic integration, differentiable theorem proving, embedding logic. | ai-symbolic-neuro |
| [lean-ai-formalization-handbook.md](lean-ai-formalization-handbook.md) | Autoformalization workflows, natural language to Lean translation. | lean-ai-formalization |
| [lean-applied-reasoning-handbook.md](lean-applied-reasoning-handbook.md) | Applied multi-step deductive reasoning and theorem structuring. | lean-applied-reasoning |
| [lean-knowledge-formalization-handbook.md](lean-knowledge-formalization-handbook.md) | Domain knowledge encoding, ontological hierarchy construction. | lean-knowledge-formalization |

---

## 5. Systems, Strategy and Governance Handbooks

Operational frameworks for research management, legal reasoning, review councils,
and retrospective audits.

| Reference File | Domain Scope | Associated Skill |
| --- | --- | --- |
| [applied-data-information-security-handbook.md](applied-data-information-security-handbook.md) | Information flow security, non-interference proofs, cryptographic protocols. | applied-data-information-security |
| [applied-engineering-disciplines-handbook.md](applied-engineering-disciplines-handbook.md) | Formal specifications in physical engineering and control systems. | applied-engineering-disciplines |
| [applied-intelligence-analysis-handbook.md](applied-intelligence-analysis-handbook.md) | Structured analytic techniques, alternative hypotheses, source evaluation. | applied-intelligence-analysis |
| [applied-legal-reasoning-handbook.md](applied-legal-reasoning-handbook.md) | Statutory interpretation, precedent trees, legal deontic constraints. | applied-legal-reasoning |
| [applied-strategy-analysis-handbook.md](applied-strategy-analysis-handbook.md) | Strategic game theory, payoff matrices, competitive equilibria. | applied-strategy-analysis |
| [epistemic-discovery-engine-handbook.md](epistemic-discovery-engine-handbook.md) | Hypothesis generation, abduction, epistemic state transitions. | epistemic-discovery-engine |
| [lean-report-handbook.md](lean-report-handbook.md) | Automated formal verification reports, audit summaries, proof metrics. | lean-report |
| [lean-research-handbook.md](lean-research-handbook.md) | Literature review methods, mathematical survey formalization. | lean-research |
| [lean-retroactive-audit-handbook.md](lean-retroactive-audit-handbook.md) | Post-hoc audit trails, theorem deprecation tracking, dependency drift. | lean-retroactive-audit |
| [lean-retro-methodology-handbook.md](lean-retro-methodology-handbook.md) | Retrospective analysis of proof campaigns, failure taxonomy generation. | lean-retro-methodology |
| [lean-review-council-handbook.md](lean-review-council-handbook.md) | Multi-agent review councils, consensus protocols, gate signoffs. | lean-review-council |
| [lean-review-council-skill-map.md](lean-review-council-skill-map.md) | Topology map of skills governed by the review council. | lean-review-council |
| [lean-security-formalization-handbook.md](lean-security-formalization-handbook.md) | Security policy verification, access control invariants. | lean-security-formalization |
| [lean-specification-handbook.md](lean-specification-handbook.md) | Formal specification authoring, axiomatic boundaries, consistency checks. | lean-specification |
| [lean-doc-improvement-handbook.md](lean-doc-improvement-handbook.md) | Documentation refinement, docstring coverage, cross-module links. | lean-doc-improvement |
| [lean-doc-requirements-handbook.md](lean-doc-requirements-handbook.md) | Traceability matrices, requirement tags, documentation gates. | lean-doc-requirements |
| [lean-integration-protocol-handbook.md](lean-integration-protocol-handbook.md) | CI/CD pipeline integration, automated lake build verification. | lean-integration-protocol |
| [math-product-management-handbook.md](math-product-management-handbook.md) | Quantitative product modeling, user flow state machines. | math-product-management |
| [math-project-management-handbook.md](math-project-management-handbook.md) | Critical path formalization, resource allocation DAGs. | math-project-management |
| [math-strategy-studio-handbook.md](math-strategy-studio-handbook.md) | Scenario planning, decision trees, minimax optimization. | math-strategy-studio |
| [research-council-handbook.md](research-council-handbook.md) | Research topic prioritization, peer review standards. | research-council |
| [research-output-templates.md](research-output-templates.md) | Standardized schemas for research memoranda and evaluation cards. | research-council |
| [research-queue.md](research-queue.md) | Task scheduling and backlog management for research workflows. | research-council |
| [research-synthesis-engine-handbook.md](research-synthesis-engine-handbook.md) | Multi-source evidence synthesis, consensus extraction. | research-synthesis-engine |
| [theorem-search.md](theorem-search.md) | Mathlib declaration search idioms: exact?, apply?, Loogle, LeanSearch. | lean-proof |
| [discovery-ladder.md](discovery-ladder.md) | Progressive discovery ladder for formalization campaigns. | lean-research |
| [discovery-ladder-evals.md](discovery-ladder-evals.md) | Evaluation rubrics for discovery ladder stages. | lean-research |
| [ecosystem-refactor.md](ecosystem-refactor.md) | Migration protocols for large-scale Mathlib refactorings. | lean-pr |
