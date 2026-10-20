<div align="center">

# proof-skills

**A bundle of [Agent Skills](https://agentskills.io) for Lean 4 + Mathlib4 proof work.**

Tactics · domain math · doc / review / research workflows · zettelkasten · generic tooling.

[![License: Apache 2.0](https://img.shields.io/badge/license-Apache_2.0-blue.svg)](LICENSE)
[![Lean 4](https://img.shields.io/badge/Lean-4-2D3748.svg?logo=lean&logoColor=white)](https://github.com/leanprover/lean4)
[![Mathlib4](https://img.shields.io/badge/Mathlib-4-4E7CD0.svg)](https://github.com/leanprover-community/mathlib4)
[![APM](https://img.shields.io/badge/APM-skill_collection-6e5494.svg)](https://github.com/microsoft/apm)
[![First-party skills](https://img.shields.io/badge/first--party%20skills-75-2c974b.svg)](skills/)
[![Legacy Stubs](https://img.shields.io/badge/legacy%20stubs-4-6e5494.svg)](skills/_overrides/)
[![Taxonomy](https://img.shields.io/badge/taxonomy-hybrid_architecture-blue.svg)](TAXONOMY.md)

</div>

Fork of [leanprover/skills](https://github.com/leanprover/skills)
---

## Quick start & Customer Environment Setup

`proof-skills` supports three progressive installation tiers depending on how your team consumes the toolkit:

### Tier 1 -- Prompt / Skill Collection Only (`apm install`)

Install the skill contracts into any coding-agent harness via [APM](https://github.com/microsoft/apm):

```bash
apm install r-irbe/proof-skills                       # entire bundle (75 skills)
apm install r-irbe/proof-skills --skill lean-proof    # single skill
apm install r-irbe/proof-skills#v0.1.0                # version-pinned
```

- **Dependencies required**: **Zero** Python or Node.js packages.
- Each `skills/<name>/SKILL.md` contract and `templates/` skeleton is hoisted directly into the consumer harness (Copilot, Claude Code, Cursor, OpenCode, Codex, Gemini, or Windsurf) and works immediately.
- Note: APM 0.x hoists markdown skills only; it does not run `pip install`, `npm ci`, or initialize git submodules. Use Tier 2 or Tier 3 below when running offline Python scripts or the `lean-lsp` MCP server.

### Tier 2 -- Offline Python Scripts, Blueprints, AltProof & Audits

Clone the repository to run the enforcement, census, blueprint, zettelkasten, visualizer, and ontology tools:

```bash
git clone --recurse-submodules https://github.com/r-irbe/proof-skills
cd proof-skills
```

- **Core Lean 4 & Ontology scripts (`scripts/lean/*.py`, `scripts/lean/altproof/*.py`, `graph/graph_query.py`, `tools/lean-serve-broker/*`, `tools/visualizer/*`, `scripts/check-structure`, `scripts/lint/apm_validate.py`)**: **100% Python `>=3.10` standard library** (`sqlite3`, `json`, `re`, `ast`, `pathlib`, `argparse`, `subprocess`, `http.server`, `unittest`) -- **zero `pip` packages required**.
- **Optional Python packages** ([`requirements.txt`](requirements.txt) / [`pyproject.toml`](pyproject.toml)):
  ```bash
  pip install -r requirements.txt      # PyYAML>=6.0 for skill-audit/check_conformance.py & eval harnesses
  pip install ".[kuzu]"                # optional kuzu>=0.7.0 for native Kuzu DB federation (graph/kuzu_federation.py)
  pip install ".[dev]"                 # optional pytest>=8.0 + PyYAML>=6.0
  ```

### Tier 3 -- Full 21-Tool `lean-lsp` MCP Server + Rust/WASM `lean-analyzer`

Bootstrap submodules, Python packages, and the Node.js `lean-lsp` MCP server (`tools/lean-lsp-mcp`, requiring Node.js `>=22.6.0` or `>=20.0.0` with compiled `dist/index.js`) in one command:

```bash
bash scripts/setup-env.sh              # or: apm run setup (pass --venv to create .venv)
bash scripts/setup-env.sh --doctor     # or: apm run doctor (non-mutating health check)
```

- **Zero-touch MCP first-run bootstrap**: `tools/lean-lsp-mcp/bin/lean-lsp-mcp.js` automatically checks for `node_modules/@modelcontextprotocol/sdk` on startup and runs `npm ci --omit=dev` (redirecting all installer output to `stderr` so MCP stdio JSON-RPC on `stdout` is never polluted). Pointing any MCP client (Claude Code, Cursor, Gemini CLI, Antigravity, Copilot) at `bin/lean-lsp-mcp.js` works out of the box even before manual `npm install`.

---

## What is in here

| Directory | What it holds | Loaded by |
|---|---|---|
| [`skills/`](skills/) | 75 first-party `SKILL.md` files: toolchain setup, Lake building, proof tactics, MWE extraction, bisection, PR hygiene, Mathlib review, domain math, applied verticals, and end-to-end process workflows. | Harness, on demand. |
| [`skills/_overrides/`](skills/_overrides/) | 4 legacy REDIRECT stubs (`mathlib-build`, `mathlib-pr`, `mathlib-review`, `nightly-testing`) preserving deprecated slugs per Chesterton protocol. | Harness, on demand. |
| [`tools/lean-lsp-mcp/`](tools/lean-lsp-mcp/) | 21-tool `lean-lsp` Model Context Protocol server + embedded Rust/WASM `lean-analyzer` (`data/lean_analyzer.wasm`). | MCP client (`bin/lean-lsp-mcp.js`). |
| [`TAXONOMY.md`](TAXONOMY.md) | Authoritative classification mapping skills into Kernel, Roles, and Facets. | Planning / routing. |
| [`ROLES.md`](ROLES.md) | Stanford ACE Prover Swarm operational contracts (Specifier, Prover, Auditor, Gardener). | Multi-agent execution. |
| [`FACETS.md`](FACETS.md) | Domain Facets catalog (Math, AI, Governance packs). | Domain consumers. |
| [`templates/`](templates/) | copy-pasteable Lean module skeletons and workflow templates. Cross-template conventions live in [`templates/00-CONVENTIONS.md`](templates/00-CONVENTIONS.md). | Author, copy-paste. |
| [`references/`](references/) | background notes and layered skill handbooks; authoritative catalog in [`references/INDEX.md`](references/INDEX.md). | Skill, by link. |
| [`scripts/`](scripts/) | Project-agnostic helpers: `setup-env.sh` bootstrap/doctor, axiom audits, DAG layer checks, bridge validators, zettelkasten linters, eval, calibration, and Glicko-2 harnesses. None hardcodes a host project; each takes the project root as an argument. | Skill / CI / author. |
| [`zettelkasten/`](zettelkasten/) | Repo-internal knowledge graph (fleeting · literature · permanent · index · tags) that captures cross-skill insights. | Synthesizer skills. |
| [`vendor/`](vendor/) | Pinned git submodules of upstream sources (e.g. `leanprover-skills`) and SQLite ontology (`itp-ontology/itp_ontology_graph.db`). | Override dispatch & MCP. |

---

## Project Structure

For a deep dive into the exact directory layout and the purpose of every folder, please see [`references/project_structure.md`](references/project_structure.md) and [`USER_GUIDE.md`](USER_GUIDE.md).

## Tooling

| Script | Purpose |
|---|---|
| [`scripts/setup-env.sh`](scripts/setup-env.sh) | **Customer Bootstrap & Doctor (`apm run setup` / `apm run doctor`).** Initializes submodules, installs/verifies Python & Node MCP dependencies, checks Lean/SQLite/Kuzu artifacts, and prints MCP config snippets. |
| [`scripts/check-structure`](scripts/check-structure) | **Offline Structural Gate.** Checks `SKILL.md` frontmatter, line budgets, and duplicate descriptions (includes pure-stdlib YAML fallback). |
| [`scripts/lint/apm_validate.py`](scripts/lint/apm_validate.py) | **Hard-gated in CI.** Checks the package stays a valid APM skill collection: manifest keys, required `name` + `description` per `SKILL.md`, directory-name match, no duplicates (includes pure-stdlib YAML fallback). |
| [`scripts/skill-audit/check_conformance.py`](scripts/skill-audit/check_conformance.py) | **Hard-gated in CI.** Checks v2 conformance, tier coverage, handoff DAG integrity, handbook links, inline `@skill` refs, and relative Markdown links. |
| [`scripts/eval/run_eval.py`](scripts/eval/run_eval.py) | Deterministic smoke runner for the 50-case suite. |
| [`scripts/eval/calibrate_judge.py`](scripts/eval/calibrate_judge.py) | Pure replay calibration gate for known-bad judge corpora. |
| [`scripts/eval/multi_model.py`](scripts/eval/multi_model.py) | Converts persisted solver + judge artifacts into pairwise match rows. |
| [`scripts/elo/glicko2.py`](scripts/elo/glicko2.py) | Authoritative Glicko-2 leaderboard with uncertainty bands. |
| [`scripts/elo/elo.py`](scripts/elo/elo.py) | Legacy vanilla-ELO dashboard helper; do not use for release rankings. |

---

## Project-specific overrides

The toolkit is **deliberately project-agnostic** -- templates and skills
use `<Project>` / `<proj>` placeholders. Downstream projects encode
their concrete values in a thin override layer rather than forking the
templates; the rule is that an override file **links back to the
generic source and lists only the deltas**.

---

## Status & contracts

| Document | Covers |
|---|---|
| [`AGENTS.md`](AGENTS.md) | Full agent contract -- belief threshold, reversibility tiers, dispatch precedence, confidentiality rules. **Required reading before any edit.** |
| [`USER_GUIDE.md`](USER_GUIDE.md) | End-to-end operator guide for customer installation tiers, skill routing, MCP server integration, templates, and CI enforcement scripts. |
| [`apm.yml`](apm.yml) | Package metadata: name, version, license, keywords, repository, and `apm run` convenience scripts (`setup`, `doctor`, `lint-conformance`, `validate-apm`). |
| [`pyproject.toml`](pyproject.toml) / [`requirements.txt`](requirements.txt) | PEP 621 Python packaging metadata and optional dependency groups (`kuzu`, `dev`, `all`). |
| [`templates/00-CONVENTIONS.md`](templates/00-CONVENTIONS.md) | Cross-template conventions: file-doc header, section skeleton, proof-comment tags, anti-patterns checklist. |

---

<div align="center">
<sub>
Apache-2.0 · authored by <a href="https://github.com/r-irbe">@r-irbe</a> ·
issues & PRs welcome at
<a href="https://github.com/r-irbe/proof-skills">github.com/r-irbe/proof-skills</a>
</sub>
</div>
