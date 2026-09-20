# Comprehensive Analysis & Proposal: Documentation Optimization

## 1. Human-Oriented Files: `README.md`, `TAXONOMY.md`, `FACETS.md`
**Goal:** Humanize the language, improve readability, remove overly technical AI-isms/rhythms, and strip non-functional facts and transient statistics.

### `README.md`
*   **Issues:**
    *   Contains transient statistics: "63 first-party skills", "4 legacy REDIRECT stubs", "38 Lean/workflow templates", "58 notes and handbooks", "50-case suite". These will easily drift out of date.
    *   Uses highly technical/AI-isms and somewhat robotic structure (e.g., "authoritative catalog", "preserving deprecated slugs per Chesterton protocol", "hoisted into the harness's runtime directory").
    *   The "Tooling" table has deep technical descriptions of CI gates which are largely irrelevant to someone just looking for an overview.
*   **Proposed Structural Changes:**
    *   Rewrite the intro and quickstart to be conversational and welcoming.
    *   Remove all raw numbers (e.g., change "63 first-party SKILL.md files" to "first-party skills").
    *   Simplify "What is in here" and "Repository layout" to give an intuitive overview rather than an exhaustive index.
    *   Relocate the dense `scripts/` tooling explanations (e.g., `apm_validate.py`, `check_conformance.py`, `run_eval.py` details) to a `scripts/README.md` or a dedicated reference file.
    *   Remove the "Status & contracts" block, folding essential pointers smoothly into the text.

### `TAXONOMY.md`
*   **Issues:**
    *   Title and header are overly formal ("Authoritative classification...", "Hybrid Architecture", "Strict 7-bit ASCII only").
    *   Transient statistics: "63 first-party skills", "14 Skills", "10 Skills", "25 Skills", "4 Overrides".
    *   The tables and ASCII art are dense. "Strict 7-bit ASCII only" is an instruction meant for agents, not humans.
*   **Proposed Structural Changes:**
    *   Refine to a clean, easy-to-read narrative of how skills are grouped (Core Kernel, Math, AI, Governance).
    *   Remove all statistics and counts. Remove the "Strict 7-bit ASCII only" directive.
    *   Simplify the ASCII art diagram or replace it with a clean markdown nested list.
    *   Remove the "Legacy Redirect Stubs" section entirely from this human-facing view.
    *   Relocate the strict architectural constraints/definitions to a reference file like `references/architecture.md`.

### `FACETS.md`
*   **Issues:**
    *   Similar to Taxonomy: starts with "Authoritative catalog...", "Strict 7-bit ASCII only."
    *   Includes an ASCII map with statistics ("14 Skills", "10 Skills", "25 Skills").
*   **Proposed Structural Changes:**
    *   Humanize descriptions. Use engaging language rather than formal catalogs.
    *   Remove the ASCII map and statistics.
    *   Convert sections into a friendly overview of the three main facets (Math, AI, Governance).
    *   Relocate the exhaustive list of specific `SKILL.md` mappings to a technical index if necessary, but keep this file focused on *what* the facets are, conceptually.

---

## 2. Machine-Oriented Files: `AGENT.md`, `ROLES.md`, `GUARDRAILS.md`
**Goal:** Maximize token/context efficiency and instruction adherence. Remove conversational fluff, contextual stories, and formatting meant for human readability. Transition to dense structures (YAML/JSON/strict bulleted lists).

### `AGENT.md`
*   **Issues:**
    *   Contains conversational prose: "Authoritative entry-point for any AI agent doing work inside this repo. Read this *before* you touch any file."
    *   Section 0 contains human-readable installation instructions and explanations of what APM does.
    *   Section 1.5.1 ("Sub-agent fleet patterns") is extremely long and written as a narrative of "Lessons captured from Rounds 18–21...".
    *   Contains statistics ("63 first-party skills") and prose formatting.
*   **Proposed Structural Changes:**
    *   Convert the entire document to YAML or a hyper-dense Markdown list structure (e.g., `rule: constraint`).
    *   Remove Section 0 entirely (or move it to `README.md` if any part of it is actually for humans).
    *   Compress Section 1.5.1 into strict, un-storied directives (e.g., `constraint: use_write_agent_for_tmp_haiku`, `constraint: use_median_for_ensembles`). Relocate the "Lessons learned" story context to `references/eval_history.md`.
    *   Remove all Markdown blockquotes, narrative transitions, and "Why" justifications unless strictly required for rule application.

### `ROLES.md`
*   **Issues:**
    *   Narrative intro: "To prevent context collapse, persona drift, and proof degradation..."
    *   ASCII art diagram.
    *   Conversational formatting of "Mission", "Assigned Skills", "Outputs", "Stop Condition".
*   **Proposed Structural Changes:**
    *   Convert to a dense structured format (e.g., YAML representing the State Machine of the swarm).
    *   Remove the ASCII art.
    *   Remove "Mission" prose. Keep only actionable triggers, constraints, required inputs, and exact stop conditions.
    *   Relocate the conceptual explanation of the Swarm methodology to `references/swarm_methodology.md`.

### `GUARDRAILS.md`
*   **Issues:**
    *   Narrative preamble explaining "Rules of maintenance".
    *   Formatting is tabular Markdown which consumes more tokens than necessary (due to pipes and spaces).
    *   Some error descriptions contain contextual stories (e.g., GT-16 "when a project claims two or more...").
*   **Proposed Structural Changes:**
    *   Strip the preamble down to absolute core directives.
    *   Convert tables into a dense JSON or YAML dictionary format (e.g., `GT-01: { fail: "...", remedy: "..." }`).
    *   Remove explanatory context from the remedies. State only the explicit corrective action.
    *   Relocate the "Rules of maintenance" philosophy to an internal contributor guide (`references/contributing.md`).

---

## Summary of Action Plan
1. **Refactor Human Files:** Make them welcoming, strip numbers/stats, remove AI-isms, drop agent-directives (like "Strict 7-bit ASCII").
2. **Refactor Agent Files:** Compress into YAML/JSON/Dense lists. Strip prose, history, and narrative justifications.
3. **Relocate Details:** Move detailed architectural lists, historical lessons, and toolings to the `references/` or `scripts/` directories as appropriate.
