# proof-skills Taxonomy -- 5-Tier Abstraction Hierarchy & Domain Facets

Classification of all first-party skills across the 5-Tier Abstraction Hierarchy,
combining deterministic compiler infrastructure, tactic discipline, domain formalization,
knowledge graph integration, and multi-agent review governance.

---

## 1. Five-Tier Abstraction Hierarchy

To eliminate sprawl and guarantee deterministic token economy (<1,200 tokens per dispatch),
all proof skills are stratified into five explicit layers of abstraction:

```text
+-------------------------------------------------------------------------------+
| L4: Governance, Audit & Review                                                |
|     lean-quality-engine, lean-review-council, lean-retroactive-audit,         |
|     lean-security-formalization, Biba integrity lattices, invariant audits    |
+-------------------------------------------------------------------------------+
                                       ^
                                       |
+-------------------------------------------------------------------------------+
| L3: Knowledge & Blueprint Garden                                              |
|     lean-blueprint, lean-dag-visualizer, lean-formalization-breakdown,        |
|     lean-pedagogical-exposition, lean-zettelkasten, Kuzu graph engine (29 bks)|
+-------------------------------------------------------------------------------+
                                       ^
                                       |
+-------------------------------------------------------------------------------+
| L2: Domain Formalization Facets                                               |
|     Mathlib analysis, stochastic, discrete, dynamical, optimization,          |
|     category theory, measure theory, game theory, neuro-symbolic AI           |
+-------------------------------------------------------------------------------+
                                       ^
                                       |
+-------------------------------------------------------------------------------+
| L1: Tactic Discipline & Proof State                                           |
|     lean-proof, lean-proof-review, lean-tautology-triage,                      |
|     lean-tactic-discipline, lean-enforcement (zero sorry / zero warning)     |
+-------------------------------------------------------------------------------+
                                       ^
                                       |
+-------------------------------------------------------------------------------+
| L0: Deterministic Infrastructure Substrate                                    |
|     lean-setup (apm-configure), lean-build, lean-mwe, lean-bisect,             |
|     lean-serve-broker, lean4-lsp-mcp (6 consolidated domain tools)           |
+-------------------------------------------------------------------------------+
```

### Layer Responsibilities & Token Budgets

| Tier | Abstraction Level | Scope & Responsibilities | Token Budget | Dependencies |
| :--- | :--- | :--- | :--- | :--- |
| **L0** | Infrastructure | Toolchain resolution, Lake compilation, MWE extraction, bisection, LSP broker, MCP server. | 0 tokens (pure deterministic CLI) | Host environment, Elan, Lake |
| **L1** | Tactic Discipline | PlainGoal inspection, tactic state filtering, tautology detection, proof golfing. | <500 tokens / query | L0 (`lean4-lsp-mcp`) |
| **L2** | Domain Formalization | Mathlib domain theories, lemma formulation, specification matching. | 800 - 1,500 tokens | L1, L0 |
| **L3** | Knowledge & Blueprints | LaTeX blueprint synchronization, DAG traversal, pedagogical walkthroughs, Kuzu graph search. | <1,000 tokens (sub-ms graph) | L2, L1, Kuzu `.kz` |
| **L4** | Governance & Review | Biba multi-level lattices, proof review councils, security proofs, CI gate audits. | Batch review / multi-agent | L3, L2, L1, L0 |

---

## 2. Core Kernel Skills

Essential skills required for interactive Lean 4 theorem proving, compilation,
diagnostic extraction, bisection, and pull-request hygiene.

| Skill | Lifecycle Role | Tier | Primary Function |
| --- | --- | --- | --- |
| [lean-setup](skills/lean-setup/SKILL.md) | Prover | Tier 1 | Toolchain resolution, elan installation, lean-toolchain pins. |
| [lean-build](skills/lean-build/SKILL.md) | Prover | Tier 1 | Lake compilation, olean artifact management, cache fetching. |
| [lean-proof](skills/lean-proof/SKILL.md) | Prover | Tier 1 | Interactive tactic proving, LSP plainGoal queries, Try this code actions. |
| [lean-gateway](skills/lean-gateway/SKILL.md) | Prover | Tier 1 | Central dispatch gateway routing proof requests to specialized skills. |
| [lean-mwe](skills/lean-mwe/SKILL.md) | Specifier | Tier 1 | Minimal Working Example extraction and dependency isolation. |
| [lean-specification](skills/lean-specification/SKILL.md) | Specifier | Tier 1 | Formal specification authoring, consistency checks, axiom minimization. |
| [lean-blueprint](skills/lean-blueprint/SKILL.md) | Specifier | Tier 2 | Formal blueprint construction and dependency DAG visualization. |
| [lean-doc-requirements](skills/lean-doc-requirements/SKILL.md) | Specifier | Tier 2 | Formal requirement traceability matrices and documentation gates. |
| [lean-bisect](skills/lean-bisect/SKILL.md) | Auditor | Tier 1 | Git bisection of compiler regressions and broken proofs across toolchains. |
| [lean-pr](skills/lean-pr/SKILL.md) | Auditor | Tier 1 | Mathlib and upstream PR preparation, branch hygiene, CI validation. |
| [lean-proof-review](skills/lean-proof-review/SKILL.md) | Auditor | Tier 1 | Proof golfing, simp-set optimization, term-mode conversion. |
| [lean-enforcement](skills/lean-enforcement/SKILL.md) | Auditor | Tier 1 | Zero-sorry, zero-warning CI policy enforcement. |
| [lean-quality-engine](skills/lean-quality-engine/SKILL.md) | Auditor | Tier 2 | Quality metrics, heartbeats monitoring, proof complexity scoring. |
| [lean-tautology-triage](skills/lean-tautology-triage/SKILL.md) | Auditor | Tier 1 | Detection of circular proofs, vacuous hypotheses, and tautological goals. |
| [lean-formalization-breakdown](skills/lean-formalization-breakdown/SKILL.md) | Auditor / Specifier | Tier 1 | Multi-wave formalization breakdown, static census, DAG depth, landmark extraction. |

---

## 3. Mathematical Domain Facet

Specialized formalization contracts aligned with Mathlib4 namespaces.

| Skill | Sub-domain | Key Mathlib Theories |
| --- | --- | --- |
| [lean-math-foundations](skills/lean-math-foundations/SKILL.md) | Foundations | Logic, SetTheory, Cardinal, Ordinal |
| [lean-math-discrete](skills/lean-math-discrete/SKILL.md) | Discrete Math | Combinatorics, Data.Finset, GraphTheory |
| [math-algebra-category](skills/math-algebra-category/SKILL.md) | Abstract Algebra | Algebra.Group, Algebra.Ring, CategoryTheory |
| [math-graph-knowledge](skills/math-graph-knowledge/SKILL.md) | Graph Theory | Combinatorics.SimpleGraph, Hypergraphs |
| [lean-math-analysis](skills/lean-math-analysis/SKILL.md) | Real Analysis | Topology.MetricSpace, Analysis.Calculus |
| [lean-math-optimization](skills/lean-math-optimization/SKILL.md) | Optimization | Analysis.Convex, Optimization.Duality |
| [math-topology-analysis](skills/math-topology-analysis/SKILL.md) | General Topology | Topology.Basic, Topology.Compactness |
| [lean-math-dynamical](skills/lean-math-dynamical/SKILL.md) | Dynamical Systems | Dynamics.Flow, Dynamics.FixedPoints |
| [math-nonlinear-dynamics](skills/math-nonlinear-dynamics/SKILL.md) | Nonlinear Systems | BifurcationTheory, LyapunovStability |
| [math-measure-probability](skills/math-measure-probability/SKILL.md) | Measure & Probability | MeasureTheory.MeasureSpace, ProbabilityTheory |
| [lean-math-stochastic](skills/lean-math-stochastic/SKILL.md) | Stochastic Processes | ProbabilityTheory.Martingale, MarkovChains |
| [math-time-series](skills/math-time-series/SKILL.md) | Time Series Analysis | StochasticProcesses.Stationarity |
| [math-optimization-game](skills/math-optimization-game/SKILL.md) | Game Theory | GameTheory.NormalForm, NashEquilibrium |
| [lean-competitive-math](skills/lean-competitive-math/SKILL.md) | Olympiad / Contest | MiniF2F, Putnam, IMO Formalizations |

---

## 4. AI and Neuro-Symbolic Facet

Contracts for autoformalization, neural proof search, and verifiable agents.

| Skill | Focus Area |
| --- | --- |
| [lean-ai-formalization](skills/lean-ai-formalization/SKILL.md) | Informal-to-formal translation and lemma extraction. |
| [lean-applied-reasoning](skills/lean-applied-reasoning/SKILL.md) | Multi-step symbolic deduction pipelines. |
| [lean-causal-reasoning](skills/lean-causal-reasoning/SKILL.md) | Pearl causal hierarchy and formal do-calculus. |
| [lean-knowledge-formalization](skills/lean-knowledge-formalization/SKILL.md) | Domain ontologies and structured mathematical knowledge. |
| [lean-nested-learning](skills/lean-nested-learning/SKILL.md) | Hierarchical reasoning and recursive problem decomposition. |
| [ai-agentic-evolving](skills/ai-agentic-evolving/SKILL.md) | Self-improving agent architectures and invariant preservation. |
| [ai-causal-deontic](skills/ai-causal-deontic/SKILL.md) | Normative ethics, obligations, permissions, and causal bounds. |
| [ai-commonsense-reasoning](skills/ai-commonsense-reasoning/SKILL.md) | Non-monotonic logics and qualitative reasoning. |
| [ai-high-stakes-verifiable](skills/ai-high-stakes-verifiable/SKILL.md) | High-assurance formal safety criteria. |
| [ai-symbolic-neuro](skills/ai-symbolic-neuro/SKILL.md) | Neuro-symbolic bridges and differentiable logic. |

---

## 5. Governance, Systems and Operations Facet

Engineering operations, documentation review councils, and cross-session knowledge gardening.

| Category | Skills |
| --- | --- |
| **Security & Systems** | [applied-data-information-security](skills/applied-data-information-security/SKILL.md), [applied-engineering-disciplines](skills/applied-engineering-disciplines/SKILL.md), [lean-security-formalization](skills/lean-security-formalization/SKILL.md), [lean-vendor-substrate](skills/lean-vendor-substrate/SKILL.md) |
| **Legal & Intelligence** | [applied-intelligence-analysis](skills/applied-intelligence-analysis/SKILL.md), [applied-legal-reasoning](skills/applied-legal-reasoning/SKILL.md), [applied-strategy-analysis](skills/applied-strategy-analysis/SKILL.md) |
| **Strategy & Management** | [math-product-management](skills/math-product-management/SKILL.md), [math-project-management](skills/math-project-management/SKILL.md), [math-strategy-studio](skills/math-strategy-studio/SKILL.md) |
| **Councils & Review** | [lean-review-council](skills/lean-review-council/SKILL.md), [research-council](skills/research-council/SKILL.md), [research-synthesis-engine](skills/research-synthesis-engine/SKILL.md), [epistemic-discovery-engine](skills/epistemic-discovery-engine/SKILL.md), [epistemic-mapping](skills/epistemic-mapping/SKILL.md) |
| **Doc & Synthesis** | [lean-doc-feedback](skills/lean-doc-feedback/SKILL.md), [lean-doc-improvement](skills/lean-doc-improvement/SKILL.md), [lean-report](skills/lean-report/SKILL.md), [lean-research](skills/lean-research/SKILL.md), [lean-research-types](skills/lean-research-types/SKILL.md), [lean-package-research](skills/lean-package-research/SKILL.md), [lean-integration-protocol](skills/lean-integration-protocol/SKILL.md), [lean-pedagogical-exposition](skills/lean-pedagogical-exposition/SKILL.md) |
| **Gardening & Memory** | [lean-zettelkasten](skills/lean-zettelkasten/SKILL.md), [lean-retro-methodology](skills/lean-retro-methodology/SKILL.md), [lean-retroactive-audit](skills/lean-retroactive-audit/SKILL.md) |

---
