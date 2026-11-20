# Domain Facet Registry (`agents/facets/registry.json`)

Catalog of the 5 modular Lean 4 domain facets (`core`, `math`, `ai`, `governance`, `multi-prover`) plus opt-in APM packs (`pack-applied-strategy`, `pack-arithmetic-geometry`, `pack-fluid-pde`, `pack-altproof`).

---

## 1. Facet Architecture (`38 Core Lean Skills = 12 Core + 6 Math + 3 AI + 13 Governance + 4 Multi-Prover`)

Machine-readable bindings between the **5 Role-Actor Containers** (`agents/*.md`), **24 Soul Overlays** (`agents/souls/*.md`), **38 Active Lean Skills** (`skills/*`), and **Skill Alias Map** (`skill_aliases`) live in [`agents/facets/registry.json`](agents/facets/registry.json) and [`apm.yml`](apm.yml).

- **`core` (12 skills)**: `lean-gateway`, `lean-specification`, `lean-blueprint`, `counterexample-first-proving`, `lean-proof`, `lean-proof-repair`, `lean-core-only`, `lean-kernel-optimization`, `lean-build`, `lean-setup`, `lean-bisect`, `lean-mwe`.
- **`math` (6 skills)**: `lean-math-foundations`, `lean-math-discrete`, `lean-math-stochastic`, `lean-math-dynamical`, `lean-math-optimization`, `lean-math-analysis`.
- **`ai` (3 skills)**: `lean-ai-formalization`, `lean-knowledge-formalization`, `lean-security-formalization`.
- **`governance` (13 skills)**: `lean-verification-gate`, `lean-proof-review`, `lean-tautology-triage`, `lean-corpus-audit`, `lean-review-council`, `lean-proof-refactor`, `lean-pedagogical-exposition`, `lean-doc-sync`, `lean-research`, `research-council`, `lean-retro-methodology`, `lean-dependency-management`, `lean-upstream-pr`.
- **`multi-prover` (4 skills)**: `itp-cross-porting`, `rocq-proof-adapter`, `isabelle-isar-adapter`, `hol-metamath-adapter`.
- **`pack-applied-strategy` (7 opt-in non-Lean skills in `packs/applied-strategy/skills/`)**: `ai-guard-judge-eval`, `applied-data-information-security`, `applied-engineering-disciplines`, `applied-legal-reasoning`, `math-product-management`, `math-project-management`, `math-strategy-studio`.
