# proof-skills Domain Facets Catalog (`agents/facets/registry.json`)

Catalog of the 5 modular domain facets (`core`, `math`, `ai`, `governance`, `multi-prover`) and 2 specialized template packs (`pack-arithmetic-geometry`, `pack-fluid-pde`) across the 65 active v2 skills in `proof-skills`.

---

## 1. Facet Architecture (`65 Skills = 12 Core + 8 Math + 8 AI + 33 Governance + 4 Multi-Prover`)

Machine-readable bindings between the **5 Role-Actor Containers** (`agents/*.md`), **23 Soul Overlays** (`agents/souls/*.md`), and **5 Domain Facets** live in [`agents/facets/registry.json`](agents/facets/registry.json) and [`apm.yml`](apm.yml).

```text
+-----------------------------------------------------------------------------------+
|                     DOMAIN FACETS MAP (65 ACTIVE V2 SKILLS)                       |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [ CORE FACET (12) ]     [ MATH FACET (8) ]      [ AI FACET (8) ]                 |
|  Gateway, Spec, Proof,   Foundations, Discrete,  AI Safety, Causal/Deontic,       |
|  Repair, Core-Only,      Stochastic, Dynamical,  Knowledge/KRR, Applied,          |
|  Build, Setup, Bisect,   Optimization, Analysis, Bigraphs, Nested Learning,       |
|  MWE, Counterexample,    Competitive,            Security, Guard-Judge Eval       |
|  Blueprint, SAIR         Convergence                                              |
|                                                                                   |
|  [ MULTI-PROVER (4) ]    [ GOVERNANCE, COUNCILS & GARDENING FACET (33) ]          |
|  Cross-ITP Porting,      Proof Review, Enforcement, Axiom Closure, Replay,        |
|  Rocq/MathComp Adapter,  Tautology Triage, Quality Engine, Review/Research        |
|  Isabelle/Isar Adapter,  Councils, Pedagogical Exposition, Reports, RETRO,        |
|  HOL/Metamath Adapter    Zettelkasten, Upstream Porting, Engineering & Legal      |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

---

## 2. Math Facet (`math` profile -- 8 Unified Skills)

Each skill pairs a `<4,000`-byte dispatch contract (`skills/<slug>/SKILL.md`) with a 3-table lookup handbook (`references/<slug>-handbook.md` containing **Goal-Shape Templates**, **Intent-to-Tactic Phrasebook**, and **Error-to-Fix Table**):

- `lean-math-foundations` (unifies `math-algebra-category`): Type universes, quotients, groups, rings, fields, Galois connections, category theory.
- `lean-math-discrete` (unifies `math-graph-knowledge`): `Finset`, `BigOperators`, simple graphs, hypergraphs, DAGs, posets, provenance chains.
- `lean-math-stochastic` (unifies `math-measure-probability` + `math-time-series`): Measure spaces, Lebesgue/Bochner integrals, Markov chains, martingales, time series, ergodic theory.
- `lean-math-dynamical` (unifies `math-nonlinear-dynamics`): Discrete & continuous Lyapunov stability, LaSalle invariance, bifurcations, cusp catastrophe.
- `lean-math-optimization` (unifies `math-optimization-game`): Convex optimization, Bellman equations, contraction mappings, Nash equilibria, mechanism design.
- `lean-math-analysis` (unifies `math-topology-analysis`): Bourbaki filters (`Filter.Tendsto`), metric/normed spaces, derivatives (`HasDerivAt`), compactness.
- `lean-competitive-math`: Competition math & Project Euler (`decide`, `norm_num`, modular arithmetic).
- `lean-convergence-verification`: Discrete Lyapunov energy certificates and loop termination bounds.

---

## 3. AI & Neuro-Symbolic Facet (`ai` profile -- 8 Unified Skills)

- `lean-ai-formalization` (unifies `ai-agentic-evolving` + `ai-high-stakes-verifiable`): Agentic AI safety barriers, self-modifying loop invariants, high-stakes certification.
- `lean-causal-reasoning` (unifies `ai-causal-deontic`): Pearl causal DAGs, interventions (`do`-calculus), counterfactuals, and deontic obligations/permissions.
- `lean-knowledge-formalization` (unifies `ai-commonsense-reasoning` + `ai-symbolic-neuro`): Ontologies, Kripke epistemic frames (`S5`/`KD45`), Allen interval calculus, neuro-symbolic KRR.
- `lean-applied-reasoning` (unifies `applied-intelligence-analysis` + `applied-strategy-analysis`): Structured Analytic Techniques (ACH), evidentiary scoring, strategic wargaming.
- `lean-bigraph-modeling`: Robin Milner Bigraphical Reactive Systems (place forests & link hyperedges).
- `lean-nested-learning`: Hierarchical multi-timescale learning dynamics.
- `lean-security-formalization`: Information-flow non-interference, Biba/Bell-LaPadula lattices, access control.
- `ai-guard-judge-eval`: Stratified safety-guard and LLM-judge calibration.

---

## 4. Multi-Prover Concordance Facet (`multi-prover` profile -- 4 Skills + 6 Dialect Tables)

Backed by `vendor/itp-ontology/cross-itp-concordance.v1.json` (**20 canonical proof mechanisms `CONC-01..20`** across **6 prover families**: `lean4`, `coq_mathcomp`, `isabelle_hol`, `hol_light`, `agda`, `metamath`) and `references/dialects/{lean4,rocq,isabelle,hol_light,agda,metamath}.json`:

- `itp-cross-porting`: Top-level cross-ITP router (`lean_search(source: "concordance")`) and Agda (`--without-K` / `--cubical`) adapter.
- `rocq-proof-adapter`: Coq / Rocq / SSReflect / Mathematical Components / Hierarchy Builder / `Equations` -> Lean 4.
- `isabelle-isar-adapter`: Isabelle/HOL / Isar / `locale` / Lifting & Transfer / `HOL-Analysis` -> Lean 4.
- `hol-metamath-adapter`: HOL Light (`.ml` tactical proofs, `REAL_RING`, `WORD_BLAST`) & Metamath (`set.mm` ZFC deduction chains) -> Lean 4.

---

## 5. Governance, Councils & Template Packs (`governance`, `pack-arithmetic-geometry`, `pack-fluid-pde`)

- **Auditing & Enforcement**: `lean-proof-review`, `lean-enforcement`, `lean-axiom-closure`, `lean-replay-verification`, `lean-tautology-triage`, `lean-quality-engine`, `lean-deep-audit`, `lean-retroactive-audit`.
- **Councils, Research & Exposition**: `lean-review-council`, `research-council`, `research-synthesis-engine`, `epistemic-discovery-engine`, `epistemic-mapping`, `lean-research`, `lean-package-research`, `lean-pedagogical-exposition`, `lean-report`, `lean-doc-improvement`, `lean-doc-feedback`, `lean-doc-requirements`.
- **Refactoring, Gardening & Engineering**: `lean-proof-refactor`, `lean-zettelkasten`, `lean-retro-methodology`, `lean-upstream-porting`, `lean-pr`, `lean-vendor-substrate`, `lean-formalization-breakdown`, `lean-dag-visualizer`, `lean-integration-protocol`, `math-product-management`, `math-project-management`, `math-strategy-studio`, `applied-engineering-disciplines`, `applied-legal-reasoning`, `applied-data-information-security`.
- **Modular Template Packs (`templates/packs/`)**:
  - `pack-arithmetic-geometry` (`templates/packs/arithmetic-geometry/`): 131 ModularJacobian, Heegner point, Euler system, Fontaine-Laffaille, and FLT templates.
  - `pack-fluid-pde` (`templates/packs/fluid-pde/`): 10 Fluid PDE, vorticity confinement, Gevrey regularity, and Reynolds cascade templates.
