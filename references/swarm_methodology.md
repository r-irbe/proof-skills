# Stanford ACE Prover Swarm Methodology

## 1. Overview and Motivation

To prevent context collapse, persona drift, and proof degradation in long-running Lean 4 sessions, the formalization lifecycle in this repository adopts a multi-agent swarm architecture. This methodology is heavily influenced by recent advancements in Agentic architectures (such as the Stanford AI Lab frameworks) and iterative multi-agent coordination.

Agents operating on mathematical formalization face severe context limits when mixing creative proving, syntax auditing, and long-term memory management. By separating concerns, we ensure agents transition sequentially and never mix generative proving with memory curation in the same context window.

## 2. Theoretical Backing & Literature

The architectural choices in this methodology build upon several core concepts in modern LLM research:

1.  **Multi-Agent Role Specialization**: Breaking complex reasoning tasks into specialized agent roles (Specifier, Prover, Auditor, Gardener) prevents persona drift and improves accuracy.
    *   *Reference*: Wu, Q., et al. (2023). "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation." *arXiv preprint arXiv:2308.08155*.
    *   *Application*: Ensures that agents focused on high-level blueprinting do not get bogged down in the syntax of `simp` tactics.

2.  **Iterative Proof Refinement and Auditing**: Using separate roles to verify and golf proofs is essential for formal systems like Lean 4, where correctness is absolute.
    *   *Reference*: Yang, K., et al. (2023). "LeanDojo: Theorem Proving with Retrieval-Augmented Language Models." *NeurIPS*.
    *   *Application*: The Auditor role acts as a strict verification layer before any knowledge is persisted.

3.  **Cross-Session Knowledge Retrieval (Zettelkasten)**:
    *   *Reference*: Lewis, P., et al. (2020). "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." *NeurIPS*.
    *   *Application*: The Gardener role persists verified tactics to a knowledge graph, preventing the swarm from repeating failures in subsequent sessions.

## 3. The Four Roles

The lifecycle is divided into four sequential roles. For technical details on the precise execution boundaries, required skills, and stop conditions of these roles, refer to the high-level routing rules in `ROLES.md`.

*   **Specifier (Architect)**: Focuses on informal-to-formal translation and module blueprinting.
*   **Prover (Tactician)**: Interacts directly with the Lean 4 Language Server Protocol (LSP) to discharge goals.
*   **Auditor (Reviewer)**: Enforces style, eliminates non-terminal tactics, and runs CI linters.
*   **Gardener (Curator)**: Indexes verified lemmas and prunes failing tactic patterns for future use.

## 4. Handoff Protocol

Transitions between swarm roles utilize structured handoff receipts. This guarantees that context is cleanly passed without carrying over unnecessary token-bloat from previous attempts.
*   *See the exact JSON schema required for handoffs in [`templates/handoff_protocol.json`](../templates/handoff_protocol.json).*
