<div align="center">

# proof-skills

**A friendly collection of [Agent Skills](https://agentskills.io) for working with Lean 4 and Mathlib4.**

Tactics · domain math · documentation & review workflows · generic tooling

[![License: Apache 2.0](https://img.shields.io/badge/license-Apache_2.0-blue.svg)](LICENSE)
[![Lean 4](https://img.shields.io/badge/Lean-4-2D3748.svg?logo=lean&logoColor=white)](https://github.com/leanprover/lean4)
[![Mathlib4](https://img.shields.io/badge/Mathlib-4-4E7CD0.svg)](https://github.com/leanprover-community/mathlib4)
[![APM](https://img.shields.io/badge/APM-skill_collection-6e5494.svg)](https://github.com/microsoft/apm)
[![First-party skills](https://img.shields.io/badge/first--party%20skills-63-2c974b.svg)](skills/)
[![Legacy Stubs](https://img.shields.io/badge/legacy%20stubs-4-6e5494.svg)](skills/_overrides/)
[![Taxonomy](https://img.shields.io/badge/taxonomy-hybrid_architecture-blue.svg)](TAXONOMY.md)

</div>

Fork of [leanprover/skills](https://github.com/leanprover/skills)
---

## Welcome!

This repository provides a comprehensive toolkit for AI agents to interact with Lean 4 and Mathlib4. Whether you're working on toolchain setup, proof tactics, minimal working examples, or end-to-end formalization workflows, these skills help streamline the process.

## Quick Start

You can install this bundle into your coding-agent harness (like Copilot, Claude Code, Cursor, Codex, or Gemini) using [APM](https://github.com/microsoft/apm):

```bash
apm install r-irbe/proof-skills                       # install the full bundle
apm install r-irbe/proof-skills --skill lean-proof    # install a specific skill
apm install r-irbe/proof-skills#v0.1.0                # install a specific version
```

Once installed, the skills become available for your agent to use by name.

If you prefer to browse or use the source tree directly:

```bash
git clone --recurse-submodules https://github.com/r-irbe/proof-skills
```

---

## What's Inside?

Here's a quick overview of how things are organized:

- **[`skills/`](skills/)**: The core collection of skills, covering everything from basic compilation and proving to domain-specific math and process workflows.
- **[`TAXONOMY.md`](TAXONOMY.md)**: A high-level view of how skills are grouped.
- **[`FACETS.md`](FACETS.md)**: An overview of the specialized domain areas (Math, AI, Governance).
- **[`ROLES.md`](ROLES.md)**: Details on how different agent roles (like Specifier, Prover, Auditor, Gardener) collaborate.
- **[`templates/`](templates/)**: Helpful starting points for Lean modules and workflows.
- **[`references/`](references/)**: Background notes, guides, and detailed manuals for the skills.
- **[`scripts/`](scripts/)**: Helpful tools for evaluation, linting, and repo checks. See [`scripts/README.md`](scripts/README.md) for technical details on CI and tooling.
- **[`zettelkasten/`](zettelkasten/)**: Our internal knowledge base.

---

## Project Customization

These tools are designed to work across any project. Instead of modifying the core templates directly, we recommend creating a thin override layer in your specific project to encode your custom details.

---

<div align="center">
<sub>
Apache-2.0 · authored by <a href="https://github.com/r-irbe">@r-irbe</a> ·
issues & PRs welcome at
<a href="https://github.com/r-irbe/proof-skills">github.com/r-irbe/proof-skills</a>
</sub>
</div>
