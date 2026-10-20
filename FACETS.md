# proof-skills Domain Facets Catalog

Catalog of domain-specialized formalization packs across the
proof-skills repository.



---

## 1. Facet Model

While Core Kernel skills (22 skills: `lean-setup`, `lean-build`, `lean-proof`, `lean-core-only`, `lean-gateway`, `lean-mwe`, `lean-specification`, `lean-blueprint`, `lean-dag-visualizer`, `lean-doc-requirements`, `lean-bisect`, `lean-pr`, `lean-proof-review`, `lean-enforcement`, `lean-axiom-closure`, `lean-replay-verification`, `lean-quality-engine`, `lean-deep-audit`, `lean-proof-refactor`, `lean-upstream-porting`, `lean-tautology-triage`, `lean-formalization-breakdown`) provide the universal mechanics of proving, compiling, auditing, and refactoring, Domain Facets (53 skills across Math, AI, and Governance) supply deep domain knowledge, Mathlib theorem vocabularies, and specialized formalization patterns.

```text
+-----------------------------------------------------------------------------+
|                    DOMAIN FACETS MAP (53 + 22 CORE = 75)                    |
+-----------------------------------------------------------------------------+
|                                                                             |
|  [ MATH FACET ]           [ AI FACET ]            [ GOVERNANCE FACET ]      |
|  16 Skills:               11 Skills:              26 Skills:                |
|  Analysis, Discrete,      Neuro-Symbolic,         Security, Intelligence,   |
|  Bigraphs, Convergence,   Causal Logic,           Legal Reasoning, Strategy,|
|  Algebra, Topology,       Verifiable Agents,      Councils, Documentation,  |
|  Probability, Games       Guard-Judge Eval        Synthesis, Zettelkasten   |
|                                                                             |
+-----------------------------------------------------------------------------+
```

---

## 2. Math Facet

Designed for pure and applied mathematicians working against Mathlib4.

- **Foundational & Discrete**:
  - `lean-math-foundations`: Type universes, inductive types, quotients, classical axioms.
  - `lean-math-discrete`: Combinatorics, graph theory, finite sets, recurrence.
  - `lean-bigraph-modeling`: Robin Milner Bigraphical Reactive Systems (Place Graph forests, Link hyperedges, tensor product).
  - `lean-convergence-verification`: Discrete Lyapunov energy decay, ceiling division loop bounds (`Nat.div_add_mod`).
  - `math-algebra-category`: Groups, rings, fields, categories, functors, limits.
  - `math-graph-knowledge`: Graph-theoretic properties, paths, cycles, chromatic numbers.
- **Continuous & Geometric**:
  - `lean-math-analysis`: Metric spaces, uniform continuity, differentiation, integration.
  - `math-topology-analysis`: General topological spaces, filters, compactness.
  - `lean-math-dynamical`: Invariant sets, flows, fixed point theorems, stability.
  - `math-nonlinear-dynamics`: Phase portraits, bifurcations, Lyapunov exponents.
- **Probabilistic & Stochastic**:
  - `math-measure-probability`: Measure spaces, sigma-algebras, Lebesgue integrals.
  - `lean-math-stochastic`: Martingales, Markov chains, stopping times.
  - `math-time-series`: Discrete stochastic processes, autocorrelation, stationarity.
- **Strategic & Competitive**:
  - `math-optimization-game`: Normal and extensive form games, minimax, equilibria.
  - `lean-math-optimization`: Convex analysis, subgradients, duality.
  - `lean-competitive-math`: Competition problem templates (Putnam, IMO, MiniF2F).

---

## 3. AI and Neuro-Symbolic Facet

Designed for AI researchers developing verifiable agents and neural-symbolic systems.

- **Autoformalization & Deduction**:
  - `lean-ai-formalization`: Translating informal LaTeX math into Lean 4 statements.
  - `lean-applied-reasoning`: Multi-step deductive theorem generation.
  - `lean-causal-reasoning`: Formal Pearl causal DAGs, KG quality gates, counterfactual proofs in Lean 4.
  - `lean-knowledge-formalization`: Encoding ontologies and domain theories.
  - `lean-nested-learning`: Recursive problem decomposition, LaSalle invariance, and multi-scale Lyapunov hierarchies.
- **Agent Architecture & Safety**:
  - `ai-agentic-evolving`: Verified self-modifying agent loops and safety bounds.
  - `ai-high-stakes-verifiable`: High-assurance safety constraints and failure modes.
  - `ai-guard-judge-eval`: Guard-style LLM judge benchmarking, band-stratified evaluation, schema adapters, and repeat-pass distributions.
  - `ai-causal-deontic`: Formal Pearl causal inference and normative deontic logic.
  - `ai-commonsense-reasoning`: Default logics, non-monotonic deduction.
  - `ai-symbolic-neuro`: Differentiable theorem proving and neural tactic scoring.

---

## 4. Governance and Systems Facet

Designed for systems engineers, legal analysts, and research program managers.

- **High-Assurance Engineering**:
  - `applied-data-information-security`: Information flow proofs and protocol models.
  - `applied-engineering-disciplines`: Formal specifications in cyber-physical systems.
  - `lean-security-formalization`: Security invariants and access control policies.
  - `lean-vendor-substrate`: Managing upstream dependencies and vendor libraries.
- **Legal, Strategic & Product Management**:
  - `applied-legal-reasoning`: Formal statutory models, precedent analysis.
  - `applied-strategy-analysis`: Strategic decisions, payoff structures.
  - `applied-intelligence-analysis`: Structured analytic techniques and hypothesis evaluation.
  - `math-product-management`: Theorem portfolio management, RICE scoring, roadmaps, and value analysis.
  - `math-project-management`: Critical path formalization, resource allocation DAGs, milestone risk.
  - `math-strategy-studio`: Scenario planning, proof strategy brainstorming, minimax decision trees.
- **Documentation, Synthesis & Exposition**:
  - `lean-doc-feedback`: Bidirectional document-to-Lean feedback loops and readability scoring.
  - `lean-doc-improvement`: Updating papers and documentation from verified Lean results.
  - `lean-report`: Automated blueprint-to-LaTeX formal verification reports.
  - `lean-research`: Literature review, Mathlib declaration discovery, and mathematical survey formalization.
  - `lean-research-types`: Typed research protocol redirect stub (folded into `lean-research` Part 9).
  - `lean-package-research`: Upstream package ecosystem evaluation and dependency readiness.
  - `lean-integration-protocol`: Cross-skill lifecycle orchestration and inter-cluster routing.
  - `lean-pedagogical-exposition`: Textbook-grade mathematical narrative and proof walkthroughs.
- **Research Operations & Gardening**:
  - `lean-review-council`: Multi-agent 5-member formal proof review council and consensus signoffs.
  - `research-council`: Multi-agent peer review boards.
  - `research-synthesis-engine`: Multi-source evidence consolidation.
  - `epistemic-discovery-engine`: Abductive reasoning and hypothesis generation.
  - `epistemic-mapping`: Formal epistemic state graphs.
  - `lean-zettelkasten`: Persistent lemma indexing and retrieval.
  - `lean-retro-methodology`: Systematic post-mortems of formalization campaigns.
  - `lean-retroactive-audit`: Tracking theorem depreciation and blast radius.
