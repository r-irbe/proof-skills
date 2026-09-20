# proof-skills Domain Facets Catalog

Catalog of domain-specialized formalization packs across the
proof-skills repository.



---

## 1. Facet Model

While Core Kernel skills provide the universal mechanics of proving and compiling,
Domain Facets supply deep domain knowledge, Mathlib theorem vocabularies, and
specialized formalization patterns.

```text
+-----------------------------------------------------------------------------+
|                            DOMAIN FACETS MAP                                |
+-----------------------------------------------------------------------------+
|                                                                             |
|  [ MATH FACET ]           [ AI FACET ]            [ GOVERNANCE FACET ]      |
|  14 Skills:               10 Skills:              25 Skills:                |
|  Analysis, Discrete,      Neuro-Symbolic,         Security, Intelligence,   |
|  Algebra, Topology,       Causal Logic,           Legal Reasoning,          |
|  Probability, Games       Verifiable Agents       Synthesis, Zettelkasten   |
|                                                                             |
+-----------------------------------------------------------------------------+
```

---

## 2. Math Facet

Designed for pure and applied mathematicians working against Mathlib4.

- **Foundational & Discrete**:
  - `lean-math-foundations`: Type universes, inductive types, quotients, classical axioms.
  - `lean-math-discrete`: Combinatorics, graph theory, finite sets, recurrence.
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
  - `lean-knowledge-formalization`: Encoding ontologies and domain theories.
  - `lean-nested-learning`: Recursive problem decomposition and sub-agent hierarchies.
- **Agent Architecture & Safety**:
  - `ai-agentic-evolving`: Verified self-modifying agent loops and safety bounds.
  - `ai-high-stakes-verifiable`: High-assurance safety constraints and failure modes.
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
- **Legal & Strategic Reasoning**:
  - `applied-legal-reasoning`: Formal statutory models, precedent analysis.
  - `applied-strategy-analysis`: Strategic decisions, payoff structures.
  - `applied-intelligence-analysis`: Structured analytic techniques and hypothesis evaluation.
- **Research Operations & Gardening**:
  - `research-council`: Multi-agent peer review boards.
  - `research-synthesis-engine`: Multi-source evidence consolidation.
  - `epistemic-discovery-engine`: Abductive reasoning and hypothesis generation.
  - `epistemic-mapping`: Formal epistemic state graphs.
  - `lean-zettelkasten`: Persistent lemma indexing and retrieval.
  - `lean-retro-methodology`: Systematic post-mortems of formalization campaigns.
  - `lean-retroactive-audit`: Tracking theorem depreciation and blast radius.
