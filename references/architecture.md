# Hybrid Architecture & Dispatch

## Architectural Model
*   **Kernel:** Core Lean 4 Compiler & Prover Lifecycle (Specifier, Prover, Auditor).
*   **Facets:** Domain-Specific Formalization & Analysis Packs (Math, AI, Governance).

## Skill Dispatch Precedence
1. `skills/<X>/`
2. `skills/_overrides/<X>/`
3. `vendor/leanprover-skills/skills/<X>/`
