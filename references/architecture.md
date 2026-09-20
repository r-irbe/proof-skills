# Hybrid Architecture & Dispatch

## 1. Architectural Model

This repository implements a Hybrid Architecture that combines core lifecycle operations with specialized domain knowledge. It is designed to scale formalization efforts reliably.

*   **Kernel**: Handles the core Lean 4 Compiler and Prover Lifecycle operations (Build, Prove, Audit, Test).
*   **Facets**: Provides domain-specific Formalization and Analysis Packs (Math, AI, Governance).

For a high-level, human-friendly summary of the Domain Facets, see `FACETS.md`. For a breakdown of the Kernel capabilities, see `TAXONOMY.md`.

## 2. Dispatch Principles & Literature

The routing of agent skills and the handling of safety gates are informed by structured deployment frameworks and cost-aware routing:

1.  **FrugalGPT and Cascade Routing**: Utilizing a hierarchy of models or fallback mechanisms based on confidence thresholds and task difficulty.
    *   *Reference*: Chen, L., et al. (2023). "FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance." *arXiv preprint arXiv:2305.05176*.
    *   *Application*: Applied in our `AGENT.md` dispatch fallback rules, where agents degrade gracefully based on human-in-the-loop (HITL) availability.

2.  **Safety and Reversibility Tiers**:
    *   *Reference*: OWASP Foundation. (2023). "OWASP LINDDUN-GO: Threat Modeling Framework."
    *   *Application*: The fail-closed discipline and the strict `reversible` vs `irreversible` tiers outlined in our agent constraints prevent unauthorized destructive actions during autonomous runs.

## 3. Skill Dispatch Precedence

When an agent requests a skill by its slug (`<X>`), the runtime must resolve the path strictly in the following order. This ensures project-specific overrides supersede upstream tools without breaking stable slug names.

1.  `skills/<X>/` (First-party skills authored in this repo)
2.  `skills/_overrides/<X>/` (Local project overrides)
3.  `vendor/leanprover-skills/skills/<X>/` (Read-only upstream fallback)
