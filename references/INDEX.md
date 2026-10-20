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
| [formalization_breakdown_guide.md](formalization_breakdown_guide.md) | 8-wave architectural deconstruction of monumental formalizations, static census, DAG depth, landmark extraction. | lean-formalization-breakdown |
| [lean_to_math_exposition_patterns.md](lean_to_math_exposition_patterns.md) | Translation dictionary from Lean types and proof tactics to beautiful, standard mathematical prose and learning materials. | lean-pedagogical-exposition |
| [mathlib4-conventions.md](mathlib4-conventions.md) | Mathlib4 style guide: snake_case for lemmas, camelCase for types, docstrings, binder hygiene, and implicit arguments. | lean-proof, lean-pr |
| [AUTHORING.md](AUTHORING.md) | Authoring standards for proof-skills SKILL.md contracts, frontmatter validation, and evaluation rubrics. | lean-quality-engine |
| [architecture.md](architecture.md) | Hybrid architecture overview (Kernel + Domain Facets), cascade routing, and skill dispatch precedence. | lean-gateway |
| [project_structure.md](project_structure.md) | Comprehensive directory map of root configurations, skill directories, templates, references, and tooling. | lean-setup, lean-gateway |
| [contributing.md](contributing.md) | Contribution guidelines, confidentiality rules, and verification requirements for proof-skills authors. | lean-pr, lean-quality-engine |
| [eval_history.md](eval_history.md) | Historical synthesis of sub-agent fleet patterns, model calibration rounds, and evaluation findings. | lean-gateway, lean-quality-engine |
| [swarm_methodology.md](swarm_methodology.md) | Stanford ACE Prover Swarm methodology, role specialization (Specifier, Prover, Auditor, Gardener), and handoff protocols. | lean-gateway, lean-review-council |
| [bibliography.md](bibliography.md) | Academic bibliography and foundational literature backing formalization, agent routing, and verification protocols. | lean-research |
| [lean4-core-only-profile.md](lean4-core-only-profile.md) | Stdlib/Core-only Lean 4 profile without Mathlib: available tactics, structural induction idioms, and arithmetic rules. | lean-core-only, lean-proof |
| [mathlib-module-system-notes.md](mathlib-module-system-notes.md) | Mathlib4 module-system migration notes: notation propagation, instance sealing, and positional-implicit pitfalls. | lean-upstream-porting, lean-proof |
| [upstream/lean-bug-report-pipeline.md](upstream/lean-bug-report-pipeline.md) | Upstream Lean 4 bug report extraction, MWE reduction, and bisect-to-issue pipeline reference. | lean-mwe, lean-bisect, lean-pr |
| [upstream/lean-nightly-infrastructure.md](upstream/lean-nightly-infrastructure.md) | Upstream Lean 4 nightly CI, radar, and toolchain bisect infrastructure reference. | lean-bisect, lean-setup |
| [upstream/lean4-pr.md](upstream/lean4-pr.md) | Upstream `leanprover/lean4` pull request workflow, commit conventions, and CI validation reference. | lean-pr, lean-upstream-porting |
| [upstream/mathlib4-pr.md](upstream/mathlib4-pr.md) | Upstream Mathlib4 pull request authoring, bors commands, and review lifecycle reference. | lean-pr, lean-upstream-porting |
| [upstream/mathlib4-review.md](upstream/mathlib4-review.md) | Upstream Mathlib4 reviewer checklist, golf idioms, and style conventions reference. | lean-proof-review, lean-pr |

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
| [../skills/math-topology-analysis/SKILL.md](../skills/math-topology-analysis/SKILL.md) | General topology, topological spaces, compactness, connected components (inline v2 skill). | math-topology-analysis |
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
| [../skills/ai-causal-deontic/SKILL.md](../skills/ai-causal-deontic/SKILL.md) | Causal inference, do-calculus, deontic logic, normative obligations (inline v2 skill). | ai-causal-deontic |
| [ai-commonsense-reasoning-handbook.md](ai-commonsense-reasoning-handbook.md) | Default reasoning, non-monotonic logic, commonsense knowledge frames. | ai-commonsense-reasoning |
| [ai-high-stakes-verifiable-handbook.md](ai-high-stakes-verifiable-handbook.md) | High-assurance verification, formal safety guarantees, fault trees. | ai-high-stakes-verifiable |
| [../skills/ai-symbolic-neuro/SKILL.md](../skills/ai-symbolic-neuro/SKILL.md) | Neuro-symbolic integration, differentiable theorem proving, embedding logic (inline v2 skill). | ai-symbolic-neuro |
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
| [research-council-skill-map.md](research-council-skill-map.md) | Topology map of skills governed by the research and review councils. | research-council, lean-review-council |
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
